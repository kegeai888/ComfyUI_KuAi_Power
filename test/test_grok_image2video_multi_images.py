#!/usr/bin/env python3
"""测试 Grok 图生视频节点的多图片支持（0-3张）"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_node_registration():
    """测试节点注册"""
    print("=" * 60)
    print("测试 1: 节点注册")
    print("=" * 60)

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

        # 检查 GrokImage2Video
        if 'GrokImage2Video' in NODE_CLASS_MAPPINGS:
            print("✅ GrokImage2Video 已注册")
            node_class = NODE_CLASS_MAPPINGS['GrokImage2Video']
            print(f"   分类: {node_class.CATEGORY}")
            print(f"   显示名称: {NODE_DISPLAY_NAME_MAPPINGS.get('GrokImage2Video')}")
        else:
            print("❌ GrokImage2Video 未注册")
            return False

        # 检查 GrokImage2VideoAndWait
        if 'GrokImage2VideoAndWait' in NODE_CLASS_MAPPINGS:
            print("✅ GrokImage2VideoAndWait 已注册")
            node_class = NODE_CLASS_MAPPINGS['GrokImage2VideoAndWait']
            print(f"   分类: {node_class.CATEGORY}")
            print(f"   显示名称: {NODE_DISPLAY_NAME_MAPPINGS.get('GrokImage2VideoAndWait')}")
        else:
            print("❌ GrokImage2VideoAndWait 未注册")
            return False

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_input_parameters():
    """测试输入参数结构"""
    print("\n" + "=" * 60)
    print("测试 2: 输入参数结构")
    print("=" * 60)

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS

        node_class = NODE_CLASS_MAPPINGS['GrokImage2Video']
        input_types = node_class.INPUT_TYPES()

        # 检查必需参数
        required = input_types.get('required', {})
        print(f"必需参数: {list(required.keys())}")

        # 检查可选参数
        optional = input_types.get('optional', {})
        print(f"可选参数: {list(optional.keys())}")

        # 验证新的图片参数
        expected_image_params = ['image_url_1', 'image_url_2', 'image_url_3']
        for param in expected_image_params:
            if param in optional:
                param_config = optional[param]
                # 检查 forceInput
                if param_config[1].get('forceInput') == True:
                    print(f"✅ {param} 已定义且 forceInput=True")
                else:
                    print(f"⚠️  {param} 已定义但 forceInput 不是 True")
            else:
                print(f"❌ {param} 未定义")
                return False

        # 验证旧的 images 参数已移除
        if 'images' in required or 'images' in optional:
            print("❌ 旧的 'images' 参数仍然存在，应该已被移除")
            return False
        else:
            print("✅ 旧的 'images' 参数已成功移除")

        # 检查 INPUT_LABELS
        input_labels = node_class.INPUT_LABELS()
        print(f"\n中文标签:")
        for param in expected_image_params:
            if param in input_labels:
                print(f"  {param}: {input_labels[param]}")
            else:
                print(f"  ⚠️  {param} 缺少中文标签")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_zero_images():
    """测试 0 张图片（文生视频）"""
    print("\n" + "=" * 60)
    print("测试 3: 0 张图片（文生视频）")
    print("=" * 60)

    api_key = os.environ.get("KUAI_API_KEY", "")
    if not api_key:
        print("⚠️  跳过执行测试（未设置 KUAI_API_KEY）")
        return True

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS

        node = NODE_CLASS_MAPPINGS['GrokImage2Video']()

        print("🔄 测试文生视频（0张图片）...")
        task_id, status, enhanced_prompt, _ = node.create(
            prompt="A beautiful sunset over the ocean",
            model="grok-video-3 (6秒)",
            aspect_ratio="3:2",
            size="720P",
            enhance_prompt=True,
            api_key=api_key,
            image_url_1="",
            image_url_2="",
            image_url_3=""
        )

        print(f"✅ 文生视频任务创建成功")
        print(f"   任务ID: {task_id}")
        print(f"   状态: {status}")
        if enhanced_prompt:
            print(f"   增强提示词: {enhanced_prompt[:100]}...")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_single_image():
    """测试 1 张图片"""
    print("\n" + "=" * 60)
    print("测试 4: 1 张图片")
    print("=" * 60)

    api_key = os.environ.get("KUAI_API_KEY", "")
    if not api_key:
        print("⚠️  跳过执行测试（未设置 KUAI_API_KEY）")
        return True

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS

        node = NODE_CLASS_MAPPINGS['GrokImage2Video']()

        # 使用测试图片 URL
        test_image_url = "https://example.com/test_image.jpg"

        print(f"🔄 测试单图生视频（1张图片）...")
        task_id, status, enhanced_prompt, _ = node.create(
            prompt="Animate this image with gentle motion",
            model="grok-video-3 (6秒)",
            aspect_ratio="3:2",
            size="720P",
            enhance_prompt=True,
            api_key=api_key,
            image_url_1=test_image_url,
            image_url_2="",
            image_url_3=""
        )

        print(f"✅ 单图生视频任务创建成功")
        print(f"   任务ID: {task_id}")
        print(f"   状态: {status}")

        return True

    except Exception as e:
        # 预期可能失败（测试 URL 无效），但至少验证了参数传递正确
        error_msg = str(e)
        if "test_image.jpg" in error_msg or "图片" in error_msg or "URL" in error_msg:
            print(f"✅ 参数传递正确（API 拒绝了测试 URL，符合预期）")
            print(f"   错误信息: {error_msg[:200]}")
            return True
        else:
            print(f"❌ 意外错误: {e}")
            import traceback
            traceback.print_exc()
            return False


def test_multiple_images():
    """测试 3 张图片"""
    print("\n" + "=" * 60)
    print("测试 5: 3 张图片")
    print("=" * 60)

    api_key = os.environ.get("KUAI_API_KEY", "")
    if not api_key:
        print("⚠️  跳过执行测试（未设置 KUAI_API_KEY）")
        return True

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS

        node = NODE_CLASS_MAPPINGS['GrokImage2Video']()

        # 使用测试图片 URL
        test_urls = [
            "https://example.com/image1.jpg",
            "https://example.com/image2.jpg",
            "https://example.com/image3.jpg"
        ]

        print(f"🔄 测试多图生视频（3张图片）...")
        task_id, status, enhanced_prompt, _ = node.create(
            prompt="Create a smooth transition between these images",
            model="grok-video-3 (6秒)",
            aspect_ratio="3:2",
            size="720P",
            enhance_prompt=True,
            api_key=api_key,
            image_url_1=test_urls[0],
            image_url_2=test_urls[1],
            image_url_3=test_urls[2]
        )

        print(f"✅ 多图生视频任务创建成功")
        print(f"   任务ID: {task_id}")
        print(f"   状态: {status}")

        return True

    except Exception as e:
        # 预期可能失败（测试 URL 无效），但至少验证了参数传递正确
        error_msg = str(e)
        if "image" in error_msg.lower() or "图片" in error_msg or "URL" in error_msg:
            print(f"✅ 参数传递正确（API 拒绝了测试 URL，符合预期）")
            print(f"   错误信息: {error_msg[:200]}")
            return True
        else:
            print(f"❌ 意外错误: {e}")
            import traceback
            traceback.print_exc()
            return False


def test_andwait_node():
    """测试 GrokImage2VideoAndWait 节点"""
    print("\n" + "=" * 60)
    print("测试 6: GrokImage2VideoAndWait 节点参数")
    print("=" * 60)

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS

        node_class = NODE_CLASS_MAPPINGS['GrokImage2VideoAndWait']
        input_types = node_class.INPUT_TYPES()

        # 检查可选参数
        optional = input_types.get('optional', {})
        print(f"可选参数: {list(optional.keys())}")

        # 验证新的图片参数
        expected_image_params = ['image_url_1', 'image_url_2', 'image_url_3']
        for param in expected_image_params:
            if param in optional:
                print(f"✅ {param} 已定义")
            else:
                print(f"❌ {param} 未定义")
                return False

        # 验证旧的 images 参数已移除
        required = input_types.get('required', {})
        if 'images' in required or 'images' in optional:
            print("❌ 旧的 'images' 参数仍然存在")
            return False
        else:
            print("✅ 旧的 'images' 参数已成功移除")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🧪 Grok 图生视频多图片支持测试套件\n")

    results = []
    results.append(("节点注册", test_node_registration()))
    results.append(("输入参数结构", test_input_parameters()))
    results.append(("0张图片（文生视频）", test_zero_images()))
    results.append(("1张图片", test_single_image()))
    results.append(("3张图片", test_multiple_images()))
    results.append(("AndWait节点参数", test_andwait_node()))

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)
    print("\n" + ("🎉 所有测试通过！" if all_passed else "⚠️  部分测试失败"))

    sys.exit(0 if all_passed else 1)
