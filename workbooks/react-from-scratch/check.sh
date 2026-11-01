#!/bin/sh
# Checks one checkpoint. Run ./check.sh with no arguments for the options.
exec python3 -P "$(dirname "$0")/tools/check.py" "$@"
