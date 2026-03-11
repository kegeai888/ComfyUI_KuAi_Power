# Grok 模型修复说明

## 问题描述

用户报告：选择了 6 秒的 Grok 模型，但生成的视频是 15 秒。

## 根本原因

之前的实现中，代码会根据用户选择的模型名称**自动计算** `duration` 参数，然后同时发送 `model` 和 `duration` 两个字段给 API：

```python
# 旧实现（有问题）
payload = {
    "model": "grok-video-3",      # 从 "grok-video-3 (6秒)" 提取
    "duration": 6,                 # 根据模型名称计算
    "prompt": "...",
    ...
}
```

这种做法存在问题：
1. **API 可能根据 `model` 字段自动决定时长**，忽略 `duration` 参数
2. **模型名称本身就包含时长信息**（如 `grok-video-3-15s`），不需要额外的 `duration` 参数
3. **与 Veo3 等其他模型的实现不一致**（Veo3 只发送 `model`，不发送 `duration`）

## 修复方案

**移除 `duration` 参数的计算和发送，让 API 根据 `model` 字段自动决定时长。**

### 修改内容

1. **移除 `get_duration_for_grok_model()` 函数的调用**
2. **移除 payload 中的 `duration` 字段**
3. **保留模型名称提取逻辑**（去掉括号中的说明）

```python
# 新实现（正确）
# 提取实际的模型名称（去掉时长说明）
actual_model = model.split(" (")[0] if " (" in model else model
effective_model = (custom_model or "").strip() or actual_model

payload = {
    "model": effective_model,     # 直接使用提取的模型名称
    "prompt": "...",
    "aspect_ratio": "...",
    "size": "...",
    "enhance_prompt": True,
    "images": [...]
}
# 不再包含 duration 字段
```

### 模型名称映射

| 用户选择 | 提取的模型名称 | API 生成时长 |
|---------|--------------|------------|
| `grok-video-3 (6秒)` | `grok-video-3` | 6 秒 |
| `grok-video-3-10s (10秒)` | `grok-video-3-10s` | 10 秒 |
| `grok-video-3-15s (15秒)` | `grok-video-3-15s` | 15 秒 |

## 影响范围

修改影响以下节点：
- `GrokCreateVideo` - 创建 Grok 视频任务
- `GrokImage2Video` - Grok 图生视频
- `GrokText2Video` - Grok 文生视频
- `GrokCreateAndWait` - 一键生成（文生视频）
- `GrokImage2VideoAndWait` - 一键生成（图生视频）
- `GrokText2VideoAndWait` - 一键生成（文生视频）

## 验证测试

运行测试验证修复：

```bash
python3 test/test_grok_model_fix.py
```

测试覆盖：
1. ✅ 模型名称提取逻辑
2. ✅ Payload 结构（不包含 duration）
3. ✅ 导入清理（移除 get_duration_for_grok_model）
4. ✅ 1080P 支持逻辑（只有 15 秒模型支持）

## 向后兼容性

此修复**不影响**现有工作流：
- 工作流中保存的模型选择仍然有效
- 只是发送给 API 的参数结构发生变化
- API 会根据模型名称自动决定时长

## 相关文件

- `nodes/Grok/grok.py` - 主要修改文件
- `test/test_grok_model_fix.py` - 验证测试
- `docs/GROK_MODEL_FIX.md` - 本文档

## 更新日期

2025-03-11
