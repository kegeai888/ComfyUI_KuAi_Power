#!/usr/bin/env python3
"""测试 AndWait 便捷节点"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_text2video_andwait_structure():
    """测试文生视频 AndWait 节点结构"""
    from nodes.Kling.kling import KlingText2VideoAndWait

    assert hasattr(KlingText2VideoAndWait, 'INPUT_TYPES')
    assert KlingText2VideoAndWait.CATEGORY == "KuAi/Kling"
    assert KlingText2VideoAndWait.RETURN_TYPES == ("STRING", "STRING", "STRING", "STRING")

def test_image2video_andwait_structure():
    """测试图生视频 AndWait 节点结构"""
    from nodes.Kling.kling import KlingImage2VideoAndWait

    assert hasattr(KlingImage2VideoAndWait, 'INPUT_TYPES')
    assert KlingImage2VideoAndWait.CATEGORY == "KuAi/Kling"

if __name__ == "__main__":
    print("\n🧪 AndWait 便捷节点测试套件\n")

    tests = [
        ("文生视频 AndWait 结构", test_text2video_andwait_structure),
        ("图生视频 AndWait 结构", test_image2video_andwait_structure),
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
