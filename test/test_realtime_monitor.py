#!/usr/bin/env python3
"""测试实时批量监控节点"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_realtime_monitor_registration():
    """测试实时监控节点注册"""
    print("=" * 60)
    print("测试 1: 实时监控节点注册")
    print("=" * 60)

    try:
        from nodes.Utils import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

        if 'RealtimeBatchMonitor' in NODE_CLASS_MAPPINGS:
            print("✅ RealtimeBatchMonitor 已注册")
            node_class = NODE_CLASS_MAPPINGS['RealtimeBatchMonitor']
            print(f"   分类: {node_class.CATEGORY}")
            print(f"   显示名称: {NODE_DISPLAY_NAME_MAPPINGS.get('RealtimeBatchMonitor')}")

            # 检查必需方法
            assert hasattr(node_class, 'INPUT_TYPES'), "缺少 INPUT_TYPES"
            assert hasattr(node_class, 'RETURN_TYPES'), "缺少 RETURN_TYPES"
            assert hasattr(node_class, 'FUNCTION'), "缺少 FUNCTION"

            input_types = node_class.INPUT_TYPES()
            print(f"   必需参数: {list(input_types.get('required', {}).keys())}")
            print(f"   可选参数: {list(input_types.get('optional', {}).keys())}")

            return True
        else:
            print("❌ RealtimeBatchMonitor 未注册")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_batch_state_enhancements():
    """测试状态管理增强功能"""
    print("\n" + "=" * 60)
    print("测试 2: 状态管理增强功能")
    print("=" * 60)

    try:
        from nodes.Utils.batch_state import BatchProcessState, LogLevel

        # 测试日志级别
        print(f"✅ LogLevel.SIMPLE = {LogLevel.SIMPLE}")
        print(f"✅ LogLevel.STANDARD = {LogLevel.STANDARD}")
        print(f"✅ LogLevel.VERBOSE = {LogLevel.VERBOSE}")

        # 测试状态管理器
        state_manager = BatchProcessState()

        # 测试新方法
        assert hasattr(state_manager, 'add_log'), "缺少 add_log 方法"
        assert hasattr(state_manager, 'get_statistics'), "缺少 get_statistics 方法"

        print("✅ add_log 方法存在")
        print("✅ get_statistics 方法存在")

        # 测试添加日志
        state_manager.start_session("test_session", 10)
        state_manager.add_log(1, "INFO", "测试日志消息")

        # 测试获取统计
        stats = state_manager.get_statistics()
        print(f"✅ 统计信息: {stats}")

        # 清理
        state_manager.clear_state()

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_frontend_extension():
    """测试前端扩展文件"""
    print("\n" + "=" * 60)
    print("测试 3: 前端扩展文件")
    print("=" * 60)

    try:
        import os
        web_file = os.path.join(os.path.dirname(__file__), "..", "web", "realtime_monitor.js")

        if os.path.exists(web_file):
            print(f"✅ 前端扩展文件存在: {web_file}")

            # 检查文件内容
            with open(web_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查关键内容
            checks = [
                ("app.registerExtension", "扩展注册"),
                ("kuai.batch.progress", "WebSocket 消息类型"),
                ("createMonitorPanel", "面板创建函数"),
                ("updateMonitorPanel", "面板更新函数"),
            ]

            for check_str, desc in checks:
                if check_str in content:
                    print(f"   ✅ {desc}")
                else:
                    print(f"   ❌ 缺少 {desc}")
                    return False

            return True
        else:
            print(f"❌ 前端扩展文件不存在: {web_file}")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🧪 实时批量监控节点测试套件\n")

    results = []
    results.append(("节点注册", test_realtime_monitor_registration()))
    results.append(("状态管理增强", test_batch_state_enhancements()))
    results.append(("前端扩展", test_frontend_extension()))

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")

    all_passed = all(r[1] for r in results)
    print("\n" + ("🎉 所有测试通过！" if all_passed else "⚠️  部分测试失败"))

    sys.exit(0 if all_passed else 1)
