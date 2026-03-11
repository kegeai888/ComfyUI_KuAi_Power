# CSV批量读取器使用指南

## 📋 节点概述

**CSV批量读取器**（CSVBatchReader）是 ComfyUI_KuAi_Power 插件的核心工具节点，用于从 CSV 文件中读取批量任务数据，并将其传递给下游的批量处理器节点（如 Grok、Veo3 并发处理器）。

**节点位置**: `KuAi/配套能力` 分类

**主要功能**:
- 支持多种文件输入方式（拖放上传、下拉选择、路径输入）
- 自动解析 CSV 文件并转换为 JSON 格式
- 智能处理文件编码（UTF-8 with BOM）
- 提供详细的错误提示和解决方案

---

## 📤 文件上传的三种方式

### 方式1：拖放上传（推荐）⭐

这是最简单、最直观的方式，适合大多数用户。

**操作步骤**:
1. 在 ComfyUI 中打开工作流
2. 找到"📂 CSV批量读取器"节点
3. 将 CSV 文件从电脑文件管理器**拖放**到节点的"CSV文件"参数框
4. 文件会自动上传到 `ComfyUI/input/` 目录
5. 上传成功后，文件名会出现在下拉列表中

**优点**:
- ✅ 操作简单，无需手动复制文件
- ✅ 跨平台兼容（Windows/Mac/Linux）
- ✅ 自动管理文件路径
- ✅ 支持即时刷新

**提示**:
- 拖放时确保鼠标指针在"CSV文件"参数框内
- 如果上传后没有立即显示，右键节点选择"Reload Node"刷新

---

### 方式2：从下拉列表选择

适合使用已经上传过的 CSV 文件。

**操作步骤**:
1. 点击"CSV文件"参数的下拉箭头
2. 从列表中选择之前上传的 CSV 文件
3. 执行工作流

**文件来源**:
- 通过方式1拖放上传的文件
- 手动复制到 `ComfyUI/input/` 目录的文件

**提示**:
- 下拉列表只显示 `.csv` 扩展名的文件
- 如果看不到新文件，尝试刷新节点或重启 ComfyUI

---

### 方式3：手动输入路径（高级用户）

适合需要使用特定路径的 CSV 文件，或者文件不在 `input/` 目录的情况。

**操作步骤**:
1. 在"CSV路径"参数中输入完整的文件路径
2. 支持绝对路径和相对路径
3. 执行工作流

**路径示例**:
```
# 绝对路径（Windows）
C:\Users\YourName\Documents\my_tasks.csv

# 绝对路径（Mac/Linux）
/home/username/documents/my_tasks.csv

# 相对路径（相对于 ComfyUI 根目录）
examples/veo3_text2video_batch.csv
```

**提示**:
- Windows 路径可以使用反斜杠 `\` 或正斜杠 `/`
- 相对路径会自动尝试从 `input/` 目录查找

---

## 📊 CSV 文件格式要求

### 基本要求

1. **文件编码**: 必须使用 **UTF-8** 编码
   - 支持 UTF-8 with BOM
   - 如果遇到编码错误，用文本编辑器重新保存为 UTF-8

2. **文件扩展名**: 必须是 `.csv`

3. **文件结构**:
   - 第一行必须是列标题（字段名）
   - 后续行是数据行
   - 空行会被自动跳过

### CSV 列说明

不同的批量处理器需要不同的列，但通常包括：

**通用列**:
- `prompt`: 生成提示词（必需）
- `output_prefix`: 输出文件名前缀（可选）

**Veo3 专用列**:
- `model`: 模型名称（如 `veo3.1`）
- `duration`: 视频时长（10/15/25秒）
- `orientation`: 方向（`portrait`/`landscape`）
- `image_1`: 参考图片URL（可选）

**Grok 专用列**:
- `model`: 模型名称（如 `grok-video-1.5`）
- `duration`: 视频时长（10秒）
- `orientation`: 方向（`portrait`/`landscape`）
- `image_1`, `image_2`, `image_3`: 参考图片URL（可选）

### 示例 CSV 文件

**基础示例**:
```csv
prompt,output_prefix
"一只可爱的小猫在玩毛线球",cat_video_1
"日落时分的海滩风景",beach_sunset
"城市夜景延时摄影",city_night
```

**高级示例（Veo3）**:
```csv
prompt,model,duration,orientation,output_prefix
"科技感十足的产品展示",veo3.1,10,landscape,product_demo
"时尚服装走秀",veo3.1,15,portrait,fashion_show
"美食制作过程",veo3.1,25,landscape,cooking_tutorial
```

---

## 🔄 数据流说明

CSV批量读取器的输出是 **JSON 格式的字符串**，包含所有任务数据：

```
CSV文件 → CSVBatchReader → JSON字符串 → 并发处理器 → 批量生成
```

**输出格式示例**:
```json
[
  {
    "prompt": "一只可爱的小猫",
    "output_prefix": "cat_video_1",
    "_row_number": 2
  },
  {
    "prompt": "日落时分的海滩",
    "output_prefix": "beach_sunset",
    "_row_number": 3
  }
]
```

**注意**: `_row_number` 字段会自动添加，用于调试和错误追踪。

---

## ❓ 常见问题解答

### Q1: 上传文件后看不到文件名？

**解决方法**:
1. 右键点击节点，选择"Reload Node"刷新
2. 检查文件是否成功上传到 `ComfyUI/input/` 目录
3. 确认文件扩展名是 `.csv`（不是 `.txt` 或其他）

### Q2: 提示"CSV 文件编码错误"？

**原因**: 文件不是 UTF-8 编码

**解决方法**:
1. 用文本编辑器（如 Notepad++、VS Code）打开 CSV 文件
2. 选择"另存为"或"Save As"
3. 在编码选项中选择"UTF-8"或"UTF-8 with BOM"
4. 保存后重新上传

**常见编码问题**:
- Excel 默认保存为 GBK/GB2312（中文 Windows）
- 需要手动转换为 UTF-8

### Q3: 提示"CSV 文件中没有有效的任务数据"？

**可能原因**:
1. CSV 文件只有标题行，没有数据行
2. 所有数据行都是空行
3. 数据行的所有单元格都是空白

**解决方法**:
- 检查 CSV 文件内容，确保至少有一行有效数据
- 删除多余的空行

### Q4: 提示词包含逗号怎么办？

**解决方法**: 用双引号包裹整个提示词

**示例**:
```csv
prompt,output_prefix
"一只小猫，正在玩毛线球，非常可爱",cat_video
```

### Q5: 如何在 Excel 中编辑 CSV？

**步骤**:
1. 用 Excel 打开 CSV 文件
2. 编辑内容
3. **重要**: 另存为时选择"CSV UTF-8（逗号分隔）(.csv)"
4. 不要选择普通的"CSV（逗号分隔）"，否则会丢失 UTF-8 编码

### Q6: 可以使用网络路径或云盘路径吗？

**答案**:
- ✅ 支持本地网络路径（如 `\\server\share\file.csv`）
- ❌ 不支持云盘同步路径（可能导致文件锁定）
- 建议先将文件复制到本地，再上传

---

## 🛠️ 故障排查指南

### 问题：节点执行失败

**检查清单**:
1. ✅ CSV 文件是否存在且路径正确
2. ✅ 文件编码是否为 UTF-8
3. ✅ CSV 格式是否正确（有标题行和数据行）
4. ✅ 必需的列是否存在（如 `prompt`）
5. ✅ 文件是否被其他程序占用（如 Excel）

### 问题：并发处理器报错

**可能原因**:
- CSV 列名与处理器期望的不匹配
- 数据格式不正确（如时长应该是数字）

**解决方法**:
- 参考对应处理器的文档，检查 CSV 列名
- 使用插件提供的示例 CSV 文件作为模板

### 问题：文件路径包含中文或空格

**解决方法**:
- ✅ 支持中文路径和文件名
- ✅ 支持包含空格的路径
- 确保使用 UTF-8 编码

---

## 📚 相关资源

### 示例文件

插件提供了多个示例 CSV 文件，位于 `examples/` 目录：

- `veo3_text2video_batch.csv` - Veo3 文生视频批量任务
- `grok_text2video_batch.csv` - Grok 文生视频批量任务
- `veo3_image2video_batch.csv` - Veo3 图生视频批量任务
- `grok_image2video_batch.csv` - Grok 图生视频批量任务

### 工作流文件

完整的批量处理工作流位于 `workflows/` 目录：

- `veo3批量文生视频.json` - Veo3 批量文生视频工作流
- `grok批量文生视频.json` - Grok 批量文生视频工作流

### 相关文档

- [Veo3 并发处理器文档](./VEO3_CONCURRENT_PROCESSOR_GUIDE.md)
- [Grok 并发处理器文档](./GROK_CONCURRENT_PROCESSOR_GUIDE.md)
- [主 README](../README.md)

---

## 💡 最佳实践

1. **使用拖放上传**: 最简单、最可靠的方式
2. **保持文件编码一致**: 始终使用 UTF-8
3. **使用示例文件作为模板**: 避免列名错误
4. **测试小批量**: 先用 2-3 行数据测试，确认无误后再批量处理
5. **备份原始文件**: 在编辑 CSV 前先备份
6. **使用有意义的 output_prefix**: 便于后续管理生成的文件

---

## 🔄 更新日志

- **2025-03-11**: 优化文件上传提示，增强错误信息
- **2025-01-XX**: 初始版本，支持文件上传和路径输入

---

## 📞 获取帮助

如果遇到问题：
1. 查看本指南的"常见问题"和"故障排查"部分
2. 检查 ComfyUI 控制台的 `[CSVBatchReader]` 日志
3. 参考示例文件和工作流
4. 在项目 GitHub 提交 Issue

---

**提示**: 本节点是批量处理工作流的起点，正确配置 CSV 文件是成功批量生成的关键！
