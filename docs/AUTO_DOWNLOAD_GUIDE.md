# 批量处理器自动下载功能使用指南

## 📋 功能概述

Grok 和 Veo3 批量处理器现已支持**自动下载视频**功能。当任务完成后，系统会自动将生成的视频下载到本地指定目录，无需手动下载。

## ✨ 新增参数

### Grok CSV 并发批量处理器

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `save_dir` | STRING | `output/grok` | 视频保存目录（相对于 ComfyUI 根目录） |
| `max_wait_time` | INT | `1200` | 单个任务最大等待时间（秒） |
| `poll_interval` | INT | `10` | 轮询间隔（秒） |
| `download_timeout` | INT | `180` | 单个视频下载超时时间（秒） |

### Veo3 CSV 并发批量处理器

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `save_dir` | STRING | `output/veo3` | 视频保存目录（相对于 ComfyUI 根目录） |
| `max_wait_time` | INT | `1200` | 单个任务最大等待时间（秒） |
| `poll_interval` | INT | `15` | 轮询间隔（秒） |
| `download_timeout` | INT | `180` | 单个视频下载超时时间（秒） |

## 🚀 使用方法

### 基本用法

1. **配置单任务最大等待时间**
   ```
   max_wait_time: 1200
   ```

2. **配置轮询间隔**
   ```
   poll_interval: 10  # Veo3 默认 15
   ```

3. **配置保存目录**（可选）
   ```
   save_dir: output/grok  # 或 output/veo3
   ```

4. **执行工作流**
   - 系统会自动轮询任务状态
   - 任务完成后自动下载视频
   - 视频保存到指定目录

### 工作流程

```
提交任务
    ↓
轮询查询状态（每 10-15 秒）
    ↓
任务完成
    ↓
自动下载视频
    ↓
保存到本地目录
    ↓
更新任务信息（添加 local_path）
```

## 📁 输出目录结构

### Grok 视频

```
/root/ComfyUI/
└── output/
    └── grok/
        ├── task_1_abc123.mp4
        ├── task_2_def456.mp4
        └── task_3_ghi789.mp4
```

### Veo3 视频

```
/root/ComfyUI/
└── output/
    └── veo3/
        ├── task_1_abc123.mp4
        ├── task_2_def456.mp4
        └── task_3_ghi789.mp4
```

### 任务信息文件

```
./output/grok_batch/
├── tasks.json                    # 所有任务列表
├── task_1_xxx.json              # 任务1详情（包含 local_path）
├── task_2_xxx.json              # 任务2详情
└── task_3_xxx.json              # 任务3详情
```

## 💡 使用场景

### 场景 1：仅提交任务（不等待）

⚠️ 当前并发批量处理器会执行“提交 → 轮询 → 下载”完整闭环，不提供仅提交不等待模式。

**替代方案**:
- 通过创建节点 + 查询节点自行编排“提交后稍后查询”流程
- 或拆分任务批次，降低单次等待压力

### 场景 2：等待并自动下载（推荐）

**配置**:
```
save_dir: output/grok
max_wait_time: 1200
poll_interval: 10
download_timeout: 180
```

**行为**:
- 提交任务并等待完成
- 自动下载视频到本地
- 保存相对路径到任务信息
- 适合中小批量任务

### 场景 3：等待但不落盘（仅查看 URL）

⚠️ 当前并发批量处理器默认在任务完成后自动下载并保存本地文件。

如果只需要 URL，可使用查询节点工作流按需获取，不经过并发处理器下载闭环。

## 📊 任务信息示例

### 启用自动下载后的任务信息

```json
{
  "task_id": "task_abc123",
  "prompt": "一只可爱的小猫在花园里玩球",
  "status": "completed",
  "video_url": "https://cdn.example.com/video.mp4",
  "local_path": "output/grok/task_1_abc123.mp4",
  "created_at": "2026-03-10 14:30:00",
  "completed_at": "2026-03-10 14:35:00"
}
```

## ⚙️ 高级配置

### 自定义保存目录

```
save_dir: output/my_videos/grok
```

### 调整下载超时

```
download_timeout: 300  # 5分钟
```

### 批量处理配置示例

```
# Grok CSV 并发批量处理器配置
save_dir: output/grok
batch_size: 10
max_wait_time: 1200
poll_interval: 10
download_timeout: 180
```

## 🔍 日志输出

### 启用自动下载时的日志

```
[GrokCSVConcurrent] 共 3 个任务，每批 3 路并发
[GrokCSVConcurrent] 保存目录: output/grok
[GrokCSVConcurrent] 会话ID: grok_1741795200
============================================================

[1/3] 处理任务 (行 2)
  提示词: 一只可爱的小猫在花园里玩球...
  任务ID: task_abc123
  状态: pending
  等待视频生成完成...
  进行中... 已等待 10/1200 秒
  进行中... 已等待 20/1200 秒
  ✓ 视频生成完成！
  视频URL: https://cdn.example.com/video.mp4
  开始下载视频...
  下载中: https://cdn.example.com/video.mp4
  ✓ 视频已保存: output/grok/task_1_abc123.mp4
✓ 任务 1 完成
```

## ⚠️ 注意事项

### 网络要求

- 需要稳定的网络连接
- 下载大文件可能需要较长时间
- 建议设置合理的 `download_timeout`

### 存储空间

- 确保有足够的磁盘空间
- 视频文件通常 5-50MB
- 批量下载前检查可用空间

### 性能影响

- 下载会增加总处理时间
- 建议结合 `batch_size` 与 `poll_interval` 做性能平衡
- 大批量任务考虑分批处理

### 错误处理

- 下载失败不会中断批量处理
- 失败的任务不会有 `local_path` 字段
- 检查日志了解失败原因

## 🆚 对比：自动下载 vs 手动下载

| 特性 | 自动下载 | 手动下载 |
|------|---------|---------|
| **便利性** | 高（全自动） | 低（需手动操作） |
| **处理时间** | 长（等待+下载） | 短（仅提交） |
| **适用场景** | 中小批量 | 大批量 |
| **网络要求** | 持续稳定 | 灵活 |
| **存储管理** | 自动保存 | 按需下载 |

## 💻 代码示例

### Python 脚本调用

```python
from nodes.Grok.csv_concurrent_processor import GrokCSVConcurrentProcessor
import json

# 创建处理器
processor = GrokCSVConcurrentProcessor()

# 准备任务
tasks = [
    {
        "prompt": "一只可爱的小猫",
        "model": "grok-video-3 (6秒)",
        "aspect_ratio": "3:2",
        "size": "1080P"
    }
]

# 执行批量处理（提交 + 轮询 + 自动下载）
report, abs_save_dir, detailed_json = processor.process(
    batch_tasks=json.dumps(tasks),
    api_key="your_api_key",
    save_dir="output/grok",
    batch_size=10,
    default_model="grok-video-3 (6秒)",
    default_aspect_ratio="3:2",
    default_size="720P",
    default_enhance_prompt=True,
    max_wait_time=1200,
    poll_interval=10,
    download_timeout=180,
)

print(report)
print(abs_save_dir)
print(detailed_json)
```

## 📚 相关文档

- [Grok 批量工作流指南](./GROK_BATCH_WORKFLOW_GUIDE.md)
- [Veo3 批量工作流指南](./VEO3_BATCH_WORKFLOW_GUIDE.md)
- [本地图片批量处理指南](./LOCAL_IMAGE_BATCH_WORKFLOW_GUIDE.md)

## 🆕 更新日志

### 2026-03-10
- ✨ Grok/Veo3 CSV 并发批量处理器支持任务完成后自动下载
- 📝 统一文档参数口径：`save_dir` / `max_wait_time` / `poll_interval` / `download_timeout`
- 📝 更新 Python 示例为 `GrokCSVConcurrentProcessor.process(...)`

## ❓ 常见问题

### Q1: 自动下载会影响性能吗？
A: 会增加总处理时间，但提供了便利性。大批量任务建议禁用自动下载。

### Q2: 下载失败会怎样？
A: 不会中断批量处理，失败的任务不会有 `local_path` 字段。

### Q3: 可以修改保存目录吗？
A: 可以，通过 `save_dir` 参数自定义。

### Q4: 视频文件名如何生成？
A: 格式：`{output_prefix}_{url_hash}.mp4`

### Q5: 如何只获取 URL 不下载？
A: 并发处理器默认会自动下载。若只需要 URL，可改用查询节点工作流，不使用并发处理器下载闭环。

### Q6: 下载超时怎么办？
A: 增加 `download_timeout` 值或检查网络连接。

### Q7: 可以并发下载吗？
A: 当前版本串行下载，未来可能支持并发。

### Q8: 如何查看下载进度？
A: 查看 ComfyUI 控制台日志。

## 💬 反馈与支持

如有问题或建议，请通过以下方式联系：
- GitHub Issues
- 插件文档
- 社区论坛
