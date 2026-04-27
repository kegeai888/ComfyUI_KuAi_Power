# Grok Extend Workflow Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore the bundled Grok text-to-video extend workflow to auto-chain the first segment task ID and duration into the extend node, and surface a clearer Chinese error when extend requests fail with `task_origin_not_exist`.

**Architecture:** Keep the code change narrow. Update only the extend-node error mapping in `nodes/Grok/grok.py`, then repair the user workflow JSON so its links match the intended closed-loop data flow. Prove the behavior with targeted tests: one unit-style node test for the friendly error and one workflow-structure test for the restored links.

**Tech Stack:** Python, requests, ComfyUI workflow JSON, repository test scripts

---

## File structure

- Modify: `nodes/Grok/grok.py`
  - Responsibility: map the specific backend extend failure `task_origin_not_exist` to a clearer Chinese `RuntimeError` while preserving backend detail for debugging.
- Modify: `test/test_grok_nodes.py`
  - Responsibility: add a focused regression test for the extend-node error message and keep the existing public-option checks intact.
- Modify: `test/test_grok_extend_workflows.py`
  - Responsibility: add a test for the user workflow JSON so the text-to-video workflow is pinned to the closed-loop `task_id` and `start_time` wiring.
- Modify: `/root/ComfyUI/user/default/workflows/0-ID-gork视频-扩展视频.json`
  - Responsibility: restore the default user workflow to automatic chaining from first-segment outputs into the extend node.

### Task 1: Add the failing extend-node error test

**Files:**
- Modify: `test/test_grok_nodes.py`
- Test: `test/test_grok_nodes.py`

- [ ] **Step 1: Write the failing test**

Add these imports near the top of `test/test_grok_nodes.py` after the existing `import os` line:

```python
from unittest.mock import Mock, patch

import requests
```

Add this test function above `test_extend_model_and_size_options()`:

```python
def test_extend_task_origin_not_exist_message():
    """测试扩展节点在原任务不存在时给出更明确提示"""
    print("\n" + "=" * 60)
    print("测试 6: GrokExtendVideo 原任务不存在提示")
    print("=" * 60)

    try:
        from nodes.Grok import NODE_CLASS_MAPPINGS

        node = NODE_CLASS_MAPPINGS['GrokExtendVideo']()

        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 400
        mock_response.text = '{"code":"task_not_exist","message":"task_origin_not_exist","data":null}'
        mock_response.json.return_value = {
            "code": "task_not_exist",
            "message": "task_origin_not_exist",
            "data": None,
        }

        with patch('nodes.Grok.grok.requests.post', return_value=mock_response):
            try:
                node.create(
                    prompt="继续扩展镜头",
                    task_id="task_invalid_origin",
                    model="grok-video-3",
                    start_time=10,
                    aspect_ratio="2:3",
                    size="720P",
                    upscale=False,
                    api_key="test-key",
                    api_base="https://ai.kegeai.top",
                    custom_model="",
                )
                print("❌ 应该抛出 RuntimeError，但没有抛出")
                return False
            except RuntimeError as e:
                message = str(e)
                checks = [
                    "原始视频任务不存在或不可扩展" in message,
                    "task_id 是否来自首段视频节点的真实输出" in message,
                    "同一个 API 地址" in message,
                    "同一账号" in message,
                    "task_origin_not_exist" in message,
                ]

                if all(checks):
                    print("✅ 错误提示包含用户指导和后端细节")
                    print(f"   错误信息: {message}")
                    return True

                print("❌ 错误提示不完整")
                print(f"   实际信息: {message}")
                return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
```

Update the printed numbering and results list in `__main__` so the new test runs before the model-options test:

```python
    results.append(("原任务不存在提示", test_extend_task_origin_not_exist_message()))
    results.append(("扩展模型和分辨率选项", test_extend_model_and_size_options()))
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python test/test_grok_nodes.py
```

Expected: FAIL in `test_extend_task_origin_not_exist_message` because the current message is only `Grok 扩展视频失败: ...task_origin_not_exist...` and does not contain the user guidance strings.

- [ ] **Step 3: Write the minimal code to make the test pass**

Do not edit production code in this task. Leave the failure in place and move to Task 2 after confirming the regression is captured.

- [ ] **Step 4: Run the single test again to confirm the same failure**

Run:

```bash
python test/test_grok_nodes.py
```

Expected: same FAIL in `test_extend_task_origin_not_exist_message`.

- [ ] **Step 5: Commit**

```bash
git add test/test_grok_nodes.py
git commit -m "test: pin grok extend invalid origin guidance"
```

### Task 2: Implement the targeted error guidance

**Files:**
- Modify: `nodes/Grok/grok.py:941-1031`
- Test: `test/test_grok_nodes.py`

- [ ] **Step 1: Write the failing implementation hook**

In `nodes/Grok/grok.py`, add this helper function above `class GrokExtendVideo`:

```python
def explain_grok_extend_error(detail: str) -> str:
    if "task_origin_not_exist" not in detail:
        return f"Grok 扩展视频失败: {detail}"

    return (
        "Grok 扩展视频失败：原始视频任务不存在或不可扩展。"
        "请确认 task_id 是否来自首段视频节点的真实输出、首段生成和扩展是否使用同一个 API 地址、"
        "以及当前 API Key 是否属于创建该任务的同一账号。"
        f" 后端详情: {detail}"
    )
```

Then replace the error raise inside `GrokExtendVideo.create()`:

```python
            if resp.status_code >= 400:
                detail = extract_error_message_from_response(resp)
                raise RuntimeError(explain_grok_extend_error(detail))
```

Do not change any other request fields, return values, or polling logic.

- [ ] **Step 2: Run test to verify it now passes**

Run:

```bash
python test/test_grok_nodes.py
```

Expected: PASS for `test_extend_task_origin_not_exist_message` and the existing extend option checks. API-backed tests may print skip warnings if `KUAI_API_KEY` or `GROK_TEST_TASK_ID` are unset.

- [ ] **Step 3: Write the minimal code to keep the test green**

No additional production changes are needed beyond the helper and the single call-site replacement above.

- [ ] **Step 4: Run the focused regression command**

Run:

```bash
python test/test_grok_nodes.py
```

Expected: same PASS result as Step 2.

- [ ] **Step 5: Commit**

```bash
git add nodes/Grok/grok.py test/test_grok_nodes.py
git commit -m "fix: clarify grok extend invalid origin error"
```

### Task 3: Add the failing user-workflow structure test

**Files:**
- Modify: `test/test_grok_extend_workflows.py`
- Test: `test/test_grok_extend_workflows.py`

- [ ] **Step 1: Write the failing test**

At the top of `test/test_grok_extend_workflows.py`, add a constant for the user workflow:

```python
USER_TEXT_WORKFLOW = Path("/root/ComfyUI/user/default/workflows/0-ID-gork视频-扩展视频.json")
```

Add these helpers below `_load()`:

```python
def _load_absolute(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _assert_no_node(nodes_by_type, node_type: str):
    nodes = nodes_by_type.get(node_type, [])
    assert len(nodes) == 0, f"{node_type} 节点数量应为 0，实际为 {len(nodes)}"
```

Add this test above `test_grok_text2video_extend_complete_workflow()`:

```python
def test_user_text2video_extend_workflow_is_closed_loop():
    data = _load_absolute(USER_TEXT_WORKFLOW)
    nodes_by_type = _nodes_by_type(data)

    text_node = _assert_single_node(nodes_by_type, "GrokText2VideoAndWait")
    extend_node = _assert_single_node(nodes_by_type, "GrokExtendVideoAndWait")
    _assert_no_node(nodes_by_type, "CR Text")

    task_input = extend_node["inputs"][1]
    duration_input = extend_node["inputs"][3]

    assert task_input["name"] == "task_id"
    assert duration_input["name"] == "start_time"

    task_link = _find_link(data.get("links", []), text_node["id"], 0, extend_node["id"], 1)
    duration_link = _find_link(data.get("links", []), text_node["id"], 4, extend_node["id"], 3)

    assert task_link is not None, "缺少首段任务ID到扩展节点 task_id 的连线"
    assert duration_link is not None, "缺少首段视频时长到扩展节点 start_time 的连线"
    assert extend_node["widgets_values"][2] == "grok-video-3", "扩展节点模型值应为 grok-video-3"
    assert extend_node["widgets_values"][8] == "https://ai.kegeai.top", "扩展节点 API 地址应为 https://ai.kegeai.top"
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python test/test_grok_extend_workflows.py
```

Expected: FAIL because the current user workflow still contains one `CR Text` node and wires its output into the extend node instead of wiring from `GrokText2VideoAndWait`.

- [ ] **Step 3: Write the minimal test-only change**

Do not edit the workflow JSON in this task. Leave the failure in place and move to Task 4 after confirming the regression is captured.

- [ ] **Step 4: Run the same workflow test again**

Run:

```bash
python test/test_grok_extend_workflows.py
```

Expected: same FAIL caused by the `CR Text` node and missing closed-loop links.

- [ ] **Step 5: Commit**

```bash
git add test/test_grok_extend_workflows.py
git commit -m "test: pin user grok extend workflow loop"
```

### Task 4: Restore the user workflow closed-loop wiring

**Files:**
- Modify: `/root/ComfyUI/user/default/workflows/0-ID-gork视频-扩展视频.json`
- Test: `test/test_grok_extend_workflows.py`

- [ ] **Step 1: Write the minimal workflow update**

In `/root/ComfyUI/user/default/workflows/0-ID-gork视频-扩展视频.json`, make these structural changes:

1. Remove the `CR Text` node with `id: 40`.
2. Remove link `[60, 40, 1, 28, 1, "STRING"]`.
3. Add one `GrokText2VideoAndWait` node that produces `任务ID` on output slot `0` and `视频时长` on output slot `4`.
4. Add a link from that node output slot `0` to `GrokExtendVideoAndWait` input slot `1`.
5. Add a link from that node output slot `4` to `GrokExtendVideoAndWait` input slot `3`.
6. Update the extend node widget values so the model entry is `"grok-video-3"` and the API base entry matches the node default `"https://ai.kegeai.top"`.

Use this target shape for the extend-node inputs involved in the closed loop:

```json
{
  "localized_name": "task_id",
  "name": "task_id",
  "type": "STRING"
},
{
  "localized_name": "start_time",
  "name": "start_time",
  "type": "INT"
}
```

After editing, the workflow must have no `CR Text` nodes and must satisfy the new user-workflow test from Task 3.

- [ ] **Step 2: Run workflow test to verify it now passes**

Run:

```bash
python test/test_grok_extend_workflows.py
```

Expected: PASS for the new user workflow test and the existing bundled workflow assertions.

- [ ] **Step 3: Write the minimal workflow-only code to keep the test green**

Do not change any Python production files in this task. Keep the change limited to the workflow JSON plus the already-added test file.

- [ ] **Step 4: Run the workflow test a second time**

Run:

```bash
python test/test_grok_extend_workflows.py
```

Expected: same PASS result as Step 2.

- [ ] **Step 5: Commit**

```bash
git add /root/ComfyUI/user/default/workflows/0-ID-gork视频-扩展视频.json test/test_grok_extend_workflows.py
git commit -m "fix: restore grok extend workflow loop"
```

### Task 5: Final verification

**Files:**
- Modify: none
- Test: `test/test_grok_nodes.py`, `test/test_grok_extend_workflows.py`

- [ ] **Step 1: Run the targeted regression suite**

Run:

```bash
python test/test_grok_nodes.py && python test/test_grok_extend_workflows.py
```

Expected:
- `test/test_grok_nodes.py` prints PASS for the invalid-origin guidance test and the extend option test; API-backed cases may skip if credentials are unset.
- `test/test_grok_extend_workflows.py` prints PASS for the user workflow closed-loop test and the bundled workflow assertions.

- [ ] **Step 2: Inspect final diff**

Run:

```bash
git diff -- nodes/Grok/grok.py test/test_grok_nodes.py test/test_grok_extend_workflows.py /root/ComfyUI/user/default/workflows/0-ID-gork视频-扩展视频.json
```

Expected: diff shows only the targeted error-message helper, the new regression tests, and the closed-loop workflow wiring updates.

- [ ] **Step 3: Write the release-ready state check**

Confirm that only these four files are intentionally changed for the feature:

```text
nodes/Grok/grok.py
test/test_grok_nodes.py
test/test_grok_extend_workflows.py
/root/ComfyUI/user/default/workflows/0-ID-gork视频-扩展视频.json
```

If any other tracked files differ, inspect them before committing.

- [ ] **Step 4: Run git status to verify the final set**

Run:

```bash
git status --short
```

Expected: only the four planned files are modified, plus any unrelated pre-existing untracked docs the engineer intentionally leaves alone.

- [ ] **Step 5: Commit**

```bash
git add nodes/Grok/grok.py test/test_grok_nodes.py test/test_grok_extend_workflows.py /root/ComfyUI/user/default/workflows/0-ID-gork视频-扩展视频.json
git commit -m "test: verify grok extend workflow recovery"
```
