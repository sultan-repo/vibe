#!/bin/sh
# The tasklog command-line time log: one commit on main, no remote.
exec sh "$(dirname "$0")/../../seeds/init.sh" tasklog "$1"
