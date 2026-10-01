#!/bin/bash
# SessionStart: make the oracle CLI (@steipete/oracle, needs Node >= 24) available in cloud sessions.
ORACLE_VERSION=0.21.3
export NVM_DIR=/opt/nvm
[ -s "$NVM_DIR/nvm.sh" ] || { echo "nvm not found; oracle not installed" >&2; exit 0; }
. "$NVM_DIR/nvm.sh"
nvm install 24 >/dev/null 2>&1 || { echo "node 24 install failed" >&2; exit 0; }
NODE_BIN="$(dirname "$(nvm which 24)")"
if [ "$("$NODE_BIN/oracle" --version 2>/dev/null)" != "$ORACLE_VERSION" ]; then
  "$NODE_BIN/npm" install -g -q "@steipete/oracle@$ORACLE_VERSION" >&2 || echo "oracle install failed" >&2
fi
# Put Node 24 (and oracle) first on PATH for the session's Bash commands.
[ -n "$CLAUDE_ENV_FILE" ] && echo "export PATH=\"$NODE_BIN:\$PATH\"" >> "$CLAUDE_ENV_FILE"
exit 0
