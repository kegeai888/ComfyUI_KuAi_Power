#!/usr/bin/env python3
"""测试 Kling 工具函数"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_parse_kling_response_success():
    """测试成功响应解析"""
    from nodes.Kling.kling_utils import parse_kling_response

    resp_json = {
        "code": 0,
        "message": "SUCCEED",
        "data": {
            "task_id": "831922345719271433",
            "task_status": "submitted",
            "created_at": 1766374262370
        }
    }

    task_id, status, created_at = parse_kling_response(resp_json)

    assert task_id == "831922345719271433"
    assert status == "submitted"
    assert created_at == 1766374262370

def test_parse_kling_response_error():
    """测试错误响应解析"""
    from nodes.Kling.kling_utils import parse_kling_response

    resp_json = {
        "code": 400,
        "message": "Invalid parameters"
    }

    try:
        parse_kling_response(resp_json)
        assert False, "应该抛出异常"
    except RuntimeError as e:
        assert "API 错误" in str(e)
        assert "Invalid parameters" in str(e)

def test_kling_models_constant():
    """测试模型列表常量"""
    from nodes.Kling.kling_utils import KLING_MODELS

    assert "kling-v1" in KLING_MODELS
    assert "kling-v1-6" in KLING_MODELS
    assert "kling-v2-master" in KLING_MODELS
    assert "kling-v3" in KLING_MODELS

def test_kling_aspect_ratios_constant():
    """测试宽高比列表常量"""
    from nodes.Kling.kling_utils import KLING_ASPECT_RATIOS

    assert "16:9" in KLING_ASPECT_RATIOS
    assert "9:16" in KLING_ASPECT_RATIOS
    assert "1:1" in KLING_ASPECT_RATIOS

if __name__ == "__main__":
    print("\n🧪 Kling 工具函数测试套件\n")

    tests = [
        ("解析成功响应", test_parse_kling_response_success),
        ("解析错误响应", test_parse_kling_response_error),
        ("模型列表常量", test_kling_models_constant),
        ("宽高比列表常量", test_kling_aspect_ratios_constant),
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

    all_passed = all(r[1] for r in results)
    print("\n" + ("🎉 所有测试通过！" if all_passed else "⚠️  部分测试失败"))
    sys.exit(0 if all_passed else 1)
