# 2026-04-30 gpt-image-2-all 设计

## 目标
新增一套严格按 API 文档命名和参数约束实现的节点，不影响现有 GPTImage 节点。

范围：
- 新增 `🖼️ gpt-image-2-all生图`
- 新增 `🖼️ gpt-image-2-all编辑图`
- 设计并保存 3 份闭环工作流 JSON 到 `/root/ComfyUI/user/default/workflows`

不做：
- 不复用旧节点名
- 不新增查询远端任务节点
- 不扩展文档外参数
- 不改现有 GPTImage 旧节点行为

## 设计结论

### 节点分类
使用现有分类：`KuAi/GPTImage`

原因：
- 与现有目录 `nodes/GPTImage/` 一致
- 不引入新分类和前端面板额外变更
- 用户仍能清楚区分旧节点和新节点

### 文件位置
- 新节点实现：`nodes/GPTImage/gpt_image_2_all.py`
- 注册更新：`nodes/GPTImage/__init__.py`
- 工作流输出：`/root/ComfyUI/user/default/workflows/`

### API 约束
严格使用：
- endpoint: `POST /v1/images/generations`
- base: 默认 `https://api.kegeai.top`
- 请求字段仅限：`model` `size` `n` `prompt` `image`

严格枚举：
- `model`: 默认 `gpt-image-2-all`
- `size`:
  - `1024x1024`
  - `1536x1024`
  - `1024x1536`
- `image`: 最多 5 张 URL

## 节点设计

### 1. `🖼️ gpt-image-2-all生图`
对应类名：`GPTImage2AllGenerate`

#### 输入
必填：
- `prompt`: STRING, multiline
- `model`: COMBO，默认 `gpt-image-2-all`
- `size`: COMBO，仅 3 个文档值
- `n`: INT
- `api_key`: STRING

可选：
- `api_base`: STRING，默认 `https://api.kegeai.top`
- `timeout`: INT

#### 请求体
```json
{
  "model": "gpt-image-2-all",
  "size": "1024x1024",
  "n": 1,
  "prompt": "..."
}
```

#### 输出
- `IMAGE`：下载结果图并转成 ComfyUI IMAGE
- `STRING`：结果图片 URL，多图换行拼接
- `STRING`：`revised_prompt`，多图换行拼接
- `STRING`：原始响应 JSON

#### 行为约束
- `prompt` 为空直接报错
- `api_key` 缺失直接报错
- 只接受文档允许的 `size`

### 2. `🖼️ gpt-image-2-all编辑图`
对应类名：`GPTImage2AllEdit`

#### 输入
必填：
- `image_url_1`: STRING
- `prompt`: STRING, multiline
- `model`: COMBO，默认 `gpt-image-2-all`
- `size`: COMBO，仅 3 个文档值
- `n`: INT
- `api_key`: STRING

可选：
- `image_url_2`: STRING
- `image_url_3`: STRING
- `image_url_4`: STRING
- `image_url_5`: STRING
- `api_base`: STRING，默认 `https://api.kegeai.top`
- `timeout`: INT

#### 请求体
```json
{
  "model": "gpt-image-2-all",
  "size": "1024x1024",
  "n": 1,
  "prompt": "将他们合并在一起",
  "image": [
    "https://...",
    "https://..."
  ]
}
```

#### 输出
- `IMAGE`
- `STRING`：结果图片 URL
- `STRING`：`revised_prompt`
- `STRING`：原始响应 JSON

#### 行为约束
- 至少 1 张图片 URL
- 最多 5 张图片 URL
- `image` 为空时报错，不自动降级为文生图
- 节点不直接接收 ComfyUI IMAGE；工作流前置使用 `📷 传图到临时图床`

## 工作流设计

### 1. `gpt-image-2-all文生图闭环.json`
结构：
- `Text Multiline` 输入提示词
- `PrimitiveString` 输入 API Key
- `PrimitiveString` 输入 API Base
- `🖼️ gpt-image-2-all生图`
- `SaveImage`
- 可选备注节点说明输出字符串用途

闭环：
- 文本输入
- 创建请求
- 节点直接返回图片、URL、revised_prompt、原始 JSON
- `SaveImage` 保存图片

### 2. `gpt-image-2-all图片编辑闭环.json`
结构：
- `LoadImage`
- `📷 传图到临时图床`
- `Text Multiline`
- `PrimitiveString` API Key
- `PrimitiveString` API Base
- `🖼️ gpt-image-2-all编辑图`
- `SaveImage`

闭环：
- 图片输入 + 文本输入
- 上传获得 URL
- URL 传给编辑节点的 `image` 参数
- 节点返回图片、URL、revised_prompt、原始 JSON
- `SaveImage` 保存图片

### 3. `gpt-image-2-all文本或图片闭环.json`
设计为同画布双分支模板，不做自动分流。

分支 A：
- 文本输入
- 文生图节点
- 保存图片

分支 B：
- 图片输入
- 上传图床
- 编辑图节点
- 保存图片

公共区域：
- API Key
- API Base
- 使用说明备注
- 模型与尺寸说明备注

原因：
- ComfyUI 中更直观
- 不引入脆弱的条件分支逻辑
- 文本和图片两种入口都能完整闭环

## 返回信息语义
用户要求包含“查询返回信息”，但选定方案不单独做查询节点。

因此定义为：
- 直接查看创建节点同步返回的信息
- 信息载体：URL、`revised_prompt`、原始 JSON

这满足“创建 + 返回信息 + 保存结果”的闭环，不伪造异步查询语义。

## 错误处理
- API Key 缺失：中文报错
- prompt 为空：中文报错
- 编辑图缺少 `image_url_1`：中文报错
- 接口响应无 `data` 或无 `url`：中文报错并附响应内容
- 图片下载失败：中文报错

## 验证标准
实现后至少验证：
1. 新节点已在 `nodes/GPTImage/__init__.py` 正确注册
2. 节点分类为 `KuAi/GPTImage`
3. `size` 仅有 3 个文档值
4. 编辑节点支持 1-5 张 URL
5. 3 个工作流 JSON 已保存到目标目录
6. 工作流连线闭环正确：输入 → 节点 → 保存
7. 旧 GPTImage 节点不受影响

## 实施拆分
1. 新建 `nodes/GPTImage/gpt_image_2_all.py`
2. 实现 `GPTImage2AllGenerate`
3. 实现 `GPTImage2AllEdit`
4. 更新 `nodes/GPTImage/__init__.py`
5. 参考现有香蕉工作流制作 3 份 JSON
6. 保存到 `/root/ComfyUI/user/default/workflows`
7. 跑节点注册和标签校验

## 范围控制
本次仅做：
- 新节点
- 新工作流
- 必要注册

不做：
- CSV 批处理
- 新前端分类
- 新上传节点
- 兼容旧 API 扩展字段
