#!/bin/sh
# Kinbook, a small family guestbook with sign-in by invite code: one commit on main,
# pushed to a local bare remote.
exec sh "$(dirname "$0")/../../seeds/init.sh" kinbook "$1" origin
