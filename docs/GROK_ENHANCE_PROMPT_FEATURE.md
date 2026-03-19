# Grok 提示词增强功能

## 🎯 功能概述

Grok 视频生成节点现已支持**提示词增强**功能，可自动优化并翻译中文提示词为英文，显著提升视频生成质量。

## ✨ 主要特性

- **自动优化**：智能优化提示词结构和描述
- **中英翻译**：自动将中文提示词翻译为英文
- **默认启用**：默认开启，无需额外配置
- **灵活控制**：可在节点界面或 CSV 文件中控制开关
- **全面支持**：所有 Grok 节点和批量处理均支持

## 📦 支持的节点

所有 Grok 视频生成节点均已支持提示词增强：

1. **🤖 Grok 创建视频** (`GrokCreateVideo`)
2. **🤖 Grok 图生视频** (`GrokImage2Video`)
3. **🤖 Grok 文生视频** (`GrokText2Video`)
4. **⚡ Grok 创建视频（一键）** (`GrokCreateAndWait`)
5. **⚡ Grok 图生视频（一键）** (`GrokImage2VideoAndWait`)
6. **⚡ Grok 文生视频（一键）** (`GrokText2VideoAndWait`)
7. **📦 Grok CSV 并发批量处理器** (`GrokCSVConcurrentProcessor`)

## 🎛️ 使用方法

### 方法 1：节点界面控制

在任何 Grok 视频生成节点中，找到 **提示词增强** 参数：

```
提示词增强: ☑️ (默认勾选)
```

- **勾选**：启用提示词增强（推荐）
- **取消勾选**：禁用提示词增强（适用于已优化的英文提示词）

### 方法 2：CSV 批量处理

在 CSV 文件中添加 `enhance_prompt` 列：

```csv
prompt,model,aspect_ratio,size,enhance_prompt,output_prefix
"一只可爱的小猫在花园里玩球",grok-video-3 (6秒),3:2,1080P,true,cat_playing
"A cute cat playing with a ball",grok-video-3 (6秒),3:2,1080P,false,cat_playing_en
```

**支持的值**：
- `true` / `false`
- `1` / `0`
- `yes` / `no`

## 💡 使用建议

### 何时启用提示词增强

✅ **推荐启用**（默认）：
- 使用中文提示词
- 提示词较简单或不够详细
- 希望获得更好的生成效果
- 不确定如何优化提示词

### 何时禁用提示词增强

❌ **可以禁用**：
- 提示词已经是精心优化的英文
- 需要精确控制提示词内容
- 进行 A/B 测试对比

## 📊 效果对比

### 示例 1：中文提示词

**原始提示词**：
```
一只可爱的小猫在阳光明媚的花园里玩彩色球
```

**启用增强后**（自动优化并翻译）：
```
A cute kitten playing with colorful balls in a sunny garden,
soft natural lighting, shallow depth of field, cinematic quality
```

### 示例 2：简单英文提示词

**原始提示词**：
```
cat playing
```

**启用增强后**（自动优化）：
```
A playful cat engaging with toys, dynamic movement,
natural lighting, high quality video
```

## 🔧 技术实现

### API 参数

提示词增强功能通过 API 参数 `enhance_prompt` 控制：

```python
payload = {
    "model": "grok-video-3",
    "prompt": "一只可爱的小猫在花园里玩球",
    "enhance_prompt": True,  # 启用提示词增强
    # ... 其他参数
}
```

### 批量处理实现

批量处理器自动解析 CSV 中的 `enhance_prompt` 列：

```python
# 解析 enhance_prompt（默认 true）
enhance_prompt = task.get("enhance_prompt", "true").strip().lower() in ["true", "1", "yes"]

# 传递给创建节点
result = self.creator.create(
    prompt=prompt,
    enhance_prompt=enhance_prompt,
    # ... 其他参数
)
```

## 📝 CSV 文件格式

### 文生视频

```csv
prompt,model,aspect_ratio,size,enhance_prompt,output_prefix
"中文提示词",grok-video-3 (6秒),3:2,1080P,true,video_001
"English prompt",grok-video-3 (6秒),3:2,1080P,false,video_002
```

### 图生视频

```csv
prompt,model,aspect_ratio,size,enhance_prompt,image_urls,output_prefix
"中文提示词",grok-video-3 (6秒),3:2,1080P,true,https://example.com/img.jpg,video_001
"English prompt",grok-video-3 (6秒),3:2,1080P,false,https://example.com/img.jpg,video_002
```

## 🎓 最佳实践

### 1. 中文用户

```csv
prompt,enhance_prompt
"一只可爱的小猫在花园里玩球，慢动作，电影级灯光",true
"夕阳下的城市天际线，延时摄影，4K画质",true
```

### 2. 英文用户（已优化提示词）

```csv
prompt,enhance_prompt
"A cinematic shot of a cat playing with a colorful ball in a sunlit garden, slow motion, professional lighting, 4K quality",false
"Time-lapse of city skyline at golden hour, dramatic clouds, ultra HD",false
```

### 3. 混合使用

```csv
prompt,enhance_prompt
"一只可爱的小猫",true
"A professionally lit studio shot of a cat, shallow depth of field, bokeh background",false
```

## 🔍 验证功能

运行验证脚本确认功能正常：

```bash
python test/verify_grok_enhance_prompt.py
```

验证内容：
- ✅ 所有节点包含 enhance_prompt 参数
- ✅ 批量处理器支持 enhance_prompt
- ✅ CSV 示例文件包含 enhance_prompt 列
- ✅ 文档已更新

## 📚 相关文档

- [Grok 批量工作流使用指南](./GROK_BATCH_WORKFLOW_GUIDE.md)
- [Grok 批量工作流快速参考](./GROK_BATCH_QUICK_REFERENCE.md)
- [主文档](../README.md)

## 🆕 更新日志

### 2026-03-10
- ✨ 新增提示词增强功能
- 🎯 所有 Grok 节点支持 enhance_prompt 参数
- 📦 批量处理器完全支持
- 📝 更新所有相关文档和示例
- 🧪 添加功能验证脚本

## ❓ 常见问题

### Q1: 提示词增强会增加生成时间吗？
A: 提示词增强在服务端处理，对生成时间影响极小（通常 < 1 秒）。

### Q2: 可以看到增强后的提示词吗？
A: 部分节点会在返回值中包含增强后的提示词，可通过输出查看。

### Q3: 提示词增强支持哪些语言？
A: 目前主要优化中文到英文的翻译，其他语言也会尝试优化。

### Q4: 如何在批量处理中混合使用？
A: 在 CSV 文件中为每个任务单独设置 `enhance_prompt` 值即可。

### Q5: 提示词增强会改变我的原意吗？
A: 提示词增强会保留原意，同时添加技术性描述（如灯光、画质等）以提升生成质量。如需精确控制，可禁用此功能。

## 💬 反馈与支持

如有问题或建议，请通过以下方式联系：
- GitHub Issues
- 插件文档
- 社区论坛
