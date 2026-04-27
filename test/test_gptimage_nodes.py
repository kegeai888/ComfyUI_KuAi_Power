#!/usr/bin/env python3
"""测试 GPT Image 节点参数定义"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_gptimage_registration():
    """测试 GPTImage 节点注册"""
    print("=" * 60)
    print("测试 1: 节点注册")
    print("=" * 60)

    try:
        from nodes.GPTImage import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

        expected_nodes = ["GPTImage2Generate", "GPTImage2Edit"]

        for node_name in expected_nodes:
            if node_name in NODE_CLASS_MAPPINGS:
                print(f"✅ {node_name} 已注册")
                node_class = NODE_CLASS_MAPPINGS[node_name]
                print(f"   分类: {node_class.CATEGORY}")
                print(f"   显示名称: {NODE_DISPLAY_NAME_MAPPINGS.get(node_name)}")
            else:
                print(f"❌ {node_name} 未注册")
                return False

        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gptimage_edit_parameters():
    """测试 GPT Image 2 图片编辑参数定义"""
    print("\n" + "=" * 60)
    print("测试 2: 图片编辑参数")
    print("=" * 60)

    try:
        from nodes.GPTImage import NODE_CLASS_MAPPINGS

        node_class = NODE_CLASS_MAPPINGS["GPTImage2Edit"]
        input_types = node_class.INPUT_TYPES()
        labels = node_class.INPUT_LABELS()

        required = input_types.get("required", {})
        optional = input_types.get("optional", {})

        assert "size" in required, "缺少 size 参数"
        assert "n" in required, "缺少 n 参数"
        assert "format" in optional, "缺少 format 参数"

        size_options = required["size"][0]
        expected_sizes = [
            "auto（默认）",
            "1024x1024（1:1｜正方形）",
            "1536x1024（3:2｜横版）",
            "1024x1536（2:3｜竖版）",
            "2048x2048（1:1｜2K正方形）",
            "2048x1152（16:9｜2K横版）",
            "3840x2160（16:9｜4K横版）",
            "2160x3840（9:16｜4K竖版）",
        ]
        assert size_options == expected_sizes, f"size 选项不匹配: {size_options}"

        format_options = optional["format"][0]
        assert format_options == ["png", "jpeg", "webp"], f"format 选项不匹配: {format_options}"

        assert labels["size"] == "图像尺寸（分辨率/比例）", labels["size"]
        assert labels["n"] == "生成数量（输出图片张数）", labels["n"]
        assert labels["format"] == "输出格式（png/jpeg/webp）", labels["format"]
        assert labels["quality"] == "图像质量（清晰度等级）", labels["quality"]

        print("✅ 图片编辑参数定义正确")
        print(f"   size 选项: {size_options}")
        print(f"   format 选项: {format_options}")
        print(f"   size 标签: {labels['size']}")
        print(f"   n 标签: {labels['n']}")
        print(f"   format 标签: {labels['format']}")
        print(f"   quality 标签: {labels['quality']}")
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gptimage_generate_shared_sizes():
    """测试文生图节点复用新的尺寸选项"""
    print("\n" + "=" * 60)
    print("测试 3: 文生图共享尺寸")
    print("=" * 60)

    try:
        from nodes.GPTImage import NODE_CLASS_MAPPINGS

        node_class = NODE_CLASS_MAPPINGS["GPTImage2Generate"]
        input_types = node_class.INPUT_TYPES()
        size_options = input_types["required"]["size"][0]

        assert "3840x2160（16:9｜4K横版）" in size_options, "缺少 4K 横版尺寸"
        assert "2160x3840（9:16｜4K竖版）" in size_options, "缺少 4K 竖版尺寸"

        print("✅ 文生图节点已复用扩展尺寸")
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🧪 GPT Image 节点测试套件\n")

    results = []
    results.append(("节点注册", test_gptimage_registration()))
    results.append(("图片编辑参数", test_gptimage_edit_parameters()))
    results.append(("文生图共享尺寸", test_gptimage_generate_shared_sizes()))

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)
    print("\n" + ("🎉 所有测试通过！" if all_passed else "⚠️  部分测试失败"))

    sys.exit(0 if all_passed else 1)
