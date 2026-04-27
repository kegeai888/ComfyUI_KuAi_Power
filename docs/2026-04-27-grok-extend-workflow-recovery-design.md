# 2026-04-27 Grok extend workflow recovery and validation design

## Goal
Restore the Grok text-to-video extend workflow to the intended closed-loop wiring so the extend node automatically consumes the first segment task ID and duration, while adding clearer node-side guidance when a manually supplied `task_id` cannot be extended.

## Scope
This design only covers:
- the user workflow file `0-ID-gork视频-扩展视频.json`
- targeted error-message handling in `nodes/Grok/grok.py` for Grok extend-video failures
- the narrow tests that describe the workflow wiring and extend-node error behavior

This design does not cover:
- broader Grok node refactors
- repo-wide API host unification
- extra preflight API queries before extend requests

## Problem summary
The current user workflow no longer follows the intended closed-loop shape. Instead of wiring the first segment node outputs into the extend node, it injects a manually typed `task_id` through a text node. That makes the default path fragile and allows stale, cross-environment, or unauthorized task IDs to reach `/v1/video/extend`.

When that happens, the backend returns `task_origin_not_exist`, but the current node error surfaces mostly raw backend detail. The user has to infer that the likely causes are an invalid source task, mismatched API host, or mismatched account context.

## Recommended approach
Use a closed-loop-first workflow and keep manual `task_id` entry only as an advanced capability at the node layer.

### Why this approach
- It restores the safest default path without removing flexibility from the node implementation.
- It keeps the runtime contract stable for existing nodes and downstream links.
- It fixes the user-facing failure mode with minimal code churn.

## Design

### 1. Workflow structure
Update the workflow so the first-segment generation node drives the extend node directly:
- `GrokText2VideoAndWait` output `任务ID` connects to `GrokExtendVideoAndWait.task_id`
- `GrokText2VideoAndWait` output `视频时长` connects to `GrokExtendVideoAndWait.start_time`

Keep the manual configuration fields that are still legitimate user choices:
- extend prompt
- model
- aspect ratio
- size
- upscale
- API key
- API base
- wait settings

Remove the current manual `CR Text` bridge for `task_id` from the default workflow so the normal path cannot accidentally point at an unrelated task.

### 2. Extend-node validation guidance
Keep the `GrokExtendVideo` and `GrokExtendVideoAndWait` public input/output shapes unchanged.

When the extend request fails with backend detail indicating `task_origin_not_exist`, convert that into a clearer Chinese error message that tells the user to verify:
1. the `task_id` came from the actual output of the first-segment video node
2. the original generation step and the extend step are using the same `api_base`
3. the current `api_key` belongs to the same account or permission context that created the original task

Append the backend detail after the user-facing explanation so debugging data is still preserved.

All other error behavior should remain as-is.

### 3. Compatibility
Preserve these contracts:
- node class names remain unchanged
- extend node inputs and outputs remain unchanged
- successful extend requests follow the existing code path
- downstream workflow consumers continue receiving the same output slots and types

This keeps the change safe for existing saved graphs while improving the default workflow and the known failure case.

## Testing
Update or add only the tests directly tied to this behavior:
- workflow test coverage should assert that the text-to-video workflow wires first-segment `任务ID` and `视频时长` into the extend node
- workflow coverage should no longer depend on the manual `CR Text` task-id bridge in the default workflow
- node tests should verify that a `task_origin_not_exist` backend response produces the clearer Chinese guidance while preserving backend detail
- run the targeted Grok workflow and node tests

## Risks and mitigations

### Risk: saved local workflow variants may still use manual task IDs
Mitigation:
- only the bundled workflow is changed; node compatibility remains intact
- the improved error message helps users diagnose old manual workflows

### Risk: over-matching unrelated backend errors
Mitigation:
- only special-case the known `task_origin_not_exist` failure text
- leave all other errors unchanged

## Success criteria
This design is successful when:
1. the bundled text-to-video extend workflow automatically chains first-segment task ID and duration into the extend node
2. the default workflow no longer relies on a manually typed task ID bridge
3. invalid extend origins returning `task_origin_not_exist` produce a clearer Chinese error message
4. existing extend-node public interfaces remain unchanged
5. targeted Grok workflow and node tests pass
