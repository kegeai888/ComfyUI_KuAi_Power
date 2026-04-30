"""Tests for GrokImage nodes."""

import importlib.util
import os
import sys
import types
from unittest.mock import MagicMock, patch

import torch

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_GROK_IMAGE_PY = os.path.join(_ROOT, "nodes", "GrokImage", "grok_image.py")


def _load_module():
    mod_name = "nodes.GrokImage.grok_image"
    if mod_name in sys.modules:
        return sys.modules[mod_name]

    if "nodes" not in sys.modules or getattr(sys.modules.get("nodes"), "__path__", None) is None:
        nodes_pkg = types.ModuleType("nodes")
        nodes_pkg.__path__ = [os.path.join(_ROOT, "nodes")]
        nodes_pkg.__package__ = "nodes"
        sys.modules["nodes"] = nodes_pkg

    if "nodes.GrokImage" not in sys.modules:
        grok_pkg = types.ModuleType("nodes.GrokImage")
        grok_pkg.__path__ = [os.path.join(_ROOT, "nodes", "GrokImage")]
        grok_pkg.__package__ = "nodes.GrokImage"
        sys.modules["nodes.GrokImage"] = grok_pkg

    spec = importlib.util.spec_from_file_location(mod_name, _GROK_IMAGE_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


_module = _load_module()
_extract_image_url = _module._extract_image_url


def test_extract_image_url():
    payload = {"data": [{"url": "https://example.com/generated.png"}]}
    assert _extract_image_url(payload) == "https://example.com/generated.png"

    try:
        _extract_image_url({"data": [{}]})
        raise AssertionError("expected RuntimeError when url is missing")
    except RuntimeError as exc:
        assert "响应中缺少图片URL" in str(exc)


@patch("nodes.GrokImage.grok_image._download_image_as_tensor")
@patch("nodes.GrokImage.grok_image.requests.post")
def test_generate_posts_documented_payload(mock_post, mock_download):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"data": [{"url": "https://img.example/grok.png"}]}
    mock_post.return_value = mock_resp
    mock_download.return_value = torch.zeros((1, 8, 8, 3), dtype=torch.float32)

    node = _module.GrokImageGenerate()
    image, url, raw = node.generate("画一只猫", "grok-4.2-image", "960x960", "secret")

    _, kwargs = mock_post.call_args
    assert kwargs["json"] == {
        "model": "grok-4.2-image",
        "prompt": "画一只猫",
        "size": "960x960",
    }
    assert url == "https://img.example/grok.png"
    assert '"url": "https://img.example/grok.png"' in raw
    assert tuple(image.shape) == (1, 8, 8, 3)


@patch("nodes.GrokImage.grok_image._download_image_as_tensor")
@patch("nodes.GrokImage.grok_image.requests.post")
def test_edit_posts_documented_multipart_payload(mock_post, mock_download):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"data": [{"url": "https://img.example/edit.png"}]}
    mock_post.return_value = mock_resp
    mock_download.return_value = torch.zeros((1, 8, 8, 3), dtype=torch.float32)

    node = _module.GrokImageEdit()
    image, url, raw = node.edit(
        "https://input.example/source.png",
        "改成暖色调",
        "grok-4.1-image",
        "secret",
        aspect_ratio="3:4",
        response_format="url",
        resolution="1k",
        quality="medium",
        n=2,
        api_base="https://api.kegeai.top",
        timeout=90,
    )

    _, kwargs = mock_post.call_args
    assert kwargs["files"] == [
        ("image", (None, "https://input.example/source.png")),
        ("model", (None, "grok-4.1-image")),
        ("prompt", (None, "改成暖色调")),
        ("aspect_ratio", (None, "3:4")),
        ("response_format", (None, "url")),
        ("resolution", (None, "1k")),
        ("quality", (None, "medium")),
        ("n", (None, "2")),
    ]
    assert "data" not in kwargs
    assert url == "https://img.example/edit.png"
    assert '"url": "https://img.example/edit.png"' in raw
    assert tuple(image.shape) == (1, 8, 8, 3)


def test_edit_requires_image_url():
    node = _module.GrokImageEdit()
    try:
        node.edit("   ", "改图", "grok-4.2-image", "key")
        raise AssertionError("expected RuntimeError")
    except RuntimeError as exc:
        assert "图片URL不能为空" in str(exc)


def test_generate_requires_prompt():
    node = _module.GrokImageGenerate()
    try:
        node.generate("   ", "grok-4.2-image", "960x960", "key")
        raise AssertionError("expected RuntimeError")
    except RuntimeError as exc:
        assert "提示词不能为空" in str(exc)
