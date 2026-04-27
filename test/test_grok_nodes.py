#!/usr/bin/env python3
"""测试 Grok 视频生成节点"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_node_registration():
    """测试节点注册"""
    print("=" * 60)
    print("测试 1: 节点注册")
    print("=" * 60)

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

        expected_nodes = [
            'GrokCreateVideo', 'GrokQueryVideo', 'GrokCreateAndWait',
            'GrokText2Video', 'GrokText2VideoAndWait',
            'GrokImage2Video', 'GrokImage2VideoAndWait',
            'GrokExtendVideo', 'GrokExtendVideoAndWait'
        ]

        for node_name in expected_nodes:
            if node_name in NODE_CLASS_MAPPINGS:
                print(f"✅ {node_name} 已注册")
                node_class = NODE_CLASS_MAPPINGS[node_name]
                print(f"   分类: {node_class.CATEGORY}")
                print(f"   显示名称: {NODE_DISPLAY_NAME_MAPPINGS.get(node_name)}")
                assert hasattr(node_class, 'INPUT_TYPES'), f"{node_name} 缺少 INPUT_TYPES"
                assert hasattr(node_class, 'RETURN_TYPES'), f"{node_name} 缺少 RETURN_TYPES"
                assert hasattr(node_class, 'FUNCTION'), f"{node_name} 缺少 FUNCTION"
            else:
                print(f"❌ {node_name} 未注册")
                return False

        assert NODE_DISPLAY_NAME_MAPPINGS['GrokExtendVideo'] == '🎬 Grok 扩展视频'
        assert NODE_DISPLAY_NAME_MAPPINGS['GrokExtendVideoAndWait'] == '⚡ Grok 扩展视频（一键）'
        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_create_video():
    """测试创建视频节点（需要API key）"""
    print("\n" + "=" * 60)
    print("测试 2: 创建视频节点")
    print("=" * 60)

    api_key = os.environ.get("KUAI_API_KEY", "")
    if not api_key:
        print("⚠️  跳过执行测试（未设置 KUAI_API_KEY）")
        print("   设置方法: export KUAI_API_KEY=your_key_here")
        return True

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS

        node_class = NODE_CLASS_MAPPINGS['GrokCreateVideo']
        node = node_class()

        print("🔄 执行创建视频测试...")
        result = node.create(
            prompt="A cat playing with a ball",
            model="grok-video-3 (6秒)",
            aspect_ratio="3:2",
            size="720P",
            enhance_prompt=True,
            api_key=api_key,
            image_urls=""
        )

        print("✅ 创建成功")
        print(f"   返回值数量: {len(result)}")
        print(f"   任务ID: {result[0]}")
        print(f"   状态: {result[1]}")
        print(f"   视频时长: {result[3]}")
        return True

    except Exception as e:
        print(f"❌ 执行测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_query_video():
    """测试查询视频节点（需要API key和任务ID）"""
    print("\n" + "=" * 60)
    print("测试 3: 查询视频节点")
    print("=" * 60)

    api_key = os.environ.get("KUAI_API_KEY", "")
    test_task_id = os.environ.get("GROK_TEST_TASK_ID", "")

    if not api_key:
        print("⚠️  跳过执行测试（未设置 KUAI_API_KEY）")
        return True

    if not test_task_id:
        print("⚠️  跳过执行测试（未设置 GROK_TEST_TASK_ID）")
        return True

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS

        node_class = NODE_CLASS_MAPPINGS['GrokQueryVideo']
        node = node_class()
        result = node.query(task_id=test_task_id, api_key=api_key)

        print("✅ 查询成功")
        print(f"   任务ID: {result[0]}")
        print(f"   状态: {result[1]}")
        print(f"   视频URL: {result[2] if result[2] else 'N/A'}")
        return True

    except Exception as e:
        print(f"❌ 执行测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_parameter_validation():
    """测试参数定义"""
    print("\n" + "=" * 60)
    print("测试 4: 参数定义")
    print("=" * 60)

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS

        text_node = NODE_CLASS_MAPPINGS['GrokText2Video']
        text_inputs = text_node.INPUT_TYPES()['required']
        assert text_inputs['model'][0] == ["grok-video-3 (6秒)", "grok-video-3-10s (10秒)"]
        assert text_inputs['size'][0] == ["720P"]

        image_node = NODE_CLASS_MAPPINGS['GrokImage2Video']
        image_inputs = image_node.INPUT_TYPES()['required']
        assert image_inputs['model'][0] == ["grok-video-3 (6秒)", "grok-video-3-10s (10秒)"]
        assert image_inputs['size'][0] == ["720P"]

        extend_node = NODE_CLASS_MAPPINGS['GrokExtendVideo']
        extend_required = extend_node.INPUT_TYPES()['required']
        assert list(extend_required.keys()) == ['prompt', 'task_id', 'model', 'start_time', 'aspect_ratio', 'size', 'upscale', 'api_key']
        assert extend_required['size'][0] == ["720P"]

        extend_wait = NODE_CLASS_MAPPINGS['GrokExtendVideoAndWait']
        assert extend_wait.RETURN_NAMES == ("任务ID", "状态", "视频URL", "扩展提示词", "视频时长")

        print("✅ 参数定义正确")
        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_duration_outputs():
    """测试视频时长输出"""
    print("\n" + "=" * 60)
    print("测试 5: 视频时长输出")
    print("=" * 60)

    try:
        from nodes.Grok.grok import get_grok_duration
        from nodes.Grok import NODE_CLASS_MAPPINGS

        assert get_grok_duration("grok-video-3 (6秒)") == 6
        assert get_grok_duration("grok-video-3-10s (10秒)") == 10
        assert get_grok_duration("unknown", "grok-video-3-10s (10秒)") == 10

        assert NODE_CLASS_MAPPINGS['GrokCreateVideo'].RETURN_NAMES[-1] == '视频时长'
        assert NODE_CLASS_MAPPINGS['GrokText2Video'].RETURN_NAMES[-1] == '视频时长'
        assert NODE_CLASS_MAPPINGS['GrokImage2Video'].RETURN_NAMES[-1] == '视频时长'
        assert NODE_CLASS_MAPPINGS['GrokText2VideoAndWait'].RETURN_NAMES[-1] == '视频时长'
        assert NODE_CLASS_MAPPINGS['GrokImage2VideoAndWait'].RETURN_NAMES[-1] == '视频时长'

        extend_node = NODE_CLASS_MAPPINGS['GrokExtendVideo']()
        payload_duration = extend_node.create
        assert callable(payload_duration)

        total_duration = 10 + get_grok_duration("grok-video-3-10s (10秒)")
        assert total_duration == 20

        print("✅ 时长输出定义正确")
        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🧪 Grok 视频生成节点测试套件\n")

    results = []
    results.append(("节点注册", test_node_registration()))
    results.append(("创建视频", test_create_video()))
    results.append(("查询视频", test_query_video()))
    results.append(("参数定义", test_parameter_validation()))
    results.append(("视频时长输出", test_duration_outputs()))

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)
    print("\n" + ("🎉 所有测试通过！" if all_passed else "⚠️  部分测试失败"))

    sys.exit(0 if all_passed else 1)
