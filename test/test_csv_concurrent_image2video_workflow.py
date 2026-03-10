#!/usr/bin/env python3
"""测试 CSV 并发图生视频工作流（带批量图片上传）"""

import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_grok_csv_concurrent_image2video_workflow_exists():
    """测试 Grok CSV 并发图生视频工作流文件存在"""
    print("=" * 60)
    print("测试 1: Grok CSV 并发图生视频工作流文件")
    print("=" * 60)

    workflow_path = Path("workflows/grok_csv_concurrent_image2video_workflow.json")

    if not workflow_path.exists():
        print(f"❌ 工作流文件不存在: {workflow_path}")
        return False

    print(f"✅ 工作流文件存在: {workflow_path}")

    # 读取并验证工作流结构
    with open(workflow_path) as f:
        workflow = json.load(f)

    nodes = workflow.get('nodes', [])
    print(f"   节点数量: {len(nodes)}")

    # 检查必需节点
    node_types = [node.get('type', '') for node in nodes]

    required_nodes = [
        'BatchImageUploader',      # 批量上传图片
        'CSVBatchReader',          # 读取 CSV
        'GrokCSVConcurrentProcessor'  # 并发处理
    ]

    for required in required_nodes:
        if required in node_types:
            print(f"   ✓ 包含节点: {required}")
        else:
            print(f"   ✗ 缺少节点: {required}")
            return False

    print(f"✅ 工作流结构正确")
    return True


def test_veo3_csv_concurrent_image2video_workflow_exists():
    """测试 Veo3 CSV 并发图生视频工作流文件存在"""
    print("\n" + "=" * 60)
    print("测试 2: Veo3 CSV 并发图生视频工作流文件")
    print("=" * 60)

    workflow_path = Path("workflows/veo3_csv_concurrent_image2video_workflow.json")

    if not workflow_path.exists():
        print(f"❌ 工作流文件不存在: {workflow_path}")
        return False

    print(f"✅ 工作流文件存在: {workflow_path}")

    # 读取并验证工作流结构
    with open(workflow_path) as f:
        workflow = json.load(f)

    nodes = workflow.get('nodes', [])
    print(f"   节点数量: {len(nodes)}")

    # 检查必需节点
    node_types = [node.get('type', '') for node in nodes]

    required_nodes = [
        'BatchImageUploader',      # 批量上传图片
        'CSVBatchReader',          # 读取 CSV
        'VeoCSVConcurrentProcessor'  # 并发处理
    ]

    for required in required_nodes:
        if required in node_types:
            print(f"   ✓ 包含节点: {required}")
        else:
            print(f"   ✗ 缺少节点: {required}")
            return False

    print(f"✅ 工作流结构正确")
    return True


def test_csv_format_for_image2video():
    """测试图生视频 CSV 格式示例"""
    print("\n" + "=" * 60)
    print("测试 3: 图生视频 CSV 格式")
    print("=" * 60)

    # 定义期望的 CSV 格式
    expected_csv_path = Path("workflows/grok_image2video_concurrent.csv")

    if not expected_csv_path.exists():
        print(f"❌ CSV 示例文件不存在: {expected_csv_path}")
        return False

    print(f"✅ CSV 示例文件存在: {expected_csv_path}")

    # 读取并验证 CSV 格式
    with open(expected_csv_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if len(lines) < 2:
        print(f"❌ CSV 文件至少需要 2 行（表头 + 数据）")
        return False

    header = lines[0].strip()
    print(f"   表头: {header}")

    # 检查必需列
    required_columns = ['prompt', 'image_urls', 'output_prefix']

    for col in required_columns:
        if col in header:
            print(f"   ✓ 包含列: {col}")
        else:
            print(f"   ✗ 缺少列: {col}")
            return False

    print(f"✅ CSV 格式正确")
    return True


if __name__ == "__main__":
    print("\n🧪 CSV 并发图生视频工作流测试套件\n")

    results = []
    results.append(("Grok 工作流文件", test_grok_csv_concurrent_image2video_workflow_exists()))
    results.append(("Veo3 工作流文件", test_veo3_csv_concurrent_image2video_workflow_exists()))
    results.append(("CSV 格式示例", test_csv_format_for_image2video()))

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)
    print("\n" + ("🎉 所有测试通过！" if all_passed else "⚠️  部分测试失败 - 需要创建工作流"))

    sys.exit(0 if all_passed else 1)
