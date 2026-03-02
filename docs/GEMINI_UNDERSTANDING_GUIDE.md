# Gemini 图片和视频理解节点使用指南

## 概述

本插件提供两个 Gemini 理解节点，用于分析图片和视频内容：
- **Gemini 图片理解**：分析图片内容并返回文本描述
- **Gemini 视频理解**：分析视频内容并返回文本总结

## 节点说明

### 1. Gemini 图片理解 (GeminiImageUnderstanding)

**功能**：接收 ComfyUI IMAGE 输入，通过 Gemini API 理解图片内容，返回文本描述。

**输入参数**：

必需参数：
- **image** (图片): ComfyUI IMAGE 格式的图片输入
- **prompt** (提示词): 对图片的提问，例如"请描述这张图片的内容"
- **api_key** (API密钥): API 密钥（留空使用环境变量 KUAI_API_KEY）

可选参数：
- **api_base** (API地址): API 端点地址（默认：https://api.vectorengine.ai）
- **timeout** (超时时间): 请求超时时间，单位秒（默认：120）

**输出**：
- **理解结果** (STRING): Gemini 返回的文本描述

**使用示例**：
1. 在 ComfyUI 中添加图片加载节点（Load Image）
2. 连接到 Gemini 图片理解节点
3. 设置提示词，例如：
   - "请详细描述这张图片"
   - "这张图片中有什么物体？"
   - "分析这张图片的构图和色彩"
4. 执行工作流，获取文本结果

### 2. Gemini 视频理解 (GeminiVideoUnderstanding)

**功能**：接收视频文件路径，通过 Gemini API 理解视频内容，返回文本总结。

**输入参数**：

必需参数：
- **video_path** (视频路径): 视频文件的完整路径
- **prompt** (提示词): 对视频的提问，例如"请用3句话总结这个视频的内容"
- **api_key** (API密钥): API 密钥（留空使用环境变量 KUAI_API_KEY）

可选参数：
- **api_base** (API地址): API 端点地址（默认：https://api.vectorengine.ai）
- **timeout** (超时时间): 请求超时时间，单位秒（默认：300）

**输出**：
- **理解结果** (STRING): Gemini 返回的文本总结

**使用示例**：
1. 准备视频文件（支持 MP4 格式）
2. 在 ComfyUI 中添加 Gemini 视频理解节点
3. 输入视频文件路径，例如：`/path/to/video.mp4`
4. 设置提示词，例如：
   - "请用3句话总结这个视频的内容"
   - "这个视频的主题是什么？"
   - "描述视频中的主要场景和动作"
5. 执行工作流，获取文本结果

## API 配置

### 方法 1：环境变量（推荐）
```bash
export KUAI_API_KEY=your_api_key_here
```

### 方法 2：节点参数
在节点的 `api_key` 参数中直接填写 API 密钥。

## 工作流示例

### 图片理解工作流
```
Load Image → Gemini 图片理解 → Show Text
```

### 视频理解工作流
```
Gemini 视频理解 → Show Text → Save Text
```

### 组合工作流
```
Load Image → Gemini 图片理解 → Text Combine → AI 文本生成
```

## 技术细节

### API 端点
- 默认端点：`https://api.vectorengine.ai/v1beta/models/gemini-2.5-pro:generateContent`
- 认证方式：通过 URL 查询参数 `key` 传递 API 密钥

### 数据格式
- 图片：转换为 PNG 格式的 base64 编码
- 视频：转换为 MP4 格式的 base64 编码

### 响应处理
节点会自动提取 Gemini API 返回的文本内容，并处理以下情况：
- 多段文本自动合并
- 错误信息友好提示
- 空结果检测

## 常见问题

### Q: 图片理解失败怎么办？
A: 检查以下几点：
1. API 密钥是否正确配置
2. 网络连接是否正常
3. 图片格式是否支持（建议使用常见格式）
4. 增加 timeout 参数值

### Q: 视频理解超时怎么办？
A: 视频理解需要较长时间，建议：
1. 增加 timeout 参数（默认 300 秒）
2. 使用较短的视频文件
3. 确保视频文件格式为 MP4

### Q: 支持哪些图片格式？
A: 节点会自动将输入图片转换为 PNG 格式，因此支持 ComfyUI 所有支持的图片格式。

### Q: 支持哪些视频格式？
A: 当前主要支持 MP4 格式。其他格式可能需要预先转换。

## 更新日志

- 2026-03-02: 初始版本
  - 实现 Gemini 图片理解节点
  - 实现 Gemini 视频理解节点
  - 支持自定义提示词
  - 支持环境变量配置 API 密钥

## 参考资料

- [Gemini 图片理解官方文档](https://ai.google.dev/gemini-api/docs/image-understanding?hl=zh-cn)
- [Gemini 视频理解官方文档](https://ai.google.dev/gemini-api/docs/video-understanding?hl=zh-cn)
