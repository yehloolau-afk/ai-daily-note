#!/usr/bin/env python3
"""AI 收获记录器 — 浮窗 + Typeless 语音 + 保存到 Obsidian"""

import webview
import threading
import os
import signal
import sys
import time

# 忽略终端关闭信号，让进程在 Terminal 关掉后继续运行
signal.signal(signal.SIGHUP, signal.SIG_IGN)
import subprocess
from datetime import datetime

OBSIDIAN_FILE = os.path.expanduser(
    "~/Documents/滴滴重要同步-OB/yehloo-OB/AI收获记录.md"
)

HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }

  body {
    background: transparent;
    font-family: -apple-system, "PingFang SC", sans-serif;
    overflow: hidden;
  }

  #drag { display: none; }
  /* div 元素用 CSS 拖拽区；button/textarea/交互 div 明确排除 */
  .card-mini, .card-expanded { -webkit-app-region: drag; }
  .mic-btn, .close-btn-mini, .close-btn,
  .btn-cancel, .btn-save, textarea { -webkit-app-region: no-drag; }

  /* ── 收起态：正方形卡片 ── */
  .card-mini {
    width: 72px;
    background: #FFFFFF;
    border-radius: 0 16px 16px 0;
    border: 1px solid rgba(0,0,0,0.08);
    border-left: none;
    box-shadow: 3px 0 16px rgba(0,0,0,0.1);
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 14px 0 12px;
    gap: 10px;
    cursor: default;
  }

  .mic-btn {
    width: 44px; height: 44px;
    border-radius: 50%;
    background: #F2F2F2;
    border: 1.5px solid rgba(0,0,0,0.08);
    cursor: pointer;
    font-size: 20px;
    display: flex; align-items: center; justify-content: center;
    transition: all 0.2s;
  }
  .mic-btn:hover { background: #E8E8E8; }
  .mic-btn.active {
    background: #FF3B30;
    border-color: #FF3B30;
    animation: pulse 1s infinite;
  }
  @keyframes pulse {
    0%,100% { box-shadow: 0 0 0 0 rgba(255,59,48,0.4); }
    50%      { box-shadow: 0 0 0 8px rgba(255,59,48,0); }
  }

  .close-btn-mini {
    width: 24px; height: 24px;
    border-radius: 50%;
    background: rgba(0,0,0,0.05);
    border: none;
    cursor: pointer;
    font-size: 10px;
    color: rgba(0,0,0,0.3);
    display: flex; align-items: center; justify-content: center;
    transition: all 0.15s;
  }
  .close-btn-mini:hover { background: #FF3B30; color: #fff; }

  /* ── 展开态：带输入区的宽卡片 ── */
  .card-expanded {
    display: none;
    background: #FFFFFF;
    border-radius: 0 16px 16px 0;
    border: 1px solid rgba(0,0,0,0.08);
    border-left: none;
    box-shadow: 3px 0 16px rgba(0,0,0,0.1);
    padding: 14px;
    flex-direction: column;
    gap: 10px;
  }
  .card-expanded.show { display: flex; }

  .exp-top {
    display: flex; align-items: center; gap: 10px;
  }
  .status {
    flex: 1;
    font-size: 11px;
    color: rgba(0,0,0,0.4);
    line-height: 1.4;
  }
  .close-btn {
    width: 20px; height: 20px;
    border-radius: 50%;
    background: rgba(0,0,0,0.05);
    border: none;
    cursor: pointer;
    font-size: 10px;
    color: rgba(0,0,0,0.3);
    display: flex; align-items: center; justify-content: center;
    transition: all 0.15s;
    flex-shrink: 0;
  }
  .close-btn:hover { background: #FF3B30; color: #fff; }

  textarea {
    width: 100%;
    min-height: 60px;
    height: auto;
    overflow: hidden;
    background: #F7F7F7;
    border: 1px solid rgba(0,0,0,0.08);
    border-radius: 9px;
    color: #1A1A1A;
    font-size: 12px;
    font-family: inherit;
    line-height: 1.6;
    padding: 9px 11px;
    resize: none;
    outline: none;
    caret-color: #1A1A1A;
  }
  textarea:focus { border-color: rgba(0,0,0,0.2); }
  textarea::placeholder { color: rgba(0,0,0,0.2); }

  .btn-row { display: flex; gap: 7px; }
  .btn {
    flex: 1; height: 32px;
    border-radius: 8px; border: none;
    font-size: 11px; font-family: inherit;
    cursor: pointer; font-weight: 500;
    transition: opacity 0.15s;
  }
  .btn:active { opacity: 0.7; }
  .btn-cancel { background: #F0F0F0; color: rgba(0,0,0,0.45); }
  .btn-save   { background: #1A1A1A; color: #FFFFFF; }
  .btn-save:disabled { opacity: 0.25; cursor: default; }
  .saved-hint {
    text-align: center; font-size: 10px;
    color: rgba(0,0,0,0.3); display: none;
  }
</style>
</head>
<body>

<div id="drag"></div>

<!-- 收起态 -->
<div class="card-mini" id="cardMini">
  <div class="mic-btn" id="micBtn" onclick="onMicClick()">🎙</div>
  <div class="close-btn-mini" onclick="onClose()">✕</div>
</div>

<!-- 展开态 -->
<div class="card-expanded" id="cardExpanded">
  <div class="exp-top">
    <div class="mic-btn" id="micBtnExp" style="width:32px;height:32px;font-size:15px;flex-shrink:0">🔴</div>
    <div class="status" id="status">说完后点「保存到 Obsidian」</div>
    <div class="close-btn" onclick="onClose()">✕</div>
  </div>
  <textarea id="textArea" placeholder="识别结果将出现在这里，也可以直接编辑…" oninput="autoResize(this)"></textarea>
  <div class="btn-row">
    <button class="btn btn-cancel" onclick="onCancel()">取消</button>
    <button class="btn btn-save" id="saveBtn" onclick="onSave()">保存到 Obsidian</button>
  </div>
  <div class="saved-hint" id="savedHint">✓ 已保存</div>
</div>

<script>
let resizeTimer = null;


function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = el.scrollHeight + 'px';
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(syncWindowHeight, 50);
}

function syncWindowHeight() {
  const card = document.getElementById('cardExpanded');
  const h = Math.max(100, Math.min(card.offsetHeight + 4, 600));
  window.pywebview.api.resizeExpanded(h);
}

function onMicClick() {
  document.getElementById('cardMini').style.display = 'none';
  document.getElementById('cardExpanded').classList.add('show');

  const textarea = document.getElementById('textArea');
  textarea.value = '';
  textarea.style.height = 'auto';

  window.pywebview.api.resizeExpanded(160).then(() => textarea.focus());

  window.pywebview.api.trigger_typeless().then(() => {
    let poll = setInterval(() => autoResize(textarea), 300);
    setTimeout(() => clearInterval(poll), 30000);
  });
}

function onCancel() {
  document.getElementById('cardExpanded').classList.remove('show');
  document.getElementById('cardMini').style.display = 'flex';
  document.getElementById('savedHint').style.display = 'none';
  document.getElementById('saveBtn').disabled = false;
  document.getElementById('saveBtn').textContent = '保存到 Obsidian';
  window.pywebview.api.resizeMini();
}

function onClose() {
  window.pywebview.api.quit_app();
}

async function onSave() {
  const text = document.getElementById('textArea').value.trim();
  if (!text) return;
  const btn = document.getElementById('saveBtn');
  btn.disabled = true;
  btn.textContent = '保存中…';
  const ok = await window.pywebview.api.save_record(text);
  if (ok) {
    btn.textContent = '✓ 已保存';
    document.getElementById('savedHint').style.display = 'block';
    setTimeout(onCancel, 1200);
  } else {
    btn.disabled = false;
    btn.textContent = '保存失败，重试';
  }
}
</script>

</body>
</html>
"""


_window_ref = None
MINI_W, MINI_H = 72, 96
EXP_W = 260
_win_x, _win_y = 0, 0  # 追踪窗口位置，供拖拽用

class RecorderApi:
    def resizeMini(self):
        global _win_x, _win_y
        sw, sh = _get_screen_size()
        _win_x, _win_y = 0, (sh - MINI_H) // 2
        if _window_ref:
            _window_ref.resize(MINI_W, MINI_H)
            _window_ref.move(_win_x, _win_y)

    def resizeExpanded(self, h: int):
        global _win_x, _win_y
        sw, sh = _get_screen_size()
        h = max(100, min(h, 600))
        _win_x, _win_y = 0, (sh - h) // 2
        if _window_ref:
            _window_ref.resize(EXP_W, h)
            _window_ref.move(_win_x, _win_y)

    def quit_app(self):
        def _do():
            time.sleep(0.1)
            try:
                from AppKit import NSApplication
                NSApplication.sharedApplication() \
                    .performSelectorOnMainThread_withObject_waitUntilDone_(
                        'terminate:', None, False
                    )
            except Exception:
                os.kill(os.getpid(), signal.SIGINT)
        threading.Thread(target=_do, daemon=True).start()
        return True

    def trigger_typeless(self):
        """用 CGEventPost 注入 fn 键硬件事件触发 Typeless"""
        def _do():
            time.sleep(0.3)
            try:
                import Quartz
                src = Quartz.CGEventSourceCreate(
                    Quartz.kCGEventSourceStateHIDSystemState
                )
                dn = Quartz.CGEventCreateKeyboardEvent(src, 63, True)
                up = Quartz.CGEventCreateKeyboardEvent(src, 63, False)
                Quartz.CGEventSetFlags(
                    dn, Quartz.kCGEventFlagMaskSecondaryFn
                )
                Quartz.CGEventPost(Quartz.kCGHIDEventTap, dn)
                time.sleep(0.05)
                Quartz.CGEventPost(Quartz.kCGHIDEventTap, up)
            except Exception as e:
                print(f"trigger error: {e}")
        threading.Thread(target=_do, daemon=True).start()

    def quit_app(self):
        sys.exit(0)

    def save_record(self, text: str) -> bool:
        text = text.strip().replace("|", "｜").replace("\n", " ").replace("\r", " ")
        if not text:
            return False
        date = datetime.now().strftime("%Y-%m-%d")
        try:
            os.makedirs(os.path.dirname(OBSIDIAN_FILE), exist_ok=True)
            is_new = not os.path.exists(OBSIDIAN_FILE) or os.path.getsize(OBSIDIAN_FILE) == 0
            with open(OBSIDIAN_FILE, "a", encoding="utf-8") as f:
                if is_new:
                    f.write("# AI 收获记录\n\n| 日期 | 收获 |\n|------|------|\n")
                f.write(f"| {date} | {text} |\n")
            print(f"✅ 已记录：{text[:50]}{'...' if len(text) > 50 else ''}")
            return True
        except Exception as e:
            print(f"保存失败: {e}")
            return False


def _get_screen_size():
    try:
        from AppKit import NSScreen
        f = NSScreen.mainScreen().visibleFrame()
        return int(f.size.width), int(f.size.height + f.origin.y)
    except Exception:
        return 1440, 900


def main():
    sw, sh = _get_screen_size()
    global _win_x, _win_y
    _win_x, _win_y = 0, (sh - MINI_H) // 2

    api = RecorderApi()
    global _window_ref
    window = webview.create_window(
        title="AI 收获记录器",
        html=HTML,
        width=MINI_W,
        height=MINI_H,
        x=_win_x,
        y=_win_y,
        resizable=False,
        frameless=True,
        on_top=True,
        transparent=True,
        js_api=api,
        min_size=(MINI_W, MINI_H),
    )

    _window_ref = window
    print("✅ AI 收获记录器已启动（左侧悬浮）")
    print(f"   保存位置：{OBSIDIAN_FILE}")
    webview.start(debug=False)


if __name__ == "__main__":
    main()
