# 2026-04-30 Grok-videos 6-10s 设计

## 概述
本设计为 ComfyUI_KuAi_Power 新增一组独立的 Grok 视频节点，对接 `https://api.kegeai.top/v1/videos` 接口，实现 `grok-videos` 模型的 6 秒 / 10 秒文生视频与图生视频能力。新能力与现有 `grok-video-3` 系列节点并存，不修改旧节点行为。

用户要求该能力拆分为三类节点：创建节点、查询节点、一键等待节点；同时提供闭环工作流，支持文本输入和可选图片输入。当 `input_reference` 为空时走文生视频；有值时走图生视频。图片上传由现有 `📷 传图到临时图床` 节点负责，上传后将 URL 传入新节点的 `input_reference` 参数。

## 目标
- 新增一组独立的 Grok-videos 节点，固定模型为 `grok-videos`
- 支持 6 秒和 10 秒视频生成
- 支持文生视频与图生视频两种模式
- 图生视频复用现有 `UploadToImageHost` 节点上传图片
- 提供完整闭环工作流：输入 → 创建/查询或一键等待 → 下载保存 → 显示结果
- 工作流文件保存到仓库 `workflows/`，并复制到 `/root/ComfyUI/user/default/workflows`

## 非目标
- 不重构现有 `GrokText2Video`、`GrokImage2Video`、`GrokCreateVideo` 等旧节点
- 不把新 API 混入现有 `nodes/Grok/grok.py` 的旧 JSON 协议逻辑中
- 不在新节点中直接接收 `IMAGE` 并自动上传图片
- 不引入 CSV 批处理支持，当前需求仅覆盖单任务与闭环工作流

## API 约束
目标接口：`POST /v1/videos`

请求格式为 `multipart/form-data`，参数：
- `model`: 固定为 `grok-videos`
- `prompt`: 提示词，必填
- `seconds`: `6` 或 `10`
- `input_reference`: 图片 URL，可空
- `size`: `16:9` 或 `9:16`

鉴于用户已明确模型固定，因此节点 UI 不暴露 model 下拉选项，内部写死 `model=grok-videos`，减少误配置。

查询接口未在需求文档中单独给出。实现前应优先确认后端是否继续复用现有查询接口；默认设计为沿用项目现有 Grok 查询模式（与当前 Grok 查询节点一致的任务查询接口），并通过测试验证返回结构。

## 文件与模块边界
### 节点实现
新能力保留在 `nodes/Grok/` 分类下，但使用独立文件承载，避免继续增大 `nodes/Grok/grok.py`。

建议新增文件：
- `nodes/Grok/grok_videos.py`

在 `nodes/Grok/__init__.py` 中注册新节点。

### 测试文件
建议新增：
- `test/test_grok_videos.py`
- 如需要单独验证工作流结构，可增补 `test/test_grok_videos_workflows.py`

### 工作流文件
建议新增：
- `workflows/grok_videos_6_10s_complete_workflow.json`
- `workflows/grok_videos_6_10s_create_query_workflow.json`

并复制到：
- `/root/ComfyUI/user/default/workflows/grok_videos_6_10s_complete_workflow.json`
- `/root/ComfyUI/user/default/workflows/grok_videos_6_10s_create_query_workflow.json`

## 节点设计
### 1. 创建节点
建议类名：`GrokVideosCreateVideo`

显示名：`🤖 Grok-videos 生视频 6-10s`

#### 输入参数
必填：
- `prompt`: `STRING`
- `seconds`: 枚举 `6` / `10`
- `size`: 枚举 `16:9` / `9:16`
- `api_key`: `STRING`

可选：
- `input_reference`: `STRING`，允许为空
- `api_base`: `STRING`，默认 `https://api.kegeai.top`

#### 行为
- 内部解析 API key，优先节点参数，其次环境变量 `KUAI_API_KEY`
- 校验 `prompt` 非空
- 校验 `seconds` 只能为 `6` 或 `10`
- 校验 `size` 只能为 `16:9` 或 `9:16`
- `input_reference` 为空时按文生视频发起请求
- `input_reference` 非空时按图生视频发起请求
- 使用 `multipart/form-data` 提交，不复用旧 JSON payload 结构
- `model` 固定写死为 `grok-videos`

#### 返回值
- `任务ID`
- `状态`
- `原始响应`

返回原始响应的目的是方便在闭环工作流中显示和调试接口响应。

### 2. 查询节点
建议类名：`GrokVideosQueryVideo`

显示名：`🔍 Grok-videos 查询视频`

#### 输入参数
- `task_id`
- `api_key`
- `api_base`

#### 行为
- 校验 `task_id` 非空
- 调用查询接口获取任务状态
- 覆盖状态：`pending` / `processing` / `completed` / `failed`
- 当状态为 `failed` 时，抛出带后端详情的中文错误
- 当状态为 `completed` 但缺少 `video_url` 时，抛出明确中文错误

#### 返回值
- `任务ID`
- `状态`
- `视频URL`
- `封面URL`
- `原始响应`

如果后端当前不返回封面图，则 `封面URL` 返回空字符串，以便保留后续兼容空间。

### 3. 一键等待节点
建议类名：`GrokVideosCreateAndWait`

显示名：`⚡ Grok-videos 生视频 6-10s（一键）`

#### 输入参数
继承创建节点全部参数，额外加入：
- `max_wait_time`
- `poll_interval`

#### 行为
1. 调用创建节点创建任务
2. 如果创建后状态已完成，则直接转查询节点拿最终结果
3. 否则循环查询直到：
   - `completed`
   - `failed`
   - 超时
4. 超时时返回明确错误，提示用户可用查询节点继续追踪

#### 返回值
- `任务ID`
- `状态`
- `视频URL`
- `原始响应`

## 节点注册
`nodes/Grok/__init__.py` 中新增：
- `GrokVideosCreateVideo`
- `GrokVideosQueryVideo`
- `GrokVideosCreateAndWait`

并补充对应显示名映射。

这样新节点与现有：
- `GrokText2Video`
- `GrokImage2Video`
- `GrokCreateVideo`
- `GrokQueryVideo`

并存，不改变已有用户工作流。

## 工作流设计
本需求不只做节点，还要做完整闭环工作流。建议产出两套工作流，分别面向普通用户与调试用户。

### 工作流 A：完整闭环一键版
文件名：`grok_videos_6_10s_complete_workflow.json`

#### 结构
- 文本输入：输入提示词
- 可选图片输入：`LoadImage`
- 上传图片：`📷 传图到临时图床` (`UploadToImageHost`)
- 生成视频：`GrokVideosCreateAndWait`
- 下载视频：`DownloadVideo`
- 显示结果：`ShowText` 显示本地路径与视频 URL / 原始响应

#### 文生 / 图生切换规则
- 若工作流中不接图片上传输出，或传给 `input_reference` 的值为空，则按文生视频执行
- 若 `UploadToImageHost` 输出 URL 接入 `input_reference`，则按图生视频执行

该工作流对普通用户最友好，满足“完全闭环”要求。

### 工作流 B：创建 + 查询分步版
文件名：`grok_videos_6_10s_create_query_workflow.json`

#### 结构
- 文本输入：输入提示词
- 可选图片输入：`LoadImage`
- 上传图片：`UploadToImageHost`
- 创建任务：`GrokVideosCreateVideo`
- 查询任务：`GrokVideosQueryVideo`
- 下载视频：`DownloadVideo`
- 显示结果：`ShowText` 显示任务 ID、状态、视频 URL、原始响应

#### 目的
- 方便手动调试
- 方便任务创建后晚些时候再查询
- 与现有仓库中 `grok_text2video_complete_workflow.json`、`grok_image2video_complete_workflow.json` 风格保持一致

## 数据流
### 文生视频
`prompt` → `GrokVideosCreate...` → `task_id/status` → `GrokVideosQuery...` 或内部轮询 → `video_url` → `DownloadVideo` → `ShowText`

### 图生视频
`LoadImage` → `UploadToImageHost` → `图片URL` → `input_reference` → `GrokVideosCreate...` → `task_id/status` → `GrokVideosQuery...` 或内部轮询 → `video_url` → `DownloadVideo` → `ShowText`

这样将图片上传职责留在工作流层，而不是耦合进视频节点内部，符合用户指定方式，也与现有工具节点职责边界一致。

## 错误处理
以下情况应返回用户友好的中文错误：
- API key 未配置
- `prompt` 为空
- `task_id` 为空
- `seconds` 非法
- `size` 非法
- 上传成功但 `input_reference` 为空时不报错，直接按文生视频处理
- 创建接口 HTTP 失败
- 查询接口 HTTP 失败
- 任务失败且后端返回错误详情
- 任务完成但缺少 `video_url`
- 一键等待超时

错误信息风格保持与现有项目一致，使用 `RuntimeError` 抛出中文消息，并保留必要后端详情。

## 测试策略
### 单元测试
1. 节点注册测试
   - 断言新类出现在 `NODE_CLASS_MAPPINGS`
   - 断言显示名正确

2. 创建节点请求测试
   - 断言调用 `POST /v1/videos`
   - 断言使用 `multipart/form-data`
   - 断言字段包含 `model=grok-videos`、`prompt`、`seconds`、`size`
   - 断言 `input_reference` 在非空时按字符串传递

3. 文生 / 图生测试
   - `input_reference=""` 时成功创建文生任务
   - `input_reference="https://..."` 时成功创建图生任务

4. 查询节点测试
   - 覆盖 `pending`
   - 覆盖 `processing`
   - 覆盖 `completed`
   - 覆盖 `failed`
   - 覆盖 `completed` 但无 `video_url`

5. 一键等待节点测试
   - 成功完成
   - 创建后立即完成
   - 失败
   - 超时

### 工作流结构测试
- 校验 workflow JSON 至少包含：
  - 文本输入相关节点
  - `UploadToImageHost`
  - 新建 Grok-videos 节点
  - `DownloadVideo`
  - `ShowText`
- 校验主要连线存在，能构成闭环

## 实施顺序
1. 新增 `nodes/Grok/grok_videos.py`
2. 实现创建节点
3. 实现查询节点
4. 实现一键等待节点
5. 更新 `nodes/Grok/__init__.py` 注册
6. 编写 `test/test_grok_videos.py`
7. 生成两份 workflow JSON 到仓库 `workflows/`
8. 复制 workflow JSON 到 `/root/ComfyUI/user/default/workflows`
9. 运行测试并检查节点注册

## 风险与对策
### 风险 1：查询接口返回结构与旧 Grok 查询不同
**对策：** 在实现前先用测试桩按当前预期结构写断言，并在真实接口验证时只最小调整查询解析逻辑，不反向污染旧节点。

### 风险 2：multipart 字段提交格式与后端预期不一致
**对策：** 测试中直接断言 `requests.post(..., files=[...])` 或等价 multipart 结构，避免误用 `json=`。

### 风险 3：用户混淆新旧 Grok 节点
**对策：** 节点显示名显式包含 `Grok-videos` 和 `6-10s`，与旧 `grok-video-3` 系列区分开。

## 验收标准
- 用户能在 ComfyUI 中看到 3 个新节点
- 文生视频可成功创建、查询、下载
- 图生视频可通过 `📷 传图到临时图床` 上传后成功创建、查询、下载
- `input_reference` 为空不会报错，而是按文生视频执行
- 两份 workflow JSON 可导入并形成闭环
- workflow 文件已保存到用户指定目录 `/root/ComfyUI/user/default/workflows`
- 不影响现有 Grok 节点和现有 Grok 工作流
