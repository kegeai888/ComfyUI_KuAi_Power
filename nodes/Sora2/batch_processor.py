"""Sora2 批量处理器"""

import json
import os
import time
from .kuai_utils import env_or
from .sora2 import SoraCreateVideo, SoraText2Video, SoraQueryTask


class Sora2BatchProcessor:
    """Sora2 视频批量生成处理器"""

    def __init__(self):
        self.creator_with_images = SoraCreateVideo()
        self.creator_text_only = SoraText2Video()
        self.querier = SoraQueryTask()

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
                    "default": "./output/sora2_batch",
                    "tooltip": "输出目录"
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
                    "default": "https://api.kuai.host",
                    "tooltip": "API端点地址"
                }),
                "wait_for_completion": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否等待视频生成完成"
                }),
                "max_wait_time": ("INT", {
                    "default": 1200,
                    "min": 600,
                    "max": 9600,
                    "tooltip": "最大等待时间（秒）"
                }),
                "poll_interval": ("INT", {
                    "default": 15,
                    "min": 5,
                    "max": 90,
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
    CATEGORY = "KuAi/Sora2"

    def process_batch(self, batch_tasks, api_key="", output_dir="./output/sora2_batch",
                     delay_between_tasks=2.0, api_base="https://api.kuai.host",
                     wait_for_completion=False, max_wait_time=1200, poll_interval=15):
        """批量生成视频"""
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
                "video_tasks": []
            }

            print(f"\n{'='*60}")
            print(f"[Sora2Batch] 开始批量生成 {len(tasks)} 个视频")
            print(f"[Sora2Batch] 输出目录: {output_dir}")
            print(f"[Sora2Batch] 等待完成: {'是' if wait_for_completion else '否'}")
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
                    results["video_tasks"].append(task_info)
                    print(f"✓ 任务 {idx} 完成")

                except Exception as e:
                    results["failed"] += 1
                    error_msg = f"任务 {idx}: {str(e)}"
                    results["errors"].append(error_msg)
                    print(f"✗ {error_msg}")

                # 任务间延迟
                if idx < len(tasks) and delay_between_tasks > 0:
                    time.sleep(delay_between_tasks)

            # 保存任务列表
            tasks_file = os.path.join(output_dir, "tasks.json")
            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump(results["video_tasks"], f, ensure_ascii=False, indent=2)

            # 生成结果报告
            report = self._generate_report(results)
            print(f"\n{'='*60}")
            print(report)
            print(f"{'='*60}\n")

            return (report, output_dir)

        except Exception as e:
            error_msg = f"批量处理失败: {str(e)}"
            print(f"[Sora2Batch] {error_msg}")
            raise RuntimeError(error_msg)

    def _process_single_task(self, task, task_idx, api_key, api_base, output_dir,
                            wait_for_completion, max_wait_time, poll_interval):
        """处理单个视频生成任务"""
        # 解析任务参数
        prompt = task.get("prompt", "").strip()
        images = task.get("images", "").strip()
        model = task.get("model", "sora-2").strip()
        duration_sora2 = task.get("duration_sora2", "10").strip()
        duration_sora2pro = task.get("duration_sora2pro", "15").strip()
        orientation = task.get("orientation", "portrait").strip()
        size = task.get("size", "large").strip()
        watermark = task.get("watermark", "false").strip().lower() in ("true", "1", "yes")
        output_prefix = task.get("output_prefix", f"video_{task_idx}").strip()

        if not prompt:
            raise ValueError("提示词不能为空")

        print(f"  提示词: {prompt[:50]}...")
        print(f"  模型: {model}")
        print(f"  方向: {orientation}")
        print(f"  尺寸: {size}")

        # 根据是否有图片选择不同的创建方法
        if images:
            print(f"  图片: {images[:50]}...")
            # 使用图生视频
            task_id, status, status_update_time = self.creator_with_images.create(
                images=images,
                prompt=prompt,
                model=model,
                duration_sora2=duration_sora2,
                duration_sora2pro=duration_sora2pro,
                api_base=api_base,
                api_key=api_key,
                orientation=orientation,
                size=size,
                watermark=watermark
            )
        else:
            print(f"  类型: 文生视频")
            # 使用文生视频
            task_id, status, status_update_time = self.creator_text_only.create(
                prompt=prompt,
                model=model,
                duration_sora2=duration_sora2,
                duration_sora2pro=duration_sora2pro,
                api_base=api_base,
                api_key=api_key,
                orientation=orientation,
                size=size,
                watermark=watermark
            )

        print(f"  任务ID: {task_id}")
        print(f"  状态: {status}")

        # 保存任务信息
        task_info = {
            "task_id": task_id,
            "prompt": prompt,
            "model": model,
            "orientation": orientation,
            "size": size,
            "has_images": bool(images),
            "status": status,
            "output_prefix": output_prefix,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        # 如果需要等待完成
        if wait_for_completion:
            print(f"  等待视频生成完成...")
            try:
                final_status, video_url, gif_url, thumbnail_url, _raw = self.querier.query(
                    task_id=task_id,
                    api_base=api_base,
                    api_key=api_key,
                    wait=True,
                    poll_interval_sec=poll_interval,
                    timeout_sec=max_wait_time
                )

                task_info["final_status"] = final_status
                task_info["video_url"] = video_url
                task_info["gif_url"] = gif_url
                task_info["thumbnail_url"] = thumbnail_url
                task_info["completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

                print(f"  最终状态: {final_status}")
                if video_url:
                    print(f"  视频URL: {video_url[:50]}...")

            except Exception as e:
                print(f"  等待完成失败: {str(e)}")
                task_info["wait_error"] = str(e)

        # 保存单个任务信息
        task_file = os.path.join(output_dir, f"{output_prefix}.json")
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(task_info, f, ensure_ascii=False, indent=2)

        return task_info

    def _generate_report(self, results):
        """生成处理结果报告"""
        lines = [
            "\n批量视频生成完成",
            f"总任务数: {results['total']}",
            f"成功: {results['success']}",
            f"失败: {results['failed']}",
        ]

        if results['errors']:
            lines.append("\n失败任务详情:")
            for error in results['errors']:
                lines.append(f"  - {error}")

        if results['video_tasks']:
            lines.append(f"\n成功创建的视频任务:")
            for task in results['video_tasks']:
                lines.append(f"  - {task['task_id']}: {task['prompt'][:30]}...")

        return "\n".join(lines)


NODE_CLASS_MAPPINGS = {
    "Sora2BatchProcessor": Sora2BatchProcessor,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Sora2BatchProcessor": "📦 Sora2 批量处理器",
}
