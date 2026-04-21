from .gpt_image import GPTImage2Generate, GPTImage2Edit

NODE_CLASS_MAPPINGS = {
    "GPTImage2Generate": GPTImage2Generate,
    "GPTImage2Edit": GPTImage2Edit,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GPTImage2Generate": "🖼️ GPT Image 2 文生图",
    "GPTImage2Edit": "🖼️ GPT Image 2 图片编辑",
}
