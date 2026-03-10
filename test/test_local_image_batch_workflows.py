#!/usr/bin/env python3
"""测试本地目录图生视频批量工作流配置"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / "workflows"


def _load(name: str):
    p = WORKFLOWS / name
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def _get_node_by_type(nodes, node_type):
    for n in nodes:
        if n.get("type") == node_type:
            return n
    return None


def _assert_local_image_batch_workflow(data, platform: str, task_converter: str, save_dir: str):
    nodes = data.get("nodes", [])
    links = data.get("links", [])

    assert _get_node_by_type(nodes, "CSVBatchReader") is None, "不应使用 CSVBatchReader"

    uploader = _get_node_by_type(nodes, "BatchImageUploader")
    assert uploader is not None, "缺少 BatchImageUploader 节点"

    uploader_values = uploader.get("widgets_values", [])
    assert uploader_values and isinstance(uploader_values[0], str), "BatchImageUploader 目录配置缺失"
    assert uploader_values[0].startswith(f"/root/ComfyUI/input/{platform}"), f"目录应在 /root/ComfyUI/input/{platform} 下"

    converter = _get_node_by_type(nodes, task_converter)
    assert converter is not None, f"缺少 {task_converter} 节点"

    processor = _get_node_by_type(nodes, f"{platform.capitalize()}BatchProcessor" if platform == "veo3" else "GrokBatchProcessor")
    assert processor is not None, "缺少批量处理节点"

    values = processor.get("widgets_values", [])
    assert len(values) >= 10, "批量处理节点参数数量不正确"
    assert values[4] is True, "wait_for_completion 必须为 true"
    assert values[5] is True, "auto_download 必须为 true"
    assert values[6] == save_dir, f"video_save_dir 必须为 {save_dir}"

    # 校验处理结果和输出目录都被连到 ShowText
    processor_id = processor["id"]
    out0 = any(l[1] == processor_id and l[2] == 0 for l in links)
    out1 = any(l[1] == processor_id and l[2] == 1 for l in links)
    assert out0, "处理结果输出未连接"
    assert out1, "输出目录输出未连接"


def test_veo3_local_image2video_batch_workflow():
    data = _load("veo3_image2video_batch_workflow.json")
    _assert_local_image_batch_workflow(
        data,
        platform="veo3",
        task_converter="ImageURLsToVeo3BatchTasks",
        save_dir="output/veo3",
    )


def test_grok_local_image2video_batch_workflow():
    data = _load("grok_image2video_batch_workflow.json")
    _assert_local_image_batch_workflow(
        data,
        platform="grok",
        task_converter="ImageURLsToGrokBatchTasks",
        save_dir="output/grok",
    )


if __name__ == "__main__":
    print("\n🧪 测试本地目录图生视频批量工作流\n")
    try:
        test_veo3_local_image2video_batch_workflow()
        print("✅ Veo3 工作流通过")
        test_grok_local_image2video_batch_workflow()
        print("✅ Grok 工作流通过")
        print("\n🎉 全部通过")
    except AssertionError as e:
        print(f"❌ 断言失败: {e}")
        raise
