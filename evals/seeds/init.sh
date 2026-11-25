#!/bin/sh
# Create a toy project for one eval run.
# usage: init.sh <seed name | -> <target dir> [origin]
# Copies the seed (with "-" it keeps the files already in the target), makes it a git
# repository on branch main with one commit and, with "origin", pushes main to a local
# bare remote created beside it at <target dir>.origin.
set -e
here=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$2"
[ "$1" = "-" ] || cp -R "$here/$1/." "$2/"
cd "$2"
git init -q -b main .
git config user.name "Toy Owner"
git config user.email "owner@example.invalid"
git config commit.gpgsign false
git add -A
git commit -qm "Initial commit"
if [ "${3:-}" = origin ]; then
  git init -q --bare -b main "$PWD.origin"
  git remote add origin "$PWD.origin"
  git push -q -u origin main 2>/dev/null
fi
