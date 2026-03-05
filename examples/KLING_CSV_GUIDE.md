# 可灵批量处理 CSV 使用指南

## CSV 格式说明

### 必需列

- `task_type` - 任务类型
  - `text2video` - 文生视频
  - `image2video` - 图生视频

- `prompt` - 提示词（text2video 必需）

### 可选列

#### 通用参数

- `model_name` - 模型名称（默认：kling-v1）
  - `kling-v1`
  - `kling-v1-6`
  - `kling-v2-master`
  - `kling-v2-1-master`
  - `kling-v2-5-turbo`
  - `kling-v3`

- `mode` - 生成模式（默认：std）
  - `std` - 标准模式，性价比高
  - `pro` - 专家模式，质量更佳

- `duration` - 视频时长（默认：5）
  - `5` - 5秒
  - `10` - 10秒

- `negative_prompt` - 负面提示词（可选）

- `cfg_scale` - CFG 强度（默认：0.5，范围：0.0-1.0）

- `multi_shot` - 是否多镜头（默认：false）
  - `true` - 启用多镜头
  - `false` - 单镜头

- `watermark` - 是否添加水印（默认：false）
  - `true` - 添加水印
  - `false` - 不添加水印

- `output_prefix` - 输出文件前缀（可选）

#### 文生视频专用参数

- `aspect_ratio` - 宽高比（默认：16:9）
  - `16:9` - 横屏
  - `9:16` - 竖屏
  - `1:1` - 方形

#### 图生视频专用参数

- `image` - 图片 URL 或 Base64（image2video 必需）

- `image_tail` - 尾帧图片 URL 或 Base64（可选）

## 使用步骤

### 1. 准备 CSV 文件

使用 Excel、Google Sheets 或文本编辑器创建 CSV 文件，确保使用 **UTF-8 编码**保存。

### 2. 在 ComfyUI 中设置工作流

```
CSVBatchReader → KlingBatchProcessor
```

1. 添加 `CSVBatchReader` 节点
2. 选择或输入 CSV 文件路径
3. 添加 `KlingBatchProcessor` 节点
4. 连接 `CSVBatchReader` 的输出到 `KlingBatchProcessor` 的 `batch_tasks` 输入
5. 配置 API Key 和输出目录
6. 执行工作流

### 3. 配置参数

**KlingBatchProcessor 参数**：
- `batch_tasks` - 来自 CSVBatchReader 的任务数据（自动连接）
- `api_key` - API 密钥（留空使用环境变量 KUAI_API_KEY）
- `output_dir` - 输出目录（默认：./output/batch）
- `delay_between_tasks` - 任务间延迟秒数（默认：2.0）

### 4. 查看结果

处理完成后：
- 控制台会显示处理进度和结果
- `output_dir` 目录下会生成 `tasks.json` 文件，包含所有任务信息
- 视频 URL 会保存在任务信息中

## 示例文件

### 基础示例 (kling_batch_basic.csv)

```csv
task_type,prompt,model_name,mode,duration,aspect_ratio,output_prefix
text2video,海边日落，海浪拍打岸边,kling-v1,std,5,16:9,sunset
text2video,城市夜景，车流穿梭,kling-v1,std,5,16:9,city
text2video,森林中的小溪，阳光透过树叶,kling-v1,std,5,16:9,forest
```

### 高级示例 (kling_batch_advanced.csv)

```csv
task_type,prompt,negative_prompt,model_name,mode,duration,aspect_ratio,cfg_scale,watermark,output_prefix
text2video,美丽的花园，蝴蝶飞舞,模糊、低质量,kling-v2-master,pro,10,16:9,0.7,true,garden
text2video,雪山风景，云雾缭绕,噪点、失真,kling-v2-master,pro,10,9:16,0.6,false,mountain
```

### 图生视频示例 (kling_batch_image2video.csv)

```csv
task_type,image,prompt,model_name,mode,duration,output_prefix
image2video,https://example.com/image1.jpg,让图片动起来,kling-v1,std,5,img2vid_1
image2video,https://example.com/image2.jpg,添加动态效果,kling-v1,std,5,img2vid_2
```

## 常见问题

### Q: CSV 文件编码问题？

**A**: 确保使用 UTF-8 编码保存 CSV 文件。在 Excel 中，选择"另存为" → "CSV UTF-8 (逗号分隔)"。

### Q: 提示词包含逗号怎么办？

**A**: 用双引号包裹整个提示词：
```csv
task_type,prompt
text2video,"美丽的风景，包含山、水、树"
```

### Q: 如何处理失败的任务？

**A**:
1. 查看控制台输出的错误信息
2. 检查 CSV 文件中对应行的参数
3. 修正后重新运行批量处理

### Q: 批量处理会等待所有任务完成吗？

**A**: 是的，批量处理器会逐个创建任务并等待完成，然后再处理下一个任务。

### Q: 可以中途停止批量处理吗？

**A**: 可以在 ComfyUI 中停止执行。已完成的任务信息会保存在 `tasks.json` 中。

### Q: 任务间延迟有什么作用？

**A**: 避免 API 请求过于频繁，建议设置 2-5 秒的延迟。

## 最佳实践

1. **小批量测试**：先用 2-3 个任务测试，确认配置正确后再批量处理
2. **合理设置延迟**：建议 2-5 秒，避免 API 限流
3. **备份 CSV 文件**：处理前备份原始 CSV 文件
4. **检查 API 配额**：确保 API 配额充足
5. **使用输出前缀**：便于识别和管理生成的视频

## 更新日志

- 2026-03-06: 初始版本
  - 支持文生视频和图生视频批量处理
  - 支持常用功能参数
  - 自动保存任务信息到 tasks.json
