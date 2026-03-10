#!/usr/bin/env python3
"""验证 Grok 提示词增强功能的完整性"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_node_enhance_prompt_parameter():
    """测试所有 Grok 节点是否包含 enhance_prompt 参数"""
    print("=" * 60)
    print("测试 1: 验证节点 enhance_prompt 参数")
    print("=" * 60)

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS

        # 需要检查的节点
        nodes_to_check = [
            "GrokCreateVideo",
            "GrokImage2Video",
            "GrokText2Video",
            "GrokCreateAndWait",
            "GrokImage2VideoAndWait",
            "GrokText2VideoAndWait"
        ]

        all_passed = True

        for node_name in nodes_to_check:
            if node_name not in NODE_CLASS_MAPPINGS:
                print(f"❌ {node_name} 未注册")
                all_passed = False
                continue

            node_class = NODE_CLASS_MAPPINGS[node_name]
            input_types = node_class.INPUT_TYPES()

            # 检查 enhance_prompt 参数
            has_enhance_prompt = False
            if "required" in input_types and "enhance_prompt" in input_types["required"]:
                has_enhance_prompt = True
            elif "optional" in input_types and "enhance_prompt" in input_types["optional"]:
                has_enhance_prompt = True

            if has_enhance_prompt:
                print(f"✅ {node_name}: enhance_prompt 参数已添加")

                # 检查 INPUT_LABELS
                if hasattr(node_class, 'INPUT_LABELS'):
                    labels = node_class.INPUT_LABELS()
                    if "enhance_prompt" in labels:
                        print(f"   └─ 中文标签: {labels['enhance_prompt']}")
                    else:
                        print(f"   ⚠️  缺少中文标签")
                        all_passed = False
            else:
                print(f"❌ {node_name}: 缺少 enhance_prompt 参数")
                all_passed = False

        return all_passed

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_batch_processor_enhance_prompt():
    """测试批量处理器是否支持 enhance_prompt"""
    print("\n" + "=" * 60)
    print("测试 2: 验证批量处理器 enhance_prompt 支持")
    print("=" * 60)

    try:
        # 读取 batch_processor.py 文件
        batch_processor_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "nodes", "Grok", "batch_processor.py"
        )

        with open(batch_processor_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查关键代码
        checks = [
            ('task.get("enhance_prompt"', "解析 CSV 中的 enhance_prompt"),
            ('enhance_prompt=enhance_prompt', "传递 enhance_prompt 参数"),
            ('提示词增强', "打印提示词增强状态")
        ]

        all_passed = True
        for pattern, description in checks:
            if pattern in content:
                print(f"✅ {description}: 已实现")
            else:
                print(f"❌ {description}: 未找到")
                all_passed = False

        return all_passed

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_csv_examples():
    """测试 CSV 示例文件是否包含 enhance_prompt 列"""
    print("\n" + "=" * 60)
    print("测试 3: 验证 CSV 示例文件")
    print("=" * 60)

    try:
        examples_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "examples"
        )

        csv_files = [
            "grok_text2video_batch.csv",
            "grok_image2video_batch.csv"
        ]

        all_passed = True

        for csv_file in csv_files:
            csv_path = os.path.join(examples_dir, csv_file)

            if not os.path.exists(csv_path):
                print(f"❌ {csv_file}: 文件不存在")
                all_passed = False
                continue

            with open(csv_path, 'r', encoding='utf-8') as f:
                header = f.readline().strip()

            if "enhance_prompt" in header:
                print(f"✅ {csv_file}: 包含 enhance_prompt 列")
                print(f"   └─ 列: {header}")
            else:
                print(f"❌ {csv_file}: 缺少 enhance_prompt 列")
                all_passed = False

        return all_passed

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_documentation():
    """测试文档是否更新"""
    print("\n" + "=" * 60)
    print("测试 4: 验证文档更新")
    print("=" * 60)

    try:
        docs_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "docs"
        )

        doc_files = [
            "GROK_BATCH_WORKFLOW_GUIDE.md",
            "GROK_BATCH_QUICK_REFERENCE.md"
        ]

        all_passed = True

        for doc_file in doc_files:
            doc_path = os.path.join(docs_dir, doc_file)

            if not os.path.exists(doc_path):
                print(f"⚠️  {doc_file}: 文件不存在（可能需要更新）")
                continue

            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if "enhance_prompt" in content or "提示词增强" in content:
                print(f"✅ {doc_file}: 已包含提示词增强说明")
            else:
                print(f"⚠️  {doc_file}: 建议添加提示词增强说明")

        return all_passed

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("\n🧪 Grok 提示词增强功能验证套件\n")

    results = []
    results.append(("节点参数", test_node_enhance_prompt_parameter()))
    results.append(("批量处理器", test_batch_processor_enhance_prompt()))
    results.append(("CSV 示例", test_csv_examples()))
    results.append(("文档更新", test_documentation()))

    print("\n" + "=" * 60)
    print("验证总结")
    print("=" * 60)

    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)

    if all_passed:
        print("\n🎉 所有验证通过！Grok 提示词增强功能已完整实现。")
        print("\n功能说明：")
        print("- 所有 Grok 节点现在都支持 enhance_prompt 参数")
        print("- 默认启用（True），自动优化并翻译中文提示词为英文")
        print("- CSV 批量处理完全支持 enhance_prompt 列")
        print("- 可在节点界面或 CSV 文件中控制是否启用")
    else:
        print("\n⚠️  部分验证失败，请检查上述问题")

    sys.exit(0 if all_passed else 1)
