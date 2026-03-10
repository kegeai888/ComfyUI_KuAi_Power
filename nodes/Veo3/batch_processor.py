"""Veo3 批量视频生成处理器"""

import json
import os
import time
from ..Sora2.kuai_utils import env_or
from .veo3 import VeoText2Video, VeoImage2Video, VeoQueryTask


class Veo3BatchProcessor:
    """Veo3 批量视频生成处理器"""

    def __init__(self):
        self.text2video = VeoText2Video()
        self.image2video = VeoImage2Video()
        self.querier = VeoQueryTask()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "batch_tasks": ("STRING", {
                    "forceInput": True,
                    "tooltip": "来自 CSV 读取器的批量任务数据"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "tooltip": "API 密钥（留空使用环境变量 KUAI_API_KEY）"
                }),
                "output_dir": ("STRING", {
                    "default": "./output/veo3_batch",
                    "tooltip": "输出目录（保存任务信息）"
                }),
                "delay_between_tasks": ("FLOAT", {
                    "default": 2.0,
                    "min": 0.0,
                    "max": 60.0,
                    "step": 0.5,
                    "tooltip": "任务间延迟（秒）"
                }),
            },
            "optional": {
                "api_base": ("STRING", {
                    "default": "https://api.kegeai.top",
                    "tooltip": "API端点地址"
                }),
                "wait_for_completion": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否等待所有任务完成（会花费较长时间）"
                }),
                "max_wait_time": ("INT", {
                    "default": 1200,
                    "min": 60,
                    "max": 3600,
                    "tooltip": "单个任务最大等待时间（秒）"
                }),
                "poll_interval": ("INT", {
                    "default": 15,
                    "min": 5,
                    "max": 60,
                    "tooltip": "轮询间隔（秒）"
                }),
            }
        }

    @classmethod
    def INPUT_LABELS(cls):
        return {
            "batch_tasks": "批量任务",
            "api_key": "API密钥",
            "output_dir": "输出目录",
            "delay_between_tasks": "任务间延迟",
            "api_base": "API地址",
            "wait_for_completion": "等待完成",
            "max_wait_time": "最大等待时间",
            "poll_interval": "轮询间隔",
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("处理结果", "输出目录")
    FUNCTION = "process_batch"
    CATEGORY = "KuAi/Veo3"

    def process_batch(self, batch_tasks, api_key="", output_dir="./output/veo3_batch",
                     delay_between_tasks=2.0, api_base="https://api.kegeai.top",
                     wait_for_completion=False, max_wait_time=1200, poll_interval=15):
        """批量处理视频生成任务"""
        try:
            # 解析任务数据
            tasks = json.loads(batch_tasks)
            if not tasks:
                raise ValueError("没有任务需要处理")

            # 获取 API Key
            api_key = env_or(api_key, "KUAI_API_KEY")
            if not api_key:
                raise ValueError("未配置 API Key")

            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)

            # 处理结果统计
            results = {
                "total": len(tasks),
                "success": 0,
                "failed": 0,
                "errors": [],
                "task_ids": []
            }

            print(f"\n{'='*60}")
            print(f"[Veo3Batch] 开始批量处理 {len(tasks)} 个视频生成任务")
            print(f"[Veo3Batch] 输出目录: {output_dir}")
            print(f"[Veo3Batch] 等待完成: {'是' if wait_for_completion else '否'}")
            print(f"{'='*60}\n")

            # 逐个处理任务
            for idx, task in enumerate(tasks, start=1):
                try:
                    print(f"\n[{idx}/{len(tasks)}] 处理任务 (行 {task.get('_row_number', '?')})")

                    # 处理单个任务
                    task_info = self._process_single_task(
                        task, idx, api_key, api_base, output_dir,
                        wait_for_completion, max_wait_time, poll_interval
                    )

                    results["success"] += 1
                    results["task_ids"].append(task_info)
                    print(f"✓ 任务 {idx} 完成")

                except Exception as e:
                    results["failed"] += 1
                    error_msg = f"任务 {idx} (行 {task.get('_row_number', '?')}): {str(e)}"
                    results["errors"].append(error_msg)
                    print(f"\033[91m✗ {error_msg}\033[0m")

                # 任务间延迟
                if idx < len(tasks) and delay_between_tasks > 0:
                    time.sleep(delay_between_tasks)

            # 保存任务列表
            tasks_file = os.path.join(output_dir, "tasks.json")
            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump(results["task_ids"], f, ensure_ascii=False, indent=2)
            print(f"\n[Veo3Batch] 任务列表已保存到: {tasks_file}")

            # 生成结果报告
            report = self._generate_report(results)
            print(f"\n{'='*60}")
            print(report)
            print(f"{'='*60}\n")

            return (report, output_dir)

        except Exception as e:
            error_msg = f"批量处理失败: {str(e)}"
            print(f"\033[91m[Veo3Batch] {error_msg}\033[0m")
            raise RuntimeError(error_msg)

    def _process_single_task(self, task, task_idx, api_key, api_base, output_dir,
                            wait_for_completion, max_wait_time, poll_interval):
        """处理单个任务"""
        # 必需参数
        prompt = task.get("prompt", "").strip()
        if not prompt:
            raise ValueError("提示词 (prompt) 不能为空")

        # 任务类型
        task_type = task.get("task_type", "text2video").strip().lower()

        # 可选参数（带默认值）
        model = task.get("model", "veo3.1").strip()
        aspect_ratio = task.get("aspect_ratio", "9:16").strip()
        enhance_prompt = task.get("enhance_prompt", "true").strip().lower() in ["true", "1", "yes"]
        enable_upsample = task.get("enable_upsample", "true").strip().lower() in ["true", "1", "yes"]
        image_urls = task.get("image_urls", "").strip()
        output_prefix = task.get("output_prefix", f"task_{task_idx}").strip()
        custom_model = task.get("custom_model", "").strip()

        # 验证参数
        if aspect_ratio not in ["16:9", "9:16"]:
            raise ValueError(f"无效的宽高比: {aspect_ratio}，必须是 16:9 或 9:16")

        print(f"  任务类型: {task_type}")
        print(f"  提示词: {prompt[:50]}...")
        print(f"  模型: {model}, 宽高比: {aspect_ratio}")
        print(f"  增强提示词: {enhance_prompt}, 超分: {enable_upsample}")
        if image_urls:
            print(f"  参考图片: {image_urls[:50]}...")

        # 根据任务类型创建任务
        if task_type == "image2video" and image_urls:
            # 图生视频
            task_id, status, enhanced_prompt = self.image2video.create(
                prompt=prompt,
                image_urls=image_urls,
                model=model,
                aspect_ratio=aspect_ratio,
                enhance_prompt=enhance_prompt,
                enable_upsample=enable_upsample,
                api_base=api_base,
                api_key=api_key,
                custom_model=custom_model
            )
        else:
            # 文生视频
            task_id, status, enhanced_prompt = self.text2video.create(
                prompt=prompt,
                model=model,
                aspect_ratio=aspect_ratio,
                enhance_prompt=enhance_prompt,
                enable_upsample=enable_upsample,
                api_base=api_base,
                api_key=api_key,
                custom_model=custom_model
            )

        print(f"  任务ID: {task_id}")
        print(f"  状态: {status}")
        if enhanced_prompt and enhanced_prompt != prompt:
            print(f"  增强提示词: {enhanced_prompt[:50]}...")

        # 任务信息
        task_info = {
            "task_id": task_id,
            "task_type": task_type,
            "prompt": prompt,
            "enhanced_prompt": enhanced_prompt,
            "model": model,
            "aspect_ratio": aspect_ratio,
            "status": status,
            "output_prefix": output_prefix,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        # 如果需要等待完成
        if wait_for_completion:
            print(f"  等待任务完成...")
            task_info = self._wait_for_task(
                task_id, task_info, api_key, api_base,
                max_wait_time, poll_interval
            )

        return task_info

    def _wait_for_task(self, task_id, task_info, api_key, api_base,
                      max_wait_time, poll_interval):
        """等待任务完成"""
        elapsed = 0
        while elapsed < max_wait_time:
            try:
                # 查询任务状态
                status, video_url, error_msg = self.querier.query(
                    task_id=task_id,
                    api_base=api_base,
                    api_key=api_key
                )

                task_info["status"] = status

                if status == "completed":
                    task_info["video_url"] = video_url
                    print(f"  ✓ 任务完成，视频URL: {video_url[:50]}...")
                    break
                elif status == "failed":
                    task_info["error"] = error_msg
                    raise RuntimeError(f"任务失败: {error_msg}")
                else:
                    print(f"  状态: {status}, 已等待 {elapsed}秒...")

            except Exception as e:
                print(f"  查询失败: {str(e)}")
                break

            time.sleep(poll_interval)
            elapsed += poll_interval

        if elapsed >= max_wait_time and task_info["status"] not in ["completed", "failed"]:
            print(f"  ⚠ 等待超时，任务仍在处理中")
            task_info["timeout"] = True

        return task_info

    def _generate_report(self, results):
        """生成处理结果报告"""
        lines = [
            "\n批量处理完成",
            f"总任务数: {results['total']}",
            f"成功: {results['success']}",
            f"失败: {results['failed']}",
        ]

        if results['errors']:
            lines.append("\n失败任务详情:")
            for error in results['errors']:
                lines.append(f"  - {error}")

        return "\n".join(lines)


NODE_CLASS_MAPPINGS = {
    "Veo3BatchProcessor": Veo3BatchProcessor,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Veo3BatchProcessor": "📦 Veo3 批量处理器",
}
