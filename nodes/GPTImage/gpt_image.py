"""GPT Image 2 节点 - 文生图和图片编辑"""

import io
import requests
import numpy as np
import torch
from PIL import Image

from ..Sora2.kuai_utils import (
    env_or,
    http_headers_json,
    http_headers_multipart,
    raise_for_bad_status,
)

MODELS = ["gpt-image-2", "gpt-image-2-all"]
SIZES = [
    "auto（默认）",
    "1024x1024（1:1｜正方形）",
    "1536x1024（3:2｜横版）",
    "1024x1536（2:3｜竖版）",
    "2048x2048（1:1｜2K正方形）",
    "2048x1152（16:9｜2K横版）",
    "3840x2160（16:9｜4K横版）",
    "2160x3840（9:16｜4K竖版）",
]
SIZE_MAP = {
    "auto（默认）": "auto",
    "1024x1024（1:1｜正方形）": "1024x1024",
    "1536x1024（3:2｜横版）": "1536x1024",
    "1024x1536（2:3｜竖版）": "1024x1536",
    "2048x2048（1:1｜2K正方形）": "2048x2048",
    "2048x1152（16:9｜2K横版）": "2048x1152",
    "3840x2160（16:9｜4K横版）": "3840x2160",
    "2160x3840（9:16｜4K竖版）": "2160x3840",
}
FORMATS = ["png", "jpeg", "webp"]
QUALITY_OPTIONS = ["auto", "low", "medium", "high"]


def _extract_urls(data: dict) -> list:
    # Standard OpenAI format: {"data": [{"url": "..."}]} or {"data": [{"b64_json": "..."}]}
    items = data.get("data") or []
    if items:
        urls = [item["url"].strip() for item in items if item.get("url")]
        if urls:
            return urls
        b64s = [f"data:image/png;base64,{item['b64_json']}" for item in items if item.get("b64_json")]
        if b64s:
            return b64s
    # Fallback: choices[0].message.content
    choices = data.get("choices") or []
    if choices:
        urls = [c["message"]["content"].strip() for c in choices if c.get("message", {}).get("content")]
        if urls:
            return urls
    raise RuntimeError(f"响应中没有图像数据: {data}")


def _url_to_tensor(url: str, timeout: int) -> torch.Tensor:
    if url.startswith("data:"):
        import base64
        content = base64.b64decode(url.split(",", 1)[1])
    else:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        content = resp.content
    pil = Image.open(io.BytesIO(content)).convert("RGB")
    arr = np.array(pil).astype(np.float32) / 255.0
    return torch.from_numpy(arr)[None,]


class GPTImage2Generate:
    """GPT Image 2 文生图节点"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "", "tooltip": "图像描述提示词"}),
                "model": (MODELS, {"default": "gpt-image-2", "tooltip": "模型选择"}),
                "size": (SIZES, {"default": "auto（默认）", "tooltip": "图像尺寸（分辨率、比例与用途）"}),
                "n": ("INT", {"default": 1, "min": 1, "max": 10, "tooltip": "生成数量（1-10张）"}),
                "api_key": ("STRING", {"default": "", "tooltip": "API密钥（留空使用环境变量 KUAI_API_KEY）"}),
            },
            "optional": {
                "api_base": ("STRING", {"default": "https://ai.kegeai.top", "tooltip": "API服务器地址"}),
                "timeout": ("INT", {"default": 1800, "min": 30, "max": 9999, "tooltip": "超时时间(秒)"}),
            }
        }

    @classmethod
    def INPUT_LABELS(cls):
        return {
            "prompt": "提示词",
            "model": "模型",
            "size": "图像尺寸（分辨率/比例）",
            "n": "生成数量（输出图片张数）",
            "api_key": "API密钥",
            "api_base": "API地址",
            "timeout": "超时",
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("图像", "图片URL")
    FUNCTION = "generate"
    CATEGORY = "KuAi/GPTImage"

    def generate(self, prompt, model, size, n, api_key, api_base="https://ai.kegeai.top", timeout=1800):
        api_key = env_or(api_key, "KUAI_API_KEY")
        if not api_key:
            raise RuntimeError("API Key 未配置，请在节点参数或环境变量 KUAI_API_KEY 中设置")
        if not prompt.strip():
            raise RuntimeError("提示词不能为空")

        payload = {"model": model, "prompt": prompt, "n": n, "size": SIZE_MAP.get(size, size)}
        resp = requests.post(
            f"{api_base.rstrip('/')}/v1/images/generations",
            json=payload,
            headers=http_headers_json(api_key),
            timeout=timeout,
        )
        raise_for_bad_status(resp, "GPTImage文生图失败")
        data = resp.json()

        urls = _extract_urls(data)
        tensors = [_url_to_tensor(u, timeout) for u in urls]
        image_tensor = torch.cat(tensors, dim=0)
        print(f"[GPTImage] 文生图完成，生成 {len(urls)} 张图像")
        return (image_tensor, "\n".join(urls))


class GPTImage2Edit:
    """GPT Image 2 图片编辑节点（支持1-4张图片URL）"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_url_1": ("STRING", {"default": "", "tooltip": "图片URL 1（必填）"}),
                "prompt": ("STRING", {"multiline": True, "default": "", "tooltip": "编辑描述提示词"}),
                "model": (MODELS, {"default": "gpt-image-2", "tooltip": "模型选择"}),
                "size": (SIZES, {"default": "auto（默认）", "tooltip": "输出图像尺寸（分辨率、比例与用途）"}),
                "n": ("INT", {"default": 1, "min": 1, "max": 10, "tooltip": "生成数量（输出图片张数，1-10张）"}),
                "api_key": ("STRING", {"default": "", "tooltip": "API密钥（留空使用环境变量 KUAI_API_KEY）"}),
            },
            "optional": {
                "image_url_2": ("STRING", {"default": "", "tooltip": "图片URL 2（可选附加参考图）"}),
                "image_url_3": ("STRING", {"default": "", "tooltip": "图片URL 3（可选附加参考图）"}),
                "image_url_4": ("STRING", {"default": "", "tooltip": "图片URL 4（可选附加参考图）"}),
                "format": (FORMATS, {"default": "png", "tooltip": "输出格式（可选 png、jpeg、webp）"}),
                "quality": (QUALITY_OPTIONS, {"default": "auto", "tooltip": "图像质量（可选 low、medium、high、auto）"}),
                "background": (["auto", "transparent", "opaque"], {"default": "auto", "tooltip": "背景透明度（auto 自动、transparent 透明、opaque 不透明）"}),
                "moderation": (["auto", "low"], {"default": "auto", "tooltip": "内容审核级别（auto 默认、low 较宽松）"}),
                "api_base": ("STRING", {"default": "https://ai.kegeai.top", "tooltip": "API服务器地址"}),
                "timeout": ("INT", {"default": 1800, "min": 30, "max": 9999, "tooltip": "超时时间(秒)"}),
            }
        }

    @classmethod
    def INPUT_LABELS(cls):
        return {
            "image_url_1": "图片URL 1（主图）",
            "image_url_2": "图片URL 2（附加图）",
            "image_url_3": "图片URL 3（附加图）",
            "image_url_4": "图片URL 4（附加图）",
            "prompt": "编辑提示词（修改要求）",
            "model": "模型（GPT Image 2）",
            "size": "图像尺寸（分辨率/比例）",
            "n": "生成数量（输出图片张数）",
            "api_key": "API密钥",
            "format": "输出格式（png/jpeg/webp）",
            "quality": "图像质量（清晰度等级）",
            "background": "背景（透明/不透明）",
            "moderation": "内容审核（安全级别）",
            "api_base": "API地址",
            "timeout": "超时（秒）",
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("图像", "图片URL")
    FUNCTION = "edit"
    CATEGORY = "KuAi/GPTImage"

    def edit(self, image_url_1, prompt, model, size, n, api_key,
             image_url_2="", image_url_3="", image_url_4="",
             format="png", quality="auto", background="auto", moderation="auto",
             api_base="https://ai.kegeai.top", timeout=1800):
        api_key = env_or(api_key, "KUAI_API_KEY")
        if not api_key:
            raise RuntimeError("API Key 未配置，请在节点参数或环境变量 KUAI_API_KEY 中设置")
        if not prompt.strip():
            raise RuntimeError("提示词不能为空")
        if not image_url_1.strip():
            raise RuntimeError("至少需要提供一张图片URL")

        image_urls = [u.strip() for u in [image_url_1, image_url_2, image_url_3, image_url_4] if u.strip()]

        files = []
        for i, url in enumerate(image_urls):
            r = requests.get(url, timeout=timeout)
            r.raise_for_status()
            files.append(("image[]", (f"image_{i}.png", r.content, "image/png")))

        form_data = {
            "model": model,
            "prompt": prompt,
            "n": str(n),
            "size": SIZE_MAP.get(size, size),
            "format": format,
            "quality": quality,
            "background": background,
            "moderation": moderation,
        }

        resp = requests.post(
            f"{api_base.rstrip('/')}/v1/images/edits",
            files=files,
            data=form_data,
            headers=http_headers_multipart(api_key),
            timeout=timeout,
        )
        raise_for_bad_status(resp, "GPTImage图片编辑失败")
        data = resp.json()

        urls = _extract_urls(data)
        tensors = [_url_to_tensor(u, timeout) for u in urls]

        image_tensor = torch.cat(tensors, dim=0)
        print(f"[GPTImage] 图片编辑完成，输入{len(image_urls)}张图，生成{len(urls)}张图像")
        return (image_tensor, "\n".join(urls))
