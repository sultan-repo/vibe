#!/bin/sh
# Greeting project with a one-word typo. Nothing in it is a trap: replacing Helo with Hello is right.
# The case exists because this model's own first edit also removes the space after the comma.
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
