"""CSV 批量读取节点 - 用于批量图像生成任务"""

import csv
import os
import json

# 尝试导入 ComfyUI 的 folder_paths
try:
    import folder_paths
    HAS_FOLDER_PATHS = True
except ImportError:
    HAS_FOLDER_PATHS = False
    print("[CSVBatchReader] 警告: folder_paths 模块不可用，文件上传功能将受限")


class CSVBatchReader:
    """CSV 批量任务读取器 - 支持文件上传和路径输入"""

    @classmethod
    def INPUT_TYPES(cls):
        # 获取上传的 CSV 文件列表
        csv_files = []
        if HAS_FOLDER_PATHS:
            try:
                input_dir = folder_paths.get_input_directory()
                if os.path.exists(input_dir):
                    csv_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.csv')]
            except Exception as e:
                print(f"[CSVBatchReader] 无法读取 input 目录: {e}")

        return {
            "required": {
                "mode": (["upload", "path"], {"default": "path" if not csv_files else "upload", "tooltip": "选择模式：上传文件或输入路径"}),
            },
            "optional": {
                "csv_file": (sorted(csv_files) if csv_files else ["无可用文件"], {"tooltip": "选择已上传的 CSV 文件"}),
                "csv_path": ("STRING", {"default": "", "multiline": False, "tooltip": "CSV 文件的完整路径（path 模式）"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("批量任务数据",)
    FUNCTION = "read_csv"
    CATEGORY = "KuAi/配套能力"

    @classmethod
    def INPUT_LABELS(cls):
        return {
            "mode": "模式",
            "csv_file": "上传的文件",
            "csv_path": "文件路径",
        }

    @classmethod
    def IS_CHANGED(cls, mode, csv_file=None, csv_path=""):
        """检测输入是否改变"""
        if mode == "upload" and csv_file and HAS_FOLDER_PATHS:
            try:
                input_dir = folder_paths.get_input_directory()
                file_path = os.path.join(input_dir, csv_file)
                if os.path.exists(file_path):
                    return os.path.getmtime(file_path)
            except:
                pass
        elif mode == "path" and csv_path:
            if os.path.exists(csv_path):
                return os.path.getmtime(csv_path)
        return float("nan")

    @classmethod
    def VALIDATE_INPUTS(cls, mode, csv_file=None, csv_path=""):
        """验证输入参数"""
        if mode == "upload":
            if not csv_file:
                return "请选择一个 CSV 文件或上传新文件"
        elif mode == "path":
            if not csv_path or not csv_path.strip():
                return "请输入 CSV 文件路径"
        return True

    def read_csv(self, mode, csv_file=None, csv_path=""):
        """读取 CSV 文件并返回 JSON 格式的任务列表"""
        try:
            # 根据模式确定文件路径
            if mode == "upload":
                if not csv_file or csv_file == "无可用文件":
                    raise ValueError("请选择一个 CSV 文件或切换到 path 模式")

                if not HAS_FOLDER_PATHS:
                    raise RuntimeError("文件上传功能不可用，请使用 path 模式")

                # 从 ComfyUI 的 input 目录读取
                input_dir = folder_paths.get_input_directory()
                file_path = os.path.join(input_dir, csv_file)

                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"上传的文件不存在: {csv_file}")

                print(f"[CSVBatchReader] 读取上传的文件: {csv_file}")

            elif mode == "path":
                if not csv_path or not csv_path.strip():
                    raise ValueError("CSV 文件路径不能为空")

                file_path = csv_path.strip()

                # 检查文件是否存在
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"CSV 文件不存在: {file_path}")

                print(f"[CSVBatchReader] 读取路径文件: {file_path}")

            else:
                raise ValueError(f"无效的模式: {mode}")

            # 检查文件扩展名
            if not file_path.lower().endswith('.csv'):
                raise ValueError(f"文件必须是 CSV 格式: {file_path}")

            # 读取 CSV 文件
            tasks = []
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)

                # 验证必需的列
                if not reader.fieldnames:
                    raise ValueError("CSV 文件为空或格式不正确")

                for row_num, row in enumerate(reader, start=2):  # 从第2行开始（第1行是标题）
                    # 跳过空行
                    if not any(row.values()):
                        continue

                    # 清理数据（去除空白）
                    cleaned_row = {k: v.strip() if isinstance(v, str) else v for k, v in row.items()}
                    cleaned_row['_row_number'] = row_num  # 添加行号用于调试
                    tasks.append(cleaned_row)

            if not tasks:
                raise ValueError("CSV 文件中没有有效的任务数据")

            # 转换为 JSON 字符串
            tasks_json = json.dumps(tasks, ensure_ascii=False, indent=2)

            print(f"[CSVBatchReader] 成功读取 {len(tasks)} 个任务")
            return (tasks_json,)

        except Exception as e:
            error_msg = f"读取 CSV 文件失败: {str(e)}"
            print(f"\033[91m[CSVBatchReader] {error_msg}\033[0m")
            raise RuntimeError(error_msg)


NODE_CLASS_MAPPINGS = {
    "CSVBatchReader": CSVBatchReader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CSVBatchReader": "CSV批量读取器",
}
