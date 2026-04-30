# GrokImage 节点与闭环工作流设计

## 背景
当前仓库已经有 `KuAi/Grok` 视频节点、`📷 传图到临时图床` 图片上传节点，以及多个 Grok / Veo3 / Kling 的闭环工作流示例，但还没有独立的 Grok 图像生成与图像编辑能力。此次需求是在不混入现有视频分类的前提下，新增一个独立的 `KuAi/GrokImage` 分类，并交付两个可直接使用的 JSON 闭环工作流。

## 目标
新增以下能力：

1. `Grok-image文生图` 节点
2. `Grok-image图片编辑` 节点
3. 两个闭环工作流 JSON：
   - `Grok-image文生图`
   - `Grok-image图片编辑`
4. 将工作流文件保存到 `/root/ComfyUI/user/default/workflows`

## 范围
### 本次包含
- 新建 `nodes/GrokImage/` 目录及节点注册
- 新增同步图片生成节点与同步图片编辑节点
- 图片编辑工作流显式串联 `📷 传图到临时图床`
- 工作流中包含输入、调用、结果展示、图片预览、保存输出，形成闭环
- 如有需要，更新 `web/kuaipower_panel.js` 以支持新分类显示

### 本次不包含
- CSV 批处理
- 一键封装节点
- 多图编辑
- 图片任务轮询查询节点
- 对现有 `KuAi/Grok` 视频节点的重构

## 分类与文件布局
新增分类：`KuAi/GrokImage`

计划文件：

- `nodes/GrokImage/__init__.py`
- `nodes/GrokImage/grok_image.py`
- `workflows/grok_image_text2image_complete_workflow.json`
- `workflows/grok_image_edit_complete_workflow.json`
- `/root/ComfyUI/user/default/workflows/Grok-image文生图.json`
- `/root/ComfyUI/user/default/workflows/Grok-image图片编辑.json`

可能修改：
- `web/kuaipower_panel.js`

## 节点设计

### 1. Grok-image文生图
**显示名：** `🖼️ Grok-image文生图`

**分类：** `KuAi/GrokImage`

**用途：** 调用 `POST /v1/images/generations` 根据文本生成图片，并将结果下载为 ComfyUI `IMAGE`。

**必填参数：**
- `prompt`：文本提示词
- `model`：
  - `grok-4.2-image`
  - `grok-4.1-image`
  - `grok-4-image`
  - `grok-3-image`
  - `grok-imagine-image`
  - `grok-imagine-image-pro`
- `size`：
  - `960x960`
  - `720x1280`
  - `1280x720`
  - `1168x784`
  - `784x1168`
- `api_key`

**可选参数：**
- `api_base`，默认 `https://api.kegeai.top`
- `timeout`

**返回：**
- `IMAGE`
- `图片URL`
- `原始响应`

**实现约束：**
- 请求体字段严格使用文档字段：`model`、`prompt`、`size`
- 从响应 `data[0].url` 提取图片 URL
- 下载 URL 对应图片并转成 ComfyUI `IMAGE`
- 若响应缺失 URL，则抛出中文错误

### 2. Grok-image图片编辑
**显示名：** `🎨 Grok-image图片编辑`

**分类：** `KuAi/GrokImage`

**用途：** 调用 `POST /v1/images/edits` 对上传后的图片进行编辑，并将结果下载为 ComfyUI `IMAGE`。

**必填参数：**
- `image`：字符串 URL，由 `📷 传图到临时图床` 节点输出
- `prompt`：编辑提示词
- `model`：
  - `grok-4.2-image`
  - `grok-4.1-image`
  - `grok-4-image`
  - `grok-3-image`
  - `grok-imagine-image`
  - `grok-imagine-image-pro`
- `api_key`

**可选参数：**
- `aspect_ratio`：
  - `1:1`
  - `3:4`
  - `4:3`
  - `9:16`
  - `16:9`
  - `2:3`
  - `3:2`
  - `9:19.5`
  - `19.5:9`
  - `9:20`
  - `20:9`
  - `1:2`
  - `2:1`
  - `auto`
- `response_format`：`url` 或 `b64_json`
- `resolution`：`1k` 或 `2k`
- `quality`：`low`、`medium`、`high`
- `n`：默认 1，最大 10
- `api_base`，默认 `https://api.kegeai.top`
- `timeout`

**返回：**
- `IMAGE`
- `图片URL`
- `原始响应`

**实现约束：**
- 虽然 API 文档示例描述 `image` 为 binary 文件，但本需求已明确采用“先上传图片到临时图床，再把 URL 传给编辑节点”的产品协议
- 因此本节点将接收 `image` 字符串 URL，并把该值作为 `image` 字段提交到 `/v1/images/edits`
- 其余字段严格按文档命名：`model`、`prompt`、`aspect_ratio`、`response_format`、`resolution`、`quality`、`n`
- 默认 `response_format` 使用 `url`，以便与现有下载转 `IMAGE` 流程匹配
- 若接口返回 `b64_json` 且无 URL，本次实现不作为主路径处理；默认工作流只走 `url`

## API 处理策略
### 文生图
- 方法：`POST`
- 路径：`/v1/images/generations`
- Content-Type：`application/json`
- Header：`Authorization: Bearer <api_key>`

### 图片编辑
- 方法：`POST`
- 路径：`/v1/images/edits`
- 本次按需求优先实现为 URL 传参方案
- 首选请求格式：`multipart/form-data`，其中 `image` 字段值为上传得到的 URL 字符串
- 若现有服务端实际兼容 JSON 或表单字符串 URL，以最终联调结果为准；但对外节点接口不变，仍保持 `image` 为 URL 输入

## 工作流设计

### 工作流 A：Grok-image文生图
**建议文件名：** `Grok-image文生图.json`

**闭环结构：**
1. 文本输入
2. `Grok-image文生图`
3. 图片预览
4. `SaveImage`
5. 文本结果展示节点，用于显示图片 URL 与原始响应

**闭环目标：**
- 从 prompt 直接生成图片
- 在工作流内预览结果
- 将图片保存到本地输出目录
- 保留结果 URL 与原始响应，便于复制和排错

### 工作流 B：Grok-image图片编辑
**建议文件名：** `Grok-image图片编辑.json`

**闭环结构：**
1. `LoadImage`
2. `📷 传图到临时图床`
3. 文本输入 prompt
4. `Grok-image图片编辑`
5. 图片预览
6. `SaveImage`
7. 文本结果展示节点，用于显示上传 URL、编辑结果 URL 与原始响应

**闭环目标：**
- 从本地图片开始
- 显式展示上传到图床这一步
- 把上传得到的 URL 输入编辑节点
- 获取编辑后图片并保存
- 把中间与最终结果信息都保留下来

## 查询返回信息的定义
由于本次图片接口为同步返回最终结果，不采用视频任务型“创建 + 轮询查询”结构。

本需求中的“查询返回信息”定义为：
- 节点返回图片 URL
- 节点返回原始响应 JSON
- 工作流使用文本展示节点将关键响应内容可视化

这可以满足“从输入、创建、查询返回信息、输出保存图片做到完全闭环”的目标，同时避免引入并不存在的伪查询接口。

## 面板分类
如果 `web/kuaipower_panel.js` 当前分类映射中没有 `GrokImage`，则新增类似映射：
- `"GrokImage": "🖼️ Grok Image 图像生成"`

这样新节点能在快捷面板中独立归类，而不是混进 `Grok` 视频分类。

## 错误处理
- `api_key` 为空时报中文错误
- `prompt` 为空时报中文错误
- 编辑节点 `image` URL 为空时报中文错误
- 接口返回 HTTP 4xx/5xx 时，尽量解析服务端报错并拼接为中文 `RuntimeError`
- 响应结构缺失图片 URL 时，输出原始响应内容便于排查

## 测试与验收
### 代码层验证
- 新节点能被自动注册系统发现
- 节点显示名、分类、输入输出定义正确
- `web/kuaipower_panel.js` 分类映射存在时可正常显示

### 工作流层验证
- `Grok-image文生图` 工作流可从文本输入直达保存图片
- `Grok-image图片编辑` 工作流可从 `LoadImage` 经 `📷 传图到临时图床` 直达编辑与保存
- 两个工作流均保存到 `/root/ComfyUI/user/default/workflows`

### 联调风险
最大的已知风险是：编辑接口文档描述 `image` 为 binary 文件，但本次产品要求固定为 URL 输入。如果服务端严格拒绝 URL，则需要单独回退为“节点内部下载 URL 再转 multipart 文件上传”的兼容方案；但这不属于当前已批准范围，除非联调实际失败再追加变更。

## 结论
本次实现将以最小必要范围交付独立 `KuAi/GrokImage` 分类、两个同步图像节点和两个闭环工作流。编辑链路严格遵循本次确认的产品要求：先使用 `📷 传图到临时图床` 获取 URL，再把该 URL 传入 `Grok-image图片编辑` 节点。