#!/bin/sh
# Opens the workbook in your browser, with Run and Submit working. Leave it running while you work.
exec python3 -P "$(dirname "$0")/tools/serve.py" "$@"
