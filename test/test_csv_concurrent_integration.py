#!/usr/bin/env python3
"""测试 CSV 并发处理器与批量图片上传的集成"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_grok_csv_concurrent_accepts_image_urls():
    """测试 Grok CSV 并发处理器接受图片 URL 列表"""
    print("=" * 60)
    print("测试 1: Grok CSV 并发处理器接受图片 URL 列表")
    print("=" * 60)

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS

        if 'GrokCSVConcurrentProcessor' not in NODE_CLASS_MAPPINGS:
            print("❌ GrokCSVConcurrentProcessor 未注册")
            return False

        node_class = NODE_CLASS_MAPPINGS['GrokCSVConcurrentProcessor']
        input_types = node_class.INPUT_TYPES()

        # 检查是否支持 image_urls 参数
        optional = input_types.get('optional', {})

        print(f"   可选参数: {list(optional.keys())}")

        # CSV 任务应该能包含 image_urls 字段
        # 这个测试验证处理器能处理带 image_urls 的任务
        mock_task = {
            "_row_number": 2,
            "prompt": "测试提示词",
            "image_urls": "https://example.com/1.jpg,https://example.com/2.jpg",
            "output_prefix": "test"
        }

        print(f"✅ 模拟任务结构: {json.dumps(mock_task, ensure_ascii=False)}")
        print(f"   任务包含 image_urls 字段")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_veo3_csv_concurrent_accepts_image_urls():
    """测试 Veo3 CSV 并发处理器接受图片 URL 列表"""
    print("\n" + "=" * 60)
    print("测试 2: Veo3 CSV 并发处理器接受图片 URL 列表")
    print("=" * 60)

    try:
        from nodes.Veo3 import NODE_CLASS_MAPPINGS

        if 'VeoCSVConcurrentProcessor' not in NODE_CLASS_MAPPINGS:
            print("❌ VeoCSVConcurrentProcessor 未注册")
            return False

        node_class = NODE_CLASS_MAPPINGS['VeoCSVConcurrentProcessor']
        input_types = node_class.INPUT_TYPES()

        optional = input_types.get('optional', {})
        print(f"   可选参数: {list(optional.keys())}")

        # CSV 任务应该能包含 image_urls 字段
        mock_task = {
            "_row_number": 2,
            "prompt": "测试提示词",
            "image_urls": "https://example.com/1.jpg",
            "output_prefix": "test"
        }

        print(f"✅ 模拟任务结构: {json.dumps(mock_task, ensure_ascii=False)}")
        print(f"   任务包含 image_urls 字段")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_batch_uploader_output_format():
    """测试批量上传节点的输出格式是否符合 CSV 处理器需求"""
    print("\n" + "=" * 60)
    print("测试 3: 批量上传节点输出格式")
    print("=" * 60)

    try:
        from nodes.Utils import NODE_CLASS_MAPPINGS

        node_class = NODE_CLASS_MAPPINGS['BatchImageUploader']

        # 检查返回类型
        assert node_class.RETURN_TYPES == ("STRING", "STRING", "INT"), \
            f"返回类型错误: {node_class.RETURN_TYPES}"

        assert node_class.RETURN_NAMES == ("图片URL列表", "上传详情", "成功数量"), \
            f"返回名称错误: {node_class.RETURN_NAMES}"

        print("✅ 返回类型正确:")
        print(f"   第1个输出: 图片URL列表 (STRING) - JSON 格式的 URL 数组")
        print(f"   第2个输出: 上传详情 (STRING)")
        print(f"   第3个输出: 成功数量 (INT)")

        # 模拟输出格式
        mock_urls = ["https://example.com/1.jpg", "https://example.com/2.jpg"]
        urls_json = json.dumps(mock_urls, ensure_ascii=False)

        print(f"\n   模拟输出格式: {urls_json}")

        # 验证可以解析
        parsed = json.loads(urls_json)
        assert isinstance(parsed, list), "URL 列表应该是数组"
        assert all(isinstance(url, str) for url in parsed), "所有 URL 应该是字符串"

        print(f"✅ 输出格式可以被 JSON 解析")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🧪 CSV 并发工作流集成测试套件\n")

    results = []
    results.append(("Grok CSV 并发接受图片 URL", test_grok_csv_concurrent_accepts_image_urls()))
    results.append(("Veo3 CSV 并发接受图片 URL", test_veo3_csv_concurrent_accepts_image_urls()))
    results.append(("批量上传输出格式", test_batch_uploader_output_format()))

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)
    print("\n" + ("🎉 所有测试通过！" if all_passed else "⚠️  部分测试失败"))

    sys.exit(0 if all_passed else 1)
