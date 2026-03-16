# Grok 图生视频多图片支持使用指南

## 概述

`GrokImage2Video` 和 `GrokImage2VideoAndWait` 节点现已支持 **0-3 张图片** 输入，实现了文生视频和图生视频的统一。

## 功能特性

- **完全可选**：支持 0-3 张参考图片
- **自动判断**：根据提供的图片数量自动判断是文生视频还是图生视频
- **节点连接**：图片 URL 必须从"📷 传图到临时图床"节点连接（不支持手动输入）
- **灵活组合**：可以只连接 1 张、2 张或 3 张图片

## 使用场景

### 场景 1：文生视频（0 张图片）

不连接任何图片节点，直接输入提示词生成视频。

```
工作流：
[提示词输入] → GrokImage2Video → [任务ID]
```

**适用于**：
- 纯文本描述生成视频
- 创意视频生成
- 概念验证

### 场景 2：单图生视频（1 张图片）

连接一个图片上传节点到 `image_url_1`。

```
工作流：
[图片] → 📷 传图到临时图床 → [图片URL] → GrokImage2Video.image_url_1
[提示词] → GrokImage2Video → [任务ID]
```

**适用于**：
- 静态图片动画化
- 产品展示视频
- 单图转场效果

### 场景 3：双图生视频（2 张图片）

连接两个图片上传节点到 `image_url_1` 和 `image_url_2`。

```
工作流：
[图片1] → 📷 传图到临时图床 → [URL1] → GrokImage2Video.image_url_1
[图片2] → 📷 传图到临时图床 → [URL2] → GrokImage2Video.image_url_2
[提示词] → GrokImage2Video → [任务ID]
```

**适用于**：
- 两张图片之间的过渡
- 对比展示
- 前后变化展示

### 场景 4：多图生视频（3 张图片）

连接三个图片上传节点到所有三个图片输入。

```
工作流：
[图片1] → 📷 传图到临时图床 → [URL1] → GrokImage2Video.image_url_1
[图片2] → 📷 传图到临时图床 → [URL2] → GrokImage2Video.image_url_2
[图片3] → 📷 传图到临时图床 → [URL3] → GrokImage2Video.image_url_3
[提示词] → GrokImage2Video → [任务ID]
```

**适用于**：
- 多场景连续展示
- 故事板动画
- 产品多角度展示

## 节点参数说明

### 必需参数

- **prompt** (提示词): 视频生成提示词，描述视频内容和动作
- **model** (模型): 选择 Grok 模型
  - `grok-video-3 (6秒)`: 6 秒视频
  - `grok-video-3-10s (10秒)`: 10 秒视频
  - `grok-video-3-15s (15秒)`: 15 秒视频
- **aspect_ratio** (宽高比): 视频宽高比
  - `2:3`: 竖屏
  - `3:2`: 横屏
  - `1:1`: 方形
- **size** (分辨率): 视频分辨率
  - `720P`: 标清（所有模型支持）
  - `1080P`: 高清（仅 15 秒模型支持）
- **enhance_prompt** (提示词增强): 自动将中文提示词优化并翻译为英文
- **api_key** (API密钥): API 密钥（留空使用环境变量 `KUAI_API_KEY`）

### 可选参数

- **image_url_1** (参考图片1): 第 1 张参考图片 URL（来自图片上传节点）
- **image_url_2** (参考图片2): 第 2 张参考图片 URL（可选）
- **image_url_3** (参考图片3): 第 3 张参考图片 URL（可选）
- **api_base** (API地址): API 端点地址（默认：`https://api.kegeai.top`）
- **custom_model** (自定义模型): 自定义模型名称（留空使用下拉模型）

### GrokImage2VideoAndWait 额外参数

- **max_wait_time** (最大等待时间): 最大等待时间（秒），默认 1200 秒
- **poll_interval** (轮询间隔): 轮询间隔（秒），默认 10 秒

## 返回值

### GrokImage2Video

- **任务ID** (STRING): 视频生成任务的唯一标识符
- **状态** (STRING): 任务状态（`pending`, `processing`, `completed`, `failed`）
- **增强提示词** (STRING): API 返回的增强后的提示词
- **状态更新时间** (INT): 状态更新的时间戳

### GrokImage2VideoAndWait

- **任务ID** (STRING): 视频生成任务的唯一标识符
- **状态** (STRING): 任务状态（通常为 `completed`）
- **视频URL** (STRING): 生成的视频下载链接
- **增强提示词** (STRING): API 返回的增强后的提示词

## 使用技巧

### 1. 提示词编写

**文生视频**（0 张图片）：
- 详细描述场景、动作、氛围
- 例如："A serene beach at sunset, gentle waves rolling onto the shore, seagulls flying in the distance"

**图生视频**（1-3 张图片）：
- 描述图片之间的过渡或动作
- 例如："Smooth transition from day to night, with lights gradually turning on"

### 2. 图片选择

- **质量**：使用高质量、清晰的图片
- **一致性**：多张图片应保持风格和主题一致
- **顺序**：按照期望的视频顺序连接图片（image_url_1 → image_url_2 → image_url_3）

### 3. 模型选择

- **6 秒模型**：适合快速预览和测试
- **10 秒模型**：适合大多数场景
- **15 秒模型**：适合需要更长时间展示的内容，支持 1080P

### 4. 宽高比选择

- **2:3 (竖屏)**：适合手机端、短视频平台
- **3:2 (横屏)**：适合桌面端、YouTube
- **1:1 (方形)**：适合社交媒体（Instagram、微信朋友圈）

## 常见问题

### Q1: 为什么图片输入不能手动输入 URL？

A: 为了确保工作流的清晰性和可追溯性，图片 URL 必须从"📷 传图到临时图床"节点连接。这样可以：
- 避免手动输入错误
- 保持工作流的可视化
- 确保图片来源可追踪

### Q2: 可以只连接第 2 张或第 3 张图片吗？

A: 建议按顺序连接（先连接 image_url_1，再连接 image_url_2，最后连接 image_url_3）。虽然技术上可以跳过，但按顺序连接可以确保最佳效果。

### Q3: 如何判断是文生视频还是图生视频？

A: 节点会自动判断：
- 如果所有图片输入都为空 → 文生视频
- 如果有 1-3 个图片输入 → 图生视频

日志中会显示"Grok 文生视频任务"或"Grok 图生视频任务（图片数: X）"。

### Q4: 支持超过 3 张图片吗？

A: 目前 Grok API 最多支持 3 张参考图片。如果需要更多图片，可以考虑：
- 将多张图片合成为一张
- 分段生成多个视频后拼接

### Q5: GrokImage2Video 和 GrokImage2VideoAndWait 有什么区别？

A:
- **GrokImage2Video**: 创建任务后立即返回任务 ID，需要手动查询状态
- **GrokImage2VideoAndWait**: 创建任务后自动等待完成，直接返回视频 URL（一键生成）

推荐使用 `GrokImage2VideoAndWait` 以获得更简单的工作流。

## 示例工作流

### 示例 1：产品展示视频（单图）

```
[产品图片] → 📷 传图到临时图床 → GrokImage2VideoAndWait.image_url_1
提示词: "Slowly rotate the product 360 degrees, highlighting its features"
模型: grok-video-3-10s (10秒)
宽高比: 1:1
```

### 示例 2：故事板动画（三图）

```
[场景1] → 📷 传图到临时图床 → GrokImage2VideoAndWait.image_url_1
[场景2] → 📷 传图到临时图床 → GrokImage2VideoAndWait.image_url_2
[场景3] → 📷 传图到临时图床 → GrokImage2VideoAndWait.image_url_3
提示词: "Smooth cinematic transitions between scenes, creating a cohesive story"
模型: grok-video-3-15s (15秒)
宽高比: 3:2
```

### 示例 3：纯文生视频（零图）

```
提示词: "A futuristic city at night, neon lights reflecting on wet streets, flying cars in the sky"
模型: grok-video-3-10s (10秒)
宽高比: 3:2
→ GrokImage2VideoAndWait → [视频URL]
```

## 技术细节

### API 调用

节点会将图片 URL 收集到一个列表中：

```python
images_list = []
for url in [image_url_1, image_url_2, image_url_3]:
    url_stripped = (url or "").strip()
    if url_stripped:
        images_list.append(url_stripped)

payload = {
    "model": "grok-video-3",
    "prompt": "...",
    "images": images_list  # 空列表 = 文生视频，非空 = 图生视频
}
```

### 日志输出

节点会在日志中显示：
- 文生视频：`[ComfyUI_KuAi_Power] Grok 文生视频任务: ...`
- 图生视频：`[ComfyUI_KuAi_Power] Grok 图生视频任务: ... (图片数: X)`

## 更新日志

- **2025-03-17**: 初始版本，支持 0-3 张图片输入
  - 移除旧的 `images` 参数（STRING multiline）
  - 添加 `image_url_1`, `image_url_2`, `image_url_3` 参数
  - 使用 `forceInput: True` 强制从节点连接
  - 自动判断文生视频/图生视频

## 相关文档

- [Grok 视频生成指南](GROK_VIDEO_GUIDE.md)
- [图片上传节点使用指南](IMAGE_UPLOAD_GUIDE.md)
- [批量处理指南](GROK_BATCH_WORKFLOW_GUIDE.md)
