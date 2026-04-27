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

        nodes_to_test = [
            'GrokCreateVideo',
            'GrokCreateAndWait',
            'GrokImage2Video',
            'GrokImage2VideoAndWait',
            'GrokText2Video',
            'GrokText2VideoAndWait',
            'GrokExtendVideo',
            'GrokExtendVideoAndWait',
        ]

        expected_models = ["grok-video-3 (6秒)", "grok-video-3-10s (10秒)"]

        for node_name in nodes_to_test:
            print(f"\n检查 {node_name}:")
            node_class = NODE_CLASS_MAPPINGS[node_name]
            input_types = node_class.INPUT_TYPES()

            if 'model' not in input_types.get('required', {}):
                print("  ❌ model 参数不存在")
                return False

            model_config = input_types['required']['model']
            if not isinstance(model_config[0], list):
                print("  ❌ model 参数不是下拉选择")
                return False

            models = model_config[0]
            print(f"  ✅ 可选模型: {models}")
            if models != expected_models:
                print(f"  ❌ 模型列表不正确: {models}")
                return False

            size_options = input_types['required']['size'][0]
            if size_options != ["720P"]:
                print(f"  ❌ 分辨率列表不正确: {size_options}")
                return False
            print(f"  ✅ 分辨率: {size_options}")

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🧪 Grok 模型选择功能测试套件\n")

    passed = test_model_parameter()
    print("\n" + ("🎉 所有测试通过！" if passed else "⚠️  部分测试失败"))
    sys.exit(0 if passed else 1)
