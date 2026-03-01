import json
import time
import requests
from ..Sora2.kuai_utils import (env_or, ensure_list_from_urls,
                           http_headers_json, json_get)


def _first_non_empty(*values):
    for v in values:
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def _extract_error_message_from_json(data):
    if not isinstance(data, dict):
        return ""

    error = data.get("error")
    if isinstance(error, dict):
        msg = _first_non_empty(
            error.get("message"),
            error.get("msg"),
            error.get("detail"),
            error.get("reason"),
            error.get("error"),
        )
        if msg:
            return msg

    msg = _first_non_empty(
        data.get("message"),
        data.get("msg"),
        data.get("detail"),
        data.get("reason"),
        data.get("error_message"),
        data.get("fail_reason"),
        data.get("failure_reason"),
    )
    if msg:
        return msg

    # 常见嵌套字段回退
    nested_msg = _first_non_empty(
        json_get(data, "error.message", ""),
        json_get(data, "error.detail", ""),
        json_get(data, "moderation.message", ""),
        json_get(data, "safety.message", ""),
    )
    return nested_msg


def _extract_error_message_from_response(resp):
    try:
        data = resp.json()
    except Exception:
        data = None

    msg = _extract_error_message_from_json(data) if data is not None else ""
    if msg:
        return msg

    try:
        text = (resp.text or "").strip()
    except Exception:
        text = ""

    return text or f"HTTP {getattr(resp, 'status_code', 'unknown')}"


class VeoText2Video:
    """使用 Veo 模型进行文生视频"""
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True, "tooltip": "视频提示词（支持中英文）"}),
                "model": ([
                    "veo3.1",
                    "veo3",
                    "veo3-fast",
                    "veo3-pro",
                    "veo_3_1-fast",
                    "veo3.1-fast-components",
                    "veo_3_1-fast-4K",
                    "veo3.1-4k",
                    "veo3.1-pro-4k",
                ], {"default": "veo3.1", "tooltip": "模型选择"}),
                "aspect_ratio": (["16:9", "9:16"], {"default": "9:16", "tooltip": "视频宽高比"}),
                "enhance_prompt": ("BOOLEAN", {"default": True, "tooltip": "自动将中文提示词优化并翻译为英文"}),
                "enable_upsample": ("BOOLEAN", {"default": True, "tooltip": "启用超分以提升视频质量"}),
            },
            "optional": {
                "api_base": ("STRING", {"default": "https://api.kegeai.top", "tooltip": "API端点地址"}),
                "api_key": ("STRING", {"default": "", "tooltip": "API密钥"}),
                "timeout": ("INT", {"default": 120, "min": 5, "max": 600, "tooltip": "超时时间(秒)"}),
                "custom_model": ("STRING", {"default": "", "tooltip": "自定义模型名（留空使用下拉模型）"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("任务ID", "状态", "状态更新时间")
    FUNCTION = "create"
    CATEGORY = "KuAi/Veo3"

    def create(self, prompt, model, aspect_ratio, enhance_prompt, enable_upsample,
               api_base="https://api.kegeai.top", api_key="", timeout=120, custom_model=""):

        api_key = env_or(api_key, "KUAI_API_KEY")
        api_base = (api_base or "https://api.kegeai.top").strip()
        endpoint = api_base.rstrip("/") + "/v1/video/create"
        effective_model = (custom_model or "").strip() or model

        payload = {
            "model": effective_model,
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "enhance_prompt": bool(enhance_prompt),
            "enable_upsample": bool(enable_upsample),
        }

        try:
            resp = requests.post(endpoint, headers=http_headers_json(api_key), data=json.dumps(payload), timeout=int(timeout))
            if resp.status_code >= 400:
                detail = _extract_error_message_from_response(resp)
                raise RuntimeError(f"创建 Veo 视频失败: {detail}")
            data = resp.json()
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"创建 Veo 视频失败: {str(e)}")

        task_id = data.get("id") or ""
        status = data.get("status") or ""
        status_update_time = int(data.get("status_update_time") or 0)

        if not task_id:
            raise RuntimeError(f"创建响应缺少任务 ID: {json.dumps(data, ensure_ascii=False)}")

        return (task_id, status, status_update_time)

class VeoImage2Video:
    """使用 Veo 模型进行图生视频"""
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True, "tooltip": "视频提示词（支持中英文）"}),
                "model": ([
                    "veo3.1",
                    "veo3",
                    "veo3-fast",
                    "veo3-pro",
                    "veo3.1-components",
                    "veo2-fast-components",
                    "veo_3_1-fast",
                    "veo3.1-fast-components",
                    "veo_3_1-fast-4K",
                    "veo3.1-4k",
                    "veo3.1-pro-4k",
                ], {"default": "veo_3_1-fast", "tooltip": "模型选择"}),
                "aspect_ratio": (["16:9", "9:16"], {"default": "9:16", "tooltip": "视频宽高比"}),
                "enhance_prompt": ("BOOLEAN", {"default": True, "tooltip": "自动将中文提示词优化并翻译为英文"}),
                "enable_upsample": ("BOOLEAN", {"default": True, "tooltip": "启用超分以提升视频质量"}),
            },
            "optional": {
                "image_1": ("STRING", {"default": "", "multiline": False, "tooltip": "参考图1 URL (首帧)"}),
                "image_2": ("STRING", {"default": "", "multiline": False, "tooltip": "参考图2 URL (尾帧)"}),
                "image_3": ("STRING", {"default": "", "multiline": False, "tooltip": "参考图3 URL (元素)"}),
                "api_base": ("STRING", {"default": "https://api.kegeai.top", "tooltip": "API端点地址"}),
                "api_key": ("STRING", {"default": "", "tooltip": "API密钥"}),
                "timeout": ("INT", {"default": 120, "min": 5, "max": 600, "tooltip": "超时时间(秒)"}),
                "custom_model": ("STRING", {"default": "", "tooltip": "自定义模型名（留空使用下拉模型）"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("任务ID", "状态", "状态更新时间")
    FUNCTION = "create"
    CATEGORY = "KuAi/Veo3"

    def create(self, prompt, model, aspect_ratio, enhance_prompt, enable_upsample,
               image_1="", image_2="", image_3="",
               api_base="https://api.kegeai.top", api_key="", timeout=120, custom_model=""):

        api_key = env_or(api_key, "KUAI_API_KEY")
        api_base = (api_base or "https://api.kegeai.top").strip()
        endpoint = api_base.rstrip("/") + "/v1/video/create"
        effective_model = (custom_model or "").strip() or model

        images_list = []
        if image_1 and image_1.strip(): images_list.append(image_1.strip())
        if image_2 and image_2.strip(): images_list.append(image_2.strip())
        if image_3 and image_3.strip(): images_list.append(image_3.strip())

        if not images_list:
            raise RuntimeError("图生视频模式下，请至少提供一个图片 URL")

        payload = {
            "model": effective_model,
            "prompt": prompt,
            "images": images_list,
            "aspect_ratio": aspect_ratio,
            "enhance_prompt": bool(enhance_prompt),
            "enable_upsample": bool(enable_upsample),
        }

        try:
            resp = requests.post(endpoint, headers=http_headers_json(api_key), data=json.dumps(payload), timeout=int(timeout))
            if resp.status_code >= 400:
                detail = _extract_error_message_from_response(resp)
                raise RuntimeError(f"创建 Veo 视频失败: {detail}")
            data = resp.json()
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"创建 Veo 视频失败: {str(e)}")

        task_id = data.get("id") or ""
        status = data.get("status") or ""
        status_update_time = int(data.get("status_update_time") or 0)

        if not task_id:
            raise RuntimeError(f"创建响应缺少任务 ID: {json.dumps(data, ensure_ascii=False)}")

        return (task_id, status, status_update_time)


class VeoQueryTask:
    """查询 Veo 视频任务"""
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "task_id": ("STRING", {"default": "", "tooltip": "任务ID"}),
            },
            "optional": {
                "api_base": ("STRING", {"default": "https://api.kegeai.top", "tooltip": "API端点地址"}),
                "api_key": ("STRING", {"default": "", "tooltip": "API密钥"}),
                "wait": ("BOOLEAN", {"default": True, "tooltip": "是否等待任务完成"}),
                "poll_interval_sec": ("INT", {"default": 15, "min": 5, "max": 90, "tooltip": "轮询间隔(秒)"}),
                "timeout_sec": ("INT", {"default": 1800, "min": 600, "max": 9600, "tooltip": "总超时时间(秒)"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("状态", "视频URL", "增强后提示词", "原始响应JSON")
    FUNCTION = "query"
    CATEGORY = "KuAi/Veo3"

    def query(self, task_id, api_base="https://api.kegeai.top", api_key="", wait=True, poll_interval_sec=5, timeout_sec=600):
        api_key = env_or(api_key, "KUAI_API_KEY")
        endpoint = api_base.rstrip("/") + "/v1/video/query"

        def once():
            try:
                resp = requests.get(endpoint, headers=http_headers_json(api_key), params={"id": task_id}, timeout=60)
                if resp.status_code >= 400:
                    detail = _extract_error_message_from_response(resp)
                    raise RuntimeError(f"查询失败: {detail}")
                data = resp.json()
            except RuntimeError:
                raise
            except Exception as e:
                raise RuntimeError(f"查询失败: {str(e)}")

            status = data.get("status") or ""
            video_url = data.get("video_url") or ""
            enhanced_prompt = data.get("enhanced_prompt") or ""

            if status == "failed":
                fail_detail = _first_non_empty(
                    data.get("error_message"),
                    data.get("failure_reason"),
                    data.get("fail_reason"),
                    data.get("reason"),
                    data.get("message"),
                    json_get(data, "error.message", ""),
                    json_get(data, "error.detail", ""),
                    json_get(data, "result.error_message", ""),
                    json_get(data, "result.error.message", ""),
                ) or _extract_error_message_from_json(data)

                if not fail_detail:
                    fail_detail = json.dumps(data, ensure_ascii=False)

                raise RuntimeError(f"任务失败: {fail_detail}")

            if status == "completed" and not str(video_url).strip():
                missing_detail = _first_non_empty(
                    data.get("error_message"),
                    data.get("message"),
                    data.get("reason"),
                ) or "任务已完成但未返回视频URL"
                raise RuntimeError(f"查询失败: {missing_detail}")

            return status, video_url, enhanced_prompt, json.dumps(data, ensure_ascii=False)

        if not wait:
            return once()

        print(f"[VeoQueryTask] 开始轮询任务 {task_id}，超时 {timeout_sec} 秒，间隔 {poll_interval_sec} 秒")
        deadline = time.time() + int(timeout_sec)
        last_raw = ""
        poll_count = 0
        while time.time() < deadline:
            poll_count += 1
            status, video_url, enhanced_prompt, raw = once()
            last_raw = raw
            print(f"[VeoQueryTask] 第 {poll_count} 次查询: 状态={status}")
            if status in ("completed", "failed"):
                print(f"[VeoQueryTask] 任务完成: {status}")
                return (status, video_url, enhanced_prompt, raw)
            time.sleep(int(poll_interval_sec))
        
        print(f"[VeoQueryTask] 轮询超时")
        return ("timeout", "", "", last_raw or json.dumps({"error": "timeout"}, ensure_ascii=False))


class VeoText2VideoAndWait:
    """一键文生视频并等待"""
    @classmethod
    def INPUT_TYPES(cls):
        inputs = VeoText2Video.INPUT_TYPES()
        query_inputs = VeoQueryTask.INPUT_TYPES()["optional"]
        query_inputs.pop("api_base", None)
        query_inputs.pop("api_key", None)
        inputs["optional"].update(query_inputs)
        inputs["optional"].pop("task_id", None)
        inputs["optional"].pop("wait", None)
        return inputs
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("状态", "视频URL", "增强后提示词", "任务ID")
    FUNCTION = "run"
    CATEGORY = "KuAi/Veo3"
    
    def run(self, **kwargs):
        creator_kwargs = {k: v for k, v in kwargs.items() if k in VeoText2Video.INPUT_TYPES()["required"] or k in VeoText2Video.INPUT_TYPES()["optional"]}
        querier_kwargs = {k: v for k, v in kwargs.items() if k in VeoQueryTask.INPUT_TYPES()["optional"]}
        
        creator = VeoText2Video()
        task_id, _, _ = creator.create(**creator_kwargs)
        
        querier_kwargs["api_base"] = creator_kwargs.get("api_base", "https://api.kegeai.top")
        querier_kwargs["api_key"] = creator_kwargs.get("api_key", "")

        querier = VeoQueryTask()
        status, video_url, enhanced_prompt, _ = querier.query(task_id=task_id, wait=True, **querier_kwargs)
        
        return (status, video_url, enhanced_prompt, task_id)

class VeoImage2VideoAndWait:
    """一键图生视频并等待"""
    @classmethod
    def INPUT_TYPES(cls):
        inputs = VeoImage2Video.INPUT_TYPES()
        query_inputs = VeoQueryTask.INPUT_TYPES()["optional"]
        query_inputs.pop("api_base", None)
        query_inputs.pop("api_key", None)
        inputs["optional"].update(query_inputs)
        inputs["optional"].pop("task_id", None)
        inputs["optional"].pop("wait", None)
        return inputs

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("状态", "视频URL", "增强后提示词", "任务ID")
    FUNCTION = "run"
    CATEGORY = "KuAi/Veo3"

    def run(self, **kwargs):
        creator_kwargs = {}
        # 从 kwargs 中分离出创建节点的参数
        creator_input_types = VeoImage2Video.INPUT_TYPES()
        creator_required_keys = creator_input_types["required"].keys()
        creator_optional_keys = creator_input_types["optional"].keys()
        for k, v in kwargs.items():
            if k in creator_required_keys or k in creator_optional_keys:
                creator_kwargs[k] = v

        # 从 kwargs 中分离出查询节点的参数
        querier_kwargs = {k: v for k, v in kwargs.items() if k in VeoQueryTask.INPUT_TYPES()["optional"]}
        
        creator = VeoImage2Video()
        task_id, _, _ = creator.create(**creator_kwargs)

        querier_kwargs["api_base"] = creator_kwargs.get("api_base", "https://api.kegeai.top")
        querier_kwargs["api_key"] = creator_kwargs.get("api_key", "")

        querier = VeoQueryTask()
        status, video_url, enhanced_prompt, _ = querier.query(task_id=task_id, wait=True, **querier_kwargs)
        
        return (status, video_url, enhanced_prompt, task_id)


NODE_CLASS_MAPPINGS = {
    "VeoText2Video": VeoText2Video,
    "VeoImage2Video": VeoImage2Video,
    "VeoQueryTask": VeoQueryTask,
    "VeoText2VideoAndWait": VeoText2VideoAndWait,
    "VeoImage2VideoAndWait": VeoImage2VideoAndWait,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VeoText2Video": "🎬 Veo 文生视频",
    "VeoImage2Video": "🖼️ Veo 图生视频",
    "VeoQueryTask": "🔍 Veo 查询任务",
    "VeoText2VideoAndWait": "⚡ Veo 一键文生视频",
    "VeoImage2VideoAndWait": "⚡ Veo 一键图生视频",
}