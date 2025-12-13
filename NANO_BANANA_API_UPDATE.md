# Nano Banana API 端点更新说明

## 更新时间
2025-12-13

## 问题描述

原实现使用了自定义的 API 端点格式：
- ❌ `/v1/images/generate` - 不存在
- ❌ `/v1/chat/images` - 不存在

导致 404 错误：
```
HTTP 404 404 Client Error: Not Found for url: https://api.kuai.host/v1/images/generate
```

## 解决方案

更新为 **Google Gemini API 官方格式**。

---

## 新的 API 端点

### 1. 单图生成

**端点**: `POST /v1beta/models/{model}:generateContent`

**示例**: `POST /v1beta/models/gemini-3-pro-image-preview:generateContent`

**请求格式**:
```json
{
  "contents": [
    {
      "parts": [
        {
          "inline_data": {
            "mime_type": "image/jpeg",
            "data": "base64_encoded_image"
          }
        },
        {
          "text": "A futuristic nano banana dish"
        }
      ]
    }
  ],
  "generationConfig": {
    "temperature": 1.0,
    "response_modalities": ["TEXT", "IMAGE"]
  },
  "imageConfig": {
    "aspect_ratio": "1:1",
    "image_size": "2K"
  },
  "tools": [
    {
      "googleSearch": {}
    }
  ]
}
```

**响应格式**:
```json
{
  "candidates": [
    {
      "content": {
        "parts": [
          {
            "inlineData": {
              "mimeType": "image/jpeg",
              "data": "base64_encoded_generated_image"
            }
          },
          {
            "text": "AI 的思考过程文本"
          }
        ]
      },
      "finishReason": "STOP",
      "groundingMetadata": {
        "webSearchQueries": ["search query 1", "search query 2"],
        "groundingChunks": [
          {
            "web": {
              "uri": "https://example.com",
              "title": "Source Title"
            }
          }
        ]
      }
    }
  ]
}
```

### 2. 多轮对话

**端点**: `POST /v1beta/models/{model}:streamGenerateContent`

**示例**: `POST /v1beta/models/gemini-3-pro-image-preview:streamGenerateContent`

**请求格式**:
```json
{
  "contents": [
    {
      "role": "user",
      "parts": [
        {
          "text": "Create a perfume bottle"
        }
      ]
    },
    {
      "role": "model",
      "parts": [
        {
          "inlineData": {
            "mimeType": "image/jpeg",
            "data": "base64_previous_image"
          }
        },
        {
          "text": "Image generated"
        }
      ]
    },
    {
      "role": "user",
      "parts": [
        {
          "inlineData": {
            "mimeType": "image/jpeg",
            "data": "base64_previous_image"
          }
        },
        {
          "text": "Make it more elegant"
        }
      ]
    }
  ],
  "generationConfig": {
    "temperature": 1.0,
    "response_modalities": ["TEXT", "IMAGE"]
  },
  "imageConfig": {
    "aspect_ratio": "1:1",
    "image_size": "2K"
  }
}
```

**响应格式**: 与单图生成相同

---

## 代码更改

### 1. NanoBananaAIO 节点

#### 端点更改
```python
# 之前
endpoint = api_base.rstrip("/") + "/v1/images/generate"

# 现在
endpoint = api_base.rstrip("/") + f"/v1beta/models/{model_name}:generateContent"
```

#### 请求格式更改
```python
# 之前（自定义格式）
payload = {
    "model": model_name,
    "prompt": prompt,
    "reference_images": reference_images_base64,
    ...
}

# 现在（Gemini API 格式）
payload = {
    "contents": [
        {
            "parts": [
                {"inline_data": {"mime_type": "image/jpeg", "data": img_base64}},
                {"text": prompt}
            ]
        }
    ],
    "generationConfig": {...},
    "imageConfig": {...},
    "tools": [{"googleSearch": {}}]  # 如果启用搜索
}
```

#### 响应解析更改
```python
# 之前（自定义格式）
image_base64 = data.get("image_base64")
thinking = data.get("thinking")
grounding_sources = data.get("grounding_sources")

# 现在（Gemini API 格式）
candidates = data.get("candidates", [])
candidate = candidates[0]
parts = candidate.get("content", {}).get("parts", [])

for part in parts:
    if "inlineData" in part:
        image_base64 = part["inlineData"]["data"]
    elif "text" in part:
        thinking += part["text"]

grounding_metadata = candidate.get("groundingMetadata", {})
grounding_sources = self._extract_grounding_info(grounding_metadata, thinking)
```

### 2. NanoBananaMultiTurnChat 节点

#### 端点更改
```python
# 之前
endpoint = api_base.rstrip("/") + "/v1/chat/images"

# 现在
endpoint = api_base.rstrip("/") + f"/v1beta/models/{model_name}:streamGenerateContent"
```

#### 请求格式更改
```python
# 之前（自定义格式）
payload = {
    "model": model_name,
    "messages": [
        {"role": "user", "content": "...", "image_base64": "..."},
        {"role": "assistant", "content": "...", "image_base64": "..."}
    ],
    ...
}

# 现在（Gemini API 格式）
payload = {
    "contents": [
        {
            "role": "user",
            "parts": [
                {"inline_data": {"mime_type": "image/jpeg", "data": "..."}},
                {"text": "..."}
            ]
        },
        {
            "role": "model",  # Gemini 使用 "model" 而不是 "assistant"
            "parts": [
                {"inline_data": {"mime_type": "image/jpeg", "data": "..."}},
                {"text": "..."}
            ]
        }
    ],
    "generationConfig": {...},
    "imageConfig": {...}
}
```

#### 对话历史保存更改
```python
# 之前
self.conversation_history.append({
    "role": "assistant",
    "content": response_text,
    "image_base64": image_base64
})

# 现在
self.conversation_history.append({
    "role": "model",  # Gemini 使用 "model"
    "content": response_text,
    "image_base64": image_base64
})
```

---

## Grounding 信息提取

新增 `_extract_grounding_info` 方法来提取 Gemini API 的 grounding 元数据：

```python
def _extract_grounding_info(self, grounding_metadata, text_content):
    """提取 grounding 信息"""
    if not grounding_metadata:
        return text_content

    lines = [text_content, "\n\n----\n## Grounding Sources\n"]

    # 提取搜索查询
    web_search_queries = grounding_metadata.get("webSearchQueries", [])
    if web_search_queries:
        lines.append(f"\n**Web Search Queries:** {', '.join(web_search_queries)}\n")

    # 提取 grounding chunks
    grounding_chunks = grounding_metadata.get("groundingChunks", [])
    if grounding_chunks:
        lines.append("\n### Sources\n")
        for i, chunk in enumerate(grounding_chunks, start=1):
            web = chunk.get("web", {})
            uri = web.get("uri", "")
            title = web.get("title", "Source")
            lines.append(f"{i}. [{title}]({uri})\n")

    return "".join(lines)
```

---

## 后端实现要求

kuai.host 后端需要实现以下功能：

### 1. 端点代理

将 Gemini API 格式的请求代理到 Google Gemini API：

```
客户端请求:
POST https://api.kuai.host/v1beta/models/gemini-3-pro-image-preview:generateContent

后端处理:
1. 验证 API Key
2. 解析请求 payload
3. 转发到 Google Gemini API
4. 返回响应
```

### 2. 认证处理

```python
# 客户端发送
headers = {
    "Authorization": "Bearer kuai_api_key",
    "Content-Type": "application/json"
}

# 后端转换
headers = {
    "Authorization": "Bearer google_api_key",  # 或使用 Vertex AI 认证
    "Content-Type": "application/json"
}
```

### 3. 响应格式保持

后端应该直接返回 Gemini API 的原始响应，不需要额外处理。

---

## 测试验证

### 测试 1: 基础文生图

```bash
curl -X POST https://api.kuai.host/v1beta/models/gemini-3-pro-image-preview:generateContent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "parts": [{"text": "A futuristic nano banana dish"}]
    }],
    "generationConfig": {
      "temperature": 1.0,
      "response_modalities": ["TEXT", "IMAGE"]
    },
    "imageConfig": {
      "aspect_ratio": "1:1",
      "image_size": "2K"
    }
  }'
```

### 测试 2: 图生图

```bash
curl -X POST https://api.kuai.host/v1beta/models/gemini-3-pro-image-preview:generateContent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "parts": [
        {
          "inline_data": {
            "mime_type": "image/jpeg",
            "data": "BASE64_ENCODED_IMAGE"
          }
        },
        {"text": "Make this image more vibrant"}
      ]
    }],
    "generationConfig": {
      "temperature": 1.0,
      "response_modalities": ["TEXT", "IMAGE"]
    },
    "imageConfig": {
      "aspect_ratio": "1:1",
      "image_size": "2K"
    }
  }'
```

### 测试 3: 搜索增强

```bash
curl -X POST https://api.kuai.host/v1beta/models/gemini-3-pro-image-preview:generateContent \
  -H "Authorization": Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "parts": [{"text": "Create an image of the current weather in Tokyo"}]
    }],
    "generationConfig": {
      "temperature": 1.0,
      "response_modalities": ["TEXT", "IMAGE"]
    },
    "imageConfig": {
      "aspect_ratio": "1:1",
      "image_size": "2K"
    },
    "tools": [{"googleSearch": {}}]
  }'
```

---

## 兼容性说明

### 与原版 Nano Banana 的兼容性

✅ **完全兼容** - 使用相同的 Gemini API 格式

### 与现有节点的兼容性

✅ **无影响** - Sora2 和 Veo3 节点继续使用 `/v1/video/create` 端点

---

## 参考文档

- [Google Gemini API 文档](https://ai.google.dev/api/rest)
- [Gemini Image Generation](https://ai.google.dev/gemini-api/docs/image-generation)
- [Gemini Grounding](https://ai.google.dev/gemini-api/docs/grounding)

---

## 总结

### 关键变更

1. ✅ 端点格式改为 Gemini API 标准格式
2. ✅ 请求 payload 改为 Gemini API 格式
3. ✅ 响应解析改为 Gemini API 格式
4. ✅ 添加 grounding 信息提取
5. ✅ 多轮对话使用 "model" 角色而不是 "assistant"

### 优势

1. ✅ 使用官方 API 格式，更标准
2. ✅ 后端实现更简单（直接代理）
3. ✅ 与原版 Nano Banana 完全兼容
4. ✅ 支持完整的 Gemini 功能

### 下一步

1. 后端实现 Gemini API 代理
2. 测试所有功能
3. 更新 API_SPECIFICATION.md 文档

---

**更新完成时间**: 2025-12-13
**版本**: 2.0
