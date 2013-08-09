#!/bin/bash
# This script will perform an out-of-source build of the perftrack GUI
# using cmake. All build products are put in the build/ directory, and
# the source directory is left pristine.

if ! [ -d build ]; then
    mkdir build
fi

cd build
cmake ..

make

EXITCODE=$?

exit $EXITCODE
