#!/usr/bin/env python3
"""测试 Gemini 理解节点"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_node_registration():
    """测试节点注册"""
    print("=" * 60)
    print("测试 1: 节点注册")
    print("=" * 60)

    try:
        from nodes.Gemini import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

        nodes = ['GeminiImageUnderstanding', 'GeminiVideoUnderstanding']

        for node_name in nodes:
            if node_name in NODE_CLASS_MAPPINGS:
                print(f"✅ {node_name} 已注册")
                node_class = NODE_CLASS_MAPPINGS[node_name]
                print(f"   分类: {node_class.CATEGORY}")
                print(f"   显示名称: {NODE_DISPLAY_NAME_MAPPINGS.get(node_name)}")

                # 检查必需方法
                assert hasattr(node_class, 'INPUT_TYPES'), "缺少 INPUT_TYPES"
                assert hasattr(node_class, 'RETURN_TYPES'), "缺少 RETURN_TYPES"
                assert hasattr(node_class, 'FUNCTION'), "缺少 FUNCTION"

                input_types = node_class.INPUT_TYPES()
                print(f"   必需参数: {list(input_types.get('required', {}).keys())}")
                print(f"   可选参数: {list(input_types.get('optional', {}).keys())}")
            else:
                print(f"❌ {node_name} 未注册")
                return False

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chinese_labels():
    """测试中文标签"""
    print("\n" + "=" * 60)
    print("测试 2: 中文标签")
    print("=" * 60)

    try:
        from nodes.Gemini import NODE_CLASS_MAPPINGS

        for node_name in ['GeminiImageUnderstanding', 'GeminiVideoUnderstanding']:
            node_class = NODE_CLASS_MAPPINGS[node_name]

            if hasattr(node_class, 'INPUT_LABELS'):
                labels = node_class.INPUT_LABELS()
                print(f"\n✅ {node_name} 中文标签:")
                for key, value in labels.items():
                    print(f"   {key}: {value}")
            else:
                print(f"⚠️  {node_name} 没有 INPUT_LABELS")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_image_understanding():
    """测试图片理解节点（需要 API key）"""
    print("\n" + "=" * 60)
    print("测试 3: 图片理解节点")
    print("=" * 60)

    api_key = os.environ.get("KUAI_API_KEY", "")
    if not api_key:
        print("⚠️  跳过执行测试（未设置 KUAI_API_KEY）")
        print("   设置方法: export KUAI_API_KEY=your_key_here")
        return True

    try:
        from nodes.Gemini import NODE_CLASS_MAPPINGS
        import torch

        node_class = NODE_CLASS_MAPPINGS['GeminiImageUnderstanding']
        node = node_class()

        # 创建测试图片（64x64 红色图片）
        test_image = torch.ones(1, 64, 64, 3) * torch.tensor([1.0, 0.0, 0.0])

        print("🔄 执行图片理解测试...")
        result = node.understand_image(
            image=test_image,
            prompt="这是什么颜色的图片？",
            api_key=api_key
        )

        print(f"✅ 图片理解成功")
        print(f"   返回类型: {type(result)}")
        print(f"   结果预览: {result[0][:100]}...")

        return True

    except Exception as e:
        print(f"❌ 执行测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🧪 Gemini 理解节点测试套件\n")

    results = []
    results.append(("节点注册", test_node_registration()))
    results.append(("中文标签", test_chinese_labels()))
    results.append(("图片理解", test_image_understanding()))

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)
    print("\n" + ("🎉 所有测试通过！" if all_passed else "⚠️  部分测试失败"))

    sys.exit(0 if all_passed else 1)
