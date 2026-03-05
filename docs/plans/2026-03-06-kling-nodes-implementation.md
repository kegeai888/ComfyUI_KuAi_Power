# 可灵视频生成节点实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为 ComfyUI_KuAi_Power 插件添加可灵（Kling）视频生成功能，包括文生视频、图生视频、任务查询、一键生成和批量处理。

**Architecture:** 创建独立的 Kling 分类目录，复用 Sora2 的通用工具函数（env_or, http_headers_json, raise_for_bad_status），实现 6 个核心节点和 1 个批量处理器。采用 TDD 方法，先写测试再实现功能。

**Tech Stack:** Python 3.x, requests, json, time, ComfyUI 节点系统, pytest

---

## Task 1: 创建 Kling 工具函数模块

**Files:**
- Create: `nodes/Kling/__init__.py`
- Create: `nodes/Kling/kling_utils.py`
- Create: `test/test_kling_utils.py`

**Step 1: 创建目录结构**

```bash
mkdir -p nodes/Kling
mkdir -p test
```

**Step 2: 编写工具函数测试**

创建 `test/test_kling_utils.py`:

```python
#!/usr/bin/env python3
"""测试 Kling 工具函数"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_parse_kling_response_success():
    """测试成功响应解析"""
    from nodes.Kling.kling_utils import parse_kling_response

    resp_json = {
        "code": 0,
        "message": "SUCCEED",
        "data": {
            "task_id": "831922345719271433",
            "task_status": "submitted",
            "created_at": 1766374262370
        }
    }

    task_id, status, created_at = parse_kling_response(resp_json)

    assert task_id == "831922345719271433"
    assert status == "submitted"
    assert created_at == 1766374262370

def test_parse_kling_response_error():
    """测试错误响应解析"""
    from nodes.Kling.kling_utils import parse_kling_response

    resp_json = {
        "code": 400,
        "message": "Invalid parameters"
    }

    try:
        parse_kling_response(resp_json)
        assert False, "应该抛出异常"
    except RuntimeError as e:
        assert "API 错误" in str(e)
        assert "Invalid parameters" in str(e)

def test_kling_models_constant():
    """测试模型列表常量"""
    from nodes.Kling.kling_utils import KLING_MODELS

    assert "kling-v1" in KLING_MODELS
    assert "kling-v1-6" in KLING_MODELS
    assert "kling-v2-master" in KLING_MODELS
    assert "kling-v3" in KLING_MODELS

def test_kling_aspect_ratios_constant():
    """测试宽高比列表常量"""
    from nodes.Kling.kling_utils import KLING_ASPECT_RATIOS

    assert "16:9" in KLING_ASPECT_RATIOS
    assert "9:16" in KLING_ASPECT_RATIOS
    assert "1:1" in KLING_ASPECT_RATIOS

if __name__ == "__main__":
    print("\n🧪 Kling 工具函数测试套件\n")

    tests = [
        ("解析成功响应", test_parse_kling_response_success),
        ("解析错误响应", test_parse_kling_response_error),
        ("模型列表常量", test_kling_models_constant),
        ("宽高比列表常量", test_kling_aspect_ratios_constant),
    ]

    results = []
    for name, test_func in tests:
        try:
            test_func()
            results.append((name, True))
            print(f"✅ {name}")
        except Exception as e:
            results.append((name, False))
            print(f"❌ {name}: {e}")

    all_passed = all(r[1] for r in results)
    print("\n" + ("🎉 所有测试通过！" if all_passed else "⚠️  部分测试失败"))
    sys.exit(0 if all_passed else 1)
```

**Step 3: 运行测试验证失败**

```bash
python test/test_kling_utils.py
```

预期输出: 测试失败，因为模块不存在

**Step 4: 实现工具函数**

创建 `nodes/Kling/kling_utils.py`:

```python
"""可灵 API 工具函数"""

# 模型列表
KLING_MODELS = [
    "kling-v1",
    "kling-v1-6",
    "kling-v2-master",
    "kling-v2-1-master",
    "kling-v2-5-turbo",
    "kling-v3"
]

# 宽高比列表
KLING_ASPECT_RATIOS = [
    "16:9",
    "9:16",
    "1:1"
]

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
        raise RuntimeError(f"API 错误: {resp_json.get('message', '未知错误')}")

    data = resp_json.get("data", {})
    task_id = data.get("task_id", "")
    status = data.get("task_status", "")
    created_at = data.get("created_at", 0)

    return (task_id, status, created_at)
```

**Step 5: 创建空的 __init__.py**

创建 `nodes/Kling/__init__.py`:

```python
"""可灵视频生成节点"""

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
```

**Step 6: 运行测试验证通过**

```bash
python test/test_kling_utils.py
```

预期输出: 所有测试通过

**Step 7: 提交**

```bash
git add nodes/Kling/__init__.py nodes/Kling/kling_utils.py test/test_kling_utils.py
git commit -m "$(cat <<'EOF'
feat: 添加可灵工具函数模块

- 创建 Kling 目录结构
- 实现 parse_kling_response() 响应解析函数
- 定义 KLING_MODELS 和 KLING_ASPECT_RATIOS 常量
- 添加完整的单元测试

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: 实现 KlingText2Video 节点

**Files:**
- Modify: `nodes/Kling/kling.py` (创建新文件)
- Create: `test/test_kling_text2video.py`

**Step 1: 编写节点测试**

创建 `test/test_kling_text2video.py`:

```python
#!/usr/bin/env python3
"""测试 KlingText2Video 节点"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_node_structure():
    """测试节点结构"""
    from nodes.Kling.kling import KlingText2Video

    # 检查必需方法
    assert hasattr(KlingText2Video, 'INPUT_TYPES')
    assert hasattr(KlingText2Video, 'INPUT_LABELS')
    assert hasattr(KlingText2Video, 'RETURN_TYPES')
    assert hasattr(KlingText2Video, 'RETURN_NAMES')
    assert hasattr(KlingText2Video, 'FUNCTION')
    assert hasattr(KlingText2Video, 'CATEGORY')

    # 检查分类
    assert KlingText2Video.CATEGORY == "KuAi/Kling"

    # 检查返回类型
    assert KlingText2Video.RETURN_TYPES == ("STRING", "STRING", "INT")
    assert KlingText2Video.RETURN_NAMES == ("任务ID", "状态", "创建时间")

def test_input_types():
    """测试输入参数定义"""
    from nodes.Kling.kling import KlingText2Video

    input_types = KlingText2Video.INPUT_TYPES()

    # 检查必需参数
    required = input_types["required"]
    assert "prompt" in required
    assert "model_name" in required
    assert "mode" in required
    assert "duration" in required
    assert "aspect_ratio" in required

    # 检查可选参数
    optional = input_types["optional"]
    assert "negative_prompt" in optional
    assert "cfg_scale" in optional
    assert "multi_shot" in optional
    assert "watermark" in optional
    assert "api_key" in optional

def test_input_labels():
    """测试中文标签"""
    from nodes.Kling.kling import KlingText2Video

    labels = KlingText2Video.INPUT_LABELS()

    assert labels["prompt"] == "提示词"
    assert labels["model_name"] == "模型名称"
    assert labels["mode"] == "模式"
    assert labels["duration"] == "时长"
    assert labels["aspect_ratio"] == "宽高比"

if __name__ == "__main__":
    print("\n🧪 KlingText2Video 节点测试套件\n")

    tests = [
        ("节点结构", test_node_structure),
        ("输入参数定义", test_input_types),
        ("中文标签", test_input_labels),
    ]

    results = []
    for name, test_func in tests:
        try:
            test_func()
            results.append((name, True))
            print(f"✅ {name}")
        except Exception as e:
            results.append((name, False))
            print(f"❌ {name}: {e}")

    all_passed = all(r[1] for r in results)
    print("\n" + ("🎉 所有测试通过！" if all_passed else "⚠️  部分测试失败"))
    sys.exit(0 if all_passed else 1)
```

**Step 2: 运行测试验证失败**

```bash
python test/test_kling_text2video.py
```

预期输出: 测试失败，模块不存在

**Step 3: 实现 KlingText2Video 节点（第1部分 - 前50行）**

创建 `nodes/Kling/kling.py`:

```python
"""可灵视频生成核心节点"""

import json
import time
import requests
from ..Sora2.kuai_utils import env_or, http_headers_json, raise_for_bad_status
from .kling_utils import parse_kling_response, KLING_MODELS, KLING_ASPECT_RATIOS


class KlingText2Video:
    """可灵文生视频节点"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "视频提示词"
                }),
                "model_name": (KLING_MODELS, {
                    "default": "kling-v1",
                    "tooltip": "模型选择"
                }),
                "mode": (["std", "pro"], {
                    "default": "std",
                    "tooltip": "生成模式：std（标准）, pro（专家）"
                }),
                "duration": (["5", "10"], {
                    "default": "5",
                    "tooltip": "视频时长（秒）"
                }),
                "aspect_ratio": (KLING_ASPECT_RATIOS, {
                    "default": "16:9",
                    "tooltip": "视频宽高比"
                }),
            },
            "optional": {
                "negative_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "负面提示词"
                }),
                "cfg_scale": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.1,
```

**Step 4: 继续实现 KlingText2Video 节点（第2部分 - 接下来50行）**

使用 Bash 追加内容：

```bash
cat >> nodes/Kling/kling.py << 'EOF'
                    "tooltip": "提示词引导强度"
                }),
                "multi_shot": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否生成多镜头视频"
                }),
                "watermark": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否添加水印"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "tooltip": "API密钥（留空使用环境变量 KUAI_API_KEY）"
                }),
                "api_base": ("STRING", {
                    "default": "https://api.kuai.host",
                    "tooltip": "API端点地址"
                }),
                "timeout": ("INT", {
                    "default": 120,
                    "min": 5,
                    "max": 600,
                    "tooltip": "超时时间(秒)"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("任务ID", "状态", "创建时间")
    FUNCTION = "create"
    CATEGORY = "KuAi/Kling"

    @classmethod
    def INPUT_LABELS(cls):
        return {
            "prompt": "提示词",
            "model_name": "模型名称",
            "mode": "模式",
            "duration": "时长",
            "aspect_ratio": "宽高比",
            "negative_prompt": "负面提示词",
            "cfg_scale": "CFG强度",
            "multi_shot": "多镜头",
            "watermark": "水印",
            "api_key": "API密钥",
            "api_base": "API地址",
            "timeout": "超时",
        }

    def create(self, prompt, model_name="kling-v1", mode="std", duration="5", aspect_ratio="16:9",
               negative_prompt="", cfg_scale=0.5, multi_shot=False, watermark=False,
               api_key="", api_base="https://api.kuai.host", timeout=120):
        """创建文生视频任务"""

        # 解析 API key
        api_key = env_or(api_key, "KUAI_API_KEY")
        if not api_key:
            raise RuntimeError("API Key 未配置，请在节点参数或环境变量中设置")

        # 构建请求
        endpoint = api_base.rstrip("/") + "/kling/v1/videos/text2video"
        headers = http_headers_json(api_key)

        payload = {
            "model_name": model_name,
            "prompt": prompt,
            "mode": mode,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "multi_shot": multi_shot,
            "watermark_info": {
                "enabled": watermark
            }
        }

        # 添加可选参数
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt

        if cfg_scale != 0.5:
            payload["cfg_scale"] = cfg_scale

        # 调用 API
        try:
            print(f"[ComfyUI_KuAi_Power] 创建可灵文生视频任务: {model_name}, {mode}, {duration}s")
            resp = requests.post(endpoint, headers=headers, json=payload, timeout=int(timeout))
            raise_for_bad_status(resp, "创建文生视频任务失败")

            data = resp.json()
            task_id, status, created_at = parse_kling_response(data)

            if not task_id:
                raise RuntimeError(f"创建响应缺少任务 ID: {json.dumps(data, ensure_ascii=False)}")

            print(f"[ComfyUI_KuAi_Power] 任务创建成功: {task_id}, 状态: {status}")
            return (task_id, status, created_at)

        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"创建文生视频任务失败: {str(e)}")
EOF
```

**Step 5: 运行测试验证通过**

```bash
python test/test_kling_text2video.py
```

预期输出: 所有测试通过

**Step 6: 提交**

```bash
git add nodes/Kling/kling.py test/test_kling_text2video.py
git commit -m "$(cat <<'EOF'
feat: 实现 KlingText2Video 文生视频节点

- 支持基础参数：prompt, model_name, mode, duration, aspect_ratio
- 支持常用功能：negative_prompt, cfg_scale, multi_shot, watermark
- 完整的参数验证和错误处理
- 中文标签和工具提示
- 添加单元测试

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: 实现 KlingImage2Video 节点

**Files:**
- Modify: `nodes/Kling/kling.py`
- Create: `test/test_kling_image2video.py`

**Step 1: 编写节点测试**

创建 `test/test_kling_image2video.py`:

```python
#!/usr/bin/env python3
"""测试 KlingImage2Video 节点"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_node_structure():
    """测试节点结构"""
    from nodes.Kling.kling import KlingImage2Video

    assert hasattr(KlingImage2Video, 'INPUT_TYPES')
    assert hasattr(KlingImage2Video, 'CATEGORY')
    assert KlingImage2Video.CATEGORY == "KuAi/Kling"

def test_input_types():
    """测试输入参数定义"""
    from nodes.Kling.kling import KlingImage2Video

    input_types = KlingImage2Video.INPUT_TYPES()

    # 检查必需参数
    required = input_types["required"]
    assert "image" in required
    assert "model_name" in required
    assert "mode" in required
    assert "duration" in required

    # 检查可选参数
    optional = input_types["optional"]
    assert "prompt" in optional
    assert "image_tail" in optional

if __name__ == "__main__":
    print("\n🧪 KlingImage2Video 节点测试套件\n")

    tests = [
        ("节点结构", test_node_structure),
        ("输入参数定义", test_input_types),
    ]

    results = []
    for name, test_func in tests:
        try:
            test_func()
            results.append((name, True))
            print(f"✅ {name}")
        except Exception as e:
            results.append((name, False))
            print(f"❌ {name}: {e}")

    all_passed = all(r[1] for r in results)
    print("\n" + ("🎉 所有测试通过！" if all_passed else "⚠️  部分测试失败"))
    sys.exit(0 if all_passed else 1)
```

**Step 2: 运行测试验证失败**

```bash
python test/test_kling_image2video.py
```

**Step 3: 实现 KlingImage2Video 节点**

追加到 `nodes/Kling/kling.py`:

```bash
cat >> nodes/Kling/kling.py << 'EOF'


class KlingImage2Video:
    """可灵图生视频节点"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "图片 URL 或 Base64 编码"
                }),
                "model_name": (KLING_MODELS, {
                    "default": "kling-v1",
                    "tooltip": "模型选择"
                }),
                "mode": (["std", "pro"], {
                    "default": "std",
                    "tooltip": "生成模式：std（标准）, pro（专家）"
                }),
                "duration": (["5", "10"], {
                    "default": "5",
                    "tooltip": "视频时长（秒）"
                }),
            },
            "optional": {
                "prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "提示词（可选，用于引导生成）"
                }),
                "image_tail": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "尾帧图片 URL 或 Base64"
                }),
                "negative_prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "tooltip": "负面提示词"
                }),
                "cfg_scale": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.1,
                    "tooltip": "提示词引导强度"
                }),
                "multi_shot": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否生成多镜头视频"
                }),
                "watermark": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否添加水印"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "tooltip": "API密钥（留空使用环境变量 KUAI_API_KEY）"
                }),
                "api_base": ("STRING", {
                    "default": "https://api.kuai.host",
                    "tooltip": "API端点地址"
                }),
                "timeout": ("INT", {
                    "default": 120,
                    "min": 5,
                    "max": 600,
                    "tooltip": "超时时间(秒)"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("任务ID", "状态", "创建时间")
    FUNCTION = "create"
    CATEGORY = "KuAi/Kling"

    @classmethod
    def INPUT_LABELS(cls):
        return {
            "image": "图片",
            "model_name": "模型名称",
            "mode": "模式",
            "duration": "时长",
            "prompt": "提示词",
            "image_tail": "尾帧图片",
            "negative_prompt": "负面提示词",
            "cfg_scale": "CFG强度",
            "multi_shot": "多镜头",
            "watermark": "水印",
            "api_key": "API密钥",
            "api_base": "API地址",
            "timeout": "超时",
        }

    def create(self, image, model_name="kling-v1", mode="std", duration="5",
               prompt="", image_tail="", negative_prompt="", cfg_scale=0.5, multi_shot=False, watermark=False,
               api_key="", api_base="https://api.kuai.host", timeout=120):
        """创建图生视频任务"""

        # 解析 API key
        api_key = env_or(api_key, "KUAI_API_KEY")
        if not api_key:
            raise RuntimeError("API Key 未配置，请在节点参数或环境变量中设置")

        if not image:
            raise RuntimeError("请提供图片 URL 或 Base64 编码")

        # 构建请求
        endpoint = api_base.rstrip("/") + "/kling/v1/videos/image2video"
        headers = http_headers_json(api_key)

        payload = {
            "model_name": model_name,
            "image": image,
            "mode": mode,
            "duration": duration,
            "multi_shot": multi_shot,
            "watermark_info": {
                "enabled": watermark
            }
        }

        # 添加可选参数
        if prompt:
            payload["prompt"] = prompt

        if image_tail:
            payload["image_tail"] = image_tail

        if negative_prompt:
            payload["negative_prompt"] = negative_prompt

        if cfg_scale != 0.5:
            payload["cfg_scale"] = cfg_scale

        # 调用 API
        try:
            print(f"[ComfyUI_KuAi_Power] 创建可灵图生视频任务: {model_name}, {mode}, {duration}s")
            resp = requests.post(endpoint, headers=headers, json=payload, timeout=int(timeout))
            raise_for_bad_status(resp, "创建图生视频任务失败")

            data = resp.json()
            task_id, status, created_at = parse_kling_response(data)

            if not task_id:
                raise RuntimeError(f"创建响应缺少任务 ID: {json.dumps(data, ensure_ascii=False)}")

            print(f"[ComfyUI_KuAi_Power] 任务创建成功: {task_id}, 状态: {status}")
            return (task_id, status, created_at)

        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"创建图生视频任务失败: {str(e)}")
EOF
```

**Step 4: 运行测试验证通过**

```bash
python test/test_kling_image2video.py
```

**Step 5: 提交**

```bash
git add nodes/Kling/kling.py test/test_kling_image2video.py
git commit -m "$(cat <<'EOF'
feat: 实现 KlingImage2Video 图生视频节点

- 支持图片 URL 和 Base64 输入
- 支持尾帧控制（image_tail）
- 可选提示词引导生成
- 复用文生视频的常用功能参数
- 添加单元测试

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

---

由于实现计划非常长（预计超过 2000 行），我将分多个文件创建。让我先保存前 3 个任务，然后继续创建剩余任务。

计划包含以下任务：
1. ✅ 创建 Kling 工具函数模块
2. ✅ 实现 KlingText2Video 节点
3. ✅ 实现 KlingImage2Video 节点
4. ⏭️ 实现 KlingQueryTask 节点
5. ⏭️ 实现 AndWait 节点
6. ⏭️ 注册节点到 __init__.py
7. ⏭️ 实现批量处理器
8. ⏭️ 创建示例 CSV 文件
9. ⏭️ 创建文档
10. ⏭️ 更新前端面板
11. ⏭️ 完整测试验证

是否继续创建完整的实现计划？

## Task 4: 实现 KlingQueryTask 节点

**Files:**
- Modify: `nodes/Kling/kling.py`
- Create: `test/test_kling_query.py`

**Step 1: 编写节点测试**

创建 `test/test_kling_query.py`:

```python
#!/usr/bin/env python3
"""测试 KlingQueryTask 节点"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_node_structure():
    """测试节点结构"""
    from nodes.Kling.kling import KlingQueryTask

    assert hasattr(KlingQueryTask, 'INPUT_TYPES')
    assert KlingQueryTask.CATEGORY == "KuAi/Kling"
    assert KlingQueryTask.RETURN_TYPES == ("STRING", "STRING", "STRING", "STRING")

def test_input_types():
    """测试输入参数定义"""
    from nodes.Kling.kling import KlingQueryTask

    input_types = KlingQueryTask.INPUT_TYPES()

    # 检查必需参数
    required = input_types["required"]
    assert "task_id" in required

    # 检查可选参数
    optional = input_types["optional"]
    assert "wait" in optional
    assert "poll_interval_sec" in optional
    assert "timeout_sec" in optional

if __name__ == "__main__":
    print("\n🧪 KlingQueryTask 节点测试套件\n")

    tests = [
        ("节点结构", test_node_structure),
        ("输入参数定义", test_input_types),
    ]

    results = []
    for name, test_func in tests:
        try:
            test_func()
            results.append((name, True))
            print(f"✅ {name}")
        except Exception as e:
            results.append((name, False))
            print(f"❌ {name}: {e}")

    all_passed = all(r[1] for r in results)
    print("\n" + ("🎉 所有测试通过！" if all_passed else "⚠️  部分测试失败"))
    sys.exit(0 if all_passed else 1)
```

**Step 2: 运行测试验证失败**

```bash
python test/test_kling_query.py
```

**Step 3: 实现 KlingQueryTask 节点**

追加到 `nodes/Kling/kling.py`:

```python


class KlingQueryTask:
    """可灵查询任务节点"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "task_id": ("STRING", {
                    "default": "",
                    "tooltip": "任务 ID"
                }),
            },
            "optional": {
                "wait": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "是否等待任务完成"
                }),
                "poll_interval_sec": ("INT", {
                    "default": 15,
                    "min": 5,
                    "max": 90,
                    "tooltip": "轮询间隔(秒)"
                }),
                "timeout_sec": ("INT", {
                    "default": 1200,
                    "min": 600,
                    "max": 9600,
                    "tooltip": "总超时时间(秒)"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "tooltip": "API密钥"
                }),
                "api_base": ("STRING", {
                    "default": "https://api.kuai.host",
                    "tooltip": "API端点地址"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("状态", "视频URL", "时长", "原始响应")
    FUNCTION = "query"
    CATEGORY = "KuAi/Kling"

    @classmethod
    def INPUT_LABELS(cls):
        return {
            "task_id": "任务ID",
            "wait": "等待完成",
            "poll_interval_sec": "轮询间隔",
            "timeout_sec": "总超时",
            "api_key": "API密钥",
            "api_base": "API地址",
        }

    def query(self, task_id, wait=True, poll_interval_sec=15, timeout_sec=1200,
              api_key="", api_base="https://api.kuai.host"):
        """查询任务状态"""

        api_key = env_or(api_key, "KUAI_API_KEY")
        if not api_key:
            raise RuntimeError("API Key 未配置")

        if not task_id:
            raise RuntimeError("请提供任务 ID")

        endpoint = api_base.rstrip("/") + f"/kling/v1/videos/text2video/{task_id}"
        headers = http_headers_json(api_key)

        def query_once():
            """查询一次"""
            try:
                resp = requests.get(endpoint, headers=headers, timeout=60)
                raise_for_bad_status(resp, "查询任务失败")

                data = resp.json()

                # 解析响应
                if data.get("code") != 0:
                    raise RuntimeError(f"查询失败: {data.get('message', '未知错误')}")

                task_data = data.get("data", {})
                status = task_data.get("task_status", "")
                task_info = task_data.get("task_info", {})
                video_url = task_info.get("video_url", "")
                duration = task_info.get("duration", "")

                # 检查任务失败
                if status == "failed":
                    error_msg = task_info.get("error", "任务失败")
                    raise RuntimeError(f"任务执行失败: {error_msg}")

                # 检查视频 URL
                if status == "succeed" and not video_url:
                    raise RuntimeError("任务完成但未返回视频 URL")

                return (status, video_url, duration, json.dumps(data, ensure_ascii=False))

            except RuntimeError:
                raise
            except Exception as e:
                raise RuntimeError(f"查询任务失败: {str(e)}")

        # 如果不等待，直接返回
        if not wait:
            return query_once()

        # 轮询等待
        print(f"[KlingQueryTask] 开始轮询任务 {task_id}，超时 {timeout_sec} 秒，间隔 {poll_interval_sec} 秒")
        deadline = time.time() + int(timeout_sec)
        last_raw = ""
        poll_count = 0

        while time.time() < deadline:
            poll_count += 1
            status, video_url, duration, raw = query_once()
            last_raw = raw

            print(f"[KlingQueryTask] 第 {poll_count} 次查询: 状态={status}")

            if status in ("succeed", "failed"):
                print(f"[KlingQueryTask] 任务完成: {status}")
                return (status, video_url, duration, raw)

            time.sleep(int(poll_interval_sec))

        # 超时
        print(f"[KlingQueryTask] 轮询超时")
        return ("timeout", "", "", last_raw or json.dumps({"error": "timeout"}, ensure_ascii=False))
```

**Step 4: 运行测试验证通过**

```bash
python test/test_kling_query.py
```

**Step 5: 提交**

```bash
git add nodes/Kling/kling.py test/test_kling_query.py
git commit -m "$(cat <<'EOF'
feat: 实现 KlingQueryTask 查询任务节点

- 支持单次查询和轮询等待
- 可配置轮询间隔和超时时间
- 完整的错误处理（任务失败、超时、URL缺失）
- 返回视频 URL、时长和原始响应
- 添加单元测试

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

EOF
)'"
```

---

## Task 5: 实现 AndWait 便捷节点

**Files:**
- Modify: `nodes/Kling/kling.py`
- Create: `test/test_kling_andwait.py`

**Step 1: 编写节点测试**

创建 `test/test_kling_andwait.py`:

```python
#!/usr/bin/env python3
"""测试 AndWait 便捷节点"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_text2video_andwait_structure():
    """测试文生视频 AndWait 节点结构"""
    from nodes.Kling.kling import KlingText2VideoAndWait

    assert hasattr(KlingText2VideoAndWait, 'INPUT_TYPES')
    assert KlingText2VideoAndWait.CATEGORY == "KuAi/Kling"
    assert KlingText2VideoAndWait.RETURN_TYPES == ("STRING", "STRING", "STRING", "STRING")

def test_image2video_andwait_structure():
    """测试图生视频 AndWait 节点结构"""
    from nodes.Kling.kling import KlingImage2VideoAndWait

    assert hasattr(KlingImage2VideoAndWait, 'INPUT_TYPES')
    assert KlingImage2VideoAndWait.CATEGORY == "KuAi/Kling"

if __name__ == "__main__":
    print("\n🧪 AndWait 便捷节点测试套件\n")

    tests = [
        ("文生视频 AndWait 结构", test_text2video_andwait_structure),
        ("图生视频 AndWait 结构", test_image2video_andwait_structure),
    ]

    results = []
    for name, test_func in tests:
        try:
            test_func()
            results.append((name, True))
            print(f"✅ {name}")
        except Exception as e:
            results.append((name, False))
            print(f"❌ {name}: {e}")

    all_passed = all(r[1] for r in results)
    print("\n" + ("🎉 所有测试通过！" if all_passed else "⚠️  部分测试失败"))
    sys.exit(0 if all_passed else 1)
```

**Step 2: 运行测试验证失败**

```bash
python test/test_kling_andwait.py
```

**Step 3: 实现 AndWait 节点（参考设计文档中的完整代码）**

**Step 4: 运行测试验证通过**

```bash
python test/test_kling_andwait.py
```

**Step 5: 提交**

```bash
git add nodes/Kling/kling.py test/test_kling_andwait.py
git commit -m "feat: 实现 AndWait 一键生成便捷节点

- KlingText2VideoAndWait: 文生视频一键生成
- KlingImage2VideoAndWait: 图生视频一键生成
- 内部组合 Create + Query 逻辑
- 可配置创建超时和轮询参数
- 添加单元测试

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 6: 注册节点到 __init__.py

**Files:**
- Modify: `nodes/Kling/__init__.py`
- Create: `test/test_kling_registration.py`

**Step 1: 编写注册测试**

创建 `test/test_kling_registration.py`:

```python
#!/usr/bin/env python3
"""测试 Kling 节点注册"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_all_nodes_registered():
    """测试所有节点已注册"""
    from nodes.Kling import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

    expected_nodes = [
        "KlingText2Video",
        "KlingImage2Video",
        "KlingQueryTask",
        "KlingText2VideoAndWait",
        "KlingImage2VideoAndWait",
    ]

    for node_name in expected_nodes:
        assert node_name in NODE_CLASS_MAPPINGS, f"{node_name} 未在 NODE_CLASS_MAPPINGS 中注册"
        assert node_name in NODE_DISPLAY_NAME_MAPPINGS, f"{node_name} 未在 NODE_DISPLAY_NAME_MAPPINGS 中注册"

    print(f"✅ 所有 {len(expected_nodes)} 个节点已注册")

def test_display_names_have_emoji():
    """测试显示名称包含 emoji"""
    from nodes.Kling import NODE_DISPLAY_NAME_MAPPINGS

    for node_name, display_name in NODE_DISPLAY_NAME_MAPPINGS.items():
        assert "🎞️" in display_name, f"{node_name} 的显示名称缺少 emoji"

    print("✅ 所有显示名称包含 emoji")

def test_all_nodes_have_category():
    """测试所有节点有正确的分类"""
    from nodes.Kling import NODE_CLASS_MAPPINGS

    for node_name, node_class in NODE_CLASS_MAPPINGS.items():
        assert hasattr(node_class, 'CATEGORY'), f"{node_name} 缺少 CATEGORY 属性"
        assert node_class.CATEGORY == "KuAi/Kling", f"{node_name} 的分类不正确"

    print("✅ 所有节点分类正确")

if __name__ == "__main__":
    print("\n🧪 Kling 节点注册测试套件\n")

    tests = [
        ("所有节点已注册", test_all_nodes_registered),
        ("显示名称包含 emoji", test_display_names_have_emoji),
        ("所有节点分类正确", test_all_nodes_have_category),
    ]

    results = []
    for name, test_func in tests:
        try:
            test_func()
            results.append((name, True))
        except Exception as e:
            results.append((name, False))
            print(f"❌ {name}: {e}")

    all_passed = all(r[1] for r in results)
    print("\n" + ("🎉 所有测试通过！" if all_passed else "⚠️  部分测试失败"))
    sys.exit(0 if all_passed else 1)
```

**Step 2: 运行测试验证失败**

```bash
python test/test_kling_registration.py
```

**Step 3: 更新 __init__.py 注册节点**

修改 `nodes/Kling/__init__.py`:

```python
"""可灵视频生成节点"""

from .kling import (
    KlingText2Video,
    KlingImage2Video,
    KlingQueryTask,
    KlingText2VideoAndWait,
    KlingImage2VideoAndWait,
)

NODE_CLASS_MAPPINGS = {
    "KlingText2Video": KlingText2Video,
    "KlingImage2Video": KlingImage2Video,
    "KlingQueryTask": KlingQueryTask,
    "KlingText2VideoAndWait": KlingText2VideoAndWait,
    "KlingImage2VideoAndWait": KlingImage2VideoAndWait,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "KlingText2Video": "🎞️ 可灵文生视频",
    "KlingImage2Video": "🎞️ 可灵图生视频",
    "KlingQueryTask": "🔍 可灵查询任务",
    "KlingText2VideoAndWait": "⚡ 可灵文生视频（一键）",
    "KlingImage2VideoAndWait": "⚡ 可灵图生视频（一键）",
}
```

**Step 4: 运行测试验证通过**

```bash
python test/test_kling_registration.py
```

**Step 5: 提交**

```bash
git add nodes/Kling/__init__.py test/test_kling_registration.py
git commit -m "feat: 注册可灵节点到 __init__.py

- 注册 5 个核心节点
- 使用 🎞️ emoji 前缀（电影胶片）
- 中文显示名称
- 添加注册测试验证

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 7: 更新前端面板

**Files:**
- Modify: `web/kuaipower_panel.js`

**Step 1: 添加 Kling 分类映射**

在 `web/kuaipower_panel.js` 的 `categoryNameMap` 中添加 Kling 分类（约第 7-15 行）:

```javascript
const categoryNameMap = {
  "ScriptGenerator": "📝 脚本生成",
  "Sora2": "🎬 Sora2 视频生成",
  "Veo3": "🚀 Veo3.1 视频生成",
  "Grok": "🤖 Grok 视频生成",
  "NanoBanana": "🍌 Nano Banana 图像生成",
  "Kling": "🎞️ 可灵视频生成",  // 添加这一行
  "Utils": "🛠️ 工具节点",
};
```

**Step 2: 测试前端面板**

1. 重启 ComfyUI
2. 按 Ctrl+Shift+K 打开快速面板
3. 验证"🎞️ 可灵视频生成"分类出现
4. 验证 5 个节点都在分类下

**Step 3: 提交**

```bash
git add web/kuaipower_panel.js
git commit -m "feat: 添加可灵分类到前端快速面板

- 在 categoryNameMap 中添加 Kling 分类
- 使用 🎞️ emoji 前缀
- 支持 Ctrl+Shift+K 快速访问

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 8: 实现批量处理器

**Files:**
- Create: `nodes/Kling/batch_processor.py`
- Modify: `nodes/Kling/__init__.py`
- Create: `test/test_kling_batch.py`

**Step 1: 编写批量处理器测试**

创建 `test/test_kling_batch.py`:

```python
#!/usr/bin/env python3
"""测试 Kling 批量处理器"""

import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_batch_processor_structure():
    """测试批量处理器结构"""
    from nodes.Kling.batch_processor import KlingBatchProcessor

    assert hasattr(KlingBatchProcessor, 'INPUT_TYPES')
    assert KlingBatchProcessor.CATEGORY == "KuAi/Kling"
    assert KlingBatchProcessor.FUNCTION == "process_batch"

def test_batch_processor_registration():
    """测试批量处理器已注册"""
    from nodes.Kling import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

    assert "KlingBatchProcessor" in NODE_CLASS_MAPPINGS
    assert "KlingBatchProcessor" in NODE_DISPLAY_NAME_MAPPINGS
    assert "📦" in NODE_DISPLAY_NAME_MAPPINGS["KlingBatchProcessor"]

if __name__ == "__main__":
    print("\n🧪 Kling 批量处理器测试套件\n")

    tests = [
        ("批量处理器结构", test_batch_processor_structure),
        ("批量处理器注册", test_batch_processor_registration),
    ]

    results = []
    for name, test_func in tests:
        try:
            test_func()
            results.append((name, True))
            print(f"✅ {name}")
        except Exception as e:
            results.append((name, False))
            print(f"❌ {name}: {e}")

    all_passed = all(r[1] for r in results)
    print("\n" + ("🎉 所有测试通过！" if all_passed else "⚠️  部分测试失败"))
    sys.exit(0 if all_passed else 1)
```

**Step 2: 运行测试验证失败**

```bash
python test/test_kling_batch.py
```

**Step 3: 实现批量处理器（参考设计文档，约 200 行代码）**

创建 `nodes/Kling/batch_processor.py`，实现 KlingBatchProcessor 类。

**Step 4: 注册批量处理器**

修改 `nodes/Kling/__init__.py`，添加:

```python
from .batch_processor import KlingBatchProcessor

NODE_CLASS_MAPPINGS["KlingBatchProcessor"] = KlingBatchProcessor
NODE_DISPLAY_NAME_MAPPINGS["KlingBatchProcessor"] = "📦 可灵批量处理"
```

**Step 5: 运行测试验证通过**

```bash
python test/test_kling_batch.py
```

**Step 6: 提交**

```bash
git add nodes/Kling/batch_processor.py nodes/Kling/__init__.py test/test_kling_batch.py
git commit -m "feat: 实现可灵批量处理器

- 支持文生视频和图生视频批量处理
- CSV 格式解析和任务路由
- 完整的错误处理和进度报告
- 保存任务列表到 tasks.json
- 添加单元测试

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 9: 创建示例 CSV 文件

**Files:**
- Create: `examples/kling_batch_basic.csv`
- Create: `examples/kling_batch_advanced.csv`
- Create: `examples/kling_batch_image2video.csv`
- Create: `examples/KLING_CSV_GUIDE.md`

**Step 1: 创建基础示例 CSV**

创建 `examples/kling_batch_basic.csv`:

```csv
task_type,prompt,model_name,mode,duration,aspect_ratio,output_prefix
text2video,海边日落，海浪拍打岸边,kling-v1,std,5,16:9,sunset
text2video,城市夜景，车流穿梭,kling-v1,std,5,16:9,city
text2video,森林中的小溪，阳光透过树叶,kling-v1,std,5,16:9,forest
```

**Step 2: 创建高级示例 CSV**

创建 `examples/kling_batch_advanced.csv`:

```csv
task_type,prompt,negative_prompt,model_name,mode,duration,aspect_ratio,cfg_scale,watermark,output_prefix
text2video,美丽的花园，蝴蝶飞舞,模糊、低质量,kling-v2-master,pro,10,16:9,0.7,true,garden
text2video,雪山风景，云雾缭绕,噪点、失真,kling-v2-master,pro,10,9:16,0.6,false,mountain
```

**Step 3: 创建图生视频示例 CSV**

创建 `examples/kling_batch_image2video.csv`:

```csv
task_type,image,prompt,model_name,mode,duration,output_prefix
image2video,https://example.com/image1.jpg,让图片动起来,kling-v1,std,5,img2vid_1
image2video,https://example.com/image2.jpg,添加动态效果,kling-v1,std,5,img2vid_2
```

**Step 4: 创建 CSV 使用指南**

创建 `examples/KLING_CSV_GUIDE.md`（参考设计文档中的完整内容）。

**Step 5: 提交**

```bash
git add examples/kling_batch_*.csv examples/KLING_CSV_GUIDE.md
git commit -m "docs: 添加可灵批量处理 CSV 示例文件

- kling_batch_basic.csv: 基础文生视频示例
- kling_batch_advanced.csv: 高级功能示例
- kling_batch_image2video.csv: 图生视频示例
- KLING_CSV_GUIDE.md: CSV 使用指南

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 10: 创建文档

**Files:**
- Create: `docs/KLING_GUIDE.md`

**Step 1: 创建节点使用指南**

创建 `docs/KLING_GUIDE.md`，包含:
- 节点概述
- 参数说明
- 使用示例
- API 说明
- 常见问题
- 更新日志

**Step 2: 提交**

```bash
git add docs/KLING_GUIDE.md
git commit -m "docs: 添加可灵节点使用指南

- 完整的节点参数说明
- 使用示例和最佳实践
- API 端点和响应格式
- 常见问题解答
- CSV 批量处理指南

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 11: 完整测试验证

**Files:**
- Run all tests

**Step 1: 运行所有单元测试**

```bash
# 工具函数测试
python test/test_kling_utils.py

# 节点测试
python test/test_kling_text2video.py
python test/test_kling_image2video.py
python test/test_kling_query.py
python test/test_kling_andwait.py

# 注册测试
python test/test_kling_registration.py

# 批量处理器测试
python test/test_kling_batch.py
```

预期: 所有测试通过

**Step 2: 运行诊断脚本**

```bash
python diagnose.py
```

预期: 所有 Kling 节点加载成功

**Step 3: 在 ComfyUI 中验证**

1. 重启 ComfyUI
2. 检查控制台日志，确认节点加载
3. 按 Ctrl+Shift+K 打开快速面板
4. 验证"🎞️ 可灵视频生成"分类
5. 添加节点到画布，检查参数和标签

**Step 4: API 集成测试（需要 API key）**

```bash
export KUAI_API_KEY=your_test_key_here

# 测试文生视频
python -c "
from nodes.Kling.kling import KlingText2VideoAndWait
node = KlingText2VideoAndWait()
result = node.run(
    prompt='测试视频',
    model_name='kling-v1',
    mode='std',
    duration='5',
    aspect_ratio='16:9'
)
print('测试成功:', result)
"
```

**Step 5: 最终提交**

```bash
git add -A
git commit -m "test: 完成可灵节点完整测试验证

- 所有单元测试通过
- 节点注册验证通过
- ComfyUI 集成测试通过
- API 集成测试通过（可选）

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## 完成检查清单

- [ ] Task 1: 创建 Kling 工具函数模块
- [ ] Task 2: 实现 KlingText2Video 节点
- [ ] Task 3: 实现 KlingImage2Video 节点
- [ ] Task 4: 实现 KlingQueryTask 节点
- [ ] Task 5: 实现 AndWait 便捷节点
- [ ] Task 6: 注册节点到 __init__.py
- [ ] Task 7: 更新前端面板
- [ ] Task 8: 实现批量处理器
- [ ] Task 9: 创建示例 CSV 文件
- [ ] Task 10: 创建文档
- [ ] Task 11: 完整测试验证

## 预估时间

- Task 1-6: 核心节点实现 - 2-3 小时
- Task 7: 前端更新 - 10 分钟
- Task 8: 批量处理器 - 1 小时
- Task 9-10: 文档和示例 - 1 小时
- Task 11: 测试验证 - 30 分钟

**总计**: 约 4-5 小时

## 注意事项

1. **TDD 原则**: 每个任务都先写测试，再实现功能
2. **频繁提交**: 每个任务完成后立即提交
3. **错误处理**: 所有 API 调用都要有完整的错误处理
4. **中文友好**: 所有用户可见的文本使用中文
5. **代码复用**: 优先使用 Sora2 的通用工具函数
6. **测试覆盖**: 确保所有核心功能都有测试覆盖

## 参考文档

- 设计文档: `docs/plans/2026-03-06-kling-nodes-design.md`
- API 文档: `docs/kling_api-i2v-t2v.md`
- Sora2 参考实现: `nodes/Sora2/sora2.py`
- 项目架构指南: `CLAUDE.md`
