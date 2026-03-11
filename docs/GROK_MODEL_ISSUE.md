# Grok 模型配置问题排查报告

## 问题描述

用户报告：选择了 6 秒的 Grok 模型，但生成的视频是 15 秒。

## 问题分析

### 1. 当前模型配置

**下拉列表**：
- `grok-video-3 (6秒)` → 实际模型名: `grok-video-3`, duration: 6
- `grok-video-3-10s (10秒)` → 实际模型名: `grok-video-3-10s`, duration: 10
- `grok-video-3-15s (15秒)` → 实际模型名: `grok-video-3-15s`, duration: 15

### 2. 代码逻辑验证

✅ **模型名称提取**：正确
```python
actual_model = model.split(" (")[0]  # "grok-video-3 (6秒)" → "grok-video-3"
```

✅ **Duration 映射**：正确
```python
get_duration_for_grok_model("grok-video-3 (6秒)")  # → 6
get_duration_for_grok_model("grok-video-3-10s (10秒)")  # → 10
get_duration_for_grok_model("grok-video-3-15s (15秒)")  # → 15
```

✅ **API Payload**：正确
```python
payload = {
    "model": "grok-video-3",  # 正确
    "duration": 6,  # 正确
    ...
}
```

### 3. 可能的原因

经过代码审查和测试，本地代码逻辑是正确的。问题可能出在：

#### 原因1：API 服务端问题
- API 服务端可能忽略了 `duration` 参数
- 或者 API 服务端根据 `model` 名称自动决定时长
- 需要确认 API 文档中的正确用法

#### 原因2：模型名称不匹配
- API 可能期望的模型名称与我们发送的不一致
- 例如：API 可能期望 `grok-video-3-6s` 而不是 `grok-video-3`

## 解决方案

### 方案1：添加调试日志（已实施）

在节点中添加了详细的调试日志，输出实际发送给 API 的参数：

```python
print(f"[ComfyUI_KuAi_Power] 模型: {effective_model}, 时长: {duration}秒, 宽高比: {aspect_ratio}, 分辨率: {effective_size}")
```

**使用方法**：
1. 运行 Grok 图生视频节点
2. 查看 ComfyUI 控制台输出
3. 确认发送的模型名称和 duration 是否正确

### 方案2：测试不同的模型名称

如果 API 期望不同的模型名称，可以尝试：

**选项A：使用完整的模型名称（包含时长）**
```python
# 当前：grok-video-3 → duration: 6
# 修改为：grok-video-3-6s → duration: 6
```

**选项B：只使用 duration 参数，不指定模型**
```python
# 使用统一的模型名称，通过 duration 控制时长
model = "grok-video-3"
duration = 6 | 10 | 15
```

### 方案3：联系 API 提供商

如果上述方案都不行，需要：
1. 查看 API 官方文档
2. 联系 API 提供商确认正确的参数格式
3. 获取 Grok 模型的正确命名规范

## 测试步骤

### 步骤1：验证本地代码

运行测试：
```bash
python test/test_grok_model.py
```

预期结果：所有测试通过 ✅

### 步骤2：查看实际发送的参数

1. 在 ComfyUI 中运行 Grok 图生视频节点
2. 选择 `grok-video-3 (6秒)` 模型
3. 查看控制台输出：
   ```
   [ComfyUI_KuAi_Power] 模型: grok-video-3, 时长: 6秒, 宽高比: 2:3, 分辨率: 720P
   ```
4. 确认参数是否正确

### 步骤3：测试 API 响应

1. 记录 API 返回的 task_id
2. 查询任务状态
3. 检查返回的视频时长
4. 如果时长不匹配，说明是 API 端问题

## 临时解决方案

如果确认是 API 端问题，可以使用以下临时方案：

### 方案A：修改模型名称映射

如果 API 期望 `grok-video-3-6s` 而不是 `grok-video-3`：

```python
# 在 grok.py 中修改
if model == "grok-video-3":
    effective_model = "grok-video-3-6s"
elif model == "grok-video-3-10s":
    effective_model = "grok-video-3-10s"
elif model == "grok-video-3-15s":
    effective_model = "grok-video-3-15s"
```

### 方案B：使用自定义模型

在节点中使用 `custom_model` 参数，手动指定正确的模型名称。

## 后续行动

1. ✅ 添加调试日志
2. ⏳ 用户测试并提供控制台输出
3. ⏳ 根据输出确定问题根源
4. ⏳ 实施相应的修复方案

## 相关文件

- 测试文件：`test/test_grok_model.py`
- 节点实现：`nodes/Grok/grok.py`
- 工具函数：`nodes/Sora2/kuai_utils.py`

## 总结

本地代码逻辑经过测试是正确的。问题很可能出在 API 服务端或者模型名称的匹配上。

已添加详细的调试日志，用户可以通过查看控制台输出来确认实际发送给 API 的参数，从而定位问题根源。
