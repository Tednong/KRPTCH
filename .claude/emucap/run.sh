#!/bin/bash
# Installs the prebuilt emucap core (checksum-verified) on first use, then
# execs the requested binary: run.sh install | run.sh <emucap-mcp|emucap-track-mcp|...> [args]
set -euo pipefail
VERSION="0.17.1"
DEST="${EMUCAP_HOME:-$HOME/.emucap-core}/$VERSION"
case "$(uname -s)-$(uname -m)" in
  Linux-x86_64) TARGET="x86_64-unknown-linux-gnu.tar.gz" ;;
  Darwin-arm64) TARGET="aarch64-apple-darwin.tar.gz" ;;
  *) echo "emucap: no prebuilt core for $(uname -s)-$(uname -m)" >&2; exit 1 ;;
esac
install_core() {
  [ -x "$DEST/target/release/emucap-mcp" ] && return 0
  local base="https://github.com/mcpads/emucap/releases/download/$VERSION"
  local name="emucap-$VERSION-$TARGET" tmp; tmp="$(mktemp -d)"
  curl -fsSL -o "$tmp/$name" "$base/$name" >&2
  curl -fsSL -o "$tmp/SHA256SUMS" "$base/SHA256SUMS" >&2
  local want got
  want="$(grep " \*\?$name\$" "$tmp/SHA256SUMS" | awk '{print $1}')"
  got="$(sha256sum "$tmp/$name" 2>/dev/null | awk '{print $1}' || shasum -a 256 "$tmp/$name" | awk '{print $1}')"
  [ -n "$want" ] && [ "$want" = "$got" ] || { echo "emucap: checksum mismatch" >&2; exit 1; }
  mkdir -p "$DEST"; tar -xzf "$tmp/$name" -C "$DEST" --strip-components=1 >&2
  rm -rf "$tmp"
}
install_core
[ "${1:-}" = "install" ] && exit 0
exec "$DEST/target/release/$1" "${@:2}"
