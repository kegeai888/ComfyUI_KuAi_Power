#!/usr/bin/env python3
"""测试 Kling 节点注册"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_all_nodes_registered():
    """测试所有节点已注册"""
    from nodes.Kling import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

    expected_nodes = [
        "KlingText2Video",
        "KlingImage2Video",
        "KlingQueryTask",
        "KlingText2VideoAndWait",
        "KlingImage2VideoAndWait",
    ]

    for node_name in expected_nodes:
        assert node_name in NODE_CLASS_MAPPINGS, f"{node_name} 未在 NODE_CLASS_MAPPINGS 中注册"
        assert node_name in NODE_DISPLAY_NAME_MAPPINGS, f"{node_name} 未在 NODE_DISPLAY_NAME_MAPPINGS 中注册"

    print(f"✅ 所有 {len(expected_nodes)} 个节点已注册")

def test_display_names_have_emoji():
    """测试显示名称包含 emoji"""
    from nodes.Kling import NODE_DISPLAY_NAME_MAPPINGS

    for node_name, display_name in NODE_DISPLAY_NAME_MAPPINGS.items():
        # 检查是否包含 emoji（🎞️ 或 🔍 或 ⚡）
        has_emoji = any(emoji in display_name for emoji in ["🎞️", "🔍", "⚡"])
        assert has_emoji, f"{node_name} 的显示名称缺少 emoji"

    print("✅ 所有显示名称包含 emoji")

def test_all_nodes_have_category():
    """测试所有节点有正确的分类"""
    from nodes.Kling import NODE_CLASS_MAPPINGS

    for node_name, node_class in NODE_CLASS_MAPPINGS.items():
        assert hasattr(node_class, 'CATEGORY'), f"{node_name} 缺少 CATEGORY 属性"
        assert node_class.CATEGORY == "KuAi/Kling", f"{node_name} 的分类不正确"

    print("✅ 所有节点分类正确")

if __name__ == "__main__":
    print("\n🧪 Kling 节点注册测试套件\n")

    tests = [
        ("所有节点已注册", test_all_nodes_registered),
        ("显示名称包含 emoji", test_display_names_have_emoji),
        ("所有节点分类正确", test_all_nodes_have_category),
    ]

    results = []
    for name, test_func in tests:
        try:
            test_func()
            results.append((name, True))
        except Exception as e:
            results.append((name, False))
            print(f"❌ {name}: {e}")

    all_passed = all(r[1] for r in results)
    print("\n" + ("🎉 所有测试通过！" if all_passed else "⚠️  部分测试失败"))
    sys.exit(0 if all_passed else 1)
