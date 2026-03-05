#!/usr/bin/env python3
"""测试 KlingText2Video 节点"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_node_structure():
    """测试节点结构"""
    from nodes.Kling.kling import KlingText2Video

    # 检查必需方法
    assert hasattr(KlingText2Video, 'INPUT_TYPES')
    assert hasattr(KlingText2Video, 'INPUT_LABELS')
    assert hasattr(KlingText2Video, 'RETURN_TYPES')
    assert hasattr(KlingText2Video, 'RETURN_NAMES')
    assert hasattr(KlingText2Video, 'FUNCTION')
    assert hasattr(KlingText2Video, 'CATEGORY')

    # 检查分类
    assert KlingText2Video.CATEGORY == "KuAi/Kling"

    # 检查返回类型
    assert KlingText2Video.RETURN_TYPES == ("STRING", "STRING", "INT")
    assert KlingText2Video.RETURN_NAMES == ("任务ID", "状态", "创建时间")

def test_input_types():
    """测试输入参数定义"""
    from nodes.Kling.kling import KlingText2Video

    input_types = KlingText2Video.INPUT_TYPES()

    # 检查必需参数
    required = input_types["required"]
    assert "prompt" in required
    assert "model_name" in required
    assert "mode" in required
    assert "duration" in required
    assert "aspect_ratio" in required

    # 检查可选参数
    optional = input_types["optional"]
    assert "negative_prompt" in optional
    assert "cfg_scale" in optional
    assert "multi_shot" in optional
    assert "watermark" in optional
    assert "api_key" in optional

def test_input_labels():
    """测试中文标签"""
    from nodes.Kling.kling import KlingText2Video

    labels = KlingText2Video.INPUT_LABELS()

    assert labels["prompt"] == "提示词"
    assert labels["model_name"] == "模型名称"
    assert labels["mode"] == "模式"
    assert labels["duration"] == "时长"
    assert labels["aspect_ratio"] == "宽高比"

if __name__ == "__main__":
    print("\n🧪 KlingText2Video 节点测试套件\n")

    tests = [
        ("节点结构", test_node_structure),
        ("输入参数定义", test_input_types),
        ("中文标签", test_input_labels),
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
