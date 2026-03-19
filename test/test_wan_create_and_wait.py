#!/usr/bin/env python3
"""测试 WAN 一键生视频节点"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_node_registration():
    """测试节点注册"""
    print("=" * 60)
    print("测试 1: 节点注册")
    print("=" * 60)

    try:
        from nodes.WAN import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

        assert "WanCreateAndWait" in NODE_CLASS_MAPPINGS, "WanCreateAndWait 未注册"
        node_class = NODE_CLASS_MAPPINGS["WanCreateAndWait"]

        assert node_class.CATEGORY == "KuAi/WAN", f"CATEGORY 异常: {node_class.CATEGORY}"
        assert node_class.FUNCTION == "create_and_wait", f"FUNCTION 异常: {node_class.FUNCTION}"
        assert node_class.RETURN_TYPES == ("STRING", "STRING", "STRING", "STRING", "STRING")
        assert node_class.RETURN_NAMES == ("任务ID", "状态", "视频URL", "原始提示词", "增强提示词")
        assert NODE_DISPLAY_NAME_MAPPINGS.get("WanCreateAndWait") == "⚡ WAN 一键生视频"

        print("✅ WanCreateAndWait 已注册")
        print(f"   分类: {node_class.CATEGORY}")
        print(f"   方法: {node_class.FUNCTION}")
        print(f"   显示名称: {NODE_DISPLAY_NAME_MAPPINGS.get('WanCreateAndWait')}")
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_parameter_structure():
    """测试参数结构与中文标签"""
    print("\n" + "=" * 60)
    print("测试 2: 参数结构")
    print("=" * 60)

    try:
        from nodes.WAN import NODE_CLASS_MAPPINGS

        node_class = NODE_CLASS_MAPPINGS["WanCreateAndWait"]
        input_types = node_class.INPUT_TYPES()
        labels = node_class.INPUT_LABELS()

        required = input_types.get("required", {})
        optional = input_types.get("optional", {})

        expected_required = [
            "model",
            "prompt",
            "negative_prompt",
            "img_url",
            "template",
            "resolution",
            "duration",
            "prompt_extend",
            "watermark",
            "audio",
            "seed",
            "api_key",
        ]
        expected_optional = ["audio_url", "custom_model", "api_base", "max_wait_time", "poll_interval"]

        for key in expected_required:
            assert key in required, f"required 缺少: {key}"
        for key in expected_optional:
            assert key in optional, f"optional 缺少: {key}"

        # 关键默认值检查
        model_options = required["model"][0]
        model_meta = required["model"][1]
        assert "wan2.6-i2v-flash" in model_options, "model 选项缺少 wan2.6-i2v-flash"
        assert "wan2.6-i2v" in model_options, "model 选项缺少 wan2.6-i2v"
        assert model_meta.get("default") == "wan2.6-i2v-flash", "model 默认值异常"

        custom_model_meta = optional["custom_model"][1]
        api_base_meta = optional["api_base"][1]
        assert custom_model_meta.get("default") == "", "custom_model 默认值应为空"
        assert api_base_meta.get("default") == "https://api.kegeai.top", "api_base 默认值异常"

        resolution_options = required["resolution"][0]
        resolution_meta = required["resolution"][1]
        assert resolution_options == ["480P", "720P", "1080P"], f"resolution 选项异常: {resolution_options}"
        assert resolution_meta.get("default") == "720P", "resolution 默认值异常"
        expected_labels = {
            "model", "custom_model", "prompt", "negative_prompt", "img_url", "audio_url",
            "template", "resolution", "duration", "prompt_extend", "watermark", "audio",
            "seed", "api_key", "api_base", "max_wait_time", "poll_interval",
        }
        missing_labels = [k for k in expected_labels if k not in labels]
        assert not missing_labels, f"INPUT_LABELS 缺少: {missing_labels}"

        print("✅ required/optional 参数完整")
        print(f"   required: {list(required.keys())}")
        print(f"   optional: {list(optional.keys())}")
        print("✅ 中文标签完整")
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_local_validation_error():
    """测试本地校验（api_key 缺失）"""
    print("\n" + "=" * 60)
    print("测试 3: 本地校验错误")
    print("=" * 60)

    # 确保不会从环境变量兜底
    old = os.environ.pop("KUAI_API_KEY", None)
    try:
        from nodes.WAN import NODE_CLASS_MAPPINGS

        node = NODE_CLASS_MAPPINGS["WanCreateAndWait"]()
        try:
            node.create_and_wait(
                model="wan2.6-i2v-flash",
                prompt="测试提示词",
                negative_prompt="不要模糊",
                img_url="https://example.com/first_frame.png",
                audio_url="https://example.com/audio.mp3",
                template="none",
                resolution="720P",
                duration=5,
                prompt_extend=True,
                watermark=False,
                audio=True,
                seed=0,
                api_key="",
            )
            print("❌ 期望抛错，但未抛错")
            return False
        except RuntimeError as e:
            msg = str(e)
            assert "API Key 未配置" in msg, f"报错文本不符合预期: {msg}"
            print("✅ 缺少 API Key 时正确报错")
            print(f"   错误信息: {msg}")
            return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if old is not None:
            os.environ["KUAI_API_KEY"] = old


def test_real_api_optional():
    """可选真实 API 测试（有 KUAI_API_KEY 时执行）"""
    print("\n" + "=" * 60)
    print("测试 4: 可选真实 API")
    print("=" * 60)

    api_key = os.environ.get("KUAI_API_KEY", "").strip()
    if not api_key:
        print("⚠️  跳过：未设置 KUAI_API_KEY")
        return True

    test_img_url = os.environ.get("WAN_TEST_IMG_URL", "").strip()
    if not test_img_url:
        print("⚠️  跳过：未设置 WAN_TEST_IMG_URL")
        print("   可设置示例: export WAN_TEST_IMG_URL=https://.../first_frame.png")
        return True

    try:
        from nodes.WAN import NODE_CLASS_MAPPINGS

        node = NODE_CLASS_MAPPINGS["WanCreateAndWait"]()

        try:
            result = node.create_and_wait(
                model="wan2.6-i2v-flash",
                custom_model=os.environ.get("WAN_TEST_CUSTOM_MODEL", "").strip(),
                prompt=os.environ.get("WAN_TEST_PROMPT", "镜头从近景平滑推到中景，人物自然微笑"),
                negative_prompt=os.environ.get("WAN_TEST_NEGATIVE_PROMPT", "低清晰度，闪烁，变形"),
                img_url=test_img_url,
                audio_url=os.environ.get("WAN_TEST_AUDIO_URL", "https://example.com/audio.mp3"),
                template=os.environ.get("WAN_TEST_TEMPLATE", "none"),
                resolution=os.environ.get("WAN_TEST_RESOLUTION", "480P"),
                duration=int(os.environ.get("WAN_TEST_DURATION", "5")),
                prompt_extend=os.environ.get("WAN_TEST_PROMPT_EXTEND", "true").lower() == "true",
                watermark=os.environ.get("WAN_TEST_WATERMARK", "false").lower() == "true",
                audio=os.environ.get("WAN_TEST_AUDIO", "true").lower() == "true",
                seed=int(os.environ.get("WAN_TEST_SEED", "0")),
                api_key=api_key,
                api_base=os.environ.get("WAN_TEST_API_BASE", "https://api.kegeai.top"),
                max_wait_time=int(os.environ.get("WAN_TEST_MAX_WAIT", "60")),
                poll_interval=int(os.environ.get("WAN_TEST_POLL", "10")),
            )

            assert isinstance(result, tuple) and len(result) == 5, "返回结构应为5元组"
            task_id, status, video_url, orig_prompt, actual_prompt = result
            assert str(task_id).strip(), "task_id 不能为空"

            print("✅ 真实 API 调用完成")
            print(f"   任务ID: {task_id}")
            print(f"   状态: {status}")
            print(f"   视频URL: {video_url[:120] if video_url else 'N/A'}")
            print(f"   原始提示词: {orig_prompt[:80] if orig_prompt else 'N/A'}")
            print(f"   增强提示词: {actual_prompt[:80] if actual_prompt else 'N/A'}")
            return True

        except RuntimeError as e:
            # 允许超时，提示可继续查询
            msg = str(e)
            if "超时" in msg and "任务ID" in msg:
                print("⚠️  真实 API 测试超时（可接受）")
                print(f"   错误信息: {msg}")
                return True
            raise

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🧪 WAN 一键生视频节点测试套件\n")

    results = []
    results.append(("节点注册", test_node_registration()))
    results.append(("参数结构", test_parameter_structure()))
    results.append(("本地校验错误", test_local_validation_error()))
    results.append(("可选真实 API", test_real_api_optional()))

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")

    all_passed = all(item[1] for item in results)
    print("\n" + ("🎉 所有测试通过！" if all_passed else "⚠️  部分测试失败"))
    sys.exit(0 if all_passed else 1)
