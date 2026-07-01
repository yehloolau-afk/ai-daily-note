# AI 每日小记

> 常驻桌面左侧的语音输入小工具，点击麦克风自动触发 Typeless，说完一键存入 Obsidian。

**macOS 专属 · 本地运行 · 不上传任何数据**

---

## 使用流程

1. 双击 `启动记录器.command` → 悬浮窗贴左侧边缘出现，Terminal 自动关闭
2. 点击麦克风按钮 → 自动注入 fn 键，Typeless 语音识别立即启动
3. 说出收获 → 文字自动填入输入框（可手动编辑）
4. 点击「保存到 Obsidian」→ 追加到 `AI收获记录.md` 表格，浮窗收回
5. 点击 ✕ → 关闭浮窗

## 安装

```bash
git clone https://github.com/yehloolau-afk/ai-daily-note.git
cd ai-daily-note
python3 -m venv venv
venv/bin/pip install pywebview pyobjc
```

然后双击 `启动记录器.command`，或手动运行：

```bash
venv/bin/python3 recorder.py
```

## 前提条件

- macOS 12+
- [Typeless](https://typeless.app) 已安装，fn 键设为语音输入快捷键
- 「系统设置 → 隐私与安全性 → 辅助功能」授权 Terminal（CGEventPost 注入按键需要）

## 修改保存位置

打开 `recorder.py`，修改第一个常量：

```python
OBSIDIAN_FILE = os.path.expanduser(
    "~/Documents/你的路径/AI收获记录.md"
)
```

## 技术架构

```
双击启动
    ↓
启动记录器.command（后台运行 + 自动关 Terminal）
    ↓
recorder.py（pywebview 无边框透明浮窗，贴左侧，置顶）
    ↓
点击麦克风 → Quartz.CGEventPost 注入 fn 键 → Typeless 激活
    ↓
Typeless 语音识别 → 文字自动填入 textarea
    ↓
点击保存 → 追加到 AI收获记录.md（Markdown 表格）
```

- `pywebview 6.x`：WKWebView 渲染 UI，frameless + transparent
- `Quartz.CGEventPost`：硬件级 fn 键注入，触发 Typeless
- `AppKit.NSApplication.performSelectorOnMainThread_`：主线程安全退出
- `signal.SIGHUP` 忽略：Terminal 关闭后进程持续运行

## License

MIT
