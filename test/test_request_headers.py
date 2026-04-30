#!/usr/bin/env python3
"""测试可选导入与请求头构造"""

import os
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

ROOT = Path(__file__).resolve().parent.parent
GPTIMAGE_2_ALL = ROOT / "nodes" / "GPTImage" / "gpt_image_2_all.py"


def _dummy_image_response():
    class DummyResponse:
        status_code = 200
        text = ""

        def raise_for_status(self):
            return None

        def json(self):
            return {"data": [{"b64_json": "aGVsbG8="}]}

    return DummyResponse()


def test_gptimage_package_import_survives_without_optional_module():
    """当 gpt_image_2_all.py 缺失时，老 GPTImage 节点包仍可导入"""
    backup = GPTIMAGE_2_ALL.with_suffix(".py.bak")
    removed = False
    try:
        if GPTIMAGE_2_ALL.exists():
            GPTIMAGE_2_ALL.rename(backup)
            removed = True

        for name in list(sys.modules):
            if name == "nodes.GPTImage" or name.startswith("nodes.GPTImage."):
                sys.modules.pop(name, None)

        from nodes import GPTImage

        mappings = GPTImage.NODE_CLASS_MAPPINGS
        assert "GPTImage2Generate" in mappings
        assert "GPTImage2Edit" in mappings
        assert "GPTImage2AllGenerate" not in mappings
        assert "GPTImage2AllEdit" not in mappings
    finally:
        for name in list(sys.modules):
            if name == "nodes.GPTImage" or name.startswith("nodes.GPTImage."):
                sys.modules.pop(name, None)
        if removed and backup.exists():
            backup.rename(GPTIMAGE_2_ALL)


def test_gptimage_generate_uses_auth_only_header_and_json_payload():
    """GPTImage 文生图应使用 json= 和仅认证头"""
    from nodes.GPTImage.gpt_image import GPTImage2Generate

    node = GPTImage2Generate()

    with patch("nodes.GPTImage.gpt_image.requests.post", return_value=_dummy_image_response()) as mock_post, \
         patch("nodes.GPTImage.gpt_image._url_to_tensor", return_value=__import__("torch").zeros((1, 1, 1, 3))):
        node.generate("提示词", "gpt-image-2", "auto（默认）", 1, "test-key")

    kwargs = mock_post.call_args.kwargs
    assert kwargs["headers"] == {"Authorization": "Bearer test-key"}, kwargs["headers"]
    assert "json" in kwargs, kwargs
    assert "data" not in kwargs, kwargs


def test_sora_create_video_uses_auth_only_header_and_json_payload():
    """SoraCreateVideo 应使用 json= 和仅认证头"""
    from nodes.Sora2.sora2 import SoraCreateVideo

    class DummyResponse:
        status_code = 200
        text = ""

        def json(self):
            return {"id": "task_123", "status": "pending", "status_update_time": 0}

    node = SoraCreateVideo()
    with patch("nodes.Sora2.sora2.requests.post", return_value=DummyResponse()) as mock_post:
        node.create(
            "https://example.com/a.png",
            "提示词",
            "sora-2-all",
            "10",
            "15",
            api_key="test-key",
        )

    kwargs = mock_post.call_args.kwargs
    assert kwargs["headers"] == {"Authorization": "Bearer test-key"}, kwargs["headers"]
    assert "json" in kwargs, kwargs
    assert "data" not in kwargs, kwargs


def test_kling_text2video_uses_auth_only_header():
    """Kling 文生视频应只显式传认证头"""
    from nodes.Kling.kling import KlingText2Video

    class DummyResponse:
        status_code = 200
        text = ""

        def raise_for_status(self):
            return None

        def json(self):
            return {"code": 0, "message": "SUCCEED", "data": {"task_id": "task_123", "task_status": "submitted", "created_at": 123456}}

    node = KlingText2Video()
    with patch("nodes.Kling.kling.requests.post", return_value=DummyResponse()) as mock_post:
        node.create("提示词", "kling-v2-6", "std", "5", "16:9", api_key="test-key")

    kwargs = mock_post.call_args.kwargs
    assert kwargs["headers"] == {"Authorization": "Bearer test-key"}, kwargs["headers"]
    assert "json" in kwargs, kwargs
    assert "data" not in kwargs, kwargs


if __name__ == "__main__":
    tests = [
        ("GPTImage 可选导入", test_gptimage_package_import_survives_without_optional_module),
        ("GPTImage 文生图请求", test_gptimage_generate_uses_auth_only_header_and_json_payload),
        ("Sora 创建视频请求", test_sora_create_video_uses_auth_only_header_and_json_payload),
        ("Kling 文生视频请求", test_kling_text2video_uses_auth_only_header),
    ]

    results = []
    for name, test_func in tests:
        try:
            test_func()
            results.append((name, True))
            print(f"✅ {name}")
        except Exception as e:
            results.append((name, False))
            print(f"❌ {name}: {e}")

    sys.exit(0 if all(r[1] for r in results) else 1)
