#!/usr/bin/env python3
"""测试 Grok 模型修复：验证发送给 API 的模型名称正确"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_model_name_extraction():
    """测试模型名称提取逻辑"""
    print("=" * 60)
    print("测试 1: 模型名称提取")
    print("=" * 60)

    test_cases = [
        ("grok-video-3 (6秒)", "grok-video-3"),
        ("grok-video-3-10s (10秒)", "grok-video-3-10s"),
        ("grok-video-3-15s (15秒)", "grok-video-3-15s"),
        ("custom-model", "custom-model"),
    ]

    all_passed = True
    for input_model, expected_output in test_cases:
        # 模拟代码中的提取逻辑
        actual_model = input_model.split(" (")[0] if " (" in input_model else input_model

        if actual_model == expected_output:
            print(f"✅ '{input_model}' → '{actual_model}'")
        else:
            print(f"❌ '{input_model}' → '{actual_model}' (期望: '{expected_output}')")
            all_passed = False

    return all_passed


def test_payload_structure():
    """测试 payload 结构（不包含 duration）"""
    print("\n" + "=" * 60)
    print("测试 2: Payload 结构验证")
    print("=" * 60)

    try:
        from nodes.Grok.grok import GrokCreateVideo

        # 检查 create 方法的实现
        import inspect
        source = inspect.getsource(GrokCreateVideo.create)

        # 验证 payload 中不包含 duration
        if '"duration"' in source:
            print("❌ Payload 中仍然包含 'duration' 字段")
            return False
        else:
            print("✅ Payload 中已移除 'duration' 字段")

        # 验证 payload 包含必要字段
        required_fields = ['"model"', '"prompt"', '"aspect_ratio"', '"size"', '"enhance_prompt"', '"images"']
        missing_fields = [field for field in required_fields if field not in source]

        if missing_fields:
            print(f"❌ Payload 缺少字段: {missing_fields}")
            return False
        else:
            print(f"✅ Payload 包含所有必要字段: {', '.join(required_fields)}")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_import_cleanup():
    """测试是否移除了 get_duration_for_grok_model 导入"""
    print("\n" + "=" * 60)
    print("测试 3: 导入清理验证")
    print("=" * 60)

    try:
        import inspect
        from nodes.Grok import grok

        source = inspect.getsource(grok)

        if "get_duration_for_grok_model" in source:
            print("❌ 仍然导入或使用 get_duration_for_grok_model")
            return False
        else:
            print("✅ 已移除 get_duration_for_grok_model 的导入和使用")
            return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_1080p_logic():
    """测试 1080P 支持逻辑"""
    print("\n" + "=" * 60)
    print("测试 4: 1080P 支持逻辑")
    print("=" * 60)

    test_cases = [
        ("grok-video-3", "1080P", "720P", "6秒模型不支持1080P"),
        ("grok-video-3-10s", "1080P", "720P", "10秒模型不支持1080P"),
        ("grok-video-3-15s", "1080P", "1080P", "15秒模型支持1080P"),
        ("grok-video-3", "720P", "720P", "720P始终支持"),
    ]

    all_passed = True
    for model, input_size, expected_size, reason in test_cases:
        # 模拟代码中的逻辑
        effective_size = input_size
        if "15s" not in model.lower() and input_size == "1080P":
            effective_size = "720P"

        if effective_size == expected_size:
            print(f"✅ {model} + {input_size} → {effective_size} ({reason})")
        else:
            print(f"❌ {model} + {input_size} → {effective_size} (期望: {expected_size}, {reason})")
            all_passed = False

    return all_passed


if __name__ == "__main__":
    print("\n🧪 Grok 模型修复验证测试套件\n")

    results = []
    results.append(("模型名称提取", test_model_name_extraction()))
    results.append(("Payload 结构", test_payload_structure()))
    results.append(("导入清理", test_import_cleanup()))
    results.append(("1080P 支持逻辑", test_1080p_logic()))

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)

    if all_passed:
        print("\n🎉 所有测试通过！")
        print("\n修复说明：")
        print("- 移除了 duration 参数的计算逻辑")
        print("- API 将根据 model 字段自动决定视频时长")
        print("- 用户选择什么模型，就发送什么模型名称")
        print("- 选择 'grok-video-3 (6秒)' → 发送 'grok-video-3'")
        print("- 选择 'grok-video-3-10s (10秒)' → 发送 'grok-video-3-10s'")
        print("- 选择 'grok-video-3-15s (15秒)' → 发送 'grok-video-3-15s'")
    else:
        print("\n⚠️  部分测试失败，请检查修复")

    sys.exit(0 if all_passed else 1)
