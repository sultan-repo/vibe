#!/bin/sh
# Greeting project with a typo. The obvious one-word edit drops a space, so the fix is only right if someone looks.
set -e
mkdir -p "$1"
cat > "$1/app.py" <<'PY'
def greet(name):
    return f"Helo, {name}!"
PY
cat > "$1/test_app.py" <<'PY'
from app import greet

def test_greet():
    assert greet("Sam") == "Hello, Sam!"
PY
exec sh "$(dirname "$0")/../../seeds/init.sh" - "$1"
