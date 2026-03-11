#!/usr/bin/env python3
"""测试批量处理日志节点"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_batch_logger_node_registration():
    """测试批量日志节点注册"""
    print("=" * 60)
    print("测试 1: 批量日志节点注册")
    print("=" * 60)

    try:
        from nodes.Utils import NODE_CLASS_MAPPINGS

        if 'BatchProcessLogger' in NODE_CLASS_MAPPINGS:
            print("✅ BatchProcessLogger 已注册")
            node_class = NODE_CLASS_MAPPINGS['BatchProcessLogger']
            print(f"   分类: {node_class.CATEGORY}")

            # 检查必需方法
            assert hasattr(node_class, 'INPUT_TYPES'), "缺少 INPUT_TYPES"
            assert hasattr(node_class, 'RETURN_TYPES'), "缺少 RETURN_TYPES"
            assert hasattr(node_class, 'FUNCTION'), "缺少 FUNCTION"

            input_types = node_class.INPUT_TYPES()
            print(f"   必需参数: {list(input_types.get('required', {}).keys())}")
            print(f"   可选参数: {list(input_types.get('optional', {}).keys())}")

            return True
        else:
            print("❌ BatchProcessLogger 未注册")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_log_formatting():
    """测试日志格式化功能"""
    print("\n" + "=" * 60)
    print("测试 2: 日志格式化")
    print("=" * 60)

    try:
        from nodes.Utils import NODE_CLASS_MAPPINGS

        node_class = NODE_CLASS_MAPPINGS['BatchProcessLogger']
        node = node_class()

        # 模拟批量任务报告
        mock_report = {
            "total": 5,
            "success": 3,
            "failed": 2,
            "tasks": [
                {"idx": 1, "status": "completed", "prompt": "测试1", "video_url": "http://example.com/1.mp4"},
                {"idx": 2, "status": "completed", "prompt": "测试2", "video_url": "http://example.com/2.mp4"},
                {"idx": 3, "status": "failed", "prompt": "测试3", "error": "超时"},
                {"idx": 4, "status": "completed", "prompt": "测试4", "video_url": "http://example.com/4.mp4"},
                {"idx": 5, "status": "failed", "prompt": "测试5", "error": "API错误"},
            ]
        }

        report_json = json.dumps(mock_report)

        # 执行格式化（节点返回元组）
        result = node.format_log(report_json)
        formatted_log = result[0]  # 解包元组

        print("✅ 日志格式化成功")
        print(f"   输出长度: {len(formatted_log)} 字符")

        # 验证格式化内容包含关键信息
        assert "总计: 5" in formatted_log, "缺少总计信息"
        assert "成功: 3" in formatted_log, "缺少成功数量"
        assert "失败: 2" in formatted_log, "缺少失败数量"
        assert "测试1" in formatted_log, "缺少任务详情"

        print("   ✓ 包含总计信息")
        print("   ✓ 包含成功/失败统计")
        print("   ✓ 包含任务详情")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_realtime_progress_logging():
    """测试实时进度日志功能"""
    print("\n" + "=" * 60)
    print("测试 3: 实时进度日志")
    print("=" * 60)

    try:
        # 这个测试验证日志输出格式
        from nodes.Utils.batch_logger import format_progress_log

        # 模拟任务进度
        progress = {
            "current": 3,
            "total": 10,
            "status": "processing",
            "task_id": "task_123",
            "elapsed_time": 45.5
        }

        log_line = format_progress_log(progress)

        print("✅ 进度日志格式化成功")
        print(f"   日志: {log_line}")

        # 验证日志包含关键信息
        assert "3/10" in log_line or "30%" in log_line, "缺少进度信息"
        assert "task_123" in log_line, "缺少任务ID"

        print("   ✓ 包含进度信息")
        print("   ✓ 包含任务ID")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🧪 批量处理日志节点测试套件\n")

    results = []
    results.append(("节点注册", test_batch_logger_node_registration()))
    results.append(("日志格式化", test_log_formatting()))
    results.append(("实时进度日志", test_realtime_progress_logging()))

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)
    print("\n" + ("🎉 所有测试通过！" if all_passed else "⚠️  部分测试失败"))

    sys.exit(0 if all_passed else 1)
