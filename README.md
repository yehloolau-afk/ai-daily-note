# AI 每日小记

> 双端语音记录工具：PC 端悬浮窗 + 移动端 iOS 快捷指令，说完即存，自动写入 Obsidian 表格。

**macOS + iOS · 本地运行 · 不上传任何数据**

---

## 功能概览

| 端 | 触发方式 | 写入文件 |
|---|---|---|
| PC | 点击桌面左侧悬浮窗麦克风 | `AI每日小记.md` |
| 移动端 | 主屏幕快捷指令图标 | `AI每日小记-移动端.md` |

两个文件均为统一格式：`| 日期 | 来源 | 收获 |`，通过 iCloud 实时同步，PC 与手机共享同一个 Obsidian 库。

---

## PC 端使用流程

1. 双击 `/Applications/AI每日小记.app` → 悬浮窗贴左侧边缘出现
2. 点击麦克风 → 自动注入 fn 键，Typeless 语音识别立即启动
3. 说出内容 → 文字自动填入输入框（可手动编辑）
4. 点击「保存到 Obsidian」→ 追加到表格，浮窗收回
5. 顶部栏可拖拽移动窗口位置

## 移动端使用流程

1. 点击主屏幕快捷指令图标
2. 弹出输入框后切换到 Typeless 键盘，开始说话
3. 等 Typeless 停止转录后点确认
4. 自动写入 `AI每日小记-移动端.md`

---

## 安装（PC 端）

```bash
git clone https://github.com/yehloolau-afk/ai-daily-note.git
cd ai-daily-note
python3 -m venv venv
venv/bin/pip install pywebview pyobjc
```

生成应用图标并安装到 `/Applications`：

```bash
venv/bin/python3 make_app.py
```

或直接运行：

```bash
venv/bin/python3 recorder.py
```

## 安装（移动端 iOS 快捷指令）

在 iOS「快捷指令」App 中新建，按以下顺序添加动作：

1. **当前日期**
2. **格式化**（自定义格式：`yyyy-MM-dd`，时间格式：无）
3. **通过「说点什么」请求文本**
4. **替换文本**（查找：换行符，替换：空格，输入：请求输入）
5. **文本**：`| 格式化后的日期 | 移动端 | 更新后的文本 |` + 末尾换行
6. **追加到文本文件** → `yehloo-OB/AI每日小记-移动端.md`，「另起一行」关闭

---

## 前提条件

- macOS 12+（PC 端）
- iOS 16+（移动端）
- [Typeless](https://typeless.app) 已安装（PC 和 iOS 均需）
- PC 端：fn 键设为 Typeless 语音输入快捷键
- PC 端：「系统设置 → 隐私与安全性 → 辅助功能」授权 Terminal
- Obsidian 库通过 iCloud 同步（PC 与 iOS 共用同一个 vault）

---

## 修改保存路径

打开 `recorder.py`，修改顶部常量：

```python
OBSIDIAN_FILE = os.path.expanduser(
    "~/Library/Mobile Documents/iCloud~md~obsidian/Documents/你的vault名/AI每日小记.md"
)
```

---

## 技术架构

```
PC 端
双击 app → recorder.py（pywebview 无边框透明浮窗）
    → Quartz.CGEventPost 注入 fn 键 → Typeless 激活
    → 语音识别 → 填入 textarea
    → 保存 → 追加 | 日期 | PC端 | 内容 | 到 Obsidian

移动端
iOS 快捷指令 → Typeless 键盘语音输入
    → 替换换行符 → 拼装表格行
    → 追加 | 日期 | 移动端 | 内容 | 到 Obsidian
```

**核心依赖：**
- `pywebview 6.x`：WKWebView 渲染 UI，frameless + transparent
- `Quartz.CGEventPost`：硬件级 fn 键注入，触发 Typeless
- `AppKit.NSApplication`：主线程安全退出 + 隐藏 Dock 图标
- `signal.SIGHUP` 忽略：Terminal 关闭后进程持续运行

---

## License

MIT
