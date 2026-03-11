#!/usr/bin/env python3
"""测试 Grok 模型名称和 duration 映射"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from nodes.Sora2.kuai_utils import get_duration_for_grok_model


def test_grok_model_duration():
    """测试 Grok 模型的 duration 映射"""
    print("=" * 60)
    print("测试 Grok 模型 duration 映射")
    print("=" * 60)

    test_cases = [
        # (输入模型名称, 期望的 duration)
        ("grok-video-3 (6秒)", 6),
        ("grok-video-3-10s (10秒)", 10),
        ("grok-video-3-15s (15秒)", 15),
        ("grok-video-3", 6),
        ("grok-video-3-10s", 10),
        ("grok-video-3-15s", 15),
    ]

    all_passed = True

    for model_input, expected_duration in test_cases:
        actual_duration = get_duration_for_grok_model(model_input)
        passed = actual_duration == expected_duration

        status = "✅" if passed else "❌"
        print(f"{status} {model_input:30} → {actual_duration}秒 (期望: {expected_duration}秒)")

        if not passed:
            all_passed = False

    print("=" * 60)
    if all_passed:
        print("🎉 所有测试通过！")
    else:
        print("⚠️  部分测试失败")

    return all_passed


def test_model_name_extraction():
    """测试模型名称提取"""
    print("\n" + "=" * 60)
    print("测试模型名称提取")
    print("=" * 60)

    test_cases = [
        ("grok-video-3 (6秒)", "grok-video-3"),
        ("grok-video-3-10s (10秒)", "grok-video-3-10s"),
        ("grok-video-3-15s (15秒)", "grok-video-3-15s"),
    ]

    all_passed = True

    for model_input, expected_name in test_cases:
        # 模拟节点中的提取逻辑
        actual_name = model_input.split(" (")[0] if " (" in model_input else model_input

        passed = actual_name == expected_name
        status = "✅" if passed else "❌"
        print(f"{status} {model_input:30} → {actual_name} (期望: {expected_name})")

        if not passed:
            all_passed = False

    print("=" * 60)
    if all_passed:
        print("🎉 所有测试通过！")
    else:
        print("⚠️  部分测试失败")

    return all_passed


if __name__ == "__main__":
    print("\n🧪 Grok 模型配置测试\n")

    result1 = test_grok_model_duration()
    result2 = test_model_name_extraction()

    print("\n" + "=" * 60)
    print("总结")
    print("=" * 60)
    print(f"Duration 映射: {'✅ 通过' if result1 else '❌ 失败'}")
    print(f"模型名称提取: {'✅ 通过' if result2 else '❌ 失败'}")

    sys.exit(0 if (result1 and result2) else 1)
