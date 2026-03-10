# CSV 并发图生视频工作流使用指南

## 概述

本工作流实现了**批量本地图片上传 + CSV 并发图生视频**的完整闭环。

## 工作流程

```
本地图片目录 → 批量上传 → 获取 URL → CSV 并发处理 → 自动下载 MP4
```

## 文件清单

### Grok
- **工作流**: `workflows/grok_csv_concurrent_image2video_workflow.json`
- **CSV 示例**: `workflows/grok_image2video_concurrent.csv`

### Veo3
- **工作流**: `workflows/veo3_csv_concurrent_image2video_workflow.json`
- **CSV 示例**: `workflows/veo3_image2video_concurrent.csv`

## 使用步骤

### 1. 准备本地图片

将图片放入指定目录：

```bash
# Grok
/root/ComfyUI/input/grok/demo1/
  ├── 1.png
  ├── 2.jpg
  ├── 3.jpeg
  └── ...

# Veo3
/root/ComfyUI/input/veo3/demo1/
  ├── 1.png
  ├── 2.jpg
  └── ...
```

**支持格式**: png, jpg, jpeg, webp, bmp, gif

### 2. 准备 CSV 文件

#### Grok CSV 格式

```csv
prompt,image_urls,output_prefix,model,aspect_ratio,size,enhance_prompt
一个科技感的视频,https://example.com/1.jpg,tech_video_1,grok-video-3 (6秒),3:2,720P,true
自然风景视频,https://example.com/2.jpg,nature_video_1,grok-video-3 (6秒),3:2,720P,true
```

**必需列**:
- `prompt`: 视频生成提示词
- `image_urls`: 参考图片 URL（可以是批量上传节点的输出）
- `output_prefix`: 输出文件名前缀

**可选列**:
- `model`: 模型名称（默认: grok-video-3 (6秒)）
- `aspect_ratio`: 宽高比（默认: 3:2）
- `size`: 分辨率（默认: 720P）
- `enhance_prompt`: 提示词增强（默认: true）

#### Veo3 CSV 格式

```csv
prompt,image_urls,output_prefix,model,aspect_ratio,enhance_prompt,enable_upsample
科技感视频,https://example.com/1.jpg,veo3_tech_1,veo_3_1-fast,9:16,true,true
自然风景,https://example.com/2.jpg,veo3_nature_1,veo_3_1-fast,9:16,true,true
```

**必需列**:
- `prompt`: 视频生成提示词
- `image_urls`: 参考图片 URL
- `output_prefix`: 输出文件名前缀

**可选列**:
- `model`: 模型名称（默认: veo_3_1-fast）
- `aspect_ratio`: 宽高比（默认: 9:16）
- `enhance_prompt`: 提示词增强（默认: true）
- `enable_upsample`: 超分辨率（默认: true）

### 3. 在 ComfyUI 中加载工作流

1. 打开 ComfyUI
2. 加载对应的工作流 JSON 文件
3. 配置节点参数

### 4. 配置节点

#### BatchImageUploader 节点

- **图片目录路径**: `/root/ComfyUI/input/grok/demo1`（或 veo3）
- **图床URL**: `https://imageproxy.zhongzhuan.chat/api/upload`
- **格式**: jpeg（推荐）
- **质量**: 90
- **超时**: 30 秒
- **最大数量**: 100

#### CSVBatchReader 节点

- **CSV文件**: 选择对应的 CSV 文件
- **API密钥**: 留空（使用环境变量）
- **编码**: utf-8

#### CSV 并发处理器节点

- **API密钥**: 填入你的 API Key
- **视频保存目录**: `output/grok` 或 `output/veo3`
- **并发批次大小**: 10（推荐）
- **最大等待时间**: 1200 秒
- **轮询间隔**: 10 秒（Grok）/ 15 秒（Veo3）

### 5. 执行工作流

点击"Queue Prompt"执行。

### 6. 查看结果

- **处理报告**: 显示每个任务的状态和本地路径
- **视频保存目录**: 显示视频保存的绝对路径
- **视频文件**: 在 `ComfyUI/output/grok/` 或 `ComfyUI/output/veo3/` 目录

## 工作流节点说明

### BatchImageUploader（批量上传本地图片）

**功能**: 扫描本地目录，批量上传图片到图床，返回 URL 列表

**输入**:
- 图片目录路径

**输出**:
- 图片 URL 列表（JSON 数组）
- 上传详情
- 成功数量

### CSVBatchReader（CSV 读取器）

**功能**: 读取 CSV 文件，解析为任务列表

**输入**:
- CSV 文件路径

**输出**:
- 批量任务（JSON 格式）

### GrokCSVConcurrentProcessor / VeoCSVConcurrentProcessor

**功能**: 并发处理视频生成任务，自动轮询、下载

**输入**:
- 批量任务（来自 CSV 读取器）

**输出**:
- 处理报告
- 视频保存目录

## 注意事项

1. **图片命名**: 建议使用数字命名（1.png, 2.jpg...），系统会按文件名排序
2. **并发数量**: 建议 5-10 路并发，避免 API 限流
3. **超时设置**: 视频生成通常需要 5-20 分钟，建议设置 1200 秒以上
4. **API 配额**: 注意 API 使用配额，避免超限
5. **网络稳定**: 确保网络连接稳定，避免上传/下载失败

## 常见问题

### Q: 图片上传失败？
A: 检查网络连接和图床 URL 是否正确。

### Q: CSV 解析错误？
A: 确保 CSV 文件使用 UTF-8 编码，表头列名正确。

### Q: 视频生成超时？
A: 增加 `max_wait_time` 参数，或减少并发数量。

### Q: 找不到视频文件？
A: 检查"处理报告"输出，确认任务状态为 completed。

## 性能对比

| 方式 | 10 个视频耗时 | 适用场景 |
|------|-------------|---------|
| 批量处理（串行） | ~100 分钟 | 小批量、API 限流 |
| CSV 并发（10路） | ~10 分钟 | 大批量生产 |

## 更新日志

- 2026-03-10: 初始版本，支持 Grok 和 Veo3 CSV 并发图生视频
