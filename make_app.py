#!/usr/bin/env python3
"""生成 AI每日小记 图标 + .app bundle，并安装到 /Applications"""

import os, shutil, subprocess, stat, tempfile

VENV_PYTHON = os.path.join(os.path.dirname(__file__), "venv/bin/python3")
RECORDER    = os.path.join(os.path.dirname(__file__), "recorder.py")
APP_NAME    = "AI每日小记"
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))

# ── 1. 生成 1024×1024 PNG 图标 ─────────────────────────────────────────────

def make_icon_png(path):
    from AppKit import (NSImage, NSBezierPath, NSColor,
                        NSBitmapImageRep, NSPNGFileType)
    import Foundation

    def R(x, y, w, h):
        return Foundation.NSMakeRect(x, y, w, h)

    SIZE = 1024
    img = NSImage.alloc().initWithSize_((SIZE, SIZE))
    img.lockFocus()

    # ── 背景：深色圆角矩形 ──
    bg = NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
        R(0, 0, SIZE, SIZE), SIZE * 0.22, SIZE * 0.22
    )
    NSColor.colorWithRed_green_blue_alpha_(0.10, 0.10, 0.11, 1.0).setFill()
    bg.fill()

    # ── 对话气泡主体 ──
    bx, by, bw, bh = 172, 340, 660, 480
    br = 90.0   # 圆角半径
    bubble = NSBezierPath.bezierPath()
    # 从底部尾巴右侧顺时针绘制
    bubble.moveToPoint_((bx + br, by))
    # 底边左段（留出尾巴位置）
    bubble.lineToPoint_((bx + 240, by))
    # 尾巴：向左下斜出
    bubble.lineToPoint_((bx + 90, by - 130))
    bubble.lineToPoint_((bx + 310, by))
    # 底边右段 → 右下圆角
    bubble.lineToPoint_((bx + bw - br, by))
    bubble.appendBezierPathWithArcWithCenter_radius_startAngle_endAngle_clockwise_(
        (bx + bw - br, by + br), br, 270, 0, False)
    # 右边 → 右上圆角
    bubble.lineToPoint_((bx + bw, by + bh - br))
    bubble.appendBezierPathWithArcWithCenter_radius_startAngle_endAngle_clockwise_(
        (bx + bw - br, by + bh - br), br, 0, 90, False)
    # 顶边 → 左上圆角
    bubble.lineToPoint_((bx + br, by + bh))
    bubble.appendBezierPathWithArcWithCenter_radius_startAngle_endAngle_clockwise_(
        (bx + br, by + bh - br), br, 90, 180, False)
    # 左边 → 左下圆角
    bubble.lineToPoint_((bx, by + br))
    bubble.appendBezierPathWithArcWithCenter_radius_startAngle_endAngle_clockwise_(
        (bx + br, by + br), br, 180, 270, False)
    bubble.closePath()

    NSColor.whiteColor().setFill()
    bubble.fill()

    # ── 气泡内三个圆点（深色）──
    dot_r = 38.0
    dot_y  = by + bh / 2 - dot_r          # 垂直居中
    dot_cx = bx + bw / 2                   # 水平居中
    dot_color = NSColor.colorWithRed_green_blue_alpha_(0.10, 0.10, 0.11, 1.0)
    dot_color.setFill()
    for dx in [-140, 0, 140]:
        d = NSBezierPath.bezierPathWithOvalInRect_(
            R(dot_cx + dx - dot_r, dot_y, dot_r * 2, dot_r * 2))
        d.fill()

    img.unlockFocus()

    tiff = img.TIFFRepresentation()
    rep  = NSBitmapImageRep.imageRepWithData_(tiff)
    png  = rep.representationUsingType_properties_(NSPNGFileType, None)
    png.writeToFile_atomically_(path, True)
    print(f"  图标 PNG → {path}")


# ── 2. 生成 .icns ───────────────────────────────────────────────────────────

def make_icns(png_src, icns_dst):
    iconset = tempfile.mkdtemp(suffix=".iconset")
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    for s in sizes:
        for scale, suffix in [(1, ""), (2, "@2x")]:
            px = s * scale
            if px > 1024:
                continue
            out = os.path.join(iconset, f"icon_{s}x{s}{suffix}.png")
            subprocess.run(
                ["sips", "-z", str(px), str(px), png_src, "--out", out],
                check=True, capture_output=True
            )
    subprocess.run(["iconutil", "-c", "icns", iconset, "-o", icns_dst],
                   check=True, capture_output=True)
    shutil.rmtree(iconset)
    print(f"  .icns    → {icns_dst}")


# ── 3. 创建 .app bundle ─────────────────────────────────────────────────────

def make_app(icns_path, dest_dir="/Applications"):
    app_path = os.path.join(dest_dir, f"{APP_NAME}.app")
    if os.path.exists(app_path):
        shutil.rmtree(app_path)

    macos_dir = os.path.join(app_path, "Contents", "MacOS")
    res_dir   = os.path.join(app_path, "Contents", "Resources")
    os.makedirs(macos_dir); os.makedirs(res_dir)

    # 复制 icns
    shutil.copy(icns_path, os.path.join(res_dir, "AppIcon.icns"))

    # Info.plist
    plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key>             <string>{APP_NAME}</string>
  <key>CFBundleDisplayName</key>      <string>{APP_NAME}</string>
  <key>CFBundleIdentifier</key>       <string>com.yehloo.ai-daily-note</string>
  <key>CFBundleVersion</key>          <string>1.0</string>
  <key>CFBundleExecutable</key>       <string>{APP_NAME}</string>
  <key>CFBundleIconFile</key>         <string>AppIcon</string>
  <key>CFBundlePackageType</key>      <string>APPL</string>
  <key>LSUIElement</key>              <true/>
  <key>NSMicrophoneUsageDescription</key>
    <string>需要麦克风权限以使用语音输入功能</string>
</dict>
</plist>"""
    with open(os.path.join(app_path, "Contents", "Info.plist"), "w") as f:
        f.write(plist)

    # 可执行启动脚本
    launcher = os.path.join(macos_dir, APP_NAME)
    with open(launcher, "w") as f:
        f.write(f"""#!/bin/bash
exec "{VENV_PYTHON}" "{RECORDER}"
""")
    os.chmod(launcher, os.stat(launcher).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    print(f"  .app     → {app_path}")
    return app_path


# ── main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tmp_png  = os.path.join(SCRIPT_DIR, "_icon_tmp.png")
    tmp_icns = os.path.join(SCRIPT_DIR, "_icon_tmp.icns")

    print("【1/3】生成图标 PNG…")
    make_icon_png(tmp_png)

    print("【2/3】生成 .icns…")
    make_icns(tmp_png, tmp_icns)

    print("【3/3】创建并安装 .app…")
    app = make_app(tmp_icns)

    # 清理临时文件
    os.remove(tmp_png)
    os.remove(tmp_icns)

    print(f"\n✅ 完成！已安装到：{app}")
    print("   在启动台或 /Applications 中找到「AI每日小记」即可启动")

    # 刷新图标缓存
    subprocess.run(["touch", app], capture_output=True)
