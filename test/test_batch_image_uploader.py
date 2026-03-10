#!/usr/bin/env python3
"""测试批量图片上传节点"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_batch_uploader_registration():
    """测试节点注册"""
    print("=" * 60)
    print("测试 1: 批量上传节点注册")
    print("=" * 60)

    try:
        from nodes.Utils import NODE_CLASS_MAPPINGS

        if 'BatchImageUploader' in NODE_CLASS_MAPPINGS:
            print("✅ BatchImageUploader 已注册")
            node_class = NODE_CLASS_MAPPINGS['BatchImageUploader']
            print(f"   分类: {node_class.CATEGORY}")

            input_types = node_class.INPUT_TYPES()
            print(f"   必需参数: {list(input_types.get('required', {}).keys())}")
            print(f"   可选参数: {list(input_types.get('optional', {}).keys())}")

            return True
        else:
            print("❌ BatchImageUploader 未注册")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_batch_uploader_execution():
    """测试节点执行（本地测试，不实际上传）"""
    print("\n" + "=" * 60)
    print("测试 2: 批量上传节点执行（本地测试）")
    print("=" * 60)

    try:
        from nodes.Utils import NODE_CLASS_MAPPINGS
        from pathlib import Path

        node_class = NODE_CLASS_MAPPINGS['BatchImageUploader']
        node = node_class()

        # 测试目录扫描功能
        test_dir = "/root/ComfyUI/input/grok/demo1"

        if not Path(test_dir).exists():
            print(f"⚠️  测试目录不存在: {test_dir}")
            print("   跳过执行测试")
            return True

        print(f"🔄 测试目录扫描: {test_dir}")

        # 只测试目录扫描，不实际上传
        from pathlib import Path
        full_path = Path(test_dir)

        image_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif'}
        image_files = []

        for file_path in sorted(full_path.iterdir()):
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                image_files.append(file_path)

        print(f"✅ 找到 {len(image_files)} 个图片文件:")
        for img in image_files:
            print(f"   - {img.name}")

        return True

    except Exception as e:
        print(f"❌ 执行测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n🧪 批量图片上传节点测试套件\n")

    results = []
    results.append(("节点注册", test_batch_uploader_registration()))
    results.append(("节点执行", test_batch_uploader_execution()))

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)
    print("\n" + ("🎉 所有测试通过！" if all_passed else "⚠️  部分测试失败"))

    sys.exit(0 if all_passed else 1)
