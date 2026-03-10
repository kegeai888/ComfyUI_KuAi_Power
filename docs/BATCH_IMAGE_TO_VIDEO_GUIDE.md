# 批量图片转视频完全闭环工作流使用指南

## 概述

本指南介绍如何使用新的桥接节点实现**完全闭环**的批量图片转视频工作流，无需手动编辑 CSV 文件。

## 核心优势

✅ **完全自动化**：从图片上传到视频生成，全程无需手动干预
✅ **无需 CSV 文件**：动态生成任务列表，告别手动编辑
✅ **灵活的模板系统**：支持 `{index}` 占位符自定义提示词和文件名
✅ **并发处理**：10 路并发，大幅提升处理速度
✅ **自动下载**：视频生成完成后自动下载到本地

## 工作流架构

```
BatchImageUploader → BatchImageToCSVTask → CSVConcurrentProcessor
  (上传图片)           (生成任务列表)          (并发处理+下载)
```

### 数据流详解

1. **BatchImageUploader** 输出：
   ```json
   ["https://cdn.com/img1.jpg", "https://cdn.com/img2.jpg", "https://cdn.com/img3.jpg"]
   ```

2. **BatchImageToCSVTask** 转换为：
   ```json
   [
     {
       "_row_number": 1,
       "prompt": "第1个视频",
       "image_urls": "https://cdn.com/img1.jpg",
       "output_prefix": "video_1",
       "model": "grok-video-3 (6秒)",
       ...
     },
     ...
   ]
   ```

3. **CSVConcurrentProcessor** 处理：
   - 10 路并发提交任务
   - 轮询等待完成
   - 自动下载 MP4 文件到 `output/grok/` 或 `output/veo3/`

## Grok 工作流使用步骤

### 1. 准备图片

将图片放到 ComfyUI 的 `input` 目录下，例如：
```
/root/ComfyUI/input/grok/demo1/
  ├── image1.jpg
  ├── image2.jpg
  └── image3.jpg
```

### 2. 加载工作流

在 ComfyUI 中加载：
```
workflows/grok_batch_image_to_video_workflow.json
```

### 3. 配置节点

#### 节点 1: BatchImageUploader（批量图片上传）
- **图片目录路径**：选择或输入图片目录（如 `grok/demo1`）
- **图片格式**：jpeg（推荐）
- **质量**：85（推荐）

#### 节点 2: GrokBatchImageToCSVTask（任务生成）
- **提示词模板**：`第{index}个科技产品视频`
  - `{index}` 会被替换为 1, 2, 3...
  - 支持多次使用占位符
- **模型**：选择 Grok 模型
  - `grok-video-3 (6秒)`
  - `grok-video-3-10s (10秒)`
  - `grok-video-3-15s (15秒)`
- **宽高比**：`3:2`（横屏）/ `2:3`（竖屏）/ `1:1`（方形）
- **分辨率**：`1080P`（推荐）/ `720P`
- **优化提示词**：✅ 启用（自动优化并翻译为英文）
- **输出前缀模板**：`tech_{index}`
  - 生成的文件名：`tech_1_a1b2c3d4.mp4`

#### 节点 3: GrokCSVConcurrentProcessor（并发处理）
- **API Key**：留空使用环境变量 `KUAI_API_KEY`
- **API Base**：`https://api.kegeai.top`（默认）
- **并发数**：10（推荐）
- **最大等待时间**：30 分钟
- **轮询间隔**：5 秒
- **输出目录**：`output/grok`
- **自动下载**：✅ 启用

### 4. 执行工作流

点击 ComfyUI 的"Queue Prompt"按钮，工作流将自动：
1. 上传所有图片到 CDN
2. 生成任务列表
3. 并发提交 10 个视频生成任务
4. 轮询等待所有任务完成
5. 自动下载 MP4 文件到 `output/grok/`

### 5. 查看结果

生成的视频文件位于：
```
output/grok/
  ├── tech_1_a1b2c3d4.mp4
  ├── tech_2_b2c3d4e5.mp4
  └── tech_3_c3d4e5f6.mp4
```

处理报告示例：
```
并发完成: 3/3 成功
[1] 行1  output/grok/tech_1_a1b2c3d4.mp4
[2] 行2  output/grok/tech_2_b2c3d4e5.mp4
[3] 行3  output/grok/tech_3_c3d4e5f6.mp4
```

## Veo3 工作流使用步骤

### 1-2. 准备图片和加载工作流

与 Grok 相同，加载：
```
workflows/veo3_batch_image_to_video_workflow.json
```

### 3. 配置节点

#### 节点 2: VeoBatchImageToCSVTask（任务生成）
- **提示词模板**：`视频{index}`
- **模型**：选择 Veo3 模型
  - `veo3.1`（推荐）
  - `veo3-fast`（快速）
  - `veo3-pro`（专业）
  - `veo3.1-4k`（4K）
- **宽高比**：`9:16`（竖屏）/ `16:9`（横屏）
- **优化提示词**：✅ 启用
- **启用超分**：✅ 启用（提升视频质量）
- **输出前缀模板**：`veo_{index}`

#### 节点 3: VeoCSVConcurrentProcessor
配置与 Grok 类似，输出目录为 `output/veo3`

## 高级用法

### 复杂提示词模板

```
提示词模板：这是第{index}个产品，展示其核心功能，编号：{index}
输出前缀模板：product_{index}_demo
```

生成结果：
- 提示词：`这是第1个产品，展示其核心功能，编号：1`
- 文件名：`product_1_demo_a1b2c3d4.mp4`

### 自定义模型

如果需要使用自定义模型（如内测模型），在"自定义模型"字段填写模型名称，将覆盖下拉选择的模型。

### 环境变量配置

推荐使用环境变量配置 API Key：
```bash
export KUAI_API_KEY=your_api_key_here
```

或在项目根目录创建 `.env` 文件：
```
KUAI_API_KEY=your_api_key_here
```

## 常见问题

### Q: 图片上传失败？
A: 检查：
- 图片目录路径是否正确
- 图片格式是否支持（JPEG/PNG/WebP）
- API Key 是否有效

### Q: 任务生成失败？
A: 检查：
- 图片 URL 列表是否为空
- 提示词模板是否有效
- 节点连接是否正确

### Q: 视频生成失败？
A: 检查：
- API Key 是否有效
- 网络连接是否正常
- 提示词是否符合内容政策
- 查看 ComfyUI 控制台的详细错误信息

### Q: 下载的视频在哪里？
A:
- Grok: `output/grok/`
- Veo3: `output/veo3/`
- 文件名格式：`{output_prefix}_{hash8}.mp4`

### Q: 如何调整并发数？
A: 在 CSVConcurrentProcessor 节点中修改"并发数"参数。建议值：
- 小批量（<10 个）：5-10
- 中批量（10-50 个）：10
- 大批量（>50 个）：10（避免 API 限流）

### Q: 可以不使用模板占位符吗？
A: 可以。如果提示词模板中不包含 `{index}`，所有任务将使用相同的提示词。但建议使用占位符以区分不同任务。

## 性能优化建议

1. **图片质量**：JPEG 质量 85 是性能和质量的最佳平衡点
2. **并发数**：10 路并发可以充分利用 API 性能，避免过高导致限流
3. **轮询间隔**：5 秒是推荐值，过短会增加 API 请求次数
4. **批量大小**：建议每批 10-50 个任务，过大可能导致超时

## 与传统 CSV 工作流的对比

| 特性 | 传统 CSV 工作流 | 新的闭环工作流 |
|------|----------------|---------------|
| 需要手动编辑 CSV | ✅ 是 | ❌ 否 |
| 图片 URL 获取 | 手动复制粘贴 | 自动获取 |
| 提示词配置 | 逐行编辑 | 模板一次配置 |
| 灵活性 | 高（可精细控制每行） | 中（统一配置） |
| 易用性 | 低 | 高 |
| 适用场景 | 复杂需求，每个任务参数不同 | 批量处理，参数相似 |

## 最佳实践

1. **先小批量测试**：先用 2-3 张图片测试工作流，确认配置正确后再大批量处理
2. **使用有意义的前缀**：输出前缀模板使用描述性名称，便于后续管理
3. **保存工作流**：配置好的工作流保存为自定义名称，便于复用
4. **监控控制台**：执行过程中关注 ComfyUI 控制台的日志输出
5. **备份原图**：处理前备份原始图片，避免意外丢失

## 技术细节

### 节点接口

**GrokBatchImageToCSVTask**:
- 输入：`image_urls_json` (STRING) - JSON 数组格式的 URL 列表
- 输出：`任务列表JSON` (STRING) - JSON 数组格式的任务列表

**VeoBatchImageToCSVTask**:
- 输入：`image_urls_json` (STRING) - JSON 数组格式的 URL 列表
- 输出：`任务列表JSON` (STRING) - JSON 数组格式的任务列表

### 数据格式

任务列表 JSON 格式（Grok）：
```json
[
  {
    "_row_number": 1,
    "prompt": "提示词",
    "image_urls": "https://cdn.com/img.jpg",
    "model": "grok-video-3 (6秒)",
    "aspect_ratio": "3:2",
    "size": "1080P",
    "enhance_prompt": "true",
    "output_prefix": "grok_1",
    "custom_model": ""
  }
]
```

## 更新日志

- **2026-03-10**: 初始版本，支持 Grok 和 Veo3 批量图片转视频闭环工作流

## 相关文档

- [CSV 并发处理器使用指南](./CSV_CONCURRENT_IMAGE2VIDEO_GUIDE.md)
- [BatchImageUploader 节点文档](../README.md#批量图片上传)
- [Grok 节点文档](../README.md#grok-视频生成)
- [Veo3 节点文档](../README.md#veo3-视频生成)
