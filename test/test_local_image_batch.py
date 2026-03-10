#!/usr/bin/env python3
"""测试本地图片批量工作流功能"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_all_nodes_registration():
    """测试所有新节点注册"""
    print("=" * 60)
    print("测试 1: 新节点注册")
    print("=" * 60)

    try:
        from nodes.Utils import NODE_CLASS_MAPPINGS

        required_nodes = [
            "BatchImageUploader",
            "ImageURLsToGrokBatchTasks",
            "ImageURLsToVeo3BatchTasks"
        ]

        all_registered = True
        for node_name in required_nodes:
            if node_name in NODE_CLASS_MAPPINGS:
                print(f"✅ {node_name} 已注册")
            else:
                print(f"❌ {node_name} 未注册")
                all_registered = False

        return all_registered

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_workflow_files():
    """测试工作流文件存在"""
    print("\n" + "=" * 60)
    print("测试 2: 工作流文件")
    print("=" * 60)

    try:
        import json
        from pathlib import Path

        workflows_dir = Path(__file__).parent.parent / "workflows"
        required_workflows = [
            "grok_local_image2video_batch_workflow.json",
            "veo3_local_image2video_batch_workflow.json"
        ]

        all_exist = True
        for workflow_file in required_workflows:
            workflow_path = workflows_dir / workflow_file
            if workflow_path.exists():
                # 验证 JSON 格式
                with open(workflow_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"✅ {workflow_file} 存在且格式正确")
                print(f"   节点数: {len(data.get('nodes', []))}")
            else:
                print(f"❌ {workflow_file} 不存在")
                all_exist = False

        return all_exist

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_test_directories():
    """测试测试目录和图片"""
    print("\n" + "=" * 60)
    print("测试 3: 测试目录和图片")
    print("=" * 60)

    try:
        from pathlib import Path

        test_dirs = [
            Path("/root/ComfyUI/input/grok/demo1"),
            Path("/root/ComfyUI/input/veo3/demo1")
        ]

        all_ready = True
        for test_dir in test_dirs:
            if test_dir.exists():
                image_files = list(test_dir.glob("*.[pj][np]g")) + list(test_dir.glob("*.png"))
                if image_files:
                    print(f"✅ {test_dir} 存在，包含 {len(image_files)} 个图片")
                else:
                    print(f"⚠️  {test_dir} 存在但没有图片")
                    all_ready = False
            else:
                print(f"❌ {test_dir} 不存在")
                all_ready = False

        return all_ready

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_documentation():
    """测试文档文件"""
    print("\n" + "=" * 60)
    print("测试 4: 文档文件")
    print("=" * 60)

    try:
        from pathlib import Path

        docs_dir = Path(__file__).parent.parent / "docs"
        required_docs = [
            "LOCAL_IMAGE_BATCH_WORKFLOW_GUIDE.md",
            "LOCAL_IMAGE_BATCH_QUICK_REFERENCE.md"
        ]

        all_exist = True
        for doc_file in required_docs:
            doc_path = docs_dir / doc_file
            if doc_path.exists():
                size = doc_path.stat().st_size
                print(f"✅ {doc_file} 存在 ({size} 字节)")
            else:
                print(f"❌ {doc_file} 不存在")
                all_exist = False

        return all_exist

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_node_functionality():
    """测试节点基本功能"""
    print("\n" + "=" * 60)
    print("测试 5: 节点功能")
    print("=" * 60)

    try:
        from nodes.Utils import NODE_CLASS_MAPPINGS
        import json

        # 测试 ImageURLsToGrokBatchTasks
        print("\n测试 ImageURLsToGrokBatchTasks:")
        grok_node = NODE_CLASS_MAPPINGS['ImageURLsToGrokBatchTasks']()

        test_urls = ["https://example.com/1.jpg", "https://example.com/2.jpg"]
        test_urls_json = json.dumps(test_urls)

        result = grok_node.convert(
            image_urls_json=test_urls_json,
            prompt_template="测试提示词",
            model="grok-video-3 (6秒)",
            aspect_ratio="3:2",
            size="1080P",
            enhance_prompt=True,
            output_prefix="test"
        )

        tasks = json.loads(result[0])
        if len(tasks) == 2:
            print(f"✅ 生成 {len(tasks)} 个任务")
            print(f"   任务1: {tasks[0]['prompt'][:20]}...")
        else:
            print(f"❌ 任务数量不正确: {len(tasks)}")
            return False

        # 测试 ImageURLsToVeo3BatchTasks
        print("\n测试 ImageURLsToVeo3BatchTasks:")
        veo3_node = NODE_CLASS_MAPPINGS['ImageURLsToVeo3BatchTasks']()

        result = veo3_node.convert(
            image_urls_json=test_urls_json,
            prompt_template="测试提示词",
            model="veo3.1",
            duration=6,
            aspect_ratio="16:9",
            enhance_prompt=True,
            enable_upsample=False,
            output_prefix="test"
        )

        tasks = json.loads(result[0])
        if len(tasks) == 2:
            print(f"✅ 生成 {len(tasks)} 个任务")
            print(f"   任务1: {tasks[0]['prompt'][:20]}...")
        else:
            print(f"❌ 任务数量不正确: {len(tasks)}")
            return False

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n🧪 本地图片批量工作流测试套件\n")

    results = []
    results.append(("新节点注册", test_all_nodes_registration()))
    results.append(("工作流文件", test_workflow_files()))
    results.append(("测试目录", test_test_directories()))
    results.append(("文档文件", test_documentation()))
    results.append(("节点功能", test_node_functionality()))

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)

    if all_passed:
        print("\n🎉 所有测试通过！")
        print("\n功能说明：")
        print("- 3个新节点已注册并可用")
        print("- 2个新工作流文件已创建")
        print("- 测试目录和图片已准备")
        print("- 完整文档已创建")
        print("\n使用方法：")
        print("1. 在 ComfyUI 中加载工作流")
        print("2. 配置图片目录路径")
        print("3. 执行工作流开始批量处理")
    else:
        print("\n⚠️  部分测试失败，请检查上述问题")

    sys.exit(0 if all_passed else 1)
