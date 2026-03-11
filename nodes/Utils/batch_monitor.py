"""批量处理实时日志监控节点"""

from .batch_state import BatchProcessState, format_realtime_log


class BatchProcessMonitor:
    """批量处理实时日志监控节点"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "max_tasks": ("INT", {
                    "default": 20,
                    "min": 5,
                    "max": 100,
                    "tooltip": "最多显示的任务数"
                }),
            }
        }

    @classmethod
    def INPUT_LABELS(cls):
        return {
            "max_tasks": "最多显示任务数",
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("实时日志",)
    FUNCTION = "monitor"
    CATEGORY = "KuAi/Utils"
    OUTPUT_NODE = True  # 标记为输出节点，可以在 UI 中显示

    def monitor(self, max_tasks=20):
        """监控批量处理状态"""
        try:
            # 获取状态管理器
            state_manager = BatchProcessState()

            # 读取当前状态
            state = state_manager.get_state()

            # 格式化日志
            log = format_realtime_log(state, max_tasks=max_tasks)

            # 输出到控制台
            print(log)

            return (log,)

        except Exception as e:
            error_msg = f"❌ 监控失败: {str(e)}"
            print(error_msg)
            return (error_msg,)


NODE_CLASS_MAPPINGS = {
    "BatchProcessMonitor": BatchProcessMonitor,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "BatchProcessMonitor": "📡 批量处理实时监控",
}
