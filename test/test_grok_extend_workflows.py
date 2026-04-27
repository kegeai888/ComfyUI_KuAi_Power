#!/usr/bin/env python3
"""测试 Grok 扩展视频工作流配置"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / "workflows"


TEXT_WORKFLOW = "grok_text2video_extend_complete_workflow.json"
IMAGE_WORKFLOW = "grok_image2video_extend_complete_workflow.json"


EXPECTED_TEXT_LINKS = [
    ("GrokText2VideoAndWait", 0, "任务ID", "STRING", "GrokExtendVideoAndWait", 0, "task_id", "STRING", None),
    ("GrokText2VideoAndWait", 4, "视频时长", "INT", "GrokExtendVideoAndWait", 1, "start_time", "INT", None),
    ("GrokExtendVideoAndWait", 2, "视频URL", "STRING", "DownloadVideo", 0, "video_url", "STRING", None),
    ("GrokExtendVideoAndWait", 3, "扩展提示词", "STRING", "ShowText", 0, "text", "STRING", "📝 扩展提示词显示"),
    ("GrokExtendVideoAndWait", 4, "视频时长", "INT", "ShowText", 0, "text", "INT", "🕒 扩展后总时长显示"),
    ("DownloadVideo", 0, "本地路径", "STRING", "ShowText", 0, "text", "STRING", "📁 本地路径显示"),
]

EXPECTED_IMAGE_LINKS = [
    ("LoadImage", 0, "IMAGE", "IMAGE", "UploadToImageHost", 0, "image", "IMAGE", None),
    ("UploadToImageHost", 0, "图片URL", "STRING", "GrokImage2VideoAndWait", 0, "image_url_1", "STRING", None),
    ("GrokImage2VideoAndWait", 0, "任务ID", "STRING", "GrokExtendVideoAndWait", 0, "task_id", "STRING", None),
    ("GrokImage2VideoAndWait", 4, "视频时长", "INT", "GrokExtendVideoAndWait", 1, "start_time", "INT", None),
    ("GrokExtendVideoAndWait", 2, "视频URL", "STRING", "DownloadVideo", 0, "video_url", "STRING", None),
    ("GrokExtendVideoAndWait", 3, "扩展提示词", "STRING", "ShowText", 0, "text", "STRING", "📝 扩展提示词显示"),
    ("GrokExtendVideoAndWait", 4, "视频时长", "INT", "ShowText", 0, "text", "INT", "🕒 扩展后总时长显示"),
    ("DownloadVideo", 0, "本地路径", "STRING", "ShowText", 0, "text", "STRING", "📁 本地路径显示"),
]


def _load(name: str):
    with open(WORKFLOWS / name, "r", encoding="utf-8") as f:
        return json.load(f)


def _nodes_by_type(data):
    result = {}
    for node in data.get("nodes", []):
        result.setdefault(node.get("type"), []).append(node)
    return result


def _assert_single_node(nodes_by_type, node_type: str, title: str = None):
    nodes = nodes_by_type.get(node_type, [])
    if title is not None:
        matched = [node for node in nodes if node.get("title") == title]
        assert len(matched) == 1, f"{node_type} 标题为 {title} 的节点数量应为 1，实际为 {len(matched)}"
        return matched[0]
    assert len(nodes) == 1, f"{node_type} 节点数量应为 1，实际为 {len(nodes)}"
    return nodes[0]


def _find_link(links, src_id, src_slot, dst_id, dst_slot):
    for link in links:
        if link[1] == src_id and link[2] == src_slot and link[3] == dst_id and link[4] == dst_slot:
            return link
    return None


def _assert_expected_links(data, expected_links):
    links = data.get("links", [])
    nodes_by_type = _nodes_by_type(data)

    for (
        src_type,
        src_slot,
        src_name,
        src_data_type,
        dst_type,
        dst_slot,
        dst_name,
        dst_data_type,
        dst_title,
    ) in expected_links:
        src_node = _assert_single_node(nodes_by_type, src_type)
        dst_node = _assert_single_node(nodes_by_type, dst_type, dst_title)

        src_output = src_node["outputs"][src_slot]
        dst_input = dst_node["inputs"][dst_slot]

        assert src_output["name"] == src_name, f"{src_type}[{src_slot}] 输出名应为 {src_name}"
        assert src_output["type"] == src_data_type, f"{src_type}[{src_slot}] 输出类型应为 {src_data_type}"
        assert dst_input["name"] == dst_name, f"{dst_type}[{dst_slot}] 输入名应为 {dst_name}"
        assert dst_input["type"] == dst_data_type, f"{dst_type}[{dst_slot}] 输入类型应为 {dst_data_type}"

        link = _find_link(links, src_node["id"], src_slot, dst_node["id"], dst_slot)
        assert link is not None, f"缺少连线: {src_type}[{src_slot}] -> {dst_type}[{dst_slot}]"
        assert link[5] == src_data_type == dst_data_type, (
            f"连线类型错误: {src_type}[{src_slot}] -> {dst_type}[{dst_slot}]，"
            f"实际 {link[5]}，期望 {src_data_type}"
        )


def test_grok_text2video_extend_complete_workflow():
    data = _load(TEXT_WORKFLOW)
    nodes_by_type = _nodes_by_type(data)

    _assert_single_node(nodes_by_type, "GrokText2VideoAndWait")
    _assert_single_node(nodes_by_type, "GrokExtendVideoAndWait")
    _assert_single_node(nodes_by_type, "DownloadVideo")

    show_text_nodes = nodes_by_type.get("ShowText", [])
    assert len(show_text_nodes) == 3, f"ShowText 节点数量应为 3，实际为 {len(show_text_nodes)}"

    _assert_expected_links(data, EXPECTED_TEXT_LINKS)



def test_grok_image2video_extend_complete_workflow():
    data = _load(IMAGE_WORKFLOW)
    nodes_by_type = _nodes_by_type(data)

    _assert_single_node(nodes_by_type, "LoadImage")
    _assert_single_node(nodes_by_type, "UploadToImageHost")
    _assert_single_node(nodes_by_type, "GrokImage2VideoAndWait")
    _assert_single_node(nodes_by_type, "GrokExtendVideoAndWait")
    _assert_single_node(nodes_by_type, "DownloadVideo")

    show_text_nodes = nodes_by_type.get("ShowText", [])
    assert len(show_text_nodes) == 3, f"ShowText 节点数量应为 3，实际为 {len(show_text_nodes)}"

    _assert_expected_links(data, EXPECTED_IMAGE_LINKS)


if __name__ == "__main__":
    print("\n🧪 测试 Grok 扩展视频工作流\n")
    try:
        test_grok_text2video_extend_complete_workflow()
        print("✅ 文生视频扩展工作流通过")
        test_grok_image2video_extend_complete_workflow()
        print("✅ 图生视频扩展工作流通过")
        print("\n🎉 全部通过")
    except AssertionError as e:
        print(f"❌ 断言失败: {e}")
        raise
