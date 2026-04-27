# Grok 扩展视频节点与闭环工作流设计

## 概述

本设计为 ComfyUI_KuAi_Power 增加 Grok 扩展视频能力，对接 `POST /v1/video/extend` 接口，并提供两套从输入到输出完全闭环的工作流：

1. 文生视频 → 扩展视频 → 下载保存
2. 图生视频 → 扩展视频 → 下载保存

设计目标：
- 保持与现有 `nodes/Grok/grok.py` 节点结构一致
- 支持独立扩展节点，也支持完整闭环 workflow
- 每个扩展节点只执行一次扩展，但允许用户手工串联多次扩展
- `start_time` 默认继承前一个视频的时长，同时允许用户手动覆盖
- 扩展节点输出的 `视频时长` 定义为扩展后总时长，便于继续串联下一次扩展

## 需求收敛

### 用户确认的关键约束

- 既要提供独立扩展节点，也要提供闭环工作流
- 同时支持两种闭环来源：
  - 文生视频扩展闭环
  - 图生视频扩展闭环
- 一次扩展一次，不在单个节点内做多次扩展循环
- 支持用户在 workflow 中手工继续串联下一次扩展
- `start_time` 默认值应等于上一个视频生成结果的视频时长，例如 10 秒视频默认传 `10`
- 时长来源采用“双保险”设计：
  - 节点直接输出视频时长
  - workflow 可保留模型到时长的映射作为兜底
- 所有 Grok 模型选项移除 `grok-video-3-15s`
- 所有 Grok 节点的分辨率统一只保留 `720P`
- 扩展节点输出的 `视频时长` 定义为扩展后总时长，不是本次新增时长

## API 对接设计

目标接口：`POST /v1/video/extend`

请求体字段：
- `model`: 模型名，例如 `grok-video-3`
- `prompt`: 扩展提示词
- `task_id`: 需要扩展的视频任务 ID
- `aspect_ratio`: `2:3`、`3:2`、`1:1`
- `size`: `720P`
- `start_time`: 开始扩展的时间点，整数秒
- `upscale`: 布尔值

典型请求体：

```json
{
  "model": "grok-video-3",
  "prompt": "play with another white cat",
  "task_id": "grok:7fd641dc-437f-44c3-97a2-e3778e0e10fb",
  "aspect_ratio": "3:2",
  "size": "720P",
  "start_time": 10,
  "upscale": false
}
```

查询阶段继续复用现有 `GET /v1/video/query` 逻辑，不新增扩展专用查询节点。

## 节点架构设计

### 新增节点

在 `nodes/Grok/grok.py` 中新增：

#### `GrokExtendVideo`
用途：创建扩展视频任务，不等待完成。

建议输入：
- `prompt`
- `task_id`
- `model`
- `start_time`
- `aspect_ratio`
- `size`
- `upscale`
- `api_key`
- `api_base`
- `custom_model`

建议输出：
- `任务ID`
- `状态`
- `扩展提示词`
- `状态更新时间`
- `视频时长`

#### `GrokExtendVideoAndWait`
用途：创建扩展任务并轮询直到完成。

建议输入：
- 与 `GrokExtendVideo` 保持一致
- `max_wait_time`
- `poll_interval`

建议输出：
- `任务ID`
- `状态`
- `视频URL`
- `扩展提示词`
- `视频时长`

### 复用节点

继续复用现有：
- `GrokQueryVideo`
- `DownloadVideo`
- `UploadToImageHost`
- `LoadImage`
- `ShowText`

不新增“扩展专用查询”节点，避免职责重复。

## 现有 Grok 节点改造

以下节点需要同步调整：
- `GrokCreateVideo`
- `GrokCreateAndWait`
- `GrokText2Video`
- `GrokText2VideoAndWait`
- `GrokImage2Video`
- `GrokImage2VideoAndWait`

### 改造内容 1：统一模型选项

所有 Grok 节点模型下拉统一只保留：
- `grok-video-3 (6秒)`
- `grok-video-3-10s (10秒)`

移除：
- `grok-video-3-15s (15秒)`

### 改造内容 2：统一分辨率选项

所有 Grok 节点分辨率下拉统一只保留：
- `720P`

删除围绕 `1080P` 与 `15s` 模型的特殊判断逻辑，避免保留已失效的条件分支。

### 改造内容 3：新增时长输出

上述生成类节点统一新增输出：
- `视频时长`

时长映射规则：
- `grok-video-3` → `6`
- `grok-video-3-10s` → `10`

对于 `custom_model`，优先基于最终生效模型名做映射；如无法识别，按与所选下拉模型一致的时长处理，避免 workflow 断流。

## 时长与 start_time 规则

### 默认规则

`start_time` 默认应来自前一个视频结果的 `视频时长` 输出。

示例：
- 前一个视频是 `grok-video-3-10s`
- 前一个节点输出 `视频时长 = 10`
- 扩展节点默认接收到 `start_time = 10`

### 手动覆盖

尽管 workflow 默认自动连线，节点参数仍保留 `start_time` 输入，允许用户断开连线后手动输入任意合法值，例如从第 3 秒开始扩展。

### 扩展后的时长定义

扩展节点输出的 `视频时长` 定义为：

`扩展后总时长 = start_time + 当前扩展模型时长`

示例：
- 原视频时长 10 秒
- 扩展模型为 `grok-video-3-10s`
- `start_time = 10`
- 扩展后输出 `视频时长 = 20`

这一定义可直接支持下一次扩展节点继续把该值接回 `start_time`，形成可手工串联的闭环。

## workflow 设计

### 1. 文生视频扩展闭环

建议新增文件：
- `workflows/grok_text2video_extend_complete_workflow.json`

节点链路：
1. `GrokText2VideoAndWait`
2. `GrokExtendVideoAndWait`
3. `DownloadVideo`
4. `ShowText` 显示下载本地路径
5. `ShowText` 显示扩展提示词
6. 可选 `ShowText` 显示扩展后总时长

核心连线：
- `GrokText2VideoAndWait.任务ID` → `GrokExtendVideoAndWait.task_id`
- `GrokText2VideoAndWait.视频时长` → `GrokExtendVideoAndWait.start_time`
- `GrokExtendVideoAndWait.视频URL` → `DownloadVideo.video_url`

用户输入内容：
- 原始文生视频提示词
- 扩展提示词
- 模型、宽高比、是否放大等参数

默认体验：
- 先生成原视频
- 自动将原视频时长传入扩展节点
- 自动下载扩展后结果

### 2. 图生视频扩展闭环

建议新增文件：
- `workflows/grok_image2video_extend_complete_workflow.json`

节点链路：
1. `LoadImage`
2. `UploadToImageHost`
3. `GrokImage2VideoAndWait`
4. `GrokExtendVideoAndWait`
5. `DownloadVideo`
6. `ShowText` 显示下载本地路径
7. `ShowText` 显示扩展提示词
8. 可选 `ShowText` 显示扩展后总时长

核心连线：
- `UploadToImageHost.图片URL` → `GrokImage2VideoAndWait.image_url_1`
- `GrokImage2VideoAndWait.任务ID` → `GrokExtendVideoAndWait.task_id`
- `GrokImage2VideoAndWait.视频时长` → `GrokExtendVideoAndWait.start_time`
- `GrokExtendVideoAndWait.视频URL` → `DownloadVideo.video_url`

默认体验：
- 从图片生成视频
- 自动把生成视频时长传给扩展节点
- 自动下载扩展后视频

## 可串联扩展设计

设计上不在单个节点中内置多次扩展循环，而是通过输出保持可串联性：
- 扩展节点输出新的 `任务ID`
- 扩展节点输出扩展后总时长

因此用户若要继续第二次扩展，只需在 workflow 中再串一个 `GrokExtendVideoAndWait`：
- 上一个扩展节点 `任务ID` → 下一个扩展节点 `task_id`
- 上一个扩展节点 `视频时长` → 下一个扩展节点 `start_time`

这样既保持节点职责清晰，也符合用户希望的一次扩展一次、手工可继续串联的模式。

## 错误处理设计

扩展节点应覆盖以下错误场景：

- `task_id` 为空：报错 `任务ID不能为空`
- `prompt` 为空：报错 `提示词不能为空`
- `start_time <= 0`：报错 `start_time 必须大于 0`
- HTTP 4xx/5xx：复用 `extract_error_message_from_response`
- 查询返回 `failed`：复用现有 `extract_task_failure_detail`
- 查询完成但无 `video_url`：报明确错误
- 响应缺少任务 ID：报错 `创建响应缺少任务 ID`

轮询超时行为与现有 Grok 一键节点保持一致：
- 报出超时信息
- 返回提示用户可继续使用查询节点检查状态

## 注册与显示名设计

`nodes/Grok/__init__.py` 需要新增注册：
- `GrokExtendVideo`
- `GrokExtendVideoAndWait`

建议显示名：
- `🎬 Grok 扩展视频`
- `⚡ Grok 扩展视频（一键）`

## 测试设计

至少覆盖以下测试点：

### 节点输入输出与注册
- 新增扩展节点已在 `nodes/Grok/__init__.py` 注册
- 显示名正确
- 输入参数完整
- 输出数量与命名符合设计

### 模型与分辨率约束
- 所有 Grok 节点模型下拉不再包含 `grok-video-3-15s`
- 所有 Grok 节点 `size` 下拉仅包含 `720P`

### 时长输出
- `grok-video-3` 输出时长 `6`
- `grok-video-3-10s` 输出时长 `10`
- 扩展节点输出时长为扩展后总时长而非本次新增时长

### 扩展请求体
- `/v1/video/extend` payload 包含：
  - `model`
  - `prompt`
  - `task_id`
  - `aspect_ratio`
  - `size`
  - `start_time`
  - `upscale`

### workflow 闭环
- 文生扩展 workflow 的 `任务ID` 与 `视频时长` 连线正确
- 图生扩展 workflow 的图片 URL、`任务ID` 与 `视频时长` 连线正确
- 扩展结果 `视频URL` 正确进入下载节点

## 实施边界

本次设计只覆盖：
- Grok 扩展视频节点
- Grok 现有生成节点的必要输出与参数收敛
- 两套闭环 workflow JSON
- 对应测试更新

本次不包含：
- 单节点内置多次扩展循环
- 新的通用时长映射工具节点
- Grok 批处理扩展视频能力
- 文档体系的大范围重构

## 推荐实施顺序

1. 先收敛 Grok 公共模型与分辨率选项
2. 给现有 Grok 生成节点增加 `视频时长` 输出
3. 实现 `GrokExtendVideo`
4. 实现 `GrokExtendVideoAndWait`
5. 更新 `nodes/Grok/__init__.py`
6. 新增两套 workflow JSON
7. 补充和更新测试
8. 最后做一次工作流连线与节点注册检查
