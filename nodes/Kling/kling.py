"""可灵视频生成核心节点"""

import json
import time
import requests
from ..Sora2.kuai_utils import env_or, http_headers_json, raise_for_bad_status
from .kling_utils import parse_kling_response, KLING_MODELS, KLING_ASPECT_RATIOS


class KlingText2Video:
    """可灵文生视频节点"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "视频提示词"
                }),
                "model_name": (KLING_MODELS, {
                    "default": "kling-v1",
                    "tooltip": "模型选择"
                }),
                "mode": (["std", "pro"], {
                    "default": "std",
                    "tooltip": "生成模式：std（标准）, pro（专家）"
                }),
                "duration": (["5", "10"], {
                    "default": "5",
                    "tooltip": "视频时长（秒）"
                }),
                "aspect_ratio": (KLING_ASPECT_RATIOS, {
                    "default": "16:9",
                    "tooltip": "视频宽高比"
                }),
            },
            "optional": {
                "negative_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "负面提示词"
                }),
                "cfg_scale": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.1,
                    "tooltip": "提示词引导强度"
                }),
                "multi_shot": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否生成多镜头视频"
                }),
                "watermark": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否添加水印"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "tooltip": "API密钥（留空使用环境变量 KUAI_API_KEY）"
                }),
                "api_base": ("STRING", {
                    "default": "https://api.kuai.host",
                    "tooltip": "API端点地址"
                }),
                "timeout": ("INT", {
                    "default": 120,
                    "min": 5,
                    "max": 600,
                    "tooltip": "超时时间(秒)"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("任务ID", "状态", "创建时间")
    FUNCTION = "create"
    CATEGORY = "KuAi/Kling"

    @classmethod
    def INPUT_LABELS(cls):
        return {
            "prompt": "提示词",
            "model_name": "模型名称",
            "mode": "模式",
            "duration": "时长",
            "aspect_ratio": "宽高比",
            "negative_prompt": "负面提示词",
            "cfg_scale": "CFG强度",
            "multi_shot": "多镜头",
            "watermark": "水印",
            "api_key": "API密钥",
            "api_base": "API地址",
            "timeout": "超时",
        }

    def create(self, prompt, model_name="kling-v1", mode="std", duration="5", aspect_ratio="16:9",
               negative_prompt="", cfg_scale=0.5, multi_shot=False, watermark=False,
               api_key="", api_base="https://api.kuai.host", timeout=120):
        """创建文生视频任务"""

        # 解析 API key
        api_key = env_or(api_key, "KUAI_API_KEY")
        if not api_key:
            raise RuntimeError("API Key 未配置，请在节点参数或环境变量中设置")

        # 构建请求
        endpoint = api_base.rstrip("/") + "/kling/v1/videos/text2video"
        headers = http_headers_json(api_key)

        payload = {
            "model_name": model_name,
            "prompt": prompt,
            "mode": mode,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "multi_shot": multi_shot,
            "watermark_info": {
                "enabled": watermark
            }
        }

        # 添加可选参数
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt

        if cfg_scale != 0.5:
            payload["cfg_scale"] = cfg_scale

        # 调用 API
        try:
            print(f"[ComfyUI_KuAi_Power] 创建可灵文生视频任务: {model_name}, {mode}, {duration}s")
            resp = requests.post(endpoint, headers=headers, json=payload, timeout=int(timeout))
            raise_for_bad_status(resp, "创建文生视频任务失败")

            data = resp.json()
            task_id, status, created_at = parse_kling_response(data)

            if not task_id:
                raise RuntimeError(f"创建响应缺少任务 ID: {json.dumps(data, ensure_ascii=False)}")

            print(f"[ComfyUI_KuAi_Power] 任务创建成功: {task_id}, 状态: {status}")
            return (task_id, status, created_at)

        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"创建文生视频任务失败: {str(e)}")


class KlingImage2Video:
    """可灵图生视频节点"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "图片 URL 或 Base64 编码"
                }),
                "model_name": (KLING_MODELS, {
                    "default": "kling-v1",
                    "tooltip": "模型选择"
                }),
                "mode": (["std", "pro"], {
                    "default": "std",
                    "tooltip": "生成模式：std（标准）, pro（专家）"
                }),
                "duration": (["5", "10"], {
                    "default": "5",
                    "tooltip": "视频时长（秒）"
                }),
            },
            "optional": {
                "prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "提示词（可选，用于引导生成）"
                }),
                "image_tail": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "尾帧图片 URL 或 Base64"
                }),
                "negative_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "负面提示词"
                }),
                "cfg_scale": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.1,
                    "tooltip": "提示词引导强度"
                }),
                "multi_shot": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否生成多镜头视频"
                }),
                "watermark": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否添加水印"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "tooltip": "API密钥（留空使用环境变量 KUAI_API_KEY）"
                }),
                "api_base": ("STRING", {
                    "default": "https://api.kuai.host",
                    "tooltip": "API端点地址"
                }),
                "timeout": ("INT", {
                    "default": 120,
                    "min": 5,
                    "max": 600,
                    "tooltip": "超时时间(秒)"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("任务ID", "状态", "创建时间")
    FUNCTION = "create"
    CATEGORY = "KuAi/Kling"

    @classmethod
    def INPUT_LABELS(cls):
        return {
            "image": "图片",
            "model_name": "模型名称",
            "mode": "模式",
            "duration": "时长",
            "prompt": "提示词",
            "image_tail": "尾帧图片",
            "negative_prompt": "负面提示词",
            "cfg_scale": "CFG强度",
            "multi_shot": "多镜头",
            "watermark": "水印",
            "api_key": "API密钥",
            "api_base": "API地址",
            "timeout": "超时",
        }

    def create(self, image, model_name="kling-v1", mode="std", duration="5",
               prompt="", image_tail="", negative_prompt="", cfg_scale=0.5, multi_shot=False, watermark=False,
               api_key="", api_base="https://api.kuai.host", timeout=120):
        """创建图生视频任务"""

        # 解析 API key
        api_key = env_or(api_key, "KUAI_API_KEY")
        if not api_key:
            raise RuntimeError("API Key 未配置，请在节点参数或环境变量中设置")

        if not image:
            raise RuntimeError("请提供图片 URL 或 Base64 编码")

        # 构建请求
        endpoint = api_base.rstrip("/") + "/kling/v1/videos/image2video"
        headers = http_headers_json(api_key)

        payload = {
            "model_name": model_name,
            "image": image,
            "mode": mode,
            "duration": duration,
            "multi_shot": multi_shot,
            "watermark_info": {
                "enabled": watermark
            }
        }

        # 添加可选参数
        if prompt:
            payload["prompt"] = prompt

        if image_tail:
            payload["image_tail"] = image_tail

        if negative_prompt:
            payload["negative_prompt"] = negative_prompt

        if cfg_scale != 0.5:
            payload["cfg_scale"] = cfg_scale

        # 调用 API
        try:
            print(f"[ComfyUI_KuAi_Power] 创建可灵图生视频任务: {model_name}, {mode}, {duration}s")
            resp = requests.post(endpoint, headers=headers, json=payload, timeout=int(timeout))
            raise_for_bad_status(resp, "创建图生视频任务失败")

            data = resp.json()
            task_id, status, created_at = parse_kling_response(data)

            if not task_id:
                raise RuntimeError(f"创建响应缺少任务 ID: {json.dumps(data, ensure_ascii=False)}")

            print(f"[ComfyUI_KuAi_Power] 任务创建成功: {task_id}, 状态: {status}")
            return (task_id, status, created_at)

        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"创建图生视频任务失败: {str(e)}")
