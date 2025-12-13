"""Nano Banana 节点 - 基于 kuai.host API"""

from .nano_banana import NanoBananaAIO, NanoBananaMultiTurnChat

NODE_CLASS_MAPPINGS = {
    "NanoBananaAIO": NanoBananaAIO,
    "NanoBananaMultiTurnChat": NanoBananaMultiTurnChat
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NanoBananaAIO": "🍌 Nano Banana 多功能",
    "NanoBananaMultiTurnChat": "🍌 Nano Banana 多轮对话"
}
