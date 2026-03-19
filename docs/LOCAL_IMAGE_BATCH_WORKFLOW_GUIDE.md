# 本地图片批量生成视频工作流使用指南

## 📋 概述

本指南介绍如何使用本地图片目录批量生成 Grok 和 Veo3 视频，无需手动上传图片或编写 CSV 文件。

## 🎯 适用场景

- 有大量本地图片需要批量生成视频
- 不想手动上传图片获取 URL
- 希望快速测试图生视频效果
- 需要对本地素材库进行批量处理

## 📁 目录结构

### 推荐的目录组织方式

```
/root/ComfyUI/input/
├── grok/
│   ├── demo1/          # 项目1的图片
│   │   ├── 1.png
│   │   ├── 2.jpg
│   │   └── 3.png
│   ├── demo2/          # 项目2的图片
│   │   ├── 1.jpg
│   │   └── 2.png
│   └── product_shots/  # 产品图片
│       ├── 1.png
│       ├── 2.png
│       └── 3.png
└── veo3/
    ├── demo1/
    │   ├── 1.jpg
    │   ├── 2.jpg
    │   └── 3.jpg
    └── landscape/
        ├── 1.png
        └── 2.png
```

### 图片命名规则

- **支持格式**: `.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`, `.gif`
- **命名建议**: 使用数字编号（1.png, 2.jpg, ...）或描述性名称
- **排序**: 文件按名称排序处理

## 🚀 Grok 本地图片批量工作流

### 工作流文件
`workflows/grok_local_image2video_batch_workflow.json`

### 节点组成

```
📤 批量上传本地图片
    ↓
🔄 图片URL转Grok批量任务
    ↓
📦 Grok CSV 并发批量处理器
    ↓
📊 处理结果显示
```

### 使用步骤

#### 1. 准备图片

```bash
# 创建目录
mkdir -p /root/ComfyUI/input/grok/my_project

# 将图片放入目录
cp /path/to/your/images/*.png /root/ComfyUI/input/grok/my_project/
```

#### 2. 加载工作流

在 ComfyUI 中加载：
```
workflows/grok_local_image2video_batch_workflow.json
```

#### 3. 配置节点

**📤 批量上传本地图片**
- **图片目录路径**: `/root/ComfyUI/input/grok/my_project`
- **图床URL**: `https://imageproxy.zhongzhuan.chat/api/upload`（默认）
- **格式**: `jpeg`（推荐，文件小）
- **质量**: `90`（推荐）
- **最大数量**: `100`（根据需要调整）

**🔄 图片URL转Grok批量任务**
- **提示词模板**: 所有图片使用相同的提示词
  ```
  将这张图片转换为视频，添加自然的镜头运动和电影级灯光效果
  ```
- **输出前缀**: `grok_local`（自定义）

**📦 Grok CSV 并发批量处理器**
- **默认模型**: `grok-video-3 (6秒)`
- **默认宽高比**: `3:2`
- **默认分辨率**: `1080P`
- **默认提示词增强**: `true`（推荐）
- **并发批次大小**: `10`（建议 5-10）
- **视频保存目录**: `output/grok`

#### 4. 执行工作流

点击 "Queue Prompt" 执行工作流。

#### 5. 查看结果

- **上传详情**: 显示每个图片的上传状态和 URL
- **处理结果**: 显示批量处理统计信息
- **任务文件**: 保存在 `./output/grok_local_batch/tasks.json`

## 🎬 Veo3 本地图片批量工作流

### 工作流文件
`workflows/veo3_local_image2video_batch_workflow.json`

### 节点组成

```
📤 批量上传本地图片
    ↓
🔄 图片URL转Veo3批量任务
    ↓
📦 Veo3 CSV 并发批量处理器
    ↓
📊 处理结果显示
```

### 使用步骤

#### 1. 准备图片

```bash
# 创建目录
mkdir -p /root/ComfyUI/input/veo3/my_project

# 将图片放入目录
cp /path/to/your/images/*.jpg /root/ComfyUI/input/veo3/my_project/
```

#### 2. 加载工作流

在 ComfyUI 中加载：
```
workflows/veo3_local_image2video_batch_workflow.json
```

#### 3. 配置节点

**📤 批量上传本地图片**
- **图片目录路径**: `/root/ComfyUI/input/veo3/my_project`
- 其他参数同 Grok

**🔄 图片URL转Veo3批量任务**
- **提示词模板**: 所有图片使用相同的提示词
- **输出前缀**: `veo3_local`

**📦 Veo3 CSV 并发批量处理器**
- **API密钥**: 留空使用环境变量 `KUAI_API_KEY`
- **视频保存目录**: `output/veo3_local_batch`
- **并发批次大小**: `10`（建议 5-10）
- **默认模型**: `veo_3_1-fast`
- **默认宽高比**: `16:9`
- **默认提示词增强**: `true`（推荐）
- **默认超分**: `false`（按需开启）
- **最大等待时间**: `1200` 秒
- **轮询间隔**: `15` 秒

#### 4. 执行和查看结果

同 Grok 工作流

## 💡 使用技巧

### 1. 目录组织

**按项目分类**
```
/root/ComfyUI/input/grok/
├── project_a/
├── project_b/
└── project_c/
```

**按内容类型分类**
```
/root/ComfyUI/input/grok/
├── products/
├── landscapes/
└── portraits/
```

### 2. 提示词优化

**通用提示词**（适合大多数场景）
```
将这张图片转换为视频，添加自然的镜头运动和电影级灯光效果
```

**产品展示**
```
产品360度旋转展示，专业灯光，高端质感
```

**风景动画**
```
风景延时摄影效果，云朵流动，光影变化，4K画质
```

**人物动画**
```
人物微动效果，自然呼吸，眼神交流，电影级质感
```

### 3. 批量处理策略

**并发处理模式**（推荐）
- `batch_size`: `5-10`
- `poll_interval`: `15` 秒
- 按批次并发提交并自动下载完成视频

**稳定保守模式**
- `batch_size`: `2-3`
- `poll_interval`: `20-30` 秒
- 适合 API 配额紧张或需要降低查询频率的场景

### 4. 图片质量控制

**上传质量设置**
- **高质量**（推荐）: `format: jpeg`, `quality: 90`
- **平衡模式**: `format: jpeg`, `quality: 80`
- **快速模式**: `format: jpeg`, `quality: 70`

**注意**: 质量过低可能影响视频生成效果

### 5. 错误处理

**上传失败**
- 检查网络连接
- 检查图床 API 是否可用
- 尝试降低图片质量或数量

**任务提交失败**
- 检查 API Key 是否正确
- 检查 API 配额是否充足
- 查看错误详情调整参数

## 📊 性能优化

### 上传优化

**并发上传**（当前版本串行，未来可优化）
- 当前: 逐个上传
- 建议: 小批量处理（10-20张）

**图片预处理**
```bash
# 批量压缩图片（可选）
for img in /root/ComfyUI/input/grok/demo1/*.png; do
    convert "$img" -quality 90 -resize 2048x2048\> "${img%.png}.jpg"
done
```

### 任务提交优化

**分批处理**
- 每批 10-20 个任务
- 避免一次提交过多任务

**延迟设置**
- 快速提交: `2.0` 秒
- 稳定提交: `3.0-5.0` 秒

## 🔍 查询和下载

### 查询任务状态

使用 `GrokQueryVideo` 或 `Veo3QueryVideo` 节点：

1. 读取 `tasks.json` 获取 task_id
2. 使用查询节点查询状态
3. 获取视频 URL

### 批量下载视频

```bash
# 从 tasks.json 提取视频 URL
cat ./output/grok_local_batch/tasks.json | jq -r '.[].video_url' > urls.txt

# 批量下载
while read url; do
    wget "$url" -P ./videos/
done < urls.txt
```

## ⚠️ 注意事项

### 图片要求

- **格式**: 常见图片格式（PNG, JPG, WEBP等）
- **大小**: 建议不超过 10MB
- **分辨率**: 建议 512x512 到 2048x2048
- **内容**: 清晰、主体明确

### API 限制

- **并发限制**: 根据 API 配额
- **文件大小**: 上传图片不超过 10MB
- **请求频率**: 遵守 API 速率限制

### 存储空间

- 上传的图片会占用图床空间
- 生成的视频会占用 API 存储
- 定期清理不需要的文件

## 📚 相关文档

- [Grok 批量工作流指南](./GROK_BATCH_WORKFLOW_GUIDE.md)
- [Veo3 批量工作流指南](./VEO3_BATCH_WORKFLOW_GUIDE.md)
- [主文档](../README.md)

## 🆕 更新日志

### 2026-03-10
- ✨ 新增本地图片批量上传节点
- ✨ 新增图片URL转批量任务节点（Grok/Veo3）
- 📦 创建 Grok 本地图片批量工作流
- 📦 创建 Veo3 本地图片批量工作流
- 📝 完整使用指南和示例

## ❓ 常见问题

### Q1: 支持哪些图片格式？
A: PNG, JPG, JPEG, WEBP, BMP, GIF

### Q2: 一次最多可以处理多少张图片？
A: 默认 100 张，可通过 `max_images` 参数调整（最大 1000）

### Q3: 图片会被永久保存吗？
A: 图片上传到临时图床，有效期根据图床设置（通常 7-30 天）

### Q4: 可以使用不同的提示词吗？
A: 当前版本所有图片使用相同提示词。如需不同提示词，请使用 CSV 批量工作流

### Q5: 上传失败怎么办？
A: 检查网络、图床 API、图片大小。可尝试降低质量或分批处理

### Q6: 如何修改图片目录？
A: 在 "批量上传本地图片" 节点中修改 "图片目录路径" 参数

### Q7: 支持子目录吗？
A: 当前版本只扫描指定目录，不递归子目录

### Q8: 图片顺序如何确定？
A: 按文件名排序（字母/数字顺序）

## 💬 反馈与支持

如有问题或建议，请通过以下方式联系：
- GitHub Issues
- 插件文档
- 社区论坛
