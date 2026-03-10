# Veo3 批量视频生成工作流使用指南

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

本插件提供了两个完整的 Veo3 批量视频生成工作流：

1. **文生视频批量工作流** (`veo3_text2video_batch_workflow.json`)
   - 纯文本提示词批量生成视频
   - 支持自动提示词增强和翻译
   - 适合大规模内容创作

2. **图生视频批量工作流** (`veo3_image2video_batch_workflow.json`)
   - 基于参考图片批量生成视频
   - 支持图片动画化、场景增强
   - 适合产品展示、图片转视频

### 工作流架构

```
CSV文件 → CSV批量读取器 → Veo3批量处理器 → 结果显示
                                    ↓
                              输出目录显示
```

---

## 文生视频批量工作流

### 工作流文件
`workflows/veo3_text2video_batch_workflow.json`

### 节点组成

1. **📂 CSV批量读取器** (`CSVBatchReader`)
   - 读取 CSV 文件
   - 解析任务数据
   - 输出 JSON 格式的批量任务

2. **📦 Veo3批量处理器** (`Veo3BatchProcessor`)
   - 接收批量任务
   - 自动识别任务类型（文生/图生）
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

**文件路径**: `examples/veo3_text2video_batch.csv`

```csv
task_type,prompt,model,aspect_ratio,enhance_prompt,enable_upsample,output_prefix
text2video,"一只可爱的小猫在花园里追逐蝴蝶",veo3.1,9:16,true,true,cat_butterfly
text2video,"雄鹰在山峰间翱翔，日出时分",veo3.1,16:9,true,true,eagle_mountains
```

---

## 图生视频批量工作流

### 工作流文件
`workflows/veo3_image2video_batch_workflow.json`

### 节点组成

与文生视频工作流相同，但 CSV 文件需要包含 `image_urls` 列和 `task_type=image2video`。

### CSV 文件示例

**文件路径**: `examples/veo3_image2video_batch.csv`

```csv
task_type,prompt,model,aspect_ratio,enhance_prompt,enable_upsample,image_urls,output_prefix
image2video,"让这张山景图动起来，添加云雾流动",veo3.1,16:9,true,true,https://images.unsplash.com/photo-xxx,mountain_clouds
image2video,"为这只猫咪添加动态效果，眨眼和转动",veo3.1,9:16,true,true,https://images.unsplash.com/photo-yyy,cat_blink
```

---

## CSV 文件格式说明

### 必需列

| 列名 | 说明 | 示例 |
|------|------|------|
| `task_type` | 任务类型 | `text2video` / `image2video` |
| `prompt` | 视频生成提示词 | "一只可爱的小猫在花园里玩球" |
| `model` | Veo3 模型选择 | `veo3.1` / `veo3-fast` / `veo3-pro` |
| `aspect_ratio` | 视频宽高比 | `16:9` / `9:16` |

### 可选列

| 列名 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `enhance_prompt` | 自动增强提示词 | `true` | `true` / `false` |
| `enable_upsample` | 启用超分提升质量 | `true` | `true` / `false` |
| `image_urls` | 参考图片URL（图生视频必需） | 空 | `https://example.com/image.jpg` |
| `output_prefix` | 输出文件名前缀 | `task_N` | `cat_playing` |
| `custom_model` | 自定义模型名称 | 空 | `veo3.1-4k` |

### 模型说明

| 模型名称 | 特点 | 适用场景 |
|---------|------|---------|
| `veo3.1` | 最新版本，质量最高 | 高质量视频、商业用途 |
| `veo3` | 标准版本 | 一般视频生成 |
| `veo3-fast` | 快速版本，速度快 | 快速预览、测试 |
| `veo3-pro` | 专业版本 | 专业级视频制作 |
| `veo3.1-fast-components` | 快速组件版 | 组件化视频 |
| `veo_3_1-fast-4K` | 4K快速版 | 高分辨率快速生成 |
| `veo3.1-4k` | 4K标准版 | 高分辨率标准质量 |
| `veo3.1-pro-4k` | 4K专业版 | 高分辨率专业质量 |

### 宽高比说明

| 宽高比 | 适用场景 |
|--------|---------|
| `16:9` | 横屏视频（YouTube、B站、电视） |
| `9:16` | 竖屏视频（抖音、快手、Instagram Stories） |

### 提示词增强

- **`enhance_prompt: true`**: 自动将中文提示词优化并翻译为英文，提升生成质量
- **`enhance_prompt: false`**: 直接使用原始提示词

### 超分功能

- **`enable_upsample: true`**: 启用超分辨率，提升视频清晰度（推荐）
- **`enable_upsample: false`**: 不使用超分，生成速度更快

---

## 参数配置详解

### CSV批量读取器参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| **csv_file** | CSV文件名（相对于 ComfyUI/input/ 目录） | `veo3_text2video_batch.csv` |
| **csv_path** | CSV文件绝对路径（优先级高于 csv_file） | 空 |
| **encoding** | 文件编码 | `utf-8` |

### Veo3批量处理器参数

| 参数 | 说明 | 默认值 | 推荐值 |
|------|------|--------|--------|
| **api_key** | API密钥 | 空（使用环境变量） | 留空或填写 |
| **output_dir** | 输出目录 | `./output/veo3_batch` | 自定义路径 |
| **delay_between_tasks** | 任务间延迟（秒） | 2.0 | 2.0-5.0 |
| **api_base** | API端点地址 | `https://api.kegeai.top` | 默认即可 |
| **wait_for_completion** | 是否等待任务完成 | `false` | `false`（推荐） |
| **max_wait_time** | 单个任务最大等待时间（秒） | 1200 | 600-3600 |
| **poll_interval** | 轮询间隔（秒） | 15 | 15-30 |

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
max_wait_time: 1800
poll_interval: 15
```
- ⚠️ 会等待所有任务完成
- ⚠️ 耗时较长（每个任务 10-30 分钟）
- ✅ 自动获取视频URL

---

## 使用步骤

### 步骤 1: 准备 CSV 文件

#### 方法 A: 使用示例文件
```bash
# 文生视频
cp examples/veo3_text2video_batch.csv ComfyUI/input/

# 图生视频
cp examples/veo3_image2video_batch.csv ComfyUI/input/
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
在 `Veo3BatchProcessor` 节点的 `api_key` 参数中填写。

### 步骤 3: 加载工作流

1. 打开 ComfyUI
2. 点击 `Load` 按钮
3. 选择工作流文件：
   - 文生视频: `workflows/veo3_text2video_batch_workflow.json`
   - 图生视频: `workflows/veo3_image2video_batch_workflow.json`

### 步骤 4: 配置节点参数

#### CSV批量读取器
- 修改 `csv_file` 为你的 CSV 文件名
- 或使用 `csv_path` 指定绝对路径

#### Veo3批量处理器
- 检查 `output_dir` 输出目录
- 调整 `delay_between_tasks` 任务间延迟
- 根据需要设置 `wait_for_completion`

### 步骤 5: 执行工作流

1. 点击 `Queue Prompt` 按钮
2. 观察控制台输出：
   ```
   ============================================================
   [Veo3Batch] 开始批量处理 8 个视频生成任务
   [Veo3Batch] 输出目录: ./output/veo3_text2video_batch
   [Veo3Batch] 等待完成: 否
   ============================================================

   [1/8] 处理任务 (行 2)
     任务类型: text2video
     提示词: 一只可爱的小猫在花园里追逐蝴蝶...
     模型: veo3.1, 宽高比: 9:16
     增强提示词: True, 超分: True
     任务ID: task_xxx
     状态: pending
   ✓ 任务 1 完成
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
./output/veo3_text2video_batch/
├── tasks.json          # 任务列表（包含 task_id）
└── ...
```

### 步骤 7: 查询视频状态

#### 方法 A: 使用 Veo3 查询节点
1. 添加 `VeoQueryTask` 节点
2. 输入 `task_id`（从 tasks.json 获取）
3. 执行查询

#### 方法 B: 使用 API 直接查询
```bash
curl -H "Authorization: Bearer $KUAI_API_KEY" \
     "https://api.kegeai.top/v1/video/query?task_id=xxx"
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
在 Veo3BatchProcessor 的 api_key 参数中填写
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
2. 使用 `VeoQueryTask` 节点查询
3. 任务完成后会返回 `video_url`
4. 使用浏览器或下载工具下载视频

### Q5: 批量处理太慢？
**A**: 优化建议：
- 设置 `wait_for_completion: false`（快速提交模式）
- 减小 `delay_between_tasks`（但不要低于 1.0 秒）
- 分批处理（每批 10-20 个任务）
- 使用 `veo3-fast` 模型加快生成速度

### Q6: 图生视频的图片 URL 格式？
**A**: 支持的格式：
- 公网可访问的 HTTP/HTTPS URL
- 已上传到 kuai.host 的图片 URL
- 单个图片 URL（Veo3 每次只支持一张参考图）

### Q7: 提示词增强是什么？
**A**:
- 自动将中文提示词优化并翻译为英文
- 添加更多细节描述
- 提升视频生成质量
- 建议保持 `enhance_prompt: true`

### Q8: 超分功能有什么用？
**A**:
- 提升视频分辨率和清晰度
- 增强画面细节
- 轻微增加生成时间
- 建议高质量视频启用

### Q9: 如何选择合适的模型？
**A**:
- **veo3.1**: 最新最好，推荐用于正式项目
- **veo3-fast**: 快速预览和测试
- **veo3-pro**: 专业级质量要求
- **4K 系列**: 需要高分辨率输出

### Q10: 任务失败如何重试？
**A**:
1. 查看错误信息（在处理结果中）
2. 修复问题（如提示词、参数等）
3. 创建新的 CSV 文件（只包含失败的任务）
4. 重新执行工作流

---

## 高级技巧

### 1. 混合任务类型
在同一个 CSV 文件中混合文生视频和图生视频：
```csv
task_type,prompt,model,aspect_ratio,image_urls,output_prefix
text2video,"纯文本生成",veo3.1,16:9,,text_video
image2video,"图片动画化",veo3.1,16:9,https://example.com/img.jpg,image_video
```

### 2. 分批处理大量任务
```python
import pandas as pd

df = pd.read_csv('large_batch.csv')
batch_size = 15

for i in range(0, len(df), batch_size):
    batch = df[i:i+batch_size]
    batch.to_csv(f'veo3_batch_{i//batch_size + 1}.csv', index=False)
```

### 3. 自动查询任务状态
```python
import json
import time
import requests

with open('./output/veo3_batch/tasks.json', 'r') as f:
    tasks = json.load(f)

for task in tasks:
    task_id = task['task_id']
    # 查询任务状态
    # ...
```

### 4. 提示词优化技巧
- 包含镜头描述：特写、航拍、跟踪镜头等
- 包含风格描述：电影级、艺术风格、写实等
- 包含光效描述：自然光、戏剧性灯光、柔和光等
- 包含动作描述：慢动作、快速移动、平滑过渡等

### 5. 图生视频最佳实践
- 使用高质量、高分辨率的参考图片
- 提示词描述期望的动态效果
- 选择与图片匹配的宽高比
- 启用超分以获得更好的质量

---

## 性能对比

| 模型 | 生成速度 | 视频质量 | 适用场景 |
|------|---------|---------|---------|
| veo3.1 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 正式项目、高质量需求 |
| veo3-fast | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 快速预览、测试 |
| veo3-pro | ⭐⭐ | ⭐⭐⭐⭐⭐ | 专业级制作 |
| veo3.1-4k | ⭐⭐ | ⭐⭐⭐⭐⭐ | 4K高清输出 |

---

## 相关文件

- 工作流文件:
  - `workflows/veo3_text2video_batch_workflow.json`
  - `workflows/veo3_image2video_batch_workflow.json`

- CSV 示例:
  - `examples/veo3_text2video_batch.csv`
  - `examples/veo3_image2video_batch.csv`

- 文档:
  - `README.md` - 插件总体说明
  - `CLAUDE.md` - 开发者文档
  - `docs/VEO3_BATCH_QUICK_REFERENCE.md` - 快速参考

---

## 技术支持

- GitHub Issues: https://github.com/kegeai888/ComfyUI_KuAi_Power/issues
- API 服务: https://api.kuai.host/register?aff=z2C8
- 视频教程: https://www.bilibili.com/video/BV1umCjBqEpt/

---

**版本**: 1.0.0
**更新日期**: 2026-03-10
**作者**: ComfyUI_KuAi_Power
