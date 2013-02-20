#!/usr/bin/env python

"""
This is an example script that shows how to use PerfTrack to load
PTDF data files into a PerfTrack database.
"""
import os, sys
import stat
from glob import glob
from PTds import PTdataStore
from getpass import getpass

def main():
    if len(sys.argv) < 2:
       print "usage: progname ptdfname"
       sys.exit(0)
    # ptdfname can be the name of a ptdf file or the name
    # of a directory containing ptdf files
    ptdfname = sys.argv[1]

    debug = False

    ptds = PTdataStore()
    ptds.connectToDB(debug)

    mode = os.stat(ptdfname)[stat.ST_MODE]

    # if not a directory, just process a single ptdf file
    if not stat.S_ISDIR(mode):
       ptds.storePTDFdata(ptdfname)
       #ptds.commitTransaction()
    # else a directory, process all ptdf files in directory
    else:
       files = glob(ptdfname + "/*.ptdf")
       files.sort()
       for ptdfname in files:
          print "Processing %s" % ptdfname
          ptds.storePTDFdata(ptdfname)
          #ptds.commitTransaction()
    ptds.closeDB()


if __name__ == "__main__":
   sys.exit(main()) 
