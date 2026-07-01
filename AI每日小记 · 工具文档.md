# AI 小灵感 · 工具文档

| | |
|---|---|
| **本地路径** | `For团队AI工具/AI收获记录/` |
| **启动方式** | 双击 `启动记录器.command` |
| **保存位置** | `~/Documents/滴滴重要同步-OB/yehloo-OB/AI收获记录.md` |
| **当前状态** | 本地可用 · 左侧悬浮窗常驻 |

---

## 是什么

一个常驻桌面左侧的悬浮输入窗口，用于随时捕捉 AI 工具使用中的洞察与收获，语音输入、一键保存到 Obsidian。

---

## 使用流程

1. **双击** `启动记录器.command` → 悬浮窗出现在屏幕左侧，Terminal 自动关闭
2. **点击麦克风按钮** → 自动触发 Typeless 开始录音
3. **说出收获** → 识别文字出现在输入框（可手动编辑）
4. **点击「保存到 Obsidian」** → 自动追加到 `AI收获记录.md` 表格，窗口收回
5. **点击 ✕** → 关闭悬浮窗（下次使用再双击启动）

---

## 文件结构

```
AI收获记录/
├── recorder.py           主程序（pywebview 浮窗 + 语音触发 + 文件写入）
├── 启动记录器.command    双击启动脚本（自动关闭 Terminal）
├── venv/                 Python 虚拟环境（含 pywebview、pynput）
└── AI小灵感 · 工具文档.md  本文档
```

**保存文件**（工具目录外）：
```
yehloo-OB/
└── AI收获记录.md         Markdown 表格，所有记录按日期追加
```

---

## 技术架构

```
双击启动
    ↓
启动记录器.command（后台运行，自动关 Terminal）
    ↓
recorder.py（pywebview 浮窗，贴左侧边缘，置顶）
    ↓
点击麦克风 → CGEventPost 注入 fn 键 → Typeless 激活
    ↓
Typeless 语音识别 → 文字打入输入框（textarea）
    ↓
点击保存 → 追加到 AI收获记录.md
```

**技术栈**：
- `pywebview 6.x`：白色无边框悬浮窗，WKWebView 渲染
- `Quartz.CGEventPost`：注入 fn 键硬件事件触发 Typeless
- `AppKit.NSApplication.performSelectorOnMainThread_`：线程安全退出
- Markdown 表格追加写入（`| 日期 | 收获 |` 格式）

---

## 浮窗设计

| 状态 | 尺寸 | 说明 |
|------|------|------|
| 收起态 | 72 × 96 px | 左侧边缘，麦克风 + 关闭按钮 |
| 展开态 | 260 × 自适应 px | 展开后显示输入框，随内容自动变高 |

- 白色背景，右侧圆角（左边贴边）
- 始终置顶，不干扰其他窗口操作
- 输入框高度随文字内容自动伸展

---

## 注意事项

- **首次运行**：系统可能弹出「辅助功能权限」提示，需在「系统设置 → 隐私与安全性 → 辅助功能」中允许 Terminal（CGEventPost 注入按键需要此权限）
- **Typeless 快捷键**：当前配置为 `fn` 键，如需修改在 `recorder.py` 的 `trigger_typeless` 方法中调整 `key code 63`
- **换行问题**：语音识别结果中的换行符会自动替换为空格，确保 Markdown 表格格式正确
- **重复启动**：如已有一个悬浮窗在运行，再次双击会启动第二个实例，建议先关闭旧的再启动

---

## 本地运行（手动方式）

```bash
cd "/Users/didi/Documents/滴滴重要同步-OB/yehloo-OB/For团队AI工具/AI收获记录"
venv/bin/python3 recorder.py
```

---

## 后续迭代方向

1. **标签分类**：保存时可选标签（工具洞察 / 产品思考 / 技术学习）
2. **开机自启**：配置 launchd LaunchAgent，登录后自动常驻
3. **历史回顾**：浮窗内展示最近 5 条记录
4. **多维度保存**：除 Obsidian 外，同步写入飞书文档或 Notion
