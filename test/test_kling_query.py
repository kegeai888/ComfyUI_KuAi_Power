#!/usr/bin/env python3
"""测试 KlingQueryTask 节点"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_node_structure():
    """测试节点结构"""
    from nodes.Kling.kling import KlingQueryTask

    assert hasattr(KlingQueryTask, 'INPUT_TYPES')
    assert KlingQueryTask.CATEGORY == "KuAi/Kling"
    assert KlingQueryTask.RETURN_TYPES == ("STRING", "STRING", "STRING", "STRING")

def test_input_types():
    """测试输入参数定义"""
    from nodes.Kling.kling import KlingQueryTask

    input_types = KlingQueryTask.INPUT_TYPES()

    # 检查必需参数
    required = input_types["required"]
    assert "task_id" in required

    # 检查可选参数
    optional = input_types["optional"]
    assert "wait" in optional
    assert "poll_interval_sec" in optional
    assert "timeout_sec" in optional

if __name__ == "__main__":
    print("\n🧪 KlingQueryTask 节点测试套件\n")

    tests = [
        ("节点结构", test_node_structure),
        ("输入参数定义", test_input_types),
    ]

    results = []
    for name, test_func in tests:
        try:
            test_func()
            results.append((name, True))
            print(f"✅ {name}")
        except Exception as e:
            results.append((name, False))
            print(f"❌ {name}: {e}")

    all_passed = all(r[1] for r in results)
    print("\n" + ("🎉 所有测试通过！" if all_passed else "⚠️  部分测试失败"))
    sys.exit(0 if all_passed else 1)
