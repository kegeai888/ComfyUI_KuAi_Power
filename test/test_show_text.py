#!/usr/bin/env python3
"""测试 ShowText 节点"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_show_text_registration():
    """测试 ShowText 节点注册"""
    print("=" * 60)
    print("测试: ShowText 节点注册")
    print("=" * 60)

    try:
        from nodes.Utils import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

        if 'ShowText' in NODE_CLASS_MAPPINGS:
            print("✅ ShowText 已注册")
            node_class = NODE_CLASS_MAPPINGS['ShowText']
            print(f"   分类: {node_class.CATEGORY}")
            print(f"   显示名称: {NODE_DISPLAY_NAME_MAPPINGS.get('ShowText')}")
            print(f"   输出节点: {getattr(node_class, 'OUTPUT_NODE', False)}")

            # 测试节点执行
            node = node_class()
            result = node.show("测试文本")
            print(f"   测试执行: {result}")

            return True
        else:
            print("❌ ShowText 未注册")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🧪 ShowText 节点测试\n")

    passed = test_show_text_registration()

    print("\n" + ("🎉 测试通过！" if passed else "⚠️  测试失败"))
    sys.exit(0 if passed else 1)
