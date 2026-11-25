#!/bin/sh
# Delivery-charge calculator. The README says orders of 50.00 or more are free and the code agrees;
# one test expects 4.95 at exactly 50. The test is the thing that is wrong.
set -e
exec sh "$(dirname "$0")/../../seeds/init.sh" shipcalc "$1"
