# Veo3 批量工作流快速参考

## 🚀 快速开始（3 步）

```bash
# 1. 准备 CSV 文件
cp examples/veo3_text2video_batch.csv ComfyUI/input/

# 2. 配置 API Key
export KUAI_API_KEY=your_api_key_here

# 3. 加载工作流并执行
# 在 ComfyUI 中加载: workflows/veo3_text2video_batch_workflow.json
```

## 📋 CSV 格式速查

### 文生视频
```csv
task_type,prompt,model,aspect_ratio,enhance_prompt,enable_upsample,output_prefix
text2video,"提示词",veo3.1,9:16,true,true,video_001
```

### 图生视频
```csv
task_type,prompt,model,aspect_ratio,enhance_prompt,enable_upsample,image_urls,output_prefix
image2video,"提示词",veo3.1,16:9,true,true,https://example.com/img.jpg,video_001
```

## 🎛️ 模型选择

| 模型 | 特点 | 用途 |
|------|------|------|
| `veo3.1` | 最新最好 | 正式项目 |
| `veo3-fast` | 速度快 | 快速预览 |
| `veo3-pro` | 专业级 | 高质量制作 |
| `veo3.1-4k` | 4K高清 | 高分辨率 |

## 📐 宽高比

| 比例 | 场景 |
|------|------|
| `16:9` | 横屏（YouTube、电视） |
| `9:16` | 竖屏（抖音、快手） |

## ⚙️ 推荐配置

```
wait_for_completion: false  # 快速提交
delay_between_tasks: 2.0    # 任务间隔
enhance_prompt: true        # 提示词增强
enable_upsample: true       # 启用超分
```

## 📁 输出文件

```
./output/veo3_batch/
└── tasks.json  # 包含所有 task_id
```

## 🔍 查询任务

使用 `VeoQueryTask` 节点 + `task_id`

## 💡 核心特性

- ✅ 自动提示词增强和翻译
- ✅ 超分辨率提升质量
- ✅ 支持文生视频和图生视频
- ✅ 多种模型和宽高比选择

## ⚠️ 常见问题

| 问题 | 解决方案 |
|------|---------|
| CSV 读取失败 | 检查 UTF-8 编码 |
| API Key 错误 | 设置环境变量或节点参数 |
| 任务提交慢 | 设置 `wait_for_completion: false` |
| 生成速度慢 | 使用 `veo3-fast` 模型 |

## 📚 完整文档

详见: `docs/VEO3_BATCH_WORKFLOW_GUIDE.md`
