# Grok 批量视频生成工作流使用指南

## 📋 目录

- [工作流概述](#工作流概述)
- [文生视频批量工作流](#文生视频批量工作流)
- [图生视频批量工作流](#图生视频批量工作流)
- [CSV 文件格式说明](#csv-文件格式说明)
- [参数配置详解](#参数配置详解)
- [使用步骤](#使用步骤)
- [常见问题](#常见问题)

---

## 工作流概述

本插件提供了两个完整的 Grok 批量视频生成工作流：

1. **文生视频批量工作流** (`grok_text2video_batch_workflow.json`)
   - 纯文本提示词批量生成视频
   - 适合大规模内容创作

2. **图生视频批量工作流** (`grok_image2video_batch_workflow.json`)
   - 基于参考图片批量生成视频
   - 适合图片动画化、产品展示

### 工作流架构

```
CSV文件 → CSV批量读取器 → Grok批量处理器 → 结果显示
                                    ↓
                              输出目录显示
```

---

## 文生视频批量工作流

### 工作流文件
`workflows/grok_text2video_batch_workflow.json`

### 节点组成

1. **📂 CSV批量读取器** (`CSVBatchReader`)
   - 读取 CSV 文件
   - 解析任务数据
   - 输出 JSON 格式的批量任务

2. **📦 Grok批量处理器** (`GrokBatchProcessor`)
   - 接收批量任务
   - 逐个提交视频生成请求
   - 可选等待任务完成
   - 保存任务信息到输出目录

3. **📊 处理结果显示** (`ShowText`)
   - 显示处理统计信息
   - 成功/失败任务数量
   - 错误详情

4. **📁 输出目录显示** (`ShowText`)
   - 显示任务信息保存路径
   - 方便后续查询和下载

### CSV 文件示例

**文件路径**: `examples/grok_text2video_batch.csv`

```csv
prompt,model,aspect_ratio,size,enhance_prompt,output_prefix
"一只可爱的小猫在阳光明媚的花园里玩彩色球，慢动作，电影级灯光",grok-video-3 (6秒),3:2,1080P,true,cat_playing
"一只雄鹰在日落时分翱翔云端，航拍视角，4K画质",grok-video-3-10s (10秒),3:2,1080P,true,eagle_sunset
"一位舞者在雨中表演，戏剧性灯光，特写镜头，艺术风格",grok-video-3 (6秒),2:3,1080P,true,dancer_rain
```

---

## 图生视频批量工作流

### 工作流文件
`workflows/grok_image2video_batch_workflow.json`

### 节点组成

与文生视频工作流相同，但 CSV 文件需要包含 `image_urls` 列。

### CSV 文件示例

**文件路径**: `examples/grok_image2video_batch.csv`

```csv
prompt,model,aspect_ratio,size,enhance_prompt,image_urls,output_prefix
"让这张图片动起来，添加柔和的镜头运动和自然光效",grok-video-3 (6秒),3:2,1080P,true,https://images.unsplash.com/photo-1506905925346-21bda4d32df4,mountain_animate
"为这个场景添加动态效果，电影风格",grok-video-3-10s (10秒),2:3,1080P,true,https://images.unsplash.com/photo-1518791841217-8f162f1e1131,cat_dynamic
```

---

## CSV 文件格式说明

### 必需列

| 列名 | 说明 | 示例 |
|------|------|------|
| `prompt` | 视频生成提示词 | "一只可爱的小猫在花园里玩球" |
| `model` | Grok 模型选择 | `grok-video-3 (6秒)` / `grok-video-3-10s (10秒)` / `grok-video-3-15s (15秒)` |
| `aspect_ratio` | 视频宽高比 | `3:2` / `2:3` / `1:1` |
| `size` | 视频分辨率 | `720P` / `1080P` |

### 可选列

| 列名 | 说明 | 示例 |
|------|------|------|
| `enhance_prompt` | 提示词增强（自动优化并翻译中文为英文） | `true` / `false` / `1` / `0` / `yes` / `no` |
| `image_urls` | 参考图片URL（图生视频必需） | `https://example.com/image.jpg` |
| `output_prefix` | 输出文件名前缀 | `cat_playing` |
| `custom_model` | 自定义模型名称 | `grok-video-custom` |

**提示词增强功能说明**：
- 默认启用（`true`）
- 自动将中文提示词优化并翻译为英文，提升生成质量
- 如果提示词已经是英文，可设置为 `false` 跳过增强

### 模型说明

| 模型名称 | 视频时长 | 适用场景 |
|---------|---------|---------|
| `grok-video-3 (6秒)` | 6秒 | 快速预览、短视频 |
| `grok-video-3-10s (10秒)` | 10秒 | 标准视频、产品展示 |
| `grok-video-3-15s (15秒)` | 15秒 | 长视频、故事叙述 |

### 宽高比说明

| 宽高比 | 适用场景 |
|--------|---------|
| `3:2` | 横屏视频（YouTube、B站） |
| `2:3` | 竖屏视频（抖音、快手） |
| `1:1` | 方形视频（Instagram、微信） |

---

## 参数配置详解

### CSV批量读取器参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| **csv_file** | CSV文件名（相对于 ComfyUI/input/ 目录） | `grok_text2video_batch.csv` |
| **csv_path** | CSV文件绝对路径（优先级高于 csv_file） | 空 |
| **encoding** | 文件编码 | `utf-8` |

### Grok批量处理器参数

| 参数 | 说明 | 默认值 | 推荐值 |
|------|------|--------|--------|
| **api_key** | API密钥 | 空（使用环境变量） | 留空或填写 |
| **output_dir** | 输出目录 | `./output/grok_batch` | 自定义路径 |
| **delay_between_tasks** | 任务间延迟（秒） | 2.0 | 2.0-5.0 |
| **api_base** | API端点地址 | `https://api.kegeai.top` | 默认即可 |
| **wait_for_completion** | 是否等待任务完成 | `false` | `false`（推荐） |
| **max_wait_time** | 单个任务最大等待时间（秒） | 1200 | 600-1800 |
| **poll_interval** | 轮询间隔（秒） | 10 | 10-30 |

### 参数配置建议

#### 快速提交模式（推荐）
```
wait_for_completion: false
delay_between_tasks: 2.0
```
- ✅ 快速提交所有任务
- ✅ 不阻塞工作流
- ✅ 后续手动查询任务状态

#### 等待完成模式
```
wait_for_completion: true
max_wait_time: 1200
poll_interval: 10
```
- ⚠️ 会等待所有任务完成
- ⚠️ 耗时较长（每个任务 5-20 分钟）
- ✅ 自动获取视频URL

---

## 使用步骤

### 步骤 1: 准备 CSV 文件

#### 方法 A: 使用示例文件
```bash
# 文生视频
cp examples/grok_text2video_batch.csv ComfyUI/input/

# 图生视频
cp examples/grok_image2video_batch.csv ComfyUI/input/
```

#### 方法 B: 创建自定义文件
1. 复制示例文件作为模板
2. 使用 Excel/WPS/记事本编辑
3. 保存为 UTF-8 编码的 CSV 文件
4. 放到 `ComfyUI/input/` 目录

### 步骤 2: 配置 API Key

#### 方法 A: 环境变量（推荐）
```bash
export KUAI_API_KEY=your_api_key_here
```

#### 方法 B: 节点参数
在 `GrokBatchProcessor` 节点的 `api_key` 参数中填写。

### 步骤 3: 加载工作流

1. 打开 ComfyUI
2. 点击 `Load` 按钮
3. 选择工作流文件：
   - 文生视频: `workflows/grok_text2video_batch_workflow.json`
   - 图生视频: `workflows/grok_image2video_batch_workflow.json`

### 步骤 4: 配置节点参数

#### CSV批量读取器
- 修改 `csv_file` 为你的 CSV 文件名
- 或使用 `csv_path` 指定绝对路径

#### Grok批量处理器
- 检查 `output_dir` 输出目录
- 调整 `delay_between_tasks` 任务间延迟
- 根据需要设置 `wait_for_completion`

### 步骤 5: 执行工作流

1. 点击 `Queue Prompt` 按钮
2. 观察控制台输出：
   ```
   ============================================================
   [GrokBatch] 开始批量处理 8 个视频生成任务
   [GrokBatch] 输出目录: ./output/grok_text2video_batch
   [GrokBatch] 等待完成: 否
   ============================================================

   [1/8] 处理任务 (行 2)
   ✓ 任务 1 完成

   [2/8] 处理任务 (行 3)
   ✓ 任务 2 完成
   ...
   ```

### 步骤 6: 查看结果

#### 处理结果显示
```
批量处理完成
总任务数: 8
成功: 8
失败: 0
```

#### 输出目录
```
./output/grok_text2video_batch/
├── tasks.json          # 任务列表（包含 task_id）
└── ...
```

### 步骤 7: 查询视频状态

#### 方法 A: 使用 Grok 查询节点
1. 添加 `GrokQueryVideo` 节点
2. 输入 `task_id`（从 tasks.json 获取）
3. 执行查询

#### 方法 B: 使用批量查询脚本
```bash
# 查询所有任务状态
python scripts/query_grok_tasks.py ./output/grok_text2video_batch/tasks.json
```

---

## 常见问题

### Q1: CSV 文件读取失败？
**A**: 检查以下几点：
- 文件编码是否为 UTF-8
- 文件路径是否正确
- 列名是否与示例一致
- 是否有多余的空行

### Q2: API Key 未配置？
**A**: 两种配置方式：
```bash
# 方法1: 环境变量
export KUAI_API_KEY=your_key

# 方法2: 节点参数
在 GrokBatchProcessor 的 api_key 参数中填写
```

### Q3: 任务提交失败？
**A**: 检查：
- API Key 是否有效
- 网络连接是否正常
- API 端点地址是否正确
- 提示词是否符合规范

### Q4: 如何获取生成的视频？
**A**:
1. 查看 `tasks.json` 获取 `task_id`
2. 使用 `GrokQueryVideo` 节点查询
3. 任务完成后会返回 `video_url`
4. 使用浏览器或下载工具下载视频

### Q5: 批量处理太慢？
**A**: 优化建议：
- 设置 `wait_for_completion: false`（快速提交模式）
- 减小 `delay_between_tasks`（但不要低于 1.0 秒）
- 分批处理（每批 10-20 个任务）

### Q6: 图生视频的图片 URL 格式？
**A**: 支持的格式：
- 公网可访问的 HTTP/HTTPS URL
- 已上传到 kuai.host 的图片 URL
- 多个 URL 用逗号分隔（最多 3 张）

### Q7: 如何自定义输出文件名？
**A**: 在 CSV 文件中添加 `output_prefix` 列：
```csv
prompt,model,aspect_ratio,size,output_prefix
"提示词",grok-video-3 (6秒),3:2,1080P,my_video_001
```

### Q8: 任务失败如何重试？
**A**:
1. 查看错误信息（在处理结果中）
2. 修复问题（如提示词、参数等）
3. 创建新的 CSV 文件（只包含失败的任务）
4. 重新执行工作流

---

## 高级技巧

### 1. 分批处理大量任务
```python
# 将大 CSV 文件拆分为多个小文件
import pandas as pd

df = pd.read_csv('large_batch.csv')
batch_size = 20

for i in range(0, len(df), batch_size):
    batch = df[i:i+batch_size]
    batch.to_csv(f'batch_{i//batch_size + 1}.csv', index=False)
```

### 2. 自动查询任务状态
```python
# 定时查询任务状态脚本
import json
import time
import requests

with open('./output/grok_batch/tasks.json', 'r') as f:
    tasks = json.load(f)

for task in tasks:
    task_id = task['task_id']
    # 查询任务状态
    # ...
```

### 3. 结合其他节点
- 使用 `ImageUpload` 节点上传本地图片
- 使用 `VideoDownload` 节点自动下载生成的视频
- 使用 `DeepSeekOCR` 节点提取图片文字作为提示词

---

## 相关文件

- 工作流文件:
  - `workflows/grok_text2video_batch_workflow.json`
  - `workflows/grok_image2video_batch_workflow.json`

- CSV 示例:
  - `examples/grok_text2video_batch.csv`
  - `examples/grok_image2video_batch.csv`
  - `examples/grok_batch_basic.csv`
  - `examples/grok_batch_with_images.csv`
  - `examples/grok_batch_template.csv`

- 文档:
  - `README.md` - 插件总体说明
  - `CLAUDE.md` - 开发者文档

---

## 技术支持

- GitHub Issues: https://github.com/kegeai888/ComfyUI_KuAi_Power/issues
- API 服务: https://api.kuai.host/register?aff=z2C8
- 视频教程: https://www.bilibili.com/video/BV1umCjBqEpt/

---

**版本**: 1.0.0
**更新日期**: 2026-03-10
**作者**: ComfyUI_KuAi_Power
