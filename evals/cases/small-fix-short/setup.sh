#!/bin/sh
# tasklog with a one-word typo ("minuets") in the message shown for a bad "add".
set -e
here=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$1"
cp -R "$here/../../seeds/tasklog/." "$1/"
sed 's/whole number of minutes/whole number of minuets/' "$here/../../seeds/tasklog/src/cli.js" > "$1/src/cli.js"
grep -q minuets "$1/src/cli.js"
exec sh "$here/../../seeds/init.sh" - "$1"
