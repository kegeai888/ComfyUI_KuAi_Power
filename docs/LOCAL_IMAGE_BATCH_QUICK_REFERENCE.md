# 本地图片批量生成视频 - 快速参考

## 🚀 3步快速开始

```bash
# 1. 准备图片目录
mkdir -p /root/ComfyUI/input/grok/demo1
cp your_images/*.png /root/ComfyUI/input/grok/demo1/

# 2. 配置 API Key
export KUAI_API_KEY=your_api_key_here

# 3. 加载工作流并执行
# Grok: workflows/grok_local_image2video_batch_workflow.json
# Veo3: workflows/veo3_local_image2video_batch_workflow.json
```

## 📁 目录结构

```
/root/ComfyUI/input/
├── grok/demo1/     # Grok 图片目录
│   ├── 1.png
│   ├── 2.jpg
│   └── 3.png
└── veo3/demo1/     # Veo3 图片目录
    ├── 1.jpg
    ├── 2.jpg
    └── 3.jpg
```

## 🎛️ 工作流节点

### Grok 工作流
```
📤 批量上传本地图片
  ↓
🔄 图片URL转Grok批量任务
  ↓
📦 Grok批量处理器
  ↓
📊 结果显示
```

### Veo3 工作流
```
📤 批量上传本地图片
  ↓
🔄 图片URL转Veo3批量任务
  ↓
📦 Veo3批量处理器
  ↓
📊 结果显示
```

## ⚙️ 关键参数

### 批量上传节点
| 参数 | 推荐值 | 说明 |
|------|--------|------|
| 图片目录路径 | `/root/ComfyUI/input/grok/demo1` | 完整路径 |
| 格式 | `jpeg` | 文件小，速度快 |
| 质量 | `90` | 平衡质量和大小 |
| 最大数量 | `100` | 根据需要调整 |

### URL转任务节点（Grok）
| 参数 | 推荐值 | 说明 |
|------|--------|------|
| 提示词模板 | "将这张图片转换为视频..." | 所有图片共用 |
| 模型 | `grok-video-3 (6秒)` | 快速预览 |
| 宽高比 | `3:2` | 横屏 |
| 分辨率 | `1080P` | 高清 |
| 提示词增强 | `true` | 推荐启用 |

### URL转任务节点（Veo3）
| 参数 | 推荐值 | 说明 |
|------|--------|------|
| 模型 | `veo3.1` | 标准模型 |
| 时长 | `6` | 6秒视频 |
| 宽高比 | `16:9` | 横屏 |
| 启用超分 | `false` | pro模型可用 |

### 批量处理器
| 参数 | 推荐值 | 说明 |
|------|--------|------|
| 等待完成 | `false` | 快速提交 |
| 任务间延迟 | `2.0` | 秒 |
| 输出目录 | `./output/xxx_batch` | 自定义 |

## 📝 提示词模板示例

### 通用
```
将这张图片转换为视频，添加自然的镜头运动和电影级灯光效果
```

### 产品展示
```
产品360度旋转展示，专业灯光，高端质感
```

### 风景动画
```
风景延时摄影效果，云朵流动，光影变化，4K画质
```

### 人物动画
```
人物微动效果，自然呼吸，眼神交流，电影级质感
```

## 🎯 支持的图片格式

`.png` `.jpg` `.jpeg` `.webp` `.bmp` `.gif`

## 📊 输出文件

```
./output/grok_local_batch/
├── tasks.json              # 所有任务信息
├── grok_local_1_xxx.json   # 任务1详情
├── grok_local_2_xxx.json   # 任务2详情
└── ...
```

## 🔍 查询任务

```bash
# 查看任务列表
cat ./output/grok_local_batch/tasks.json | jq '.[].task_id'

# 提取视频URL
cat ./output/grok_local_batch/tasks.json | jq -r '.[].video_url'
```

## ⚠️ 注意事项

- 图片大小建议不超过 10MB
- 分辨率建议 512x512 到 2048x2048
- 图片按文件名排序处理
- 当前版本所有图片使用相同提示词
- 上传到临时图床，有效期 7-30 天

## 🆚 对比：本地图片 vs CSV

| 特性 | 本地图片工作流 | CSV工作流 |
|------|---------------|-----------|
| 图片来源 | 本地目录 | URL（需手动上传） |
| 提示词 | 统一模板 | 每个任务独立 |
| 配置方式 | 节点参数 | CSV文件 |
| 适用场景 | 快速批量处理 | 精细控制 |
| 灵活性 | 中等 | 高 |
| 上手难度 | 简单 | 中等 |

## 💡 使用技巧

1. **分批处理**: 每批 10-20 张图片
2. **质量优先**: 使用 `quality: 90` 确保效果
3. **快速提交**: `wait_for_completion: false`
4. **目录组织**: 按项目/类型分类
5. **提示词优化**: 根据内容类型调整

## 📚 完整文档

详见: `docs/LOCAL_IMAGE_BATCH_WORKFLOW_GUIDE.md`

## 🔗 相关工作流

- Grok CSV批量: `workflows/grok_image2video_batch_workflow.json`
- Veo3 CSV批量: `workflows/veo3_image2video_batch_workflow.json`
- Grok 本地批量: `workflows/grok_local_image2video_batch_workflow.json`
- Veo3 本地批量: `workflows/veo3_local_image2video_batch_workflow.json`
