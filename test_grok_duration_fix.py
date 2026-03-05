#!/usr/bin/env python3
"""测试 Grok duration 和 size 修复"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_duration_mapping():
    """测试 duration 映射函数"""
    print("=" * 60)
    print("测试 1: get_duration_for_grok_model 函数")
    print("=" * 60)

    try:
        from nodes.Sora2.kuai_utils import get_duration_for_grok_model

        test_cases = [
            ("grok-video-3 (6秒)", 6),
            ("grok-video-3-10s (10秒)", 10),
            ("grok-video-3-15s (15秒)", 15),
            ("grok-video-3", 6),
            ("grok-video-3-10s", 10),
            ("grok-video-3-15s", 15),
            ("GROK-VIDEO-3-10S (10秒)", 10),  # 测试大小写
        ]

        all_passed = True
        for model, expected_duration in test_cases:
            result = get_duration_for_grok_model(model)
            status = "✓" if result == expected_duration else "✗"
            print(f"{status} {model:35s} → {result}秒 (期望: {expected_duration}秒)")
            if result != expected_duration:
                all_passed = False

        return all_passed

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_size_validation():
    """测试 size 参数验证逻辑"""
    print("\n" + "=" * 60)
    print("测试 2: Size 参数验证（只有 15 秒模型支持 1080P）")
    print("=" * 60)

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS

        test_nodes = [
            ("GrokCreateVideo", "create"),
            ("GrokImage2Video", "create"),
            ("GrokText2Video", "create"),
        ]

        all_passed = True
        for node_name, method_name in test_nodes:
            if node_name not in NODE_CLASS_MAPPINGS:
                print(f"✗ {node_name} 未注册")
                all_passed = False
                continue

            node_class = NODE_CLASS_MAPPINGS[node_name]
            print(f"\n检查 {node_name}:")

            # 检查是否有 size 验证逻辑
            import inspect
            source = inspect.getsource(node_class)

            if "effective_size" in source and "duration != 15" in source:
                print(f"  ✓ 包含 size 验证逻辑")
            else:
                print(f"  ✗ 缺少 size 验证逻辑")
                all_passed = False

            if "已自动降级到 720P" in source:
                print(f"  ✓ 包含降级警告信息")
            else:
                print(f"  ✗ 缺少降级警告信息")
                all_passed = False

        return all_passed

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_node_payload():
    """测试节点 payload 是否包含 duration"""
    print("\n" + "=" * 60)
    print("测试 3: 节点 payload 包含 duration 字段")
    print("=" * 60)

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS

        # 测试所有创建节点
        test_nodes = [
            ("GrokCreateVideo", "create"),
            ("GrokImage2Video", "create"),
            ("GrokText2Video", "create"),
        ]

        all_passed = True
        for node_name, method_name in test_nodes:
            if node_name not in NODE_CLASS_MAPPINGS:
                print(f"✗ {node_name} 未注册")
                all_passed = False
                continue

            node_class = NODE_CLASS_MAPPINGS[node_name]
            print(f"\n检查 {node_name}:")

            # 检查是否导入了 get_duration_for_grok_model
            import inspect
            source = inspect.getsource(node_class)
            if "get_duration_for_grok_model" in source:
                print(f"  ✓ 导入了 get_duration_for_grok_model")
            else:
                print(f"  ✗ 未导入 get_duration_for_grok_model")
                all_passed = False

            if '"duration": duration' in source or "'duration': duration" in source:
                print(f"  ✓ payload 包含 duration 字段")
            else:
                print(f"  ✗ payload 缺少 duration 字段")
                all_passed = False

            # 检查 custom_model 逻辑
            if "custom_model" in source and "duration = 15" in source:
                print(f"  ✓ custom_model 使用默认 duration=15")
            else:
                print(f"  ✗ custom_model 逻辑缺失")
                all_passed = False

        return all_passed

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🧪 Grok Duration 和 Size 修复测试套件\n")

    results = []
    results.append(("Duration 映射函数", test_duration_mapping()))
    results.append(("Size 参数验证", test_size_validation()))
    results.append(("节点 Payload", test_node_payload()))

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)
    print("\n" + ("🎉 所有测试通过！修复成功！" if all_passed else "⚠️  部分测试失败"))

    sys.exit(0 if all_passed else 1)
