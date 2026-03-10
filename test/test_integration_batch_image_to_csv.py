#!/usr/bin/env python3
"""集成测试：验证 BatchImageUploader → BatchImageToCSVTask → CSVConcurrentProcessor 数据流"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_data_flow_integration():
    """测试完整数据流集成"""
    print("=" * 60)
    print("集成测试：完整数据流")
    print("=" * 60)

    try:
        # 1. 模拟 BatchImageUploader 输出
        print("\n[步骤 1] 模拟 BatchImageUploader 输出")
        mock_urls = [
            "https://example.com/image1.jpg",
            "https://example.com/image2.jpg",
            "https://example.com/image3.jpg"
        ]
        urls_json = json.dumps(mock_urls, ensure_ascii=False)
        print(f"✓ 生成 {len(mock_urls)} 个图片 URL")
        print(f"  格式: {type(urls_json).__name__}")
        print(f"  示例: {urls_json[:80]}...")

        # 2. 通过 GrokBatchImageToCSVTask 转换
        print("\n[步骤 2] 通过 GrokBatchImageToCSVTask 转换")
        from nodes.Grok import NODE_CLASS_MAPPINGS as GROK_MAPPINGS

        task_generator = GROK_MAPPINGS['GrokBatchImageToCSVTask']()
        tasks_json, task_count = task_generator.generate_tasks(
            image_urls_json=urls_json,
            prompt_template="第{index}个科技视频",
            model="grok-video-3 (6秒)",
            aspect_ratio="3:2",
            size="1080P",
            enhance_prompt=True,
            output_prefix_template="tech_{index}",
            custom_model=""
        )
        print(f"✓ 生成 {task_count} 个任务")
        print(f"  格式: {type(tasks_json).__name__}")

        # 3. 验证任务列表格式（模拟 CSVConcurrentProcessor 接收）
        print("\n[步骤 3] 验证任务列表格式")
        tasks = json.loads(tasks_json)
        assert isinstance(tasks, list), "任务列表应该是数组"
        assert len(tasks) == len(mock_urls), "任务数量应该与图片数量一致"

        print(f"✓ 任务列表格式正确")
        print(f"  任务数量: {len(tasks)}")
        print(f"  第一个任务:")
        for key, value in tasks[0].items():
            print(f"    {key}: {value}")

        # 4. 验证 CSVConcurrentProcessor 可以解析
        print("\n[步骤 4] 验证 CSVConcurrentProcessor 兼容性")
        from nodes.Grok import NODE_CLASS_MAPPINGS as GROK_MAPPINGS

        # 检查必需字段
        required_fields = ["_row_number", "prompt", "image_urls", "model",
                          "aspect_ratio", "size", "enhance_prompt", "output_prefix"]

        for task in tasks:
            for field in required_fields:
                assert field in task, f"缺少必需字段: {field}"

        print(f"✓ 所有必需字段都存在")
        print(f"  必需字段: {', '.join(required_fields)}")

        # 5. 验证数据类型
        print("\n[步骤 5] 验证数据类型")
        task = tasks[0]
        assert isinstance(task["_row_number"], int), "_row_number 应该是整数"
        assert isinstance(task["prompt"], str), "prompt 应该是字符串"
        assert isinstance(task["image_urls"], str), "image_urls 应该是字符串"
        assert task["image_urls"].startswith("http"), "image_urls 应该是有效 URL"
        assert task["enhance_prompt"] in ["true", "false"], "enhance_prompt 应该是 'true' 或 'false'"

        print(f"✓ 所有数据类型正确")

        # 6. 验证模板替换
        print("\n[步骤 6] 验证模板替换")
        for idx, task in enumerate(tasks, start=1):
            expected_prompt = f"第{idx}个科技视频"
            expected_prefix = f"tech_{idx}"
            assert task["prompt"] == expected_prompt, f"提示词模板替换错误: {task['prompt']}"
            assert task["output_prefix"] == expected_prefix, f"输出前缀模板替换错误: {task['output_prefix']}"

        print(f"✓ 模板替换正确")
        print(f"  提示词: {[t['prompt'] for t in tasks]}")
        print(f"  输出前缀: {[t['output_prefix'] for t in tasks]}")

        print("\n" + "=" * 60)
        print("✅ 集成测试通过！数据流完全兼容")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_veo3_data_flow():
    """测试 Veo3 数据流"""
    print("\n" + "=" * 60)
    print("集成测试：Veo3 数据流")
    print("=" * 60)

    try:
        # 模拟数据流
        mock_urls = ["https://example.com/img1.jpg", "https://example.com/img2.jpg"]
        urls_json = json.dumps(mock_urls)

        from nodes.Veo3 import NODE_CLASS_MAPPINGS as VEO_MAPPINGS

        task_generator = VEO_MAPPINGS['VeoBatchImageToCSVTask']()
        tasks_json, task_count = task_generator.generate_tasks(
            image_urls_json=urls_json,
            prompt_template="视频{index}",
            model="veo3.1",
            aspect_ratio="9:16",
            enhance_prompt=True,
            enable_upsample=True,
            output_prefix_template="veo_{index}",
            custom_model=""
        )

        tasks = json.loads(tasks_json)

        # 验证 Veo3 特有字段
        assert "enable_upsample" in tasks[0], "缺少 enable_upsample 字段"
        assert tasks[0]["enable_upsample"] in ["true", "false"], "enable_upsample 格式错误"

        print(f"✓ Veo3 数据流测试通过")
        print(f"  任务数量: {task_count}")
        print(f"  enable_upsample: {tasks[0]['enable_upsample']}")

        return True

    except Exception as e:
        print(f"❌ Veo3 数据流测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🧪 BatchImageToCSVTask 集成测试套件\n")

    results = []
    results.append(("Grok 完整数据流", test_data_flow_integration()))
    results.append(("Veo3 数据流", test_veo3_data_flow()))

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)
    print("\n" + ("🎉 所有集成测试通过！" if all_passed else "⚠️  部分测试失败"))

    sys.exit(0 if all_passed else 1)
