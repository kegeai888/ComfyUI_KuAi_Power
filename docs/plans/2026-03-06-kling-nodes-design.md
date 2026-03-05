# 可灵视频生成节点设计文档

**日期**: 2026-03-06
**作者**: Claude Code
**状态**: 已批准

## 概述

为 ComfyUI_KuAi_Power 插件添加可灵（Kling）视频生成功能，包括文生视频和图生视频两种模式，支持单任务和批量处理。

## 需求确认

### 1. 节点分类
- **决策**: 创建新的 `Kling` 分类目录
- **理由**: 可灵和 Sora 是不同的服务，API 结构差异较大，独立管理更清晰

### 2. 功能范围
- **决策**: 常用功能（选项 B）
- **包含功能**:
  - 基础功能: `prompt`, `model_name`, `mode`, `duration`, `aspect_ratio`
  - 常用功能: `negative_prompt`, `cfg_scale`, `multi_shot`, `watermark`
- **不包含**: 高级功能（摄像机控制、声音生成、遮罩等）可后续迭代

### 3. 节点结构
- **决策**: 完整式（选项 C）
- **节点列表**:
  - `KlingText2Video` - 文生视频（创建任务）
  - `KlingImage2Video` - 图生视频（创建任务）
  - `KlingQueryTask` - 查询任务状态
  - `KlingText2VideoAndWait` - 文生视频一键生成
  - `KlingImage2VideoAndWait` - 图生视频一键生成
  - `KlingBatchProcessor` - CSV 批量处理器

### 4. 批量处理
- **决策**: 同步实现（选项 B）
- **理由**: 批量处理是电商视频内容创作的核心场景

### 5. 实现方案
- **决策**: 复用通用工具函数（方案 B）
- **理由**: 减少代码重复，保持一致性，风险可控

## 架构设计

### 目录结构

```
nodes/Kling/
├── __init__.py              # 节点注册
├── kling_utils.py           # 可灵特定工具函数
├── kling.py                 # 核心节点实现
└── batch_processor.py       # CSV 批量处理器
```

### 依赖关系

**复用 Sora2 通用工具**:
- `env_or()` - API key 优先级解析
- `http_headers_json()` - 生成标准 JSON 请求头
- `raise_for_bad_status()` - 统一错误处理

**创建 Kling 特定工具** (`kling_utils.py`):
- `parse_kling_response()` - 解析响应格式（`data.task_id` → `task_id`）
- `KLING_MODELS` - 模型列表常量
- `KLING_ASPECT_RATIOS` - 宽高比列表

### 分类和显示

- **分类**: `KuAi/Kling`
- **Emoji 前缀**: 🎞️（电影胶片，区别于 Sora 的 🎬）

## 核心组件设计

### 1. KlingText2Video（文生视频创建）

**职责**: 创建文生视频任务，返回 task_id

**输入参数**:

必需参数:
- `prompt` (STRING) - 提示词
- `model_name` (下拉) - 模型选择
  - kling-v1
  - kling-v1-6
  - kling-v2-master
  - kling-v2-1-master
  - kling-v2-5-turbo
  - kling-v3
- `mode` (下拉) - 模式
  - std（标准）
  - pro（专家）
- `duration` (下拉) - 时长
  - 5s
  - 10s
- `aspect_ratio` (下拉) - 宽高比
  - 16:9
  - 9:16
  - 1:1

可选参数:
- `negative_prompt` (STRING) - 负面提示词
- `cfg_scale` (FLOAT, 0.0-1.0, 默认 0.5) - 提示词引导强度
- `multi_shot` (BOOLEAN, 默认 False) - 是否多镜头
- `watermark` (BOOLEAN, 默认 False) - 是否添加水印
- `api_key` (STRING) - API 密钥
- `api_base` (STRING, 默认 "https://api.kuai.host")
- `timeout` (INT, 默认 120)

**返回值**:
- `task_id` (STRING) - 任务 ID
- `status` (STRING) - 任务状态
- `created_at` (INT) - 创建时间戳

### 2. KlingImage2Video（图生视频创建）

**职责**: 创建图生视频任务

**输入参数**:

必需参数:
- `image` (STRING) - 图片 URL 或 Base64
- `model_name`, `mode`, `duration` - 同文生视频

可选参数:
- `prompt` (STRING) - 提示词（可选，用于引导生成）
- `image_tail` (STRING) - 尾帧图片 URL 或 Base64
- `negative_prompt`, `cfg_scale`, `multi_shot`, `watermark` - 同文生视频
- `api_key`, `api_base`, `timeout` - 同文生视频

**返回值**: 同文生视频

### 3. KlingQueryTask（查询任务）

**职责**: 查询任务状态，支持轮询等待

**输入参数**:

必需参数:
- `task_id` (STRING) - 任务 ID

可选参数:
- `wait` (BOOLEAN, 默认 True) - 是否等待完成
- `poll_interval_sec` (INT, 默认 15) - 轮询间隔
- `timeout_sec` (INT, 默认 1200) - 总超时时间
- `api_key`, `api_base`

**返回值**:
- `status` (STRING) - 任务状态：submitted, processing, succeed, failed
- `video_url` (STRING) - 视频 URL
- `duration` (STRING) - 实际时长
- `raw_response` (STRING) - 原始响应 JSON

### 4. AndWait 节点

`KlingText2VideoAndWait` 和 `KlingImage2VideoAndWait` 内部组合 Create + Query 逻辑，参数合并，直接返回最终结果。

### 5. KlingBatchProcessor（批量处理器）

**职责**: 从 CSV 读取任务列表，批量创建视频并等待完成

**输入参数**:
- `batch_tasks` (STRING, forceInput) - 来自 CSVBatchReader 的 JSON 任务列表
- `api_key` (STRING) - API 密钥
- `output_dir` (STRING, 默认 "./output/batch") - 输出目录
- `delay_between_tasks` (FLOAT, 默认 2.0) - 任务间延迟（秒）

**返回值**:
- `report` (STRING) - 处理结果报告
- `output_dir` (STRING) - 输出目录路径

## 数据流设计

### 创建任务流程

```
用户输入参数
  ↓
解析 API Key (env_or)
  ↓
构建请求 payload
  ├─ 文生视频: {model_name, prompt, mode, duration, aspect_ratio, ...}
  └─ 图生视频: {model_name, image, mode, duration, ...}
  ↓
POST /kling/v1/videos/text2video (或 image2video)
  ↓
响应格式转换 (parse_kling_response)
  ├─ 可灵格式: {code, message, data: {task_id, task_status, created_at}}
  └─ 统一格式: (task_id, status, created_at)
  ↓
返回给用户
```

### 查询任务流程

```
接收 task_id
  ↓
GET /kling/v1/videos/text2video/{task_id}
  ↓
解析响应
  ├─ status: submitted → 继续轮询
  ├─ status: processing → 继续轮询
  ├─ status: succeed → 提取 video_url，返回
  └─ status: failed → 提取错误信息，抛出异常
  ↓
如果 wait=True，循环轮询直到完成或超时
```

### 响应格式处理

创建 `parse_kling_response()` 函数处理可灵特定的响应格式：

```python
def parse_kling_response(resp_json):
    """解析可灵 API 响应格式

    可灵格式:
    {
      "code": 0,
      "message": "SUCCEED",
      "data": {
        "task_id": "831922345719271433",
        "task_status": "submitted",
        "created_at": 1766374262370
      }
    }

    返回: (task_id, status, created_at)
    """
    if resp_json.get("code") != 0:
        raise RuntimeError(f"API 错误: {resp_json.get('message')}")

    data = resp_json.get("data", {})
    task_id = data.get("task_id", "")
    status = data.get("task_status", "")
    created_at = data.get("created_at", 0)

    return (task_id, status, created_at)
```

### AndWait 节点数据流

```
用户输入 → Create 节点 → 获取 task_id
                ↓
            Query 节点（wait=True）
                ↓
            轮询直到完成
                ↓
            返回最终结果
```

## 错误处理

### 错误处理层次

```
Level 1: HTTP 错误
  ├─ 使用 raise_for_bad_status() 统一处理 4xx/5xx
  └─ 提取响应体中的错误信息

Level 2: 业务错误
  ├─ 检查 response.code != 0
  └─ 抛出 RuntimeError 包含 message 字段

Level 3: 任务失败
  ├─ status == "failed"
  └─ 从 data.task_info 提取失败原因
```

### 具体错误场景

| 场景 | 检测方式 | 处理策略 |
|------|---------|---------|
| API Key 未配置 | `not api_key` | 抛出 "API Key 未配置，请在节点参数或环境变量中设置" |
| HTTP 请求失败 | `status_code >= 400` | 调用 `raise_for_bad_status()`，提取错误详情 |
| 业务逻辑错误 | `code != 0` | 抛出 "API 错误: {message}" |
| 任务创建失败 | `task_id` 为空 | 抛出 "创建任务失败: 响应缺少 task_id" |
| 任务执行失败 | `status == "failed"` | 提取 `task_info` 中的错误信息 |
| 轮询超时 | `time.time() > deadline` | 返回 status="timeout"，不抛异常 |
| 视频 URL 缺失 | `status == "succeed" but not video_url` | 抛出 "任务完成但未返回视频 URL" |

### 错误消息设计原则

1. **中文友好**: 所有错误消息使用中文
2. **上下文清晰**: 包含操作类型（创建/查询）和关键参数
3. **可操作性**: 提示用户如何解决问题
4. **保留原始信息**: 在错误消息中包含 API 返回的原始错误

### 轮询超时处理

与 Sora2 保持一致，超时不抛异常，而是返回 `status="timeout"`，让用户可以手动重新查询。

## 批量处理设计

### CSV 格式定义

**通用列**:
- `task_type` (必需) - 任务类型：text2video, image2video
- `prompt` (必需) - 提示词
- `model_name` (可选，默认 kling-v1) - 模型名称
- `mode` (可选，默认 std) - 模式：std, pro
- `duration` (可选，默认 5) - 时长：5, 10
- `aspect_ratio` (可选，默认 16:9) - 宽高比
- `output_prefix` (可选) - 输出文件前缀

**常用功能列**:
- `negative_prompt` (可选) - 负面提示词
- `cfg_scale` (可选，默认 0.5) - CFG 强度
- `multi_shot` (可选，默认 false) - 是否多镜头
- `watermark` (可选，默认 false) - 是否水印

**图生视频专用列**:
- `image` (image2video 必需) - 图片 URL
- `image_tail` (可选) - 尾帧图片 URL

### 批量处理流程

```
CSVBatchReader 读取 CSV
  ↓
解析为 JSON 任务列表
  ↓
KlingBatchProcessor 接收
  ↓
逐个处理任务：
  ├─ 根据 task_type 选择节点（Text2Video 或 Image2Video）
  ├─ 创建任务并等待完成
  ├─ 下载视频到 output_dir
  ├─ 记录成功/失败
  └─ 延迟 delay_between_tasks 秒
  ↓
生成处理报告
  ├─ 总任务数
  ├─ 成功数
  ├─ 失败数
  └─ 失败详情
  ↓
保存 tasks.json 到 output_dir
```

### 示例 CSV 文件

创建 3 个示例文件：

1. **kling_batch_basic.csv** - 基础文生视频
2. **kling_batch_advanced.csv** - 高级功能
3. **kling_batch_image2video.csv** - 图生视频

## 测试策略

### 测试文件结构

```
test/
├── test_kling_nodes.py          # 节点注册和基础功能测试
├── test_kling_batch.py          # 批量处理器测试
└── test_kling_api.py            # API 集成测试（需要真实 API key）
```

### 测试覆盖范围

**test_kling_nodes.py**:
- ✓ 节点注册验证（6个节点都在 NODE_CLASS_MAPPINGS 中）
- ✓ INPUT_TYPES 结构验证
- ✓ INPUT_LABELS 中文标签验证
- ✓ RETURN_TYPES 和 RETURN_NAMES 验证
- ✓ CATEGORY 分类验证（KuAi/Kling）
- ✓ 参数默认值合理性检查

**test_kling_batch.py**:
- ✓ 批量处理器注册验证
- ✓ CSV 格式解析测试（mock 数据）
- ✓ 任务类型路由测试（text2video vs image2video）
- ✓ 错误处理测试（缺少必需参数）

**test_kling_api.py**（需要 API key）:
- ✓ 文生视频创建测试
- ✓ 图生视频创建测试
- ✓ 任务查询测试
- ✓ AndWait 节点端到端测试
- ✓ 批量处理实际执行测试

### 测试执行方式

```bash
# 1. 基础测试（无需 API key）
python test/test_kling_nodes.py

# 2. 批量处理器测试（无需 API key）
python test/test_kling_batch.py

# 3. API 集成测试（需要 API key）
export KUAI_API_KEY=your_key_here
python test/test_kling_api.py

# 4. 完整验证
python diagnose.py  # 验证所有节点加载
```

## 文件清单

### 实现文件

```
nodes/Kling/
├── __init__.py              # 节点注册（~30 行）
├── kling_utils.py           # 工具函数（~100 行）
├── kling.py                 # 核心节点（~300 行）
└── batch_processor.py       # 批量处理器（~200 行）
```

### 测试文件

```
test/
├── test_kling_nodes.py      # 节点测试（~150 行）
├── test_kling_batch.py      # 批量测试（~100 行）
└── test_kling_api.py        # API 测试（~150 行）
```

### 示例和文档

```
examples/
├── kling_batch_basic.csv           # 基础示例
├── kling_batch_advanced.csv        # 高级示例
├── kling_batch_image2video.csv     # 图生视频示例
└── KLING_CSV_GUIDE.md              # CSV 使用指南（~200 行）

docs/
├── KLING_GUIDE.md                  # 节点使用指南（~300 行）
└── plans/
    └── 2026-03-06-kling-nodes-design.md  # 本设计文档
```

### 前端更新

```
web/kuaipower_panel.js       # 添加 Kling 分类映射（1 行）
```

## 技术栈

- Python 3.x
- requests（HTTP 请求）
- json（数据处理）
- time（轮询控制）
- 复用 Sora2 的 kuai_utils

## 预估工作量

- 核心节点实现：~300 行代码
- 工具函数：~100 行代码
- 批量处理器：~200 行代码
- 测试文件：~400 行代码
- 文档和示例：~500 行文本
- **总计**：~1500 行

## API 参考

### 文生视频 API

**端点**: `POST /kling/v1/videos/text2video`

**请求示例**:
```json
{
  "model_name": "kling-v1",
  "prompt": "生成一个海边有一个人跳舞的视频",
  "negative_prompt": "",
  "cfg_scale": 0.5,
  "mode": "std",
  "aspect_ratio": "16:9",
  "duration": "5",
  "multi_shot": false,
  "watermark_info": {
    "enabled": false
  }
}
```

**响应示例**:
```json
{
  "code": 0,
  "message": "SUCCEED",
  "request_id": "603e2a28-fb89-4146-ae33-412d74012a6d",
  "data": {
    "task_id": "831922345719271433",
    "task_status": "submitted",
    "task_info": {},
    "created_at": 1766374262370,
    "updated_at": 1766374262370
  }
}
```

### 图生视频 API

**端点**: `POST /kling/v1/videos/image2video`

**请求示例**:
```json
{
  "model_name": "kling-v1",
  "image": "https://example.com/image.jpg",
  "prompt": "让图片动起来",
  "mode": "std",
  "duration": "5",
  "cfg_scale": 0.5
}
```

**响应格式**: 同文生视频

### 查询任务 API

**端点**: `GET /kling/v1/videos/text2video/{task_id}`

**响应示例**:
```json
{
  "code": 0,
  "message": "SUCCEED",
  "data": {
    "task_id": "831922345719271433",
    "task_status": "succeed",
    "task_info": {
      "video_url": "https://example.com/video.mp4",
      "duration": "5"
    },
    "created_at": 1766374262370,
    "updated_at": 1766374300000
  }
}
```

## 与 Sora2 的差异

| 特性 | Sora2 | Kling |
|------|-------|-------|
| 端点路径 | `/v1/video/create` | `/kling/v1/videos/text2video` |
| 响应格式 | `{id, status}` | `{code, data: {task_id, task_status}}` |
| 查询方式 | `GET /v1/video/query?id=xxx` | `GET /kling/v1/videos/text2video/{id}` |
| 模型参数 | `model` | `model_name` |
| 方向参数 | `orientation` (portrait/landscape) | `aspect_ratio` (16:9/9:16/1:1) |
| 尺寸参数 | `size` (small/large) | `mode` (std/pro) |
| 多镜头 | 不支持 | `multi_shot`, `shot_type`, `multi_prompt` |

## 下一步

1. ✅ 设计文档已完成并批准
2. ⏭️ 创建实现计划（调用 writing-plans 技能）
3. ⏭️ 实现核心节点
4. ⏭️ 实现批量处理器
5. ⏭️ 编写测试
6. ⏭️ 创建文档和示例
7. ⏭️ 更新前端面板
8. ⏭️ 完整测试验证

## 批准记录

- **设计批准日期**: 2026-03-06
- **批准人**: 用户
- **状态**: 已批准，准备进入实现阶段
