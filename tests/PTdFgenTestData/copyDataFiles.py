#!/usr/local/bin/python

import sys
from glob import glob
import shutil

usage = " usage: copyDataFiles.py fromPrefix toPrefix"
# copies all files that start with fromPrefix to new files that start
# with toPrefix
# assumes all files  are of the form fromPrefix.suffix

# example: copyDataFiles.py sppm-10 sppm-11
# you'll get sppm-11.run sppm-11.bld sppm-11.output0 ...


if len(sys.argv) < 3:
   print usage
   sys.exit(0)

fromPrefix = sys.argv[1]
toPrefix = sys.argv[2]

fromFiles = glob(fromPrefix+".*")

for fromFile in fromFiles:
    fromSuffix = fromFile.split('.')[1]
    toFile = toPrefix + "." + fromSuffix 
    print " cp " + fromFile + " " + toFile
    shutil.copyfile(fromFile, toFile)


