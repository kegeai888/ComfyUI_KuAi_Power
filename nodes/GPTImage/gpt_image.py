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

MODEL = "gpt-image-2-all"
SIZES = ["auto（自动）", "1024x1024（1:1）", "1536x1024（16:9）", "1024x1536（9:16）"]
SIZE_MAP = {
    "auto（自动）": "auto",
    "1024x1024（1:1）": "1024x1024",
    "1536x1024（16:9）": "1536x1024",
    "1024x1536（9:16）": "1024x1536",
}


def _extract_urls(data: dict) -> list:
    # Standard OpenAI format: {"data": [{"url": "..."}]}
    items = data.get("data") or []
    if items:
        urls = [item["url"].strip() for item in items if item.get("url")]
        if urls:
            return urls
    # Fallback: choices[0].message.content
    choices = data.get("choices") or []
    if choices:
        urls = [c["message"]["content"].strip() for c in choices if c.get("message", {}).get("content")]
        if urls:
            return urls
    raise RuntimeError(f"响应中没有图像数据: {data}")


def _url_to_tensor(url: str, timeout: int) -> torch.Tensor:
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    pil = Image.open(io.BytesIO(resp.content)).convert("RGB")
    arr = np.array(pil).astype(np.float32) / 255.0
    return torch.from_numpy(arr)[None,]


class GPTImage2Generate:
    """GPT Image 2 文生图节点"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": "", "tooltip": "图像描述提示词"}),
                "size": (SIZES, {"default": "auto（自动）", "tooltip": "图像尺寸"}),
                "n": ("INT", {"default": 1, "min": 1, "max": 4, "tooltip": "生成图像数量"}),
                "api_key": ("STRING", {"default": "", "tooltip": "API密钥（留空使用环境变量 KUAI_API_KEY）"}),
            },
            "optional": {
                "api_base": ("STRING", {"default": "https://ai.kegeai.top", "tooltip": "API服务器地址"}),
                "timeout": ("INT", {"default": 120, "min": 30, "max": 600, "tooltip": "超时时间(秒)"}),
            }
        }

    @classmethod
    def INPUT_LABELS(cls):
        return {
            "prompt": "提示词",
            "size": "图像尺寸",
            "n": "生成数量",
            "api_key": "API密钥",
            "api_base": "API地址",
            "timeout": "超时",
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("图像", "图片URL")
    FUNCTION = "generate"
    CATEGORY = "KuAi/GPTImage"

    def generate(self, prompt, size, n, api_key, api_base="https://ai.kegeai.top", timeout=120):
        api_key = env_or(api_key, "KUAI_API_KEY")
        if not api_key:
            raise RuntimeError("API Key 未配置，请在节点参数或环境变量 KUAI_API_KEY 中设置")
        if not prompt.strip():
            raise RuntimeError("提示词不能为空")

        payload = {"model": MODEL, "prompt": prompt, "n": n, "size": SIZE_MAP.get(size, size)}
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
                "size": (SIZES, {"default": "auto（自动）", "tooltip": "输出图像尺寸"}),
                "n": ("INT", {"default": 1, "min": 1, "max": 4, "tooltip": "生成图像数量"}),
                "api_key": ("STRING", {"default": "", "tooltip": "API密钥（留空使用环境变量 KUAI_API_KEY）"}),
            },
            "optional": {
                "image_url_2": ("STRING", {"default": "", "tooltip": "图片URL 2（可选）"}),
                "image_url_3": ("STRING", {"default": "", "tooltip": "图片URL 3（可选）"}),
                "image_url_4": ("STRING", {"default": "", "tooltip": "图片URL 4（可选）"}),
                "quality": (["auto", "high", "medium", "low"], {"default": "auto", "tooltip": "图像质量"}),
                "background": (["auto", "transparent", "opaque"], {"default": "auto", "tooltip": "背景透明度"}),
                "moderation": (["auto", "low"], {"default": "auto", "tooltip": "内容审核级别"}),
                "api_base": ("STRING", {"default": "https://ai.kegeai.top", "tooltip": "API服务器地址"}),
                "timeout": ("INT", {"default": 120, "min": 30, "max": 600, "tooltip": "超时时间(秒)"}),
            }
        }

    @classmethod
    def INPUT_LABELS(cls):
        return {
            "image_url_1": "图片URL 1",
            "image_url_2": "图片URL 2",
            "image_url_3": "图片URL 3",
            "image_url_4": "图片URL 4",
            "prompt": "编辑提示词",
            "size": "图像尺寸",
            "n": "生成数量",
            "api_key": "API密钥",
            "quality": "图像质量",
            "background": "背景",
            "moderation": "内容审核",
            "api_base": "API地址",
            "timeout": "超时",
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("图像", "图片URL")
    FUNCTION = "edit"
    CATEGORY = "KuAi/GPTImage"

    def edit(self, image_url_1, prompt, size, n, api_key,
             image_url_2="", image_url_3="", image_url_4="",
             quality="auto", background="auto", moderation="auto",
             api_base="https://ai.kegeai.top", timeout=120):
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
            "model": MODEL,
            "prompt": prompt,
            "n": str(n),
            "size": SIZE_MAP.get(size, size),
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
