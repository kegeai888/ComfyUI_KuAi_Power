#!/usr/bin/env python3
"""测试 Grok 模型名称和 duration 映射"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from nodes.Sora2.kuai_utils import get_duration_for_grok_model
from nodes.Grok.grok import get_grok_duration, normalize_grok_model


def test_grok_model_duration():
    """测试 Grok 模型的 duration 映射"""
    print("=" * 60)
    print("测试 Grok 模型 duration 映射")
    print("=" * 60)

    test_cases = [
        ("grok-video-3 (6秒)", 6),
        ("grok-video-3-10s (10秒)", 10),
        ("grok-video-3", 6),
        ("grok-video-3-10s", 10),
    ]

    all_passed = True

    for model_input, expected_duration in test_cases:
        actual_duration = get_duration_for_grok_model(model_input)
        passed = actual_duration == expected_duration
        status = "✅" if passed else "❌"
        print(f"{status} {model_input:30} → {actual_duration}秒 (期望: {expected_duration}秒)")
        if not passed:
            all_passed = False

    return all_passed


def test_model_name_extraction():
    """测试模型名称提取"""
    print("\n" + "=" * 60)
    print("测试模型名称提取")
    print("=" * 60)

    test_cases = [
        ("grok-video-3 (6秒)", "grok-video-3"),
        ("grok-video-3-10s (10秒)", "grok-video-3-10s"),
    ]

    all_passed = True

    for model_input, expected_name in test_cases:
        actual_name = normalize_grok_model(model_input)
        passed = actual_name == expected_name
        status = "✅" if passed else "❌"
        print(f"{status} {model_input:30} → {actual_name} (期望: {expected_name})")
        if not passed:
            all_passed = False

    return all_passed


def test_extend_total_duration():
    """测试扩展后总时长计算"""
    print("\n" + "=" * 60)
    print("测试扩展后总时长")
    print("=" * 60)

    test_cases = [
        (10, "grok-video-3", 16),
        (10, "grok-video-3-10s", 20),
    ]

    all_passed = True

    for start_time, model_name, expected_total in test_cases:
        total_duration = start_time + get_grok_duration(model_name)
        passed = total_duration == expected_total
        status = "✅" if passed else "❌"
        print(
            f"{status} start_time={start_time} + 模型 {model_name} 时长 {get_grok_duration(model_name)} = {total_duration}"
        )
        if not passed:
            all_passed = False

    return all_passed


if __name__ == "__main__":
    print("\n🧪 Grok 模型配置测试\n")

    result1 = test_grok_model_duration()
    result2 = test_model_name_extraction()
    result3 = test_extend_total_duration()

    print("\n" + "=" * 60)
    print("总结")
    print("=" * 60)
    print(f"Duration 映射: {'✅ 通过' if result1 else '❌ 失败'}")
    print(f"模型名称提取: {'✅ 通过' if result2 else '❌ 失败'}")
    print(f"扩展总时长: {'✅ 通过' if result3 else '❌ 失败'}")

    sys.exit(0 if (result1 and result2 and result3) else 1)
