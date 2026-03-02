# 二次开发记录（todo）

> 项目：ComfyUI_KuAi_Power
> GitHub 仓库：https://github.com/kegeai888/ComfyUI_KuAi_Power
> 记录日期：2026-02-19
> 目的：沉淀本次对 Veo3 节点的二次开发、优化修复与经验，便于后续回溯。

---

## 1. 本次需求背景

用户希望在 Veo3 文生视频与图生视频节点中：

1. 扩展可选模型列表（下拉直接可选）。
2. 支持手动输入模型名（无需等待插件更新）。
3. 保持现有请求流程、轮询流程、一键节点和节点注册逻辑不变。

---

## 2. 关键改动概览

### 2.1 扩展 Veo3 模型下拉（文生 + 图生）

在 `nodes/Veo3/veo3.py` 中扩展了模型选项，新增模型：

- `veo_3_1-fast`
- `veo3.1-fast-components`
- `veo_3_1-fast-4K`
- `veo3.1-4k`
- `veo3.1-pro-4k`

说明：`veo3-pro` 原本已存在，保持不变。

### 2.2 增加自定义模型覆盖字段

在两个节点的 optional 参数中新增：

- `model_custom`（字符串，默认空）

覆盖规则：

- `model_custom` 为空：使用下拉 `model`
- `model_custom` 非空：使用 `model_custom.strip()` 覆盖下拉值

实现变量：

- `effective_model = (model_custom or "").strip() or model`

payload 中统一使用：

- `"model": effective_model`

### 2.3 保持原有架构不动

以下逻辑保持不变：

- API 请求与错误处理（`requests.post` + `raise_for_bad_status`）
- API key 解析（`env_or(api_key, "KUAI_API_KEY")`）
- 一键节点（`VeoText2VideoAndWait` / `VeoImage2VideoAndWait`）
- 节点注册映射

### 2.4 README 同步

更新了 `README.md` 的 Veo3 功能说明，补充：

- 新增下拉模型清单
- `model_custom` 高级用法说明

---

## 3. 修复记录（关键问题）

### 问题现象

在“图生视频 + `veo_3_1-fast`”场景中报错：

- `创建 Veo 视频失败: Invalid URL '/v1/video/create': No scheme supplied...`

### 根因分析

新增 `model_custom` 后，曾将其插入到 `create()` 参数列表中间，导致某些调用路径（尤其历史 workflow 或按位置传参路径）出现参数错位，`api_base` 取值异常，最终拼出无 scheme 的 URL。

### 修复措施

1. 将 `create()` 参数顺序恢复为兼容顺序（保持原有参数相对位置）。
2. `model_custom` 放到函数参数末尾，降低位置传参错位风险。
3. 增加 `api_base` 兜底：
   - `api_base = (api_base or "http://api.kuai.host").strip()`
4. 在 `INPUT_TYPES()["optional"]` 中将 `model_custom` 放在后部，减少旧序列化/反序列化场景受影响概率。

### 结果

- 语法检查通过：`python -m py_compile nodes/Veo3/veo3.py`
- 兼容性风险显著下降，旧工作流更安全。

---

## 4. 本次改动文件

- `nodes/Veo3/veo3.py`（必改）
- `README.md`（文档同步）

---

## 5. 回归测试建议（后续可复用）

1. **节点加载**：重启 ComfyUI，确认 Veo3 五个节点都显示。
2. **文生视频透传**：
   - 下拉模式：`model_custom` 为空，验证 payload 用下拉值。
   - 覆盖模式：填写 `model_custom`，验证 payload 用自定义值。
3. **图生视频透传**：同上两种模式，并验证图片 URL 校验仍有效。
4. **旧工作流兼容**：导入不含 `model_custom` 的历史 workflow，确认行为一致。
5. **一键节点回归**：`create + query` 全链路通过。

---

## 6. 二次开发经验总结（可复用）

1. **对已有 ComfyUI 节点做增强时，优先“最小改动”**
   - 只改输入定义与最小覆盖逻辑，不动请求/轮询主干。

2. **新增 optional 参数时，重点关注“参数顺序兼容性”**
   - 不能只看 `kwargs` 路径；要考虑历史工作流与位置传参路径。

3. **对关键基础参数做兜底非常必要**
   - 像 `api_base` 这类 URL 根参数应做非空兜底，避免产生无效 endpoint。

4. **文档要与 UI 能力同步**
   - 新增模型与高级用法要同步到 README，避免用户“功能有了但不会用”。

5. **手动输入能力是插件“抗 API 变化”关键设计**
   - `model_custom` 让用户在 API 新模型上线时能立即试用，降低插件发布耦合。

---

## 7. 后续可选优化（待确认）

1. **输入校验提示优化**
   - 对 `model_custom` 可增加轻量提示（如首尾空格自动处理说明）。

2. **日志增强（调试开关）**
   - 在调试模式下打印“最终生效模型名”，便于排障（注意不打印敏感信息）。

3. **代码清理**
   - 清理 `veo3.py` 中未使用 import（确保零行为变化）。

---

## 8. 回滚说明

若需快速回退：

1. 移除 `model_custom` 字段与 `effective_model` 覆盖逻辑。
2. 保留模型下拉扩展（可独立保留，不影响主流程）。
3. 若仍需最大兼容，可仅保留下拉扩展，不改函数签名。

---

## 9. 2026-03-02 二次开发与修复补充记录（Grok + Gemini + 工作流）

> 目的：补充近期对 Grok/Gemini 相关节点、工作流与显示链路的修复与经验，形成可追溯维护档案。

### 9.1 本轮需求与结果总览

1. **Grok 模型能力恢复**
   - 恢复 `custom_model` 自定义模型覆盖能力。
   - 增加 15 秒模型可选项，保持旧工作流兼容。

2. **新增 Gemini 理解能力（图片 + 视频）**
   - 新增节点：`GeminiImageUnderstanding`、`GeminiVideoUnderstanding`。
   - 支持 6 个 Gemini 模型下拉 + `custom_model` 覆盖。
   - `api_base` 默认改为 `https://ai.kegeai.top`。
   - 支持超时参数配置，后续将图片/视频理解节点 `timeout` 最大值提升到 **6000 秒**。

3. **工作流可用性修复**
   - 新增 `ShowText` 节点，消除工作流导入时“缺少插件”报错。
   - 修复 `ShowText` 的 UI 输出字段，确保展示完整文本而非仅长度日志。
   - 更新视频理解工作流，支持直接连接 ComfyUI 内置 `LoadVideo` 的 `VIDEO` 输出。

---

### 9.2 核心改动（按模块）

#### A. Grok 模块

- 恢复并统一 `custom_model` 覆盖逻辑：
  - `effective_model = (custom_model or "").strip() or model`
- 同步覆盖链路到：
  - 一键节点
  - 文生视频节点
  - 图生视频节点
- 目标：避免模型参数在节点间传递丢失。

#### B. Gemini 模块

- 新增目录与节点：
  - `nodes/Gemini/__init__.py`
  - `nodes/Gemini/gemini_understanding.py`
- 图片理解节点：
  - 输入 `IMAGE + prompt + model + api_key`
  - 可选 `custom_model + api_base + timeout`
- 视频理解节点（两阶段演进）：
  1) 初版：`video_path` 字符串输入
  2) 修复后：支持 `VIDEO` 类型输入，可直连 `LoadVideo`
     - 兼容旧流程：保留可选 `video_path`
     - 优先级：`video` 输入 > `video_path`

#### C. 公共工具复用（去重）

- 将 Gemini 与其他节点可复用逻辑沉淀至：
  - `nodes/Sora2/kuai_utils.py`
- 新增通用函数：
  - `pil_to_base64`
  - `file_to_base64`
  - `extract_gemini_text_from_response`
- 统一错误提取：
  - 使用 `extract_error_message_from_response`，减少重复错误处理代码。

#### D. 显示链路与工作流

- 新增节点：`nodes/Utils/show_text.py`
- 注册入口更新：`nodes/Utils/__init__.py`
- `ShowText` 返回值改为兼容格式：
  - `{"ui": {"string": [...], "text": [...]}, "result": (...)}`
- 工作流：
  - `workflows/gemini_image_understanding_workflow.json`
  - `workflows/gemini_video_understanding_workflow.json`（已改为 `LoadVideo -> GeminiVideoUnderstanding(video) -> ShowText`）

---

### 9.3 关键问题与根因-修复映射

1. **问题：Gemini 工作流导入提示缺少插件**
   - 根因：工作流依赖的 `ShowText` 节点在仓库内不存在。
   - 修复：补齐并注册 `ShowText` 节点。

2. **问题：ShowText 不显示完整理解文本**
   - 根因：前端识别字段差异导致 UI 渲染不稳定。
   - 修复：同时返回 `ui.string` 与 `ui.text`，兼容不同前端处理路径。

3. **问题：视频理解节点无法与“加载视频”直连**
   - 根因：原节点仅接受 `video_path` 字符串。
   - 修复：改为接受 `VIDEO` 输入并做文件解析/临时落盘，保留 `video_path` 兼容。

4. **问题：代码重复与维护成本偏高**
   - 根因：图片/视频理解节点存在重复编码与响应解析逻辑。
   - 修复：抽取公共函数到 `kuai_utils.py`，统一复用。

---

### 9.4 本轮涉及文件（新增/修改）

- 新增：
  - `nodes/Gemini/__init__.py`
  - `nodes/Gemini/gemini_understanding.py`
  - `nodes/Utils/show_text.py`
  - `test/test_gemini_understanding.py`
  - `test/test_show_text.py`
  - `docs/GEMINI_UNDERSTANDING_GUIDE.md`
  - `workflows/gemini_image_understanding_workflow.json`
  - `workflows/gemini_video_understanding_workflow.json`

- 修改：
  - `nodes/Sora2/kuai_utils.py`
  - `nodes/Utils/__init__.py`
  - （以及相关 README/文档同步）

---

### 9.5 可复用维护经验（重点）

1. **新增参数优先做兼容设计**
   - 对历史工作流保持“可用而不破坏”，新能力优先放 optional。

2. **节点输出必须按 ComfyUI 前端可识别格式返回**
   - 输出类型正确不代表前端一定显示，UI 字段名要做兼容。

3. **多节点相同逻辑必须沉淀到工具层**
   - Base64 编码、响应文本提取、错误解析等应统一，避免散落复制。

4. **工作流是第一等产物**
   - 节点改动后必须同步更新示例 workflow，否则用户导入体验会断裂。

5. **日志只做辅助，不替代真实输出**
   - “结果长度”日志用于排障，最终结果必须在节点输出链路完整透传。

---

### 9.6 建议的回归检查清单（后续每次发版）

1. 节点注册检查：`python test/test_gemini_understanding.py`
2. 显示节点检查：`python test/test_show_text.py`
3. 语法检查：`python -m py_compile nodes/Gemini/gemini_understanding.py`
4. 工作流导入检查：图片/视频两个 workflow 均可直接运行
5. 兼容性检查：
   - 视频节点 `VIDEO` 输入路径
   - 旧 `video_path` 路径
   - `custom_model` 覆盖路径

---

## 10. 2026-03-02 文档与仓库信息同步

1. 已确认并同步仓库地址：
   - `https://github.com/kegeai888/ComfyUI_KuAi_Power`
2. 用户手册已补齐并纳入项目：
   - `用户使用手册.md`
3. README 已补充用户手册入口，便于使用者快速定位。

---

（完）
