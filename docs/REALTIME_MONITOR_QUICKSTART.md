# 实时批量监控 - 快速启动指南

## 🚀 5 分钟快速上手

### 1. 启动 ComfyUI
```bash
cd /root/ComfyUI
python main.py
```

### 2. 打开工作流
在浏览器中打开 ComfyUI，加载工作流：
```
/root/ComfyUI/user/default/workflows/0-批量veo3-grok3/grok批量图生视频.json
```

### 3. 找到实时监控节点
在工作流画布中找到：
- **节点 14**: `📡 实时批量监控（WebSocket推送）`
- 位置：右侧，坐标 [2150, 100]

### 4. 配置参数（可选）
默认配置已经很好，如需调整：
- **启用监控**: `true`（默认）
- **刷新间隔**: `3.0` 秒（默认）
- **最多显示任务数**: `10`（默认）
- **最多显示日志条数**: `50`（默认）

### 5. 执行工作流
1. 配置节点 1（`BatchImageUploader`）的图片目录
2. 配置节点 11（`PrimitiveString`）的 API Key
3. 点击 "Queue Prompt" 执行工作流
4. **浮动面板自动出现在右上角** 🎉

## 📊 浮动面板功能

### 实时显示
- ✅ 总体进度条（动画效果）
- ✅ 状态统计（✓ 成功、✗ 失败、⟳ 处理中、○ 等待中）
- ✅ 统计信息（平均耗时、成功率、预计剩余时间）
- ✅ 最新任务列表（最新 5 个）
- ✅ 详细日志（最新 20 条，自动滚动）

### 面板操作
- **拖动**: 点击标题栏拖动到任意位置
- **关闭**: 点击右上角 `×` 关闭面板
- **自动隐藏**: 任务完成后 3 秒自动隐藏

## 🔍 日志示例

```
[14:05:30] [8] 任务准备就绪 | 提示词: 生成产品视频...
[14:05:31] [8] 任务已提交 | task_id: abc123 | 模型: grok-video-1.5
[14:05:34] [8] 轮询中 3/600s | 状态: processing
[14:05:37] [8] 轮询中 6/600s | 状态: processing
...
[14:06:00] [8] 生成完成 | 开始下载: https://...
[14:06:05] [8] 下载完成 | 保存至: output/grok/grok_8_xxx.mp4
```

## ⚙️ 高级配置

### 更快的刷新（1 秒）
```json
{
  "enable": true,
  "refresh_rate": 1.0,
  "max_tasks": 20,
  "max_logs": 100
}
```

### 显示更多日志（详细模式）
```json
{
  "enable": true,
  "refresh_rate": 2.0,
  "max_tasks": 50,
  "max_logs": 200
}
```

## 🐛 常见问题

### Q: 浮动面板不出现？
**A**:
1. 检查 `enable` 参数是否为 `true`
2. 刷新浏览器页面
3. 查看 ComfyUI 控制台是否有错误

### Q: 进度不更新？
**A**:
1. 确认批量处理器正在运行
2. 检查状态文件：`ComfyUI/temp/batch_process_state.json`
3. 查看控制台日志：`[RealtimeBatchMonitor] 监控线程已启动`

### Q: 如何停止监控？
**A**:
1. 将 `enable` 参数设置为 `false`
2. 重新执行节点
3. 或者直接关闭浮动面板

## 📚 更多文档

- **使用指南**: `docs/REALTIME_MONITOR_GUIDE.md`
- **实施总结**: `docs/REALTIME_MONITOR_IMPLEMENTATION.md`
- **完整报告**: `docs/REALTIME_MONITOR_COMPLETE_REPORT.md`

## 🎉 开始使用

现在你已经准备好了！启动 ComfyUI，打开工作流，执行节点，享受实时监控带来的便利吧！

---

**有问题？** 运行测试脚本：
```bash
python test/test_realtime_monitor.py
```
