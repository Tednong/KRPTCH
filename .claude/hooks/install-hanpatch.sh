#!/bin/bash
# SessionStart: make the hanpatch CLI available in cloud sessions.
command -v hanpatch >/dev/null 2>&1 && exit 0
pip install -q "git+https://github.com/yazzang-homelab/hanpatch.git" >&2 || echo "hanpatch install failed" >&2
exit 0
