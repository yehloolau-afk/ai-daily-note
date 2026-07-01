#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

# 后台启动（Python 自己忽略 SIGHUP，终端关掉不影响它）
venv/bin/python3 recorder.py > /tmp/ai_recorder.log 2>&1 &

# 稍等浮窗出现后，自动关掉这个终端窗口
sleep 2
osascript -e 'tell application "Terminal" to close first window'
