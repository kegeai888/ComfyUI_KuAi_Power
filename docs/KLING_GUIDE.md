# 可灵视频生成节点使用指南

## 概述

可灵（Kling）视频生成节点为 ComfyUI 提供了强大的 AI 视频生成能力，支持文生视频和图生视频两种模式。通过 kuai.host API 接入可灵模型，提供高质量的视频生成服务。

**主要功能**：
- 🎞️ 文生视频：根据文本提示词生成视频
- 🎞️ 图生视频：基于图片生成动态视频
- 🔍 任务查询：查询视频生成任务状态
- ⚡ 一键生成：创建并等待任务完成
- 📦 批量处理：CSV 批量生成视频

**支持的模型**：
- kling-v1
- kling-v1-6
- kling-v2-master
- kling-v2-1-master
- kling-v2-5-turbo
- kling-v3

## 节点列表

### 1. 🎞️ 可灵文生视频 (KlingText2Video)

创建文生视频任务，返回任务 ID。

**输入参数**：

必需参数：
- `prompt` (提示词) - 视频描述文本
- `model_name` (模型名称) - 选择使用的模型
- `mode` (模式) - std（标准）或 pro（专家）
- `duration` (时长) - 5s 或 10s
- `aspect_ratio` (宽高比) - 16:9、9:16 或 1:1

可选参数：
- `negative_prompt` (负面提示词) - 不希望出现的内容
- `cfg_scale` (CFG强度) - 0.0-1.0，默认 0.5
- `multi_shot` (多镜头) - 是否生成多镜头视频
- `watermark` (水印) - 是否添加水印
- `api_key` (API密钥) - 留空使用环境变量
- `api_base` (API地址) - 默认 https://api.kuai.host
- `timeout` (超时) - 请求超时时间（秒）

**返回值**：
- `任务ID` - 用于查询任务状态
- `状态` - 任务初始状态
- `创建时间` - 任务创建时间戳

### 2. 🎞️ 可灵图生视频 (KlingImage2Video)

基于图片创建视频任务。

**输入参数**：

必需参数：
- `image` (图片) - 图片 URL 或 Base64 编码
- `model_name`, `mode`, `duration` - 同文生视频

可选参数：
- `prompt` (提示词) - 可选，用于引导生成
- `image_tail` (尾帧图片) - 控制视频结束画面
- 其他参数同文生视频

**返回值**：同文生视频

### 3. 🔍 可灵查询任务 (KlingQueryTask)

查询视频生成任务状态。

**输入参数**：

必需参数：
- `task_id` (任务ID) - 要查询的任务 ID

可选参数：
- `wait` (等待完成) - 是否轮询等待任务完成
- `poll_interval_sec` (轮询间隔) - 查询间隔秒数
- `timeout_sec` (总超时) - 最大等待时间
- `api_key`, `api_base`

**返回值**：
- `状态` - submitted, processing, succeed, failed, timeout
- `视频URL` - 生成的视频下载地址
- `时长` - 实际视频时长
- `原始响应` - 完整的 API 响应 JSON

### 4. ⚡ 可灵文生视频（一键）(KlingText2VideoAndWait)

一键创建文生视频并等待完成。

**输入参数**：合并了创建和查询的所有参数

**返回值**：
- `状态` - 最终任务状态
- `视频URL` - 视频下载地址
- `时长` - 视频时长
- `任务ID` - 任务 ID

### 5. ⚡ 可灵图生视频（一键）(KlingImage2VideoAndWait)

一键创建图生视频并等待完成。

**输入参数**：合并了创建和查询的所有参数

**返回值**：同文生视频一键节点

### 6. 📦 可灵批量处理 (KlingBatchProcessor)

批量处理 CSV 任务列表。

**输入参数**：
- `batch_tasks` (批量任务) - 来自 CSVBatchReader 的 JSON 数据
- `api_key` (API密钥)
- `output_dir` (输出目录) - 保存任务信息的目录
- `delay_between_tasks` (任务间延迟) - 避免 API 限流

**返回值**：
- `处理结果` - 批量处理报告
- `输出目录` - 任务信息保存路径

## 使用示例

### 示例 1：基础文生视频

```
1. 添加"可灵文生视频"节点
2. 设置参数：
   - 提示词：海边日落，海浪拍打岸边
   - 模型：kling-v1
   - 模式：std
   - 时长：5s
   - 宽高比：16:9
3. 添加"可灵查询任务"节点
4. 连接任务ID输出到查询节点
5. 执行工作流
```

### 示例 2：一键生成（推荐）

```
1. 添加"可灵文生视频（一键）"节点
2. 设置提示词和参数
3. 执行工作流，自动等待完成
4. 获取视频URL
```

### 示例 3：图生视频

```
1. 上传图片获取 URL
2. 添加"可灵图生视频（一键）"节点
3. 设置：
   - 图片：图片 URL
   - 提示词：让图片动起来
   - 其他参数
4. 执行工作流
```

### 示例 4：批量处理

```
1. 准备 CSV 文件（参考 examples/kling_batch_basic.csv）
2. 添加"CSVBatchReader"节点，选择 CSV 文件
3. 添加"可灵批量处理"节点
4. 连接节点
5. 配置 API Key 和输出目录
6. 执行工作流
```

## 参数详解

### 模型选择

| 模型 | 特点 | 适用场景 |
|------|------|---------|
| kling-v1 | 基础模型，速度快 | 快速测试、大批量生成 |
| kling-v1-6 | 改进版本 | 平衡质量和速度 |
| kling-v2-master | 高质量模型 | 专业内容创作 |
| kling-v2-1-master | 最新版本 | 最佳质量 |
| kling-v2-5-turbo | 快速版本 | 快速生成 |
| kling-v3 | 最新模型 | 最新功能 |

### 生成模式

- **std（标准模式）**：性价比高，适合大批量生成
- **pro（专家模式）**：质量更佳，适合精品内容

### CFG Scale

控制提示词引导强度：
- **0.0-0.3**：模型自由度高，创意性强
- **0.4-0.6**：平衡（推荐）
- **0.7-1.0**：严格遵循提示词

### 宽高比

- **16:9**：横屏视频，适合电脑观看
- **9:16**：竖屏视频，适合手机观看
- **1:1**：方形视频，适合社交媒体

## API 说明

### 端点

- 文生视频：`POST /kling/v1/videos/text2video`
- 图生视频：`POST /kling/v1/videos/image2video`
- 查询任务：`GET /kling/v1/videos/text2video/{task_id}`

### 认证

使用 Bearer Token 认证：
```
Authorization: Bearer YOUR_API_KEY
```

### 响应格式

**创建任务响应**：
```json
{
  "code": 0,
  "message": "SUCCEED",
  "data": {
    "task_id": "831922345719271433",
    "task_status": "submitted",
    "created_at": 1766374262370
  }
}
```

**查询任务响应**：
```json
{
  "code": 0,
  "message": "SUCCEED",
  "data": {
    "task_id": "831922345719271433",
    "task_status": "succeed",
    "task_info": {
      "video_url": "https://example.com/video.mp4",
      "duration": "5"
    }
  }
}
```

### 任务状态

- `submitted` - 已提交
- `processing` - 处理中
- `succeed` - 成功完成
- `failed` - 失败
- `timeout` - 超时（本地轮询超时）

## 常见问题

### Q: API Key 如何配置？

**A**: 两种方式：
1. 在节点参数中直接输入
2. 设置环境变量 `KUAI_API_KEY`

```bash
export KUAI_API_KEY=your_key_here
```

### Q: 视频生成需要多长时间？

**A**:
- 标准模式：通常 2-5 分钟
- 专家模式：通常 5-10 分钟
- 具体时间取决于队列情况

### Q: 如何获取 API Key？

**A**: 访问 https://api.kuai.host/register?aff=z2C8 注册账号并获取 API Key。

### Q: 支持哪些图片格式？

**A**: 支持 JPEG、PNG、WebP 格式，可以使用 URL 或 Base64 编码。

### Q: 批量处理失败怎么办？

**A**:
1. 查看控制台错误信息
2. 检查 CSV 文件格式
3. 确认 API Key 和配额
4. 修正后重新运行

### Q: 可以中途取消任务吗？

**A**: 可以在 ComfyUI 中停止执行，但已提交到 API 的任务会继续处理。

### Q: 视频质量如何优化？

**A**:
1. 使用更高级的模型（v2-master, v3）
2. 选择 pro 模式
3. 调整 CFG Scale
4. 优化提示词描述
5. 使用负面提示词排除不需要的内容

### Q: 支持多长的视频？

**A**: 目前支持 5 秒和 10 秒两种时长。

## 最佳实践

### 提示词编写

1. **具体描述**：详细描述场景、动作、光线等
2. **使用负面提示词**：排除不需要的元素
3. **参考示例**：查看成功案例的提示词
4. **迭代优化**：根据结果调整提示词

### 批量处理

1. **小批量测试**：先测试 2-3 个任务
2. **合理延迟**：设置 2-5 秒任务间延迟
3. **监控配额**：确保 API 配额充足
4. **错误处理**：记录失败任务，单独重试

### 性能优化

1. **选择合适模型**：根据需求平衡质量和速度
2. **使用一键节点**：简化工作流
3. **批量处理**：提高效率
4. **缓存结果**：保存任务 ID 和视频 URL

## 故障排查

### 节点不显示

1. 检查依赖：`pip install -r requirements.txt`
2. 运行诊断：`python diagnose.py`
3. 查看 ComfyUI 控制台日志
4. 重启 ComfyUI

### API 调用失败

1. 验证 API Key：`echo $KUAI_API_KEY`
2. 测试连接：`curl -H "Authorization: Bearer $KUAI_API_KEY" https://api.kuai.host/v1/models`
3. 检查网络连接
4. 查看 API 配额

### 任务一直处理中

1. 检查任务状态：使用查询节点
2. 增加超时时间
3. 联系 API 服务商

## 更新日志

### 2026-03-06 - v1.0.0

**新增功能**：
- ✅ 可灵文生视频节点
- ✅ 可灵图生视频节点
- ✅ 任务查询节点
- ✅ 一键生成便捷节点
- ✅ CSV 批量处理器
- ✅ 前端快速面板集成

**支持的功能**：
- 基础参数：prompt, model_name, mode, duration, aspect_ratio
- 常用功能：negative_prompt, cfg_scale, multi_shot, watermark
- 图生视频：image, image_tail
- 批量处理：CSV 格式，任务路由，进度报告

## 相关资源

- **API 服务**: https://api.kuai.host/register?aff=z2C8
- **视频教程**: https://www.bilibili.com/video/BV1umCjBqEpt/
- **项目主页**: ComfyUI_KuAi_Power
- **CSV 使用指南**: examples/KLING_CSV_GUIDE.md
- **示例文件**: examples/kling_batch_*.csv

## 技术支持

如遇问题，请：
1. 查看本文档的常见问题部分
2. 检查 ComfyUI 控制台日志
3. 运行 `python diagnose.py` 诊断
4. 查看项目 README.md

---

**文档版本**: 1.0.0
**更新日期**: 2026-03-06
**适用版本**: ComfyUI_KuAi_Power v1.0.0+
