#!/bin/sh
# Run one of Vibe's Python hooks. Whatever happens, exit 0 and stay quiet on errors:
# a missing or broken Python must never block a session or show the owner an error.
command -v python3 >/dev/null 2>&1 || exit 0
# Apple's /usr/bin/python3 is a stub that pops up an installer until the command-line tools exist.
[ "$(command -v python3)" = /usr/bin/python3 ] && [ "$(uname -s 2>/dev/null)" = Darwin ] && ! xcode-select -p >/dev/null 2>&1 && exit 0
python3 -B "$(dirname "$0")/$1" 2>/dev/null
exit 0
