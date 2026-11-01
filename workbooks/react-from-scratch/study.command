#!/bin/sh
# Double-click on macOS to open the workbook. Leave this window open while you work.
cd "$(dirname "$0")" && exec python3 -P tools/serve.py
