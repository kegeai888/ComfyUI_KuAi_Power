"""批量处理实时状态管理"""

import json
import os
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import threading


class BatchProcessState:
    """批量处理状态管理（单例模式）"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.state_file = Path(__file__).parent.parent.parent.parent.parent / "temp" / "batch_process_state.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.current_state = {
            "session_id": "",
            "start_time": "",
            "total": 0,
            "completed": 0,
            "failed": 0,
            "processing": 0,
            "tasks": [],
            "last_update": ""
        }

    def start_session(self, session_id: str, total: int):
        """开始新的批量处理会话"""
        self.current_state = {
            "session_id": session_id,
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total": total,
            "completed": 0,
            "failed": 0,
            "processing": 0,
            "tasks": [],
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self._save_state()

    def update_task(self, task_idx: int, status: str, **kwargs):
        """更新任务状态"""
        # 查找现有任务
        task = None
        for t in self.current_state["tasks"]:
            if t["idx"] == task_idx:
                task = t
                break

        # 如果任务不存在，创建新任务
        if task is None:
            task = {
                "idx": task_idx,
                "status": "pending",
                "prompt": "",
                "task_id": "",
                "video_url": "",
                "local_path": "",
                "error": "",
                "start_time": datetime.now().strftime("%H:%M:%S"),
                "update_time": datetime.now().strftime("%H:%M:%S")
            }
            self.current_state["tasks"].append(task)

        # 更新任务状态
        old_status = task["status"]
        task["status"] = status
        task["update_time"] = datetime.now().strftime("%H:%M:%S")

        # 更新其他字段
        for key, value in kwargs.items():
            if key in task:
                task[key] = value

        # 更新统计
        if old_status != status:
            if old_status == "processing":
                self.current_state["processing"] -= 1
            elif old_status == "completed":
                self.current_state["completed"] -= 1
            elif old_status == "failed":
                self.current_state["failed"] -= 1

            if status == "processing":
                self.current_state["processing"] += 1
            elif status == "completed":
                self.current_state["completed"] += 1
            elif status == "failed":
                self.current_state["failed"] += 1

        self.current_state["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save_state()

    def _save_state(self):
        """保存状态到文件"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[BatchProcessState] 保存状态失败: {e}")

    def get_state(self) -> Dict[str, Any]:
        """获取当前状态"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[BatchProcessState] 读取状态失败: {e}")

        return self.current_state

    def clear_state(self):
        """清除状态"""
        self.current_state = {
            "session_id": "",
            "start_time": "",
            "total": 0,
            "completed": 0,
            "failed": 0,
            "processing": 0,
            "tasks": [],
            "last_update": ""
        }
        if self.state_file.exists():
            self.state_file.unlink()


def format_realtime_log(state: Dict[str, Any], max_tasks: int = 20) -> str:
    """
    格式化实时日志（最新的在前面）

    Args:
        state: 状态字典
        max_tasks: 最多显示的任务数

    Returns:
        格式化的日志字符串
    """
    if not state or not state.get("session_id"):
        return "暂无批量处理任务运行"

    total = state.get("total", 0)
    completed = state.get("completed", 0)
    failed = state.get("failed", 0)
    processing = state.get("processing", 0)
    pending = total - completed - failed - processing

    # 计算进度
    progress = (completed + failed) / total * 100 if total > 0 else 0

    # 计算耗时
    start_time = state.get("start_time", "")
    if start_time:
        try:
            start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            elapsed = (datetime.now() - start_dt).total_seconds()
            elapsed_str = f"{int(elapsed)}秒"
        except:
            elapsed_str = "未知"
    else:
        elapsed_str = "未知"

    lines = [
        "",
        "=" * 70,
        "📊 批量处理实时状态",
        "=" * 70,
        f"会话ID: {state.get('session_id', 'N/A')}",
        f"开始时间: {start_time}",
        f"最后更新: {state.get('last_update', 'N/A')}",
        f"已耗时: {elapsed_str}",
        "",
        f"总进度: {completed + failed}/{total} ({progress:.1f}%)",
        f"  ✓ 已完成: {completed}",
        f"  ✗ 已失败: {failed}",
        f"  ⟳ 处理中: {processing}",
        f"  ○ 等待中: {pending}",
        "=" * 70,
    ]

    # 获取任务列表（按更新时间倒序，最新的在前面）
    tasks = state.get("tasks", [])
    if tasks:
        # 按更新时间排序（最新的在前）
        sorted_tasks = sorted(tasks, key=lambda x: x.get("update_time", ""), reverse=True)

        lines.append("")
        lines.append(f"最新任务状态（显示最近 {min(max_tasks, len(sorted_tasks))} 个）:")
        lines.append("")

        for task in sorted_tasks[:max_tasks]:
            idx = task.get("idx", 0)
            status = task.get("status", "unknown")
            prompt = task.get("prompt", "")
            update_time = task.get("update_time", "")

            # 状态图标
            status_icon = {
                "completed": "✓",
                "failed": "✗",
                "processing": "⟳",
                "pending": "○"
            }.get(status, "?")

            # 截断提示词
            prompt_short = prompt[:40] + "..." if len(prompt) > 40 else prompt

            # 基础信息
            line = f"  [{update_time}] [{idx}] {status_icon} {status.upper()}"

            if prompt_short:
                line += f" | {prompt_short}"

            # 添加详细信息
            if status == "completed":
                local_path = task.get("local_path", "")
                if local_path:
                    line += f"\n    └─ 已保存: {local_path}"
            elif status == "failed":
                error = task.get("error", "未知错误")
                line += f"\n    └─ 错误: {error}"
            elif status == "processing":
                task_id = task.get("task_id", "")
                if task_id:
                    line += f"\n    └─ 任务ID: {task_id}"

            lines.append(line)

    lines.append("")
    lines.append("=" * 70)
    lines.append("💡 提示: 重新执行此节点可刷新日志")
    lines.append("=" * 70)

    return "\n".join(lines)
