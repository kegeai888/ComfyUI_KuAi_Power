#!/usr/bin/env python3
"""测试 BatchImageToCSVTask 节点（Grok 和 Veo3）"""

import sys
import os
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_grok_node_registration():
    """测试 Grok 节点注册"""
    print("=" * 60)
    print("测试 1: Grok 节点注册")
    print("=" * 60)

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

        if 'GrokBatchImageToCSVTask' in NODE_CLASS_MAPPINGS:
            print("✅ GrokBatchImageToCSVTask 已注册")
            node_class = NODE_CLASS_MAPPINGS['GrokBatchImageToCSVTask']
            print(f"   分类: {node_class.CATEGORY}")
            print(f"   显示名称: {NODE_DISPLAY_NAME_MAPPINGS.get('GrokBatchImageToCSVTask')}")

            # 检查必需方法
            assert hasattr(node_class, 'INPUT_TYPES'), "缺少 INPUT_TYPES"
            assert hasattr(node_class, 'RETURN_TYPES'), "缺少 RETURN_TYPES"
            assert hasattr(node_class, 'FUNCTION'), "缺少 FUNCTION"

            input_types = node_class.INPUT_TYPES()
            print(f"   必需参数: {list(input_types.get('required', {}).keys())}")
            print(f"   可选参数: {list(input_types.get('optional', {}).keys())}")

            return True
        else:
            print("❌ GrokBatchImageToCSVTask 未注册")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_veo3_node_registration():
    """测试 Veo3 节点注册"""
    print("\n" + "=" * 60)
    print("测试 2: Veo3 节点注册")
    print("=" * 60)

    try:
        from nodes.Veo3 import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

        if 'VeoBatchImageToCSVTask' in NODE_CLASS_MAPPINGS:
            print("✅ VeoBatchImageToCSVTask 已注册")
            node_class = NODE_CLASS_MAPPINGS['VeoBatchImageToCSVTask']
            print(f"   分类: {node_class.CATEGORY}")
            print(f"   显示名称: {NODE_DISPLAY_NAME_MAPPINGS.get('VeoBatchImageToCSVTask')}")

            input_types = node_class.INPUT_TYPES()
            print(f"   必需参数: {list(input_types.get('required', {}).keys())}")
            print(f"   可选参数: {list(input_types.get('optional', {}).keys())}")

            return True
        else:
            print("❌ VeoBatchImageToCSVTask 未注册")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_grok_json_parsing():
    """测试 Grok JSON 解析和任务生成"""
    print("\n" + "=" * 60)
    print("测试 3: Grok JSON 解析和任务生成")
    print("=" * 60)

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS

        node_class = NODE_CLASS_MAPPINGS['GrokBatchImageToCSVTask']
        node = node_class()

        # 模拟 BatchImageUploader 的输出
        mock_urls = [
            "https://example.com/image1.jpg",
            "https://example.com/image2.jpg",
            "https://example.com/image3.jpg"
        ]
        urls_json = json.dumps(mock_urls, ensure_ascii=False)

        print("🔄 测试任务生成...")
        tasks_json, task_count = node.generate_tasks(
            image_urls_json=urls_json,
            prompt_template="第{index}个科技视频",
            model="grok-video-3 (6秒)",
            aspect_ratio="3:2",
            size="1080P",
            enhance_prompt=True,
            output_prefix_template="tech_{index}",
            custom_model=""
        )

        # 验证输出
        tasks = json.loads(tasks_json)
        assert isinstance(tasks, list), "任务列表应该是数组"
        assert len(tasks) == 3, f"期望 3 个任务，实际 {len(tasks)}"
        assert task_count == 3, f"任务数量应该是 3，实际 {task_count}"

        # 验证第一个任务的结构
        task1 = tasks[0]
        assert task1["_row_number"] == 1, "行号错误"
        assert task1["prompt"] == "第1个科技视频", f"提示词错误: {task1['prompt']}"
        assert task1["image_urls"] == mock_urls[0], "图片 URL 错误"
        assert task1["output_prefix"] == "tech_1", f"输出前缀错误: {task1['output_prefix']}"
        assert task1["model"] == "grok-video-3 (6秒)", "模型错误"
        assert task1["enhance_prompt"] == "true", "enhance_prompt 错误"

        print("✅ JSON 解析和任务生成成功")
        print(f"   生成任务数: {task_count}")
        print(f"   第一个任务: {json.dumps(task1, ensure_ascii=False, indent=2)}")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_veo3_json_parsing():
    """测试 Veo3 JSON 解析和任务生成"""
    print("\n" + "=" * 60)
    print("测试 4: Veo3 JSON 解析和任务生成")
    print("=" * 60)

    try:
        from nodes.Veo3 import NODE_CLASS_MAPPINGS

        node_class = NODE_CLASS_MAPPINGS['VeoBatchImageToCSVTask']
        node = node_class()

        # 模拟 BatchImageUploader 的输出
        mock_urls = [
            "https://example.com/image1.jpg",
            "https://example.com/image2.jpg"
        ]
        urls_json = json.dumps(mock_urls, ensure_ascii=False)

        print("🔄 测试任务生成...")
        tasks_json, task_count = node.generate_tasks(
            image_urls_json=urls_json,
            prompt_template="视频{index}",
            model="veo3.1",
            aspect_ratio="9:16",
            enhance_prompt=True,
            enable_upsample=True,
            output_prefix_template="veo_{index}",
            custom_model=""
        )

        # 验证输出
        tasks = json.loads(tasks_json)
        assert isinstance(tasks, list), "任务列表应该是数组"
        assert len(tasks) == 2, f"期望 2 个任务，实际 {len(tasks)}"
        assert task_count == 2, f"任务数量应该是 2，实际 {task_count}"

        # 验证第一个任务的结构
        task1 = tasks[0]
        assert task1["_row_number"] == 1, "行号错误"
        assert task1["prompt"] == "视频1", f"提示词错误: {task1['prompt']}"
        assert task1["image_urls"] == mock_urls[0], "图片 URL 错误"
        assert task1["output_prefix"] == "veo_1", f"输出前缀错误: {task1['output_prefix']}"
        assert task1["model"] == "veo3.1", "模型错误"
        assert task1["enable_upsample"] == "true", "enable_upsample 错误"

        print("✅ JSON 解析和任务生成成功")
        print(f"   生成任务数: {task_count}")
        print(f"   第一个任务: {json.dumps(task1, ensure_ascii=False, indent=2)}")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_template_replacement():
    """测试模板占位符替换"""
    print("\n" + "=" * 60)
    print("测试 5: 模板占位符替换")
    print("=" * 60)

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS

        node_class = NODE_CLASS_MAPPINGS['GrokBatchImageToCSVTask']
        node = node_class()

        mock_urls = ["https://example.com/img.jpg"]
        urls_json = json.dumps(mock_urls)

        # 测试复杂模板
        tasks_json, _ = node.generate_tasks(
            image_urls_json=urls_json,
            prompt_template="这是第{index}个视频，编号：{index}",
            model="grok-video-3 (6秒)",
            aspect_ratio="3:2",
            size="1080P",
            enhance_prompt=True,
            output_prefix_template="video_{index}_final",
            custom_model=""
        )

        tasks = json.loads(tasks_json)
        task = tasks[0]

        assert task["prompt"] == "这是第1个视频，编号：1", f"模板替换错误: {task['prompt']}"
        assert task["output_prefix"] == "video_1_final", f"输出前缀模板替换错误: {task['output_prefix']}"

        print("✅ 模板占位符替换成功")
        print(f"   提示词: {task['prompt']}")
        print(f"   输出前缀: {task['output_prefix']}")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling():
    """测试错误处理"""
    print("\n" + "=" * 60)
    print("测试 6: 错误处理")
    print("=" * 60)

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS

        node_class = NODE_CLASS_MAPPINGS['GrokBatchImageToCSVTask']
        node = node_class()

        # 测试无效 JSON
        try:
            node.generate_tasks(
                image_urls_json="invalid json",
                prompt_template="test",
                model="grok-video-3 (6秒)",
                aspect_ratio="3:2",
                size="1080P",
                enhance_prompt=True,
                output_prefix_template="test",
                custom_model=""
            )
            print("❌ 应该抛出异常但没有")
            return False
        except RuntimeError as e:
            print(f"✅ 正确捕获无效 JSON 错误: {str(e)}")

        # 测试空数组
        try:
            node.generate_tasks(
                image_urls_json="[]",
                prompt_template="test",
                model="grok-video-3 (6秒)",
                aspect_ratio="3:2",
                size="1080P",
                enhance_prompt=True,
                output_prefix_template="test",
                custom_model=""
            )
            print("❌ 应该抛出异常但没有")
            return False
        except RuntimeError as e:
            print(f"✅ 正确捕获空数组错误: {str(e)}")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🧪 BatchImageToCSVTask 节点测试套件\n")

    results = []
    results.append(("Grok 节点注册", test_grok_node_registration()))
    results.append(("Veo3 节点注册", test_veo3_node_registration()))
    results.append(("Grok JSON 解析", test_grok_json_parsing()))
    results.append(("Veo3 JSON 解析", test_veo3_json_parsing()))
    results.append(("模板占位符替换", test_template_replacement()))
    results.append(("错误处理", test_error_handling()))

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)
    print("\n" + ("🎉 所有测试通过！" if all_passed else "⚠️  部分测试失败"))

    sys.exit(0 if all_passed else 1)
