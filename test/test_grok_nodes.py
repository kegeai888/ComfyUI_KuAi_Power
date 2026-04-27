#!/usr/bin/env python3
"""测试 Grok 视频生成节点"""

import sys
import os
import requests
from unittest.mock import Mock, patch

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_node_registration():
    """测试节点注册"""
    print("=" * 60)
    print("测试 1: 节点注册")
    print("=" * 60)

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

        expected_nodes = ['GrokCreateVideo', 'GrokQueryVideo', 'GrokCreateAndWait']

        for node_name in expected_nodes:
            if node_name in NODE_CLASS_MAPPINGS:
                print(f"✅ {node_name} 已注册")
                node_class = NODE_CLASS_MAPPINGS[node_name]
                print(f"   分类: {node_class.CATEGORY}")
                print(f"   显示名称: {NODE_DISPLAY_NAME_MAPPINGS.get(node_name)}")

                # 检查必需方法
                assert hasattr(node_class, 'INPUT_TYPES'), f"{node_name} 缺少 INPUT_TYPES"
                assert hasattr(node_class, 'RETURN_TYPES'), f"{node_name} 缺少 RETURN_TYPES"
                assert hasattr(node_class, 'FUNCTION'), f"{node_name} 缺少 FUNCTION"

                input_types = node_class.INPUT_TYPES()
                print(f"   必需参数: {list(input_types.get('required', {}).keys())}")
                print(f"   可选参数: {list(input_types.get('optional', {}).keys())}")
                print()
            else:
                print(f"❌ {node_name} 未注册")
                return False

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

        # 执行测试
        print("🔄 执行创建视频测试...")
        result = node.create(
            prompt="A cat playing with a ball",
            aspect_ratio="3:2",
            size="1080P",
            api_key=api_key,
            image_urls=""
        )

        print(f"✅ 创建成功")
        print(f"   返回类型: {type(result)}")
        print(f"   返回值数量: {len(result)}")
        print(f"   任务ID: {result[0]}")
        print(f"   状态: {result[1]}")
        print(f"   增强提示词: {result[2][:100] if result[2] else 'N/A'}...")

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
        print("   设置方法: export GROK_TEST_TASK_ID=your_task_id")
        return True

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS

        node_class = NODE_CLASS_MAPPINGS['GrokQueryVideo']
        node = node_class()

        # 执行测试
        print(f"🔄 查询任务: {test_task_id}")
        result = node.query(
            task_id=test_task_id,
            api_key=api_key
        )

        print(f"✅ 查询成功")
        print(f"   任务ID: {result[0]}")
        print(f"   状态: {result[1]}")
        print(f"   视频URL: {result[2] if result[2] else 'N/A'}")
        print(f"   增强提示词: {result[3][:100] if result[3] else 'N/A'}...")

        return True

    except Exception as e:
        print(f"❌ 执行测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_input_labels():
    """测试中文标签"""
    print("\n" + "=" * 60)
    print("测试 4: 中文标签")
    print("=" * 60)

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS

        for node_name in ['GrokCreateVideo', 'GrokQueryVideo', 'GrokCreateAndWait']:
            node_class = NODE_CLASS_MAPPINGS[node_name]

            if hasattr(node_class, 'INPUT_LABELS'):
                labels = node_class.INPUT_LABELS()
                print(f"✅ {node_name} 中文标签:")
                for key, label in labels.items():
                    print(f"   {key}: {label}")
            else:
                print(f"⚠️  {node_name} 没有 INPUT_LABELS 方法")

            print()

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_parameter_validation():
    """测试参数验证"""
    print("\n" + "=" * 60)
    print("测试 5: 参数验证")
    print("=" * 60)

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS

        # 测试 GrokCreateVideo 参数
        node_class = NODE_CLASS_MAPPINGS['GrokCreateVideo']
        input_types = node_class.INPUT_TYPES()

        required = input_types.get('required', {})
        optional = input_types.get('optional', {})

        print("GrokCreateVideo 参数检查:")

        # 检查必需参数
        expected_required = ['prompt', 'aspect_ratio', 'size', 'api_key']
        for param in expected_required:
            if param in required:
                print(f"   ✅ {param} (必需)")
            else:
                print(f"   ❌ {param} (缺失)")

        # 检查可选参数
        expected_optional = ['image_urls', 'custom_model']
        for param in expected_optional:
            if param in optional:
                print(f"   ✅ {param} (可选)")
            else:
                print(f"   ⚠️  {param} (未定义)")

        # 检查宽高比选项
        aspect_ratio_options = required.get('aspect_ratio', [None])[0]
        print(f"\n   宽高比选项: {aspect_ratio_options}")

        # 检查分辨率选项
        size_options = required.get('size', [None])[0]
        print(f"   分辨率选项: {size_options}")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_extend_task_origin_not_exist_message():
    """回归测试: task_origin_not_exist 错误应包含操作指引"""
    print("\n" + "=" * 60)
    print("测试 6: GrokExtendVideo task_origin_not_exist 错误指引")
    print("=" * 60)

    try:
        from nodes.Grok.grok import GrokExtendVideo

        mock_resp = Mock()
        mock_resp.status_code = 400
        mock_resp.json.return_value = {"error": {"message": "task_origin_not_exist"}}
        mock_resp.text = "task_origin_not_exist"

        with patch("nodes.Grok.grok.requests.post", return_value=mock_resp):
            node = GrokExtendVideo()
            try:
                node.create(
                    prompt="test prompt",
                    task_id="fake-task-id",
                    model="grok-video-3",
                    start_time=10,
                    aspect_ratio="3:2",
                    size="720P",
                    api_key="test-key",
                )
                print("❌ 应抛出 RuntimeError 但未抛出")
                return False
            except RuntimeError as e:
                msg = str(e)
                required_fragments = [
                    "原始视频任务不存在或不可扩展",
                    "task_id 是否来自首段视频节点的真实输出",
                    "同一个 API 地址",
                    "同一账号",
                    "task_origin_not_exist",
                ]
                missing = [f for f in required_fragments if f not in msg]
                if missing:
                    print(f"❌ 错误消息缺少以下内容: {missing}")
                    print(f"   实际消息: {msg}")
                    return False
                print("✅ 错误消息包含所有必要指引")
                return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_extend_model_and_size_options():
    """测试 GrokExtendVideoAndWait 模型、分辨率与默认 API 地址"""
    print("\n" + "=" * 60)
    print("测试 6: GrokExtendVideoAndWait 参数选项")
    print("=" * 60)

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS

        node_class = NODE_CLASS_MAPPINGS['GrokExtendVideoAndWait']
        input_types = node_class.INPUT_TYPES()
        model_options = input_types['required']['model'][0]
        size_options = input_types['required']['size'][0]
        api_base_default = input_types['optional']['api_base'][1]['default']

        expected_models = ['grok-video-3']
        expected_sizes = ['720P', '1080P']
        expected_api_base = 'https://ai.kegeai.top'

        model_ok = model_options == expected_models
        size_ok = size_options == expected_sizes
        api_base_ok = api_base_default == expected_api_base

        if model_ok:
            print(f"✅ 模型选项正确: {model_options}")
        else:
            print(f"❌ 模型选项不符合预期")
            print(f"   期望: {expected_models}")
            print(f"   实际: {model_options}")

        if size_ok:
            print(f"✅ 分辨率选项正确: {size_options}")
        else:
            print(f"❌ 分辨率选项不符合预期")
            print(f"   期望: {expected_sizes}")
            print(f"   实际: {size_options}")

        if api_base_ok:
            print(f"✅ API 地址默认值正确: {api_base_default}")
        else:
            print(f"❌ API 地址默认值不符合预期")
            print(f"   期望: {expected_api_base}")
            print(f"   实际: {api_base_default}")

        return model_ok and size_ok and api_base_ok

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
    results.append(("中文标签", test_input_labels()))
    results.append(("参数验证", test_parameter_validation()))
    results.append(("扩展无效来源错误指引", test_extend_task_origin_not_exist_message()))
    results.append(("扩展模型和分辨率选项", test_extend_model_and_size_options()))

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)
    print("\n" + ("🎉 所有测试通过！" if all_passed else "⚠️  部分测试失败"))

    sys.exit(0 if all_passed else 1)
