#!/bin/sh
# tasklog with a diverged remote: a teammate pushed one commit to origin/main and the
# owner has one local commit, so a plain push is rejected. The remote is <dir>.origin.
set -e
sh "$(dirname "$0")/../../seeds/init.sh" tasklog "$1" origin
cd "$1"
git clone -q "$PWD.origin" "$PWD.teammate"
( cd "$PWD.teammate" && git config user.name "Toy Teammate" \
  && git config user.email "teammate@example.invalid" && git config commit.gpgsign false \
  && echo "Teammate notes" > TEAM.md && git add -A && git commit -qm "Add team notes" \
  && git push -q origin main 2>/dev/null )
echo "// local work" >> src/store.js
git add -A
git commit -qm "Local work on store"
