"""Task 2-4 tests for gpt_image_2_all."""

import importlib.util
import os
import sys
import types
from unittest.mock import MagicMock, patch

import torch

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_GPTIMAGE_2_ALL_PY = os.path.join(_ROOT, "nodes", "GPTImage", "gpt_image_2_all.py")


def _load_module():
    mod_name = "nodes.GPTImage.gpt_image_2_all"
    if mod_name in sys.modules:
        return sys.modules[mod_name]

    if "nodes" not in sys.modules or getattr(sys.modules.get("nodes"), "__path__", None) is None:
        nodes_pkg = types.ModuleType("nodes")
        nodes_pkg.__path__ = [os.path.join(_ROOT, "nodes")]
        nodes_pkg.__package__ = "nodes"
        sys.modules["nodes"] = nodes_pkg

    if "nodes.GPTImage" not in sys.modules:
        gptimage_pkg = types.ModuleType("nodes.GPTImage")
        gptimage_pkg.__path__ = [os.path.join(_ROOT, "nodes", "GPTImage")]
        gptimage_pkg.__package__ = "nodes.GPTImage"
        sys.modules["nodes.GPTImage"] = gptimage_pkg

    spec = importlib.util.spec_from_file_location(mod_name, _GPTIMAGE_2_ALL_PY)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


_module = _load_module()
_extract_generation_result = _module._extract_generation_result
_url_to_tensor = _module._url_to_tensor


def test_extract_generation_result():
    """Task 2: Test _extract_generation_result function."""
    import json

    payload = {
        "data": [
            {"url": "https://example.com/image1.png"},
            {"url": "https://example.com/image2.png"},
        ]
    }
    result = _extract_generation_result(payload)
    assert result == ["https://example.com/image1.png", "https://example.com/image2.png"]

    try:
        _extract_generation_result({"data": [{"revised_prompt": "missing url"}]})
        raise AssertionError("expected RuntimeError when url is missing")
    except RuntimeError as exc:
        assert "响应中没有图像URL" in str(exc)
        assert json.loads(str(exc).split(": ", 1)[1])["data"][0]["revised_prompt"] == "missing url"


def test_url_to_tensor():
    """Task 2: Test _url_to_tensor function."""
    import base64
    from unittest.mock import Mock

    png_bytes = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )
    response = Mock()
    response.content = png_bytes
    response.raise_for_status = Mock()

    with patch("nodes.GPTImage.gpt_image_2_all.requests.get", return_value=response) as mock_get:
        tensor = _url_to_tensor("https://example.com/image.png", timeout=30)

    mock_get.assert_called_once_with("https://example.com/image.png", timeout=30)
    assert isinstance(tensor, torch.Tensor)
    assert tensor.ndim == 4
    assert tensor.shape[0] == 1
    assert tensor.dtype == torch.float32
    assert tensor.min() >= 0.0 and tensor.max() <= 1.0


def test_generate_rejects_blank_prompt():
    """Task 3: blank prompt should fail."""
    node = _module.GPTImage2AllGenerate()
    try:
        node.generate("   ", "gpt-image-2-all", "1024x1024", 1, "key")
        raise AssertionError("expected RuntimeError")
    except RuntimeError as exc:
        assert "提示词不能为空" in str(exc)


@patch("nodes.GPTImage.gpt_image_2_all._url_to_tensor")
@patch("nodes.GPTImage.gpt_image_2_all.requests.post")
def test_generate_posts_documented_payload(mock_post, mock_url_to_tensor):
    """Task 3: generate should post documented payload."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "created": 1,
        "data": [{"revised_prompt": "rp", "url": "https://a.example/1.webp"}],
    }
    mock_post.return_value = mock_resp
    mock_url_to_tensor.return_value = torch.zeros((1, 8, 8, 3), dtype=torch.float32)

    node = _module.GPTImage2AllGenerate()
    image, urls, revised, raw = node.generate(
        "画一只猫",
        "gpt-image-2-all",
        "1024x1024",
        1,
        "secret",
        api_base="https://api.kegeai.top",
        timeout=120,
    )

    _, kwargs = mock_post.call_args
    assert kwargs["json"] == {
        "model": "gpt-image-2-all",
        "size": "1024x1024",
        "n": 1,
        "prompt": "画一只猫",
    }
    assert urls == "https://a.example/1.webp"
    assert revised == "rp"
    assert '"created": 1' in raw
    assert tuple(image.shape) == (1, 8, 8, 3)


@patch("nodes.GPTImage.gpt_image_2_all._url_to_tensor")
@patch("nodes.GPTImage.gpt_image_2_all.requests.post")
def test_edit_posts_documented_image_array(mock_post, mock_url_to_tensor):
    """Task 4: edit should post documented image array."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "created": 2,
        "data": [{"revised_prompt": "rp-edit", "url": "https://a.example/edit.webp"}],
    }
    mock_post.return_value = mock_resp
    mock_url_to_tensor.return_value = torch.zeros((1, 8, 8, 3), dtype=torch.float32)

    node = _module.GPTImage2AllEdit()
    image, urls, revised, raw = node.edit(
        "https://img/1.png",
        "改成暖色调",
        "gpt-image-2-all",
        "1536x1024",
        1,
        "secret",
        image_url_2="https://img/2.png",
        api_base="https://api.kegeai.top",
        timeout=120,
    )

    _, kwargs = mock_post.call_args
    assert kwargs["json"] == {
        "model": "gpt-image-2-all",
        "size": "1536x1024",
        "n": 1,
        "prompt": "改成暖色调",
        "image": ["https://img/1.png", "https://img/2.png"],
    }
    assert urls == "https://a.example/edit.webp"
    assert revised == "rp-edit"
    assert '"created": 2' in raw
    assert tuple(image.shape) == (1, 8, 8, 3)


def test_edit_requires_first_image_url():
    """Task 4: first image URL is required."""
    node = _module.GPTImage2AllEdit()
    try:
        node.edit("   ", "改图", "gpt-image-2-all", "1024x1024", 1, "key")
        raise AssertionError("expected RuntimeError")
    except RuntimeError as exc:
        assert "至少需要提供一张图片URL" in str(exc)
