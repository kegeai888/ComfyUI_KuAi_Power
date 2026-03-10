# Grok 批量工作流快速参考

## 🚀 快速开始（3 步）

```bash
# 1. 准备 CSV 文件
cp examples/grok_text2video_batch.csv ComfyUI/input/

# 2. 配置 API Key
export KUAI_API_KEY=your_api_key_here

# 3. 加载工作流并执行
# 在 ComfyUI 中加载: workflows/grok_text2video_batch_workflow.json
```

## 📋 CSV 格式速查

### 文生视频
```csv
prompt,model,aspect_ratio,size,enhance_prompt,output_prefix
"提示词",grok-video-3 (6秒),3:2,1080P,true,video_001
```

### 图生视频
```csv
prompt,model,aspect_ratio,size,enhance_prompt,image_urls,output_prefix
"提示词",grok-video-3 (6秒),3:2,1080P,true,https://example.com/img.jpg,video_001
```

**新功能：提示词增强**
- `enhance_prompt`: 自动优化并翻译中文提示词为英文（默认：true）
- 支持值：`true`/`false`、`1`/`0`、`yes`/`no`

## 🎛️ 模型选择

| 模型 | 时长 | 用途 |
|------|------|------|
| `grok-video-3 (6秒)` | 6s | 快速预览 |
| `grok-video-3-10s (10秒)` | 10s | 标准视频 |
| `grok-video-3-15s (15秒)` | 15s | 长视频 |

## 📐 宽高比

| 比例 | 场景 |
|------|------|
| `3:2` | 横屏（YouTube） |
| `2:3` | 竖屏（抖音） |
| `1:1` | 方形（Instagram） |

## ⚙️ 推荐配置

```
wait_for_completion: false  # 快速提交
delay_between_tasks: 2.0    # 任务间隔
output_dir: ./output/grok_batch
```

## 📁 输出文件

```
./output/grok_batch/
└── tasks.json  # 包含所有 task_id
```

## 🔍 查询任务

使用 `GrokQueryVideo` 节点 + `task_id`

## ⚠️ 常见问题

| 问题 | 解决方案 |
|------|---------|
| CSV 读取失败 | 检查 UTF-8 编码 |
| API Key 错误 | 设置环境变量或节点参数 |
| 任务提交慢 | 设置 `wait_for_completion: false` |

## 📚 完整文档

详见: `docs/GROK_BATCH_WORKFLOW_GUIDE.md`
