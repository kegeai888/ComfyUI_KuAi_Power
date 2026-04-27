# 2026-04-27 Grok extend-video API alignment design

## Goal
Align the `⚡ Grok 扩展视频（一键）` flow with the `/v1/video/extend` unified request format while keeping the scope limited to the Grok extend nodes.

## Scope
This design only covers:
- `GrokExtendVideo`
- `GrokExtendVideoAndWait`
- Their targeted tests for public parameter options and behavior

This design does not unify model values across all other Grok nodes. That broader cleanup should be handled as a separate follow-up task.

## Current mismatch
The current extend-video implementation in `nodes/Grok/grok.py` still uses older public parameter constraints:
- `model` only exposes `grok-video-3 (6秒)`
- `size` only exposes `720P`
- the implementation still strips display text into a request model value
- the default API base still points at `https://api.kegeai.top`

The new API documentation for `POST /v1/video/extend` expects a unified JSON body with these fields:
- `model`
- `prompt`
- `task_id`
- `aspect_ratio`
- `size`
- `start_time`
- `upscale`

Required fields are `model`, `prompt`, `task_id`, and `start_time`.

## Recommended approach
Apply a focused alignment only to the extend-video nodes.

### Public parameter design
For both `GrokExtendVideo` and `GrokExtendVideoAndWait`:
- `model` dropdown exposes only `grok-video-3`
- `size` dropdown exposes `720P` and `1080P`
- `aspect_ratio` keeps `2:3`, `3:2`, `1:1`
- `start_time` remains an integer input and must be greater than 0
- `upscale` remains a boolean input
- `custom_model` remains available as an optional override for advanced use

### Request construction
The request payload sent to `/v1/video/extend` should strictly use the unified fields:
- `model`
- `prompt`
- `task_id`
- `aspect_ratio`
- `size`
- `start_time`
- `upscale`

Behavioral rules:
- If `custom_model` is provided, send that exact value as `model`
- Otherwise send the selected dropdown value directly
- Do not parse or transform a display label like `grok-video-3 (6秒)` because that label is no longer part of this node’s public input

### API base handling
Change the default `api_base` for these extend nodes to the unified API host used by the rest of the current API documentation.

## Compatibility strategy
Keep the node output shape unchanged so existing downstream workflow links remain valid:
- create node still returns task id, status, enhanced prompt, status update time, video duration
- one-click node still returns task id, status, video URL, enhanced prompt, video duration

This keeps workflow graph compatibility while updating the request contract.

## Duration behavior
For this focused fix, keep the current duration return behavior stable instead of redesigning how post-extension duration is computed. The goal here is API contract alignment, not duration semantics redesign.

If duration semantics need to be revisited later, do that in a dedicated follow-up tied to the existing Grok extend-video behavior decisions.

## Testing
Update targeted tests so they validate the new public contract for the extend nodes:
- model options should be `['grok-video-3']`
- size options should include `['720P', '1080P']`
- existing extend workflow tests should continue to validate node presence and basic configuration, but any assertion pinned to `grok-video-3 (6秒)` for the extend node should be updated to `grok-video-3`

Avoid broad test churn outside the extend-node surface.

## Risks and mitigations
### Risk: existing saved workflows may show old widget values
Mitigation:
- Keep the node class names and outputs unchanged
- Limit the public input change to the extend nodes only
- Update targeted workflow tests to catch obvious config drift

### Risk: API host inconsistency across nodes
Mitigation:
- Only update the extend-node default in this change
- Leave repo-wide API host unification for the separate broader Grok cleanup

## Success criteria
This design is successful when:
1. The one-click extend node sends the documented unified request body to `/v1/video/extend`
2. The node’s `model` public option is `grok-video-3`
3. The node’s `size` options include `720P` and `1080P`
4. Extend-node tests are updated and pass for the new public contract
5. No unrelated Grok nodes are changed in this task
