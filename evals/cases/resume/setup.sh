#!/bin/sh
# tasklog as a finished "pause" left it: step 1 of 3 and the status note are committed on
# the branch feature/report-options, and the folder is back on main, where there is no note.
set -e
here=$(cd "$(dirname "$0")" && pwd)
sh "$here/../../seeds/init.sh" tasklog "$1"
cd "$1"
git checkout -q -b feature/report-options
git apply "$here/feature.patch"
mkdir -p docs
cp "$here/STATUS.md" docs/STATUS.md
git add -A
git commit -qm "Add report --csv; save status note"
git checkout -q main
