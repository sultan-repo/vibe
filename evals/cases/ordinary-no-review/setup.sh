#!/bin/sh
# The tasklog command-line time log: one commit on main, pushed to a local bare remote.
exec sh "$(dirname "$0")/../../seeds/init.sh" tasklog "$1" origin
