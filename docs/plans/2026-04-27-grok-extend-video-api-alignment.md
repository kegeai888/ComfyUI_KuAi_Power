# Grok Extend-Video API Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update the `⚡ Grok 扩展视频（一键）` flow to use the unified `/v1/video/extend` request contract and public parameter options without changing unrelated Grok nodes.

**Architecture:** Keep the change isolated to `GrokExtendVideo` and `GrokExtendVideoAndWait` in `nodes/Grok/grok.py`, plus the narrow tests and workflow assertions that describe their public contract. Preserve node class names and return shapes so existing workflow wiring keeps working while the extend-node request payload and widget options are updated.

**Tech Stack:** Python, requests, ComfyUI node definitions, pytest-style test scripts, JSON workflow fixtures

---

## File map

- Modify: `nodes/Grok/grok.py`
  - Update `GrokExtendVideo.INPUT_TYPES()` and `GrokExtendVideoAndWait.INPUT_TYPES()` so `model` exposes only `grok-video-3`, `size` exposes `720P` and `1080P`, and the default `api_base` is `https://ai.kegeai.top`.
  - Update `GrokExtendVideo.create()` and `GrokExtendVideoAndWait.create_and_wait()` to send the selected `model` value directly unless `custom_model` overrides it.
- Modify: `test/test_grok_nodes.py`
  - Update the extend-node public option test to assert the new model value and size options.
- Modify: `test/test_grok_extend_workflows.py`
  - Update workflow fixture assertions that currently pin extend-node widget values to `grok-video-3 (6秒)`.
- Modify: `workflows/grok_text2video_extend_complete_workflow.json`
  - Update the extend-node saved widget value from `grok-video-3 (6秒)` to `grok-video-3`.
- Modify: `workflows/grok_image2video_extend_complete_workflow.json`
  - Update the extend-node saved widget value from `grok-video-3 (6秒)` to `grok-video-3`.

## Task 1: Lock in the new extend-node public contract with tests

**Files:**
- Modify: `test/test_grok_nodes.py:222-260`
- Modify: `test/test_grok_extend_workflows.py:99-128`

- [ ] **Step 1: Write the failing test updates for model and size options**

Replace the extend-node option test in `test/test_grok_nodes.py` with this version:

```python
def test_extend_model_and_size_options():
    """测试 GrokExtendVideoAndWait 模型与分辨率选项符合统一格式接口"""
    print("\n" + "=" * 60)
    print("测试 6: GrokExtendVideoAndWait 参数选项")
    print("=" * 60)

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS

        node_class = NODE_CLASS_MAPPINGS['GrokExtendVideoAndWait']
        required = node_class.INPUT_TYPES()['required']

        model_options = required['model'][0]
        size_options = required['size'][0]

        expected_models = ['grok-video-3']
        expected_sizes = ['720P', '1080P']

        if model_options != expected_models:
            print("❌ 模型选项不符合预期")
            print(f"   期望: {expected_models}")
            print(f"   实际: {model_options}")
            return False

        if size_options != expected_sizes:
            print("❌ 分辨率选项不符合预期")
            print(f"   期望: {expected_sizes}")
            print(f"   实际: {size_options}")
            return False

        print(f"✅ 模型选项正确: {model_options}")
        print(f"✅ 分辨率选项正确: {size_options}")
        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
```

Also update the `__main__` result list at the bottom of the file so the label matches the new test name:

```python
results.append(("扩展参数选项", test_extend_model_and_size_options()))
```

- [ ] **Step 2: Update the workflow assertions so they expect the new saved widget value**

In `test/test_grok_extend_workflows.py`, replace the two extend-node widget assertions with:

```python
assert text_extend["widgets_values"][2] == "grok-video-3"
```

and

```python
assert image_extend["widgets_values"][2] == "grok-video-3"
```

- [ ] **Step 3: Run the targeted tests to verify they fail before implementation**

Run:

```bash
python test/test_grok_nodes.py
python test/test_grok_extend_workflows.py
```

Expected:
- `test/test_grok_nodes.py` fails because `model` is still `['grok-video-3 (6秒)']` and `size` is still `['720P']`
- `test/test_grok_extend_workflows.py` fails because the workflow fixtures still store `grok-video-3 (6秒)`

- [ ] **Step 4: Commit the red tests**

```bash
git add test/test_grok_nodes.py test/test_grok_extend_workflows.py
git commit -m "test: pin grok extend unified contract"
```

## Task 2: Implement the node contract change in `nodes/Grok/grok.py`

**Files:**
- Modify: `nodes/Grok/grok.py:945-1056`
- Test: `test/test_grok_nodes.py`

- [ ] **Step 1: Update the extend-node input definitions**

In `GrokExtendVideo.INPUT_TYPES()`, change the `required` and `optional` entries to this shape:

```python
"required": {
    "prompt": ("STRING", {"default": "", "multiline": True, "tooltip": "扩展视频提示词"}),
    "task_id": ("STRING", {"default": "", "tooltip": "待扩展的视频任务ID"}),
    "model": (["grok-video-3"], {"default": "grok-video-3", "tooltip": "选择 Grok 模型"}),
    "start_time": ("INT", {"default": 10, "min": 1, "max": 9999, "tooltip": "从第几秒开始扩展"}),
    "aspect_ratio": (["2:3", "3:2", "1:1"], {"default": "3:2", "tooltip": "视频宽高比"}),
    "size": (["720P", "1080P"], {"default": "720P", "tooltip": "视频分辨率"}),
    "upscale": ("BOOLEAN", {"default": False, "tooltip": "是否启用放大"}),
    "api_key": ("STRING", {"default": "", "tooltip": "API密钥（留空使用环境变量 KUAI_API_KEY）"}),
},
"optional": {
    "api_base": ("STRING", {"default": "https://ai.kegeai.top", "tooltip": "API端点地址"}),
    "custom_model": ("STRING", {"default": "", "tooltip": "自定义模型（留空使用下拉模型）"}),
}
```

Make the same `model`, `size`, and `api_base` changes in `GrokExtendVideoAndWait.INPUT_TYPES()`.

- [ ] **Step 2: Remove the old display-label parsing from `GrokExtendVideo.create()`**

Inside `GrokExtendVideo.create()`, replace:

```python
actual_model = model.split(" (")[0] if " (" in model else model
effective_model = (custom_model or "").strip() or actual_model
```

with:

```python
effective_model = (custom_model or "").strip() or model
```

Keep the existing payload shape:

```python
payload = {
    "model": effective_model,
    "prompt": prompt,
    "task_id": task_id,
    "aspect_ratio": aspect_ratio,
    "size": size,
    "start_time": normalized_start_time,
    "upscale": bool(upscale),
}
```

Do not add any new request fields.

- [ ] **Step 3: Keep output compatibility while leaving duration behavior stable**

Do not change the return tuple shapes. Leave this duration calculation intact for now:

```python
total_duration = normalized_start_time + (6 if effective_model == "grok-video-3" else 6)
```

This task is about request-contract alignment only.

- [ ] **Step 4: Run the targeted node test to verify the implementation passes**

Run:

```bash
python test/test_grok_nodes.py
```

Expected:
- PASS for the extend-node option test with model `['grok-video-3']`
- PASS for the size option test with `['720P', '1080P']`

- [ ] **Step 5: Commit the node implementation**

```bash
git add nodes/Grok/grok.py test/test_grok_nodes.py
git commit -m "fix: align grok extend node contract"
```

## Task 3: Update workflow fixtures to match the new node contract

**Files:**
- Modify: `workflows/grok_text2video_extend_complete_workflow.json`
- Modify: `workflows/grok_image2video_extend_complete_workflow.json`
- Test: `test/test_grok_extend_workflows.py`

- [ ] **Step 1: Update the saved extend-node widget values in both workflow fixtures**

In `workflows/grok_text2video_extend_complete_workflow.json`, change the extend-node `widgets_values` model entry from:

```json
"grok-video-3 (6秒)"
```

to:

```json
"grok-video-3"
```

In `workflows/grok_image2video_extend_complete_workflow.json`, make the same replacement for the `GrokExtendVideoAndWait` node.

- [ ] **Step 2: Run the workflow test to verify the fixtures now match the new contract**

Run:

```bash
python test/test_grok_extend_workflows.py
```

Expected:
- PASS for both workflow tests
- PASS for the assertions checking the extend-node model widget value

- [ ] **Step 3: Run both targeted test files together as the final verification pass**

Run:

```bash
python test/test_grok_nodes.py && python test/test_grok_extend_workflows.py
```

Expected:
- Both commands exit with code 0
- No assertion still references `grok-video-3 (6秒)` for the extend node surface

- [ ] **Step 4: Commit the fixture alignment**

```bash
git add workflows/grok_text2video_extend_complete_workflow.json workflows/grok_image2video_extend_complete_workflow.json test/test_grok_extend_workflows.py
git commit -m "test: update grok extend workflow fixtures"
```

## Self-review checklist

- Spec coverage:
  - Unified `/v1/video/extend` request fields are preserved in Task 2.
  - Public `model` option change is covered in Tasks 1 and 2.
  - `size` option expansion is covered in Tasks 1 and 2.
  - Workflow compatibility checks are covered in Task 3.
  - Scope isolation is preserved by only touching the extend nodes, their tests, and their workflow fixtures.
- Placeholder scan:
  - No `TODO`, `TBD`, or vague “write tests” steps remain.
- Type consistency:
  - `model` is consistently `grok-video-3`.
  - `size` is consistently `['720P', '1080P']`.
  - Return tuple shapes remain unchanged throughout the plan.
