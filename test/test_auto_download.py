#!/usr/bin/env python3
"""测试批量处理器自动下载功能"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_grok_batch_processor_params():
    """测试 Grok 批量处理器参数"""
    print("=" * 60)
    print("测试 1: Grok 批量处理器参数")
    print("=" * 60)

    try:
        from nodes.Grok.batch_processor import GrokBatchProcessor

        input_types = GrokBatchProcessor.INPUT_TYPES()
        optional = input_types.get('optional', {})

        required_params = ['auto_download', 'video_save_dir', 'download_timeout']
        all_present = True

        for param in required_params:
            if param in optional:
                print(f"✅ {param}: {optional[param][1].get('default', 'N/A')}")
            else:
                print(f"❌ {param}: 缺失")
                all_present = False

        # 检查 INPUT_LABELS
        labels = GrokBatchProcessor.INPUT_LABELS()
        if 'auto_download' in labels:
            print(f"✅ 中文标签: {labels['auto_download']}")

        return all_present

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_veo3_batch_processor_params():
    """测试 Veo3 批量处理器参数"""
    print("\n" + "=" * 60)
    print("测试 2: Veo3 批量处理器参数")
    print("=" * 60)

    try:
        from nodes.Veo3.batch_processor import Veo3BatchProcessor

        input_types = Veo3BatchProcessor.INPUT_TYPES()
        optional = input_types.get('optional', {})

        required_params = ['auto_download', 'video_save_dir', 'download_timeout']
        all_present = True

        for param in required_params:
            if param in optional:
                print(f"✅ {param}: {optional[param][1].get('default', 'N/A')}")
            else:
                print(f"❌ {param}: 缺失")
                all_present = False

        # 检查 INPUT_LABELS
        labels = Veo3BatchProcessor.INPUT_LABELS()
        if 'auto_download' in labels:
            print(f"✅ 中文标签: {labels['auto_download']}")

        return all_present

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_download_method_exists():
    """测试下载方法是否存在"""
    print("\n" + "=" * 60)
    print("测试 3: 下载方法存在性")
    print("=" * 60)

    try:
        from nodes.Grok.batch_processor import GrokBatchProcessor
        from nodes.Veo3.batch_processor import Veo3BatchProcessor

        grok_processor = GrokBatchProcessor()
        veo3_processor = Veo3BatchProcessor()

        if hasattr(grok_processor, '_download_video'):
            print("✅ Grok 批量处理器包含 _download_video 方法")
        else:
            print("❌ Grok 批量处理器缺少 _download_video 方法")
            return False

        if hasattr(veo3_processor, '_download_video'):
            print("✅ Veo3 批量处理器包含 _download_video 方法")
        else:
            print("❌ Veo3 批量处理器缺少 _download_video 方法")
            return False

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_method_signature():
    """测试方法签名"""
    print("\n" + "=" * 60)
    print("测试 4: 方法签名")
    print("=" * 60)

    try:
        from nodes.Grok.batch_processor import GrokBatchProcessor
        import inspect

        processor = GrokBatchProcessor()

        # 检查 process_batch 方法签名
        sig = inspect.signature(processor.process_batch)
        params = list(sig.parameters.keys())

        required_params = ['auto_download', 'video_save_dir', 'download_timeout']
        all_present = True

        for param in required_params:
            if param in params:
                print(f"✅ process_batch 包含参数: {param}")
            else:
                print(f"❌ process_batch 缺少参数: {param}")
                all_present = False

        return all_present

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("\n🧪 批量处理器自动下载功能测试套件\n")

    results = []
    results.append(("Grok 参数", test_grok_batch_processor_params()))
    results.append(("Veo3 参数", test_veo3_batch_processor_params()))
    results.append(("下载方法", test_download_method_exists()))
    results.append(("方法签名", test_method_signature()))

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)

    if all_passed:
        print("\n🎉 所有测试通过！")
        print("\n新增功能：")
        print("- auto_download: 自动下载视频到本地（默认：True）")
        print("- video_save_dir: 视频保存目录")
        print("  - Grok: output/grok")
        print("  - Veo3: output/veo3")
        print("- download_timeout: 下载超时时间（默认：180秒）")
        print("\n使用方法：")
        print("1. 设置 wait_for_completion=True")
        print("2. 设置 auto_download=True（默认）")
        print("3. 执行工作流，视频将自动下载到指定目录")
    else:
        print("\n⚠️  部分测试失败，请检查上述问题")

    sys.exit(0 if all_passed else 1)
