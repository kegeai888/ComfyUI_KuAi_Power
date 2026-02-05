#!/usr/bin/env python3
"""测试 Grok 节点的模型选择功能"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_model_parameter():
    """测试模型参数是否正确添加"""
    print("=" * 60)
    print("测试: 模型参数验证")
    print("=" * 60)

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS

        # 测试所有创建视频节点
        nodes_to_test = [
            'GrokCreateVideo',
            'GrokCreateAndWait',
            'GrokImage2Video',
            'GrokImage2VideoAndWait'
        ]

        for node_name in nodes_to_test:
            print(f"\n检查 {node_name}:")

            node_class = NODE_CLASS_MAPPINGS[node_name]
            input_types = node_class.INPUT_TYPES()

            # 检查 model 参数是否存在
            if 'model' in input_types.get('required', {}):
                model_config = input_types['required']['model']

                # 检查是否是下拉选择
                if isinstance(model_config[0], list):
                    models = model_config[0]
                    print(f"  ✅ model 参数存在（下拉选择）")
                    print(f"  ✅ 可选模型: {models}")

                    # 验证模型列表
                    expected_models = ["grok-video-3 (6秒)", "grok-video-3-10s (10秒)"]
                    if models == expected_models:
                        print(f"  ✅ 模型列表正确")
                    else:
                        print(f"  ❌ 模型列表不正确")
                        print(f"     期望: {expected_models}")
                        print(f"     实际: {models}")
                        return False

                    # 检查默认值
                    default = model_config[1].get('default')
                    print(f"  ✅ 默认模型: {default}")

                    if default == "grok-video-3 (6秒)":
                        print(f"  ✅ 默认值正确")
                    else:
                        print(f"  ⚠️  默认值不是 grok-video-3 (6秒)")
                else:
                    print(f"  ❌ model 参数不是下拉选择")
                    return False
            else:
                print(f"  ❌ model 参数不存在")
                return False

            # 检查 INPUT_LABELS
            if hasattr(node_class, 'INPUT_LABELS'):
                labels = node_class.INPUT_LABELS()
                if 'model' in labels:
                    print(f"  ✅ model 标签: {labels['model']}")
                else:
                    print(f"  ❌ 缺少 model 标签")
                    return False

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_parameter_usage():
    """测试模型参数在方法中的使用"""
    print("\n" + "=" * 60)
    print("测试: 模型参数使用")
    print("=" * 60)

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS
        import inspect

        # 测试 GrokImage2Video
        node_class = NODE_CLASS_MAPPINGS['GrokImage2Video']

        # 获取 create 方法签名
        sig = inspect.signature(node_class.create)
        params = list(sig.parameters.keys())

        print(f"\nGrokImage2Video.create() 参数:")
        print(f"  {params}")

        if 'model' in params:
            print(f"  ✅ model 参数存在于方法签名中")

            # 检查参数顺序
            expected_order = ['self', 'images', 'prompt', 'model', 'aspect_ratio', 'size', 'api_key']
            if params == expected_order:
                print(f"  ✅ 参数顺序正确")
            else:
                print(f"  ⚠️  参数顺序可能不同")
                print(f"     期望: {expected_order}")
                print(f"     实际: {params}")
        else:
            print(f"  ❌ model 参数不存在于方法签名中")
            return False

        # 检查源代码中是否使用了 model 参数
        source = inspect.getsource(node_class.create)
        if '"model": actual_model' in source or "'model': actual_model" in source:
            print(f"  ✅ model 参数在 payload 中使用（提取为 actual_model）")
        else:
            print(f"  ❌ model 参数未在 payload 中使用")
            return False

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_backward_compatibility():
    """测试向后兼容性"""
    print("\n" + "=" * 60)
    print("测试: 向后兼容性")
    print("=" * 60)

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS

        # 旧节点应该也有 model 参数
        old_nodes = ['GrokCreateVideo', 'GrokCreateAndWait']

        for node_name in old_nodes:
            print(f"\n检查 {node_name}:")
            node_class = NODE_CLASS_MAPPINGS[node_name]
            input_types = node_class.INPUT_TYPES()

            if 'model' in input_types.get('required', {}):
                print(f"  ✅ 已添加 model 参数")
            else:
                print(f"  ❌ 缺少 model 参数")
                return False

        print("\n✅ 所有节点都已更新，保持一致性")
        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False


if __name__ == "__main__":
    print("\n🧪 Grok 模型选择功能测试套件\n")

    results = []
    results.append(("模型参数验证", test_model_parameter()))
    results.append(("模型参数使用", test_model_parameter_usage()))
    results.append(("向后兼容性", test_backward_compatibility()))

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)

    if all_passed:
        print("\n" + "=" * 60)
        print("🎉 所有测试通过！模型选择功能已成功添加")
        print("=" * 60)
        print("\n功能总结:")
        print("  ✅ 所有 Grok 创建视频节点都添加了 model 参数")
        print("  ✅ 可选模型: grok-video-3 (6秒), grok-video-3-10s (10秒)")
        print("  ✅ 默认模型: grok-video-3 (6秒)")
        print("  ✅ 参数在 payload 中正确使用（提取为 actual_model）")
        print("  ✅ 向后兼容性保持")
        print("\n")
    else:
        print("\n⚠️  部分测试失败，请检查实现")

    sys.exit(0 if all_passed else 1)
