"""Grok 视频生成节点集合"""

from .grok import (
    GrokCreateVideo,
    GrokQueryVideo,
    GrokCreateAndWait,
    GrokImage2Video,
    GrokImage2VideoAndWait,
    GrokText2Video,
    GrokText2VideoAndWait
)
from .batch_processor import GrokBatchProcessor

NODE_CLASS_MAPPINGS = {
    "GrokCreateVideo": GrokCreateVideo,
    "GrokQueryVideo": GrokQueryVideo,
    "GrokCreateAndWait": GrokCreateAndWait,
    "GrokImage2Video": GrokImage2Video,
    "GrokImage2VideoAndWait": GrokImage2VideoAndWait,
    "GrokText2Video": GrokText2Video,
    "GrokText2VideoAndWait": GrokText2VideoAndWait,
    "GrokBatchProcessor": GrokBatchProcessor,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GrokCreateVideo": "🤖 Grok 创建视频",
    "GrokQueryVideo": "🔍 Grok 查询视频",
    "GrokCreateAndWait": "⚡ Grok 一键生成视频",
    "GrokImage2Video": "🎬 Grok 图生视频",
    "GrokImage2VideoAndWait": "⚡ Grok 图生视频（一键）",
    "GrokText2Video": "📝 Grok 文生视频",
    "GrokText2VideoAndWait": "⚡ Grok 文生视频（一键）",
    "GrokBatchProcessor": "📦 Grok 批量处理器",
}

