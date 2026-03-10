"""图片URL列表转CSV任务 - 将批量上传的URL列表转换为批量处理任务"""

import json


class ImageURLsToGrokBatchTasks:
    """将图片URL列表转换为Grok批量图生视频任务"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_urls_json": ("STRING", {
                    "forceInput": True,
                    "tooltip": "来自批量上传节点的图片URL列表（JSON格式）"
                }),
                "prompt_template": ("STRING", {
                    "default": "将这张图片转换为视频，添加自然的镜头运动",
                    "multiline": True,
                    "tooltip": "提示词模板（每个图片使用相同的提示词）"
                }),
                "model": (["grok-video-3 (6秒)", "grok-video-3-10s (10秒)", "grok-video-3-15s (15秒)"], {
                    "default": "grok-video-3 (6秒)",
                    "tooltip": "Grok 模型选择"
                }),
                "aspect_ratio": (["2:3", "3:2", "1:1"], {
                    "default": "3:2",
                    "tooltip": "视频宽高比"
                }),
                "size": (["720P", "1080P"], {
                    "default": "1080P",
                    "tooltip": "视频分辨率"
                }),
                "enhance_prompt": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "是否启用提示词增强"
                }),
            },
            "optional": {
                "output_prefix": ("STRING", {
                    "default": "video",
                    "tooltip": "输出文件名前缀"
                }),
            }
        }

    @classmethod
    def INPUT_LABELS(cls):
        return {
            "image_urls_json": "图片URL列表",
            "prompt_template": "提示词模板",
            "model": "模型",
            "aspect_ratio": "宽高比",
            "size": "分辨率",
            "enhance_prompt": "提示词增强",
            "output_prefix": "输出前缀",
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("批量任务",)
    FUNCTION = "convert"
    CATEGORY = "KuAi/Utils"

    def convert(self, image_urls_json, prompt_template, model, aspect_ratio, size,
               enhance_prompt, output_prefix="video"):
        """将URL列表转换为Grok批量任务"""

        try:
            # 解析 URL 列表
            image_urls = json.loads(image_urls_json)

            if not isinstance(image_urls, list):
                raise ValueError("image_urls_json 必须是 JSON 数组格式")

            if not image_urls:
                raise ValueError("图片URL列表为空")

            print(f"[ComfyUI_KuAi_Power] 转换 {len(image_urls)} 个图片URL为Grok批量任务")

            # 生成批量任务
            tasks = []
            for idx, url in enumerate(image_urls, start=1):
                task = {
                    "_row_number": idx + 1,
                    "task_type": "image2video",
                    "prompt": prompt_template,
                    "model": model,
                    "aspect_ratio": aspect_ratio,
                    "size": size,
                    "enhance_prompt": "true" if enhance_prompt else "false",
                    "image_urls": url,
                    "output_prefix": f"{output_prefix}_{idx}"
                }
                tasks.append(task)

            tasks_json = json.dumps(tasks, ensure_ascii=False, indent=2)
            print(f"[ComfyUI_KuAi_Power] 生成 {len(tasks)} 个Grok批量任务")

            return (tasks_json,)

        except json.JSONDecodeError as e:
            raise RuntimeError(f"解析图片URL列表失败: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"转换失败: {str(e)}")


class ImageURLsToVeo3BatchTasks:
    """将图片URL列表转换为Veo3批量图生视频任务"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_urls_json": ("STRING", {
                    "forceInput": True,
                    "tooltip": "来自批量上传节点的图片URL列表（JSON格式）"
                }),
                "prompt_template": ("STRING", {
                    "default": "将这张图片转换为视频，添加自然的镜头运动",
                    "multiline": True,
                    "tooltip": "提示词模板（每个图片使用相同的提示词）"
                }),
                "model": (["veo3.1", "veo3.1-pro", "veo3.1-pro-upsample"], {
                    "default": "veo3.1",
                    "tooltip": "Veo3 模型选择"
                }),
                "duration": ([6, 10], {
                    "default": 6,
                    "tooltip": "视频时长（秒）"
                }),
                "aspect_ratio": (["16:9", "9:16", "1:1"], {
                    "default": "16:9",
                    "tooltip": "视频宽高比"
                }),
                "enhance_prompt": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "是否启用提示词增强"
                }),
                "enable_upsample": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否启用超分辨率（仅pro模型支持）"
                }),
            },
            "optional": {
                "output_prefix": ("STRING", {
                    "default": "video",
                    "tooltip": "输出文件名前缀"
                }),
            }
        }

    @classmethod
    def INPUT_LABELS(cls):
        return {
            "image_urls_json": "图片URL列表",
            "prompt_template": "提示词模板",
            "model": "模型",
            "duration": "时长",
            "aspect_ratio": "宽高比",
            "enhance_prompt": "提示词增强",
            "enable_upsample": "启用超分",
            "output_prefix": "输出前缀",
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("批量任务",)
    FUNCTION = "convert"
    CATEGORY = "KuAi/Utils"

    def convert(self, image_urls_json, prompt_template, model, duration, aspect_ratio,
               enhance_prompt, enable_upsample, output_prefix="video"):
        """将URL列表转换为Veo3批量任务"""

        try:
            # 解析 URL 列表
            image_urls = json.loads(image_urls_json)

            if not isinstance(image_urls, list):
                raise ValueError("image_urls_json 必须是 JSON 数组格式")

            if not image_urls:
                raise ValueError("图片URL列表为空")

            print(f"[ComfyUI_KuAi_Power] 转换 {len(image_urls)} 个图片URL为Veo3批量任务")

            # 生成批量任务
            tasks = []
            for idx, url in enumerate(image_urls, start=1):
                task = {
                    "_row_number": idx + 1,
                    "task_type": "image2video",
                    "prompt": prompt_template,
                    "model": model,
                    "duration": duration,
                    "aspect_ratio": aspect_ratio,
                    "enhance_prompt": "true" if enhance_prompt else "false",
                    "enable_upsample": "true" if enable_upsample else "false",
                    "image_urls": url,
                    "output_prefix": f"{output_prefix}_{idx}"
                }
                tasks.append(task)

            tasks_json = json.dumps(tasks, ensure_ascii=False, indent=2)
            print(f"[ComfyUI_KuAi_Power] 生成 {len(tasks)} 个Veo3批量任务")

            return (tasks_json,)

        except json.JSONDecodeError as e:
            raise RuntimeError(f"解析图片URL列表失败: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"转换失败: {str(e)}")


NODE_CLASS_MAPPINGS = {
    "ImageURLsToGrokBatchTasks": ImageURLsToGrokBatchTasks,
    "ImageURLsToVeo3BatchTasks": ImageURLsToVeo3BatchTasks,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageURLsToGrokBatchTasks": "🔄 图片URL转Grok批量任务",
    "ImageURLsToVeo3BatchTasks": "🔄 图片URL转Veo3批量任务",
}
