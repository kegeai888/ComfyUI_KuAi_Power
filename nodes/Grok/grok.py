"""Grok 视频生成节点"""

import os
import time
import requests
from ..Sora2.kuai_utils import env_or, http_headers_json, http_headers_auth_only, raise_for_bad_status, ensure_list_from_urls


class GrokCreateVideo:
    """创建 Grok 视频生成任务"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "视频生成提示词"
                }),
                "model": (["grok-video-3 (6秒)", "grok-video-3-10s (10秒)"], {
                    "default": "grok-video-3 (6秒)",
                    "tooltip": "选择 Grok 模型"
                }),
                "aspect_ratio": (["1:1", "2:3", "3:2"], {
                    "default": "3:2",
                    "tooltip": "视频宽高比"
                }),
                "size": (["720P", "1080P"], {
                    "default": "1080P",
                    "tooltip": "视频分辨率"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "tooltip": "API密钥（留空使用环境变量 KUAI_API_KEY）"
                }),
            },
            "optional": {
                "image_urls": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "参考图片URL（多个用逗号、分号或换行分隔）"
                }),
                "api_base": ("STRING", {
                    "default": "https://api.kegeai.top",
                    "tooltip": "API端点地址"
                }),
            }
        }

    @classmethod
    def INPUT_LABELS(cls):
        return {
            "prompt": "提示词",
            "model": "模型",
            "aspect_ratio": "宽高比",
            "size": "分辨率",
            "api_key": "API密钥",
            "image_urls": "参考图片URL",
            "api_base": "API地址"
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("任务ID", "状态", "增强提示词")
    FUNCTION = "create"
    CATEGORY = "KuAi/Grok"

    def create(self, prompt, model, aspect_ratio, size, api_key="", image_urls="", api_base="https://api.kegeai.top"):
        """创建 Grok 视频生成任务"""
        api_key = env_or(api_key, "KUAI_API_KEY")
        if not api_key:
            raise RuntimeError("API Key 未配置，请在节点参数或环境变量中设置 KUAI_API_KEY")

        api_base = api_base.rstrip("/")
        headers = http_headers_auth_only(api_key)

        # 提取实际的模型名称（去掉时长说明）
        actual_model = model.split(" (")[0] if " (" in model else model

        # 解析图片URL列表
        images = ensure_list_from_urls(image_urls) if image_urls else []

        payload = {
            "model": actual_model,
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "size": size,
            "images": images
        }

        print(f"[ComfyUI_KuAi_Power] Grok 创建视频任务: {prompt[:50]}...")

        try:
            resp = requests.post(
                f"{api_base}/v1/video/create",
                json=payload,
                headers=headers,
                timeout=30
            )
            raise_for_bad_status(resp, "Grok 视频创建失败")

            result = resp.json()
            task_id = result.get("id", "")
            status = result.get("status", "pending")
            enhanced_prompt = result.get("enhanced_prompt", "")

            print(f"[ComfyUI_KuAi_Power] Grok 任务已创建: {task_id}, 状态: {status}")

            return (task_id, status, enhanced_prompt)

        except Exception as e:
            raise RuntimeError(f"Grok 视频创建失败: {str(e)}")


class GrokQueryVideo:
    """查询 Grok 视频生成任务状态"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "task_id": ("STRING", {
                    "default": "",
                    "tooltip": "任务ID"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "tooltip": "API密钥（留空使用环境变量 KUAI_API_KEY）"
                }),
            },
            "optional": {
                "api_base": ("STRING", {
                    "default": "https://api.kegeai.top",
                    "tooltip": "API端点地址"
                }),
            }
        }

    @classmethod
    def INPUT_LABELS(cls):
        return {
            "task_id": "任务ID",
            "api_key": "API密钥",
            "api_base": "API地址"
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "INT")
    RETURN_NAMES = ("任务ID", "状态", "视频URL", "增强提示词", "状态更新时间")
    FUNCTION = "query"
    CATEGORY = "KuAi/Grok"

    def query(self, task_id, api_key="", api_base="https://api.kegeai.top"):
        """查询 Grok 视频生成任务状态"""
        api_key = env_or(api_key, "KUAI_API_KEY")
        if not api_key:
            raise RuntimeError("API Key 未配置，请在节点参数或环境变量中设置 KUAI_API_KEY")

        if not task_id:
            raise RuntimeError("任务ID不能为空")

        api_base = api_base.rstrip("/")
        headers = http_headers_json(api_key)

        print(f"[ComfyUI_KuAi_Power] Grok 查询任务: {task_id}")

        try:
            resp = requests.get(
                f"{api_base}/v1/video/query",
                params={"id": task_id},
                headers=headers,
                timeout=30
            )
            raise_for_bad_status(resp, "Grok 视频查询失败")

            result = resp.json()
            status = result.get("status", "unknown")
            video_url = result.get("video_url") or ""
            enhanced_prompt = result.get("enhanced_prompt", "")
            status_update_time = int(result.get("status_update_time", 0))

            print(f"[ComfyUI_KuAi_Power] Grok 任务状态: {status}")
            if video_url:
                print(f"[ComfyUI_KuAi_Power] Grok 视频URL: {video_url}")

            return (task_id, status, video_url, enhanced_prompt, status_update_time)

        except Exception as e:
            raise RuntimeError(f"Grok 视频查询失败: {str(e)}")


class GrokCreateAndWait:
    """创建 Grok 视频并等待完成（一键生成）"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "视频生成提示词"
                }),
                "model": (["grok-video-3 (6秒)", "grok-video-3-10s (10秒)"], {
                    "default": "grok-video-3 (6秒)",
                    "tooltip": "选择 Grok 模型"
                }),
                "aspect_ratio": (["1:1", "2:3", "3:2"], {
                    "default": "3:2",
                    "tooltip": "视频宽高比"
                }),
                "size": (["720P", "1080P"], {
                    "default": "1080P",
                    "tooltip": "视频分辨率"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "tooltip": "API密钥（留空使用环境变量 KUAI_API_KEY）"
                }),
            },
            "optional": {
                "image_urls": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "参考图片URL（多个用逗号、分号或换行分隔）"
                }),
                "api_base": ("STRING", {
                    "default": "https://api.kegeai.top",
                    "tooltip": "API端点地址"
                }),
                "max_wait_time": ("INT", {
                    "default": 1200,
                    "min": 60,
                    "max": 1800,
                    "tooltip": "最大等待时间（秒）"
                }),
                "poll_interval": ("INT", {
                    "default": 10,
                    "min": 5,
                    "max": 60,
                    "tooltip": "轮询间隔（秒）"
                }),
            }
        }

    @classmethod
    def INPUT_LABELS(cls):
        return {
            "prompt": "提示词",
            "model": "模型",
            "aspect_ratio": "宽高比",
            "size": "分辨率",
            "api_key": "API密钥",
            "image_urls": "参考图片URL",
            "api_base": "API地址",
            "max_wait_time": "最大等待时间",
            "poll_interval": "轮询间隔"
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("任务ID", "状态", "视频URL", "增强提示词")
    FUNCTION = "create_and_wait"
    CATEGORY = "KuAi/Grok"

    def create_and_wait(self, prompt, model, aspect_ratio, size, api_key="",
                       image_urls="", api_base="https://api.kegeai.top",
                       max_wait_time=1200, poll_interval=10):
        """创建 Grok 视频并等待完成"""
        # 创建任务
        creator = GrokCreateVideo()
        task_id, status, enhanced_prompt = creator.create(
            prompt, model, aspect_ratio, size, api_key, image_urls, api_base
        )

        # 如果已经完成，直接返回
        if status in ["completed", "failed"]:
            querier = GrokQueryVideo()
            task_id, status, video_url, enhanced_prompt, _ = querier.query(task_id, api_key, api_base)
            return (task_id, status, video_url, enhanced_prompt)

        # 轮询等待完成
        print(f"[ComfyUI_KuAi_Power] Grok 等待视频生成完成，最多等待 {max_wait_time} 秒...")

        querier = GrokQueryVideo()
        elapsed = 0

        while elapsed < max_wait_time:
            time.sleep(poll_interval)
            elapsed += poll_interval

            try:
                task_id, status, video_url, enhanced_prompt, _ = querier.query(task_id, api_key, api_base)

                if status == "completed":
                    print(f"[ComfyUI_KuAi_Power] Grok 视频生成完成！")
                    return (task_id, status, video_url, enhanced_prompt)
                elif status == "failed":
                    raise RuntimeError(f"Grok 视频生成失败，任务ID: {task_id}")

                print(f"[ComfyUI_KuAi_Power] Grok 任务进行中... 已等待 {elapsed}/{max_wait_time} 秒")

            except Exception as e:
                print(f"[ComfyUI_KuAi_Power] Grok 查询出错: {str(e)}")
                # 继续等待，不立即失败

        # 超时
        raise RuntimeError(
            f"Grok 视频生成超时（等待了 {max_wait_time} 秒）。"
            f"任务ID: {task_id}，可使用查询节点继续检查状态。"
        )


class GrokImage2Video:
    """Grok 图生视频创建节点（images 必需）"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "图片URL列表（多个用逗号、分号或换行分隔）- 必需"
                }),
                "prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "视频生成提示词"
                }),
                "model": (["grok-video-3 (6秒)", "grok-video-3-10s (10秒)"], {
                    "default": "grok-video-3 (6秒)",
                    "tooltip": "选择 Grok 模型"
                }),
                "aspect_ratio": (["1:1", "2:3", "3:2"], {
                    "default": "3:2",
                    "tooltip": "视频宽高比"
                }),
                "size": (["720P", "1080P"], {
                    "default": "720P",
                    "tooltip": "视频分辨率（暂只支持720P）"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "tooltip": "API密钥（留空使用环境变量 KUAI_API_KEY）"
                }),
            },
            "optional": {
                "api_base": ("STRING", {
                    "default": "https://api.kegeai.top",
                    "tooltip": "API端点地址"
                }),
            }
        }

    @classmethod
    def INPUT_LABELS(cls):
        return {
            "images": "图片列表",
            "prompt": "提示词",
            "model": "模型",
            "aspect_ratio": "宽高比",
            "size": "分辨率",
            "api_key": "API密钥",
            "api_base": "API地址"
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "INT")
    RETURN_NAMES = ("任务ID", "状态", "增强提示词", "状态更新时间")
    FUNCTION = "create"
    CATEGORY = "KuAi/Grok"

    def create(self, images, prompt, model, aspect_ratio, size, api_key="", api_base="https://api.kegeai.top"):
        """创建 Grok 图生视频任务"""
        # 1. 解析 API key
        api_key = env_or(api_key, "KUAI_API_KEY")
        if not api_key:
            raise RuntimeError("API Key 未配置，请在节点参数或环境变量中设置 KUAI_API_KEY")

        # 2. 解析图片列表（必需）
        images_list = ensure_list_from_urls(images)
        if not images_list:
            raise RuntimeError("请至少提供一个图片 URL")

        # 3. 构建请求
        api_base = api_base.rstrip("/")
        headers = http_headers_auth_only(api_key)

        # 提取实际的模型名称（去掉时长说明）
        actual_model = model.split(" (")[0] if " (" in model else model

        payload = {
            "model": actual_model,
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "size": size,
            "images": images_list
        }

        print(f"[ComfyUI_KuAi_Power] Grok 图生视频任务: {prompt[:50]}... (图片数: {len(images_list)})")

        # 4. 调用 API
        try:
            resp = requests.post(
                f"{api_base}/v1/video/create",
                json=payload,
                headers=headers,
                timeout=30
            )
            raise_for_bad_status(resp, "Grok 图生视频创建失败")

            result = resp.json()
            task_id = result.get("id", "")
            status = result.get("status", "pending")
            enhanced_prompt = result.get("enhanced_prompt", "")
            status_update_time = int(result.get("status_update_time", 0))

            if not task_id:
                raise RuntimeError(f"创建响应缺少任务 ID")

            print(f"[ComfyUI_KuAi_Power] Grok 图生视频任务已创建: {task_id}, 状态: {status}")

            return (task_id, status, enhanced_prompt, status_update_time)

        except Exception as e:
            raise RuntimeError(f"Grok 图生视频创建失败: {str(e)}")


class GrokImage2VideoAndWait:
    """Grok 图生视频一键生成节点（images 必需）"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "图片URL列表（多个用逗号、分号或换行分隔）- 必需"
                }),
                "prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "视频生成提示词"
                }),
                "model": (["grok-video-3 (6秒)", "grok-video-3-10s (10秒)"], {
                    "default": "grok-video-3 (6秒)",
                    "tooltip": "选择 Grok 模型"
                }),
                "aspect_ratio": (["1:1", "2:3", "3:2"], {
                    "default": "3:2",
                    "tooltip": "视频宽高比"
                }),
                "size": (["720P", "1080P"], {
                    "default": "720P",
                    "tooltip": "视频分辨率（暂只支持720P）"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "tooltip": "API密钥（留空使用环境变量 KUAI_API_KEY）"
                }),
            },
            "optional": {
                "api_base": ("STRING", {
                    "default": "https://api.kegeai.top",
                    "tooltip": "API端点地址"
                }),
                "max_wait_time": ("INT", {
                    "default": 1200,
                    "min": 60,
                    "max": 1800,
                    "tooltip": "最大等待时间（秒）"
                }),
                "poll_interval": ("INT", {
                    "default": 10,
                    "min": 5,
                    "max": 60,
                    "tooltip": "轮询间隔（秒）"
                }),
            }
        }

    @classmethod
    def INPUT_LABELS(cls):
        return {
            "images": "图片列表",
            "prompt": "提示词",
            "model": "模型",
            "aspect_ratio": "宽高比",
            "size": "分辨率",
            "api_key": "API密钥",
            "api_base": "API地址",
            "max_wait_time": "最大等待时间",
            "poll_interval": "轮询间隔"
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("任务ID", "状态", "视频URL", "增强提示词")
    FUNCTION = "create_and_wait"
    CATEGORY = "KuAi/Grok"

    def create_and_wait(self, images, prompt, model, aspect_ratio, size,
                       api_key="", api_base="https://api.kegeai.top",
                       max_wait_time=1200, poll_interval=10):
        """创建 Grok 图生视频并等待完成"""
        # 1. 创建任务
        creator = GrokImage2Video()
        task_id, status, enhanced_prompt, _ = creator.create(
            images, prompt, model, aspect_ratio, size, api_key, api_base
        )

        # 2. 如果已经完成，直接返回
        if status in ["completed", "failed"]:
            querier = GrokQueryVideo()
            task_id, status, video_url, enhanced_prompt, _ = querier.query(task_id, api_key, api_base)
            return (task_id, status, video_url, enhanced_prompt)

        # 3. 轮询等待完成
        print(f"[ComfyUI_KuAi_Power] Grok 等待图生视频完成，最多等待 {max_wait_time} 秒...")

        querier = GrokQueryVideo()
        elapsed = 0

        while elapsed < max_wait_time:
            time.sleep(poll_interval)
            elapsed += poll_interval

            try:
                task_id, status, video_url, enhanced_prompt, _ = querier.query(task_id, api_key, api_base)

                if status == "completed":
                    print(f"[ComfyUI_KuAi_Power] Grok 图生视频完成！")
                    return (task_id, status, video_url, enhanced_prompt)
                elif status == "failed":
                    raise RuntimeError(f"Grok 图生视频失败，任务ID: {task_id}")

                print(f"[ComfyUI_KuAi_Power] Grok 任务进行中... 已等待 {elapsed}/{max_wait_time} 秒")

            except Exception as e:
                print(f"[ComfyUI_KuAi_Power] Grok 查询出错: {str(e)}")
                # 继续等待，不立即失败

        # 4. 超时
        raise RuntimeError(
            f"Grok 图生视频超时（等待了 {max_wait_time} 秒）。"
            f"任务ID: {task_id}，可使用查询节点继续检查状态。"
        )


class GrokText2Video:
    """Grok 文生视频创建节点"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "视频生成提示词"
                }),
                "model": (["grok-video-3 (6秒)", "grok-video-3-10s (10秒)"], {
                    "default": "grok-video-3 (6秒)",
                    "tooltip": "选择 Grok 模型"
                }),
                "aspect_ratio": (["1:1", "2:3", "3:2"], {
                    "default": "3:2",
                    "tooltip": "视频宽高比"
                }),
                "size": (["720P", "1080P"], {
                    "default": "720P",
                    "tooltip": "视频分辨率（暂只支持720P）"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "tooltip": "API密钥（留空使用环境变量 KUAI_API_KEY）"
                }),
            },
            "optional": {
                "api_base": ("STRING", {
                    "default": "https://api.kegeai.top",
                    "tooltip": "API端点地址"
                }),
            }
        }

    @classmethod
    def INPUT_LABELS(cls):
        return {
            "prompt": "提示词",
            "model": "模型",
            "aspect_ratio": "宽高比",
            "size": "分辨率",
            "api_key": "API密钥",
            "api_base": "API地址"
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("任务ID", "状态", "增强提示词")
    FUNCTION = "create"
    CATEGORY = "KuAi/Grok"

    def create(self, prompt, model, aspect_ratio, size, api_key="", api_base="https://api.kegeai.top"):
        """创建 Grok 文生视频任务"""
        api_key = env_or(api_key, "KUAI_API_KEY")
        if not api_key:
            raise RuntimeError("API Key 未配置，请在节点参数或环境变量中设置 KUAI_API_KEY")

        api_base = api_base.rstrip("/")
        headers = http_headers_auth_only(api_key)

        # 提取实际的模型名称（去掉时长说明）
        actual_model = model.split(" (")[0] if " (" in model else model

        payload = {
            "model": actual_model,
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "size": size,
            "images": []  # 文生视频不需要图片
        }

        print(f"[ComfyUI_KuAi_Power] Grok 文生视频任务: {prompt[:50]}...")

        try:
            resp = requests.post(
                f"{api_base}/v1/video/create",
                json=payload,
                headers=headers,
                timeout=30
            )
            raise_for_bad_status(resp, "Grok 文生视频创建失败")

            result = resp.json()
            task_id = result.get("id", "")
            status = result.get("status", "pending")
            enhanced_prompt = result.get("enhanced_prompt", "")

            print(f"[ComfyUI_KuAi_Power] Grok 文生视频任务已创建: {task_id}, 状态: {status}")

            return (task_id, status, enhanced_prompt)

        except Exception as e:
            raise RuntimeError(f"Grok 文生视频创建失败: {str(e)}")


class GrokText2VideoAndWait:
    """Grok 文生视频一键生成节点"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "视频生成提示词"
                }),
                "model": (["grok-video-3 (6秒)", "grok-video-3-10s (10秒)"], {
                    "default": "grok-video-3 (6秒)",
                    "tooltip": "选择 Grok 模型"
                }),
                "aspect_ratio": (["1:1", "2:3", "3:2"], {
                    "default": "3:2",
                    "tooltip": "视频宽高比"
                }),
                "size": (["720P", "1080P"], {
                    "default": "720P",
                    "tooltip": "视频分辨率（暂只支持720P）"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "tooltip": "API密钥（留空使用环境变量 KUAI_API_KEY）"
                }),
            },
            "optional": {
                "api_base": ("STRING", {
                    "default": "https://api.kegeai.top",
                    "tooltip": "API端点地址"
                }),
                "max_wait_time": ("INT", {
                    "default": 1200,
                    "min": 60,
                    "max": 1800,
                    "tooltip": "最大等待时间（秒）"
                }),
                "poll_interval": ("INT", {
                    "default": 10,
                    "min": 5,
                    "max": 60,
                    "tooltip": "轮询间隔（秒）"
                }),
            }
        }

    @classmethod
    def INPUT_LABELS(cls):
        return {
            "prompt": "提示词",
            "model": "模型",
            "aspect_ratio": "宽高比",
            "size": "分辨率",
            "api_key": "API密钥",
            "api_base": "API地址",
            "max_wait_time": "最大等待时间",
            "poll_interval": "轮询间隔"
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("任务ID", "状态", "视频URL", "增强提示词")
    FUNCTION = "create_and_wait"
    CATEGORY = "KuAi/Grok"

    def create_and_wait(self, prompt, model, aspect_ratio, size,
                       api_key="", api_base="https://api.kegeai.top",
                       max_wait_time=1200, poll_interval=10):
        """创建 Grok 文生视频并等待完成"""
        # 1. 创建任务
        creator = GrokText2Video()
        task_id, status, enhanced_prompt = creator.create(
            prompt, model, aspect_ratio, size, api_key, api_base
        )

        # 2. 如果已经完成，直接返回
        if status in ["completed", "failed"]:
            querier = GrokQueryVideo()
            task_id, status, video_url, enhanced_prompt, _ = querier.query(task_id, api_key, api_base)
            return (task_id, status, video_url, enhanced_prompt)

        # 3. 轮询等待完成
        print(f"[ComfyUI_KuAi_Power] Grok 等待文生视频完成，最多等待 {max_wait_time} 秒...")

        querier = GrokQueryVideo()
        elapsed = 0

        while elapsed < max_wait_time:
            time.sleep(poll_interval)
            elapsed += poll_interval

            try:
                task_id, status, video_url, enhanced_prompt, _ = querier.query(task_id, api_key, api_base)

                if status == "completed":
                    print(f"[ComfyUI_KuAi_Power] Grok 文生视频完成！")
                    return (task_id, status, video_url, enhanced_prompt)
                elif status == "failed":
                    raise RuntimeError(f"Grok 文生视频失败，任务ID: {task_id}")

                print(f"[ComfyUI_KuAi_Power] Grok 任务进行中... 已等待 {elapsed}/{max_wait_time} 秒")

            except Exception as e:
                print(f"[ComfyUI_KuAi_Power] Grok 查询出错: {str(e)}")
                # 继续等待，不立即失败

        # 4. 超时
        raise RuntimeError(
            f"Grok 文生视频超时（等待了 {max_wait_time} 秒）。"
            f"任务ID: {task_id}，可使用查询节点继续检查状态。"
        )

