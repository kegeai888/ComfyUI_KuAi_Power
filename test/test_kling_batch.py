#!/usr/bin/env python3
"""测试 Kling 批量处理器"""

import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_batch_processor_structure():
    """测试批量处理器结构"""
    from nodes.Kling.batch_processor import KlingBatchProcessor

    assert hasattr(KlingBatchProcessor, 'INPUT_TYPES')
    assert KlingBatchProcessor.CATEGORY == "KuAi/Kling"
    assert KlingBatchProcessor.FUNCTION == "process_batch"

def test_batch_processor_registration():
    """测试批量处理器已注册"""
    from nodes.Kling import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

    assert "KlingBatchProcessor" in NODE_CLASS_MAPPINGS
    assert "KlingBatchProcessor" in NODE_DISPLAY_NAME_MAPPINGS
    assert "📦" in NODE_DISPLAY_NAME_MAPPINGS["KlingBatchProcessor"]

if __name__ == "__main__":
    print("\n🧪 Kling 批量处理器测试套件\n")

    tests = [
        ("批量处理器结构", test_batch_processor_structure),
        ("批量处理器注册", test_batch_processor_registration),
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
