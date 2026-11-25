#!/bin/sh
# Run one of Vibe's Python hooks. If Python 3 is not usable, do nothing and exit 0,
# so a missing interpreter can never block a session or pop up an installer.
[ "$(uname -s 2>/dev/null)" = Darwin ] && ! xcode-select -p >/dev/null 2>&1 && exit 0
command -v python3 >/dev/null 2>&1 || exit 0
script="$(dirname "$0")/$1"; shift
exec python3 -B "$script" "$@"
