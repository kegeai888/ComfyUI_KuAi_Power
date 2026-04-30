"""Tests for Grok-videos nodes."""

import importlib.util
import os
import sys
import types
from unittest.mock import MagicMock, patch

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_GROK_VIDEOS_PY = os.path.join(_ROOT, "nodes", "Grok", "grok_videos.py")
_GROK_INIT_PY = os.path.join(_ROOT, "nodes", "Grok", "__init__.py")


def _ensure_package(name, path):
    if name in sys.modules:
        return
    pkg = types.ModuleType(name)
    pkg.__path__ = [path]
    pkg.__package__ = name
    sys.modules[name] = pkg


def _load_module(mod_name, file_path):
    if mod_name in sys.modules:
        return sys.modules[mod_name]
    spec = importlib.util.spec_from_file_location(mod_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


_ensure_package("nodes", os.path.join(_ROOT, "nodes"))
_ensure_package("nodes.Grok", os.path.join(_ROOT, "nodes", "Grok"))
_module = _load_module("nodes.Grok.grok_videos", _GROK_VIDEOS_PY)


@patch("nodes.Grok.grok_videos.requests.post")
def test_create_posts_documented_multipart_payload(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"id": "task-1", "status": "pending"}
    mock_post.return_value = mock_resp

    node = _module.GrokVideosCreateVideo()
    task_id, status, raw = node.create(
        "一只猫在雨夜霓虹街头奔跑",
        "10",
        "9:16",
        "secret",
        input_reference="https://img.example/cat.png",
        api_base="https://api.kegeai.top",
    )

    _, kwargs = mock_post.call_args
    assert kwargs["files"] == [
        ("model", (None, "grok-videos")),
        ("prompt", (None, "一只猫在雨夜霓虹街头奔跑")),
        ("seconds", (None, "10")),
        ("size", (None, "9:16")),
        ("input_reference", (None, "https://img.example/cat.png")),
    ]
    assert kwargs["headers"] == {"Authorization": "Bearer secret"}
    assert task_id == "task-1"
    assert status == "pending"
    assert '"id": "task-1"' in raw


@patch("nodes.Grok.grok_videos.requests.post")
def test_create_skips_empty_input_reference(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"task_id": "task-2", "status": "processing"}
    mock_post.return_value = mock_resp

    node = _module.GrokVideosCreateVideo()
    task_id, status, _raw = node.create("文生视频", "6", "16:9", "secret", input_reference="   ")

    _, kwargs = mock_post.call_args
    assert kwargs["files"] == [
        ("model", (None, "grok-videos")),
        ("prompt", (None, "文生视频")),
        ("seconds", (None, "6")),
        ("size", (None, "16:9")),
    ]
    assert task_id == "task-2"
    assert status == "processing"


@patch("nodes.Grok.grok_videos.requests.get")
def test_query_returns_video_and_cover(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "id": "task-3",
        "status": "completed",
        "video_url": "https://video.example/out.mp4",
        "cover_url": "https://video.example/out.jpg",
    }
    mock_get.return_value = mock_resp

    node = _module.GrokVideosQueryVideo()
    task_id, status, video_url, cover_url, raw = node.query("task-3", "secret")

    _, kwargs = mock_get.call_args
    assert kwargs["params"] == {"id": "task-3"}
    assert status == "completed"
    assert video_url == "https://video.example/out.mp4"
    assert cover_url == "https://video.example/out.jpg"
    assert '"status": "completed"' in raw
    assert task_id == "task-3"


@patch("nodes.Grok.grok_videos.requests.get")
def test_query_raises_for_failed_task(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"id": "task-4", "status": "failed", "message": "内容不合规"}
    mock_get.return_value = mock_resp

    node = _module.GrokVideosQueryVideo()
    try:
        node.query("task-4", "secret")
        raise AssertionError("expected RuntimeError")
    except RuntimeError as exc:
        assert "Grok-videos 任务失败" in str(exc)
        assert "内容不合规" in str(exc)


@patch("nodes.Grok.grok_videos.requests.get")
def test_query_raises_when_completed_without_video_url(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"id": "task-5", "status": "completed"}
    mock_get.return_value = mock_resp

    node = _module.GrokVideosQueryVideo()
    try:
        node.query("task-5", "secret")
        raise AssertionError("expected RuntimeError")
    except RuntimeError as exc:
        assert "任务已完成但未返回视频URL" in str(exc)


@patch("nodes.Grok.grok_videos.time.sleep", return_value=None)
@patch("nodes.Grok.grok_videos.requests.get")
@patch("nodes.Grok.grok_videos.requests.post")
def test_create_and_wait_polls_until_completed(mock_post, mock_get, _mock_sleep):
    create_resp = MagicMock()
    create_resp.status_code = 200
    create_resp.json.return_value = {"id": "task-6", "status": "pending"}
    mock_post.return_value = create_resp

    query_processing = MagicMock()
    query_processing.status_code = 200
    query_processing.json.return_value = {"id": "task-6", "status": "processing"}
    query_completed = MagicMock()
    query_completed.status_code = 200
    query_completed.json.return_value = {
        "id": "task-6",
        "status": "completed",
        "video_url": "https://video.example/final.mp4",
    }
    mock_get.side_effect = [query_processing, query_completed]

    node = _module.GrokVideosCreateAndWait()
    task_id, status, video_url, raw = node.create_and_wait(
        "测试视频",
        "6",
        "16:9",
        "secret",
        max_wait_time=60,
        poll_interval=10,
    )

    assert task_id == "task-6"
    assert status == "completed"
    assert video_url == "https://video.example/final.mp4"
    assert '"video_url": "https://video.example/final.mp4"' in raw
    assert mock_get.call_count == 2


@patch("nodes.Grok.grok_videos.time.sleep", return_value=None)
@patch("nodes.Grok.grok_videos.requests.get")
@patch("nodes.Grok.grok_videos.requests.post")
def test_create_and_wait_times_out(mock_post, mock_get, _mock_sleep):
    create_resp = MagicMock()
    create_resp.status_code = 200
    create_resp.json.return_value = {"id": "task-7", "status": "pending"}
    mock_post.return_value = create_resp

    query_resp = MagicMock()
    query_resp.status_code = 200
    query_resp.json.return_value = {"id": "task-7", "status": "processing"}
    mock_get.return_value = query_resp

    node = _module.GrokVideosCreateAndWait()
    try:
        node.create_and_wait("测试视频", "6", "16:9", "secret", max_wait_time=60, poll_interval=10)
        raise AssertionError("expected RuntimeError")
    except RuntimeError as exc:
        assert "Grok-videos 视频生成超时" in str(exc)
        assert "task-7" in str(exc)


def test_create_validates_prompt():
    node = _module.GrokVideosCreateVideo()
    try:
        node.create("   ", "6", "16:9", "secret")
        raise AssertionError("expected RuntimeError")
    except RuntimeError as exc:
        assert "提示词不能为空" in str(exc)


def test_create_validates_seconds():
    node = _module.GrokVideosCreateVideo()
    try:
        node.create("提示词", "8", "16:9", "secret")
        raise AssertionError("expected RuntimeError")
    except RuntimeError as exc:
        assert "seconds 只能是 6 或 10" in str(exc)


def test_create_validates_size():
    node = _module.GrokVideosCreateVideo()
    try:
        node.create("提示词", "6", "1:1", "secret")
        raise AssertionError("expected RuntimeError")
    except RuntimeError as exc:
        assert "size 只能是 16:9 或 9:16" in str(exc)


def test_query_validates_task_id():
    node = _module.GrokVideosQueryVideo()
    try:
        node.query("   ", "secret")
        raise AssertionError("expected RuntimeError")
    except RuntimeError as exc:
        assert "任务ID不能为空" in str(exc)


def test_create_and_wait_validates_max_wait_time():
    node = _module.GrokVideosCreateAndWait()
    try:
        node.create_and_wait("测试视频", "6", "16:9", "secret", max_wait_time=30)
        raise AssertionError("expected RuntimeError")
    except RuntimeError as exc:
        assert "最大等待时间必须在 60 到 1800 秒之间" in str(exc)


def test_create_and_wait_validates_poll_interval():
    node = _module.GrokVideosCreateAndWait()
    try:
        node.create_and_wait("测试视频", "6", "16:9", "secret", poll_interval=2)
        raise AssertionError("expected RuntimeError")
    except RuntimeError as exc:
        assert "轮询间隔必须在 5 到 60 秒之间" in str(exc)


def test_registration_exports_new_nodes():
    for mod_name in [
        "nodes.Grok.grok",
        "nodes.Grok.batch_processor",
        "nodes.Grok.concurrent_processor",
        "nodes.Grok.csv_concurrent_processor",
        "nodes.Grok.batch_image_to_csv_task",
        "nodes.Grok.dir_batch_image2video",
        "nodes.Grok.__init__",
    ]:
        sys.modules.pop(mod_name, None)

    grok_stub = types.ModuleType("nodes.Grok.grok")
    for name in [
        "GrokCreateVideo",
        "GrokQueryVideo",
        "GrokCreateAndWait",
        "GrokImage2Video",
        "GrokImage2VideoAndWait",
        "GrokText2Video",
        "GrokText2VideoAndWait",
        "GrokExtendVideo",
        "GrokExtendVideoAndWait",
    ]:
        setattr(grok_stub, name, type(name, (), {}))
    sys.modules["nodes.Grok.grok"] = grok_stub

    batch_stub = types.ModuleType("nodes.Grok.batch_processor")
    batch_stub.GrokBatchProcessor = type("GrokBatchProcessor", (), {})
    sys.modules["nodes.Grok.batch_processor"] = batch_stub

    concurrent_stub = types.ModuleType("nodes.Grok.concurrent_processor")
    concurrent_stub.GrokText2Video10Concurrent = type("GrokText2Video10Concurrent", (), {})
    concurrent_stub.GrokImage2Video10Concurrent = type("GrokImage2Video10Concurrent", (), {})
    sys.modules["nodes.Grok.concurrent_processor"] = concurrent_stub

    csv_stub = types.ModuleType("nodes.Grok.csv_concurrent_processor")
    csv_stub.GrokCSVConcurrentProcessor = type("GrokCSVConcurrentProcessor", (), {})
    sys.modules["nodes.Grok.csv_concurrent_processor"] = csv_stub

    batch_image_stub = types.ModuleType("nodes.Grok.batch_image_to_csv_task")
    batch_image_stub.GrokBatchImageToCSVTask = type("GrokBatchImageToCSVTask", (), {})
    sys.modules["nodes.Grok.batch_image_to_csv_task"] = batch_image_stub

    dir_batch_stub = types.ModuleType("nodes.Grok.dir_batch_image2video")
    dir_batch_stub.GrokDirBatchImage2Video = type("GrokDirBatchImage2Video", (), {})
    sys.modules["nodes.Grok.dir_batch_image2video"] = dir_batch_stub

    init_module = _load_module("nodes.Grok.__init__", _GROK_INIT_PY)

    assert init_module.NODE_CLASS_MAPPINGS["GrokVideosCreateVideo"] is _module.GrokVideosCreateVideo
    assert init_module.NODE_CLASS_MAPPINGS["GrokVideosQueryVideo"] is _module.GrokVideosQueryVideo
    assert init_module.NODE_CLASS_MAPPINGS["GrokVideosCreateAndWait"] is _module.GrokVideosCreateAndWait
    assert init_module.NODE_DISPLAY_NAME_MAPPINGS["GrokVideosCreateVideo"] == "🤖 Grok-videos 生视频 6-10s"
    assert init_module.NODE_DISPLAY_NAME_MAPPINGS["GrokVideosQueryVideo"] == "🔍 Grok-videos 查询视频"
    assert init_module.NODE_DISPLAY_NAME_MAPPINGS["GrokVideosCreateAndWait"] == "⚡ Grok-videos 生视频 6-10s（一键）"
