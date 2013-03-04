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
       print("usage: progname ptdfnames")
       return 1
    # ptdfname can be the name of a ptdf file or the name
    # of a directory containing ptdf files
    ptdfs = sys.argv[1:]
    debug = False
    ptds = PTdataStore()
    if not ptds.connectToDB(debug):
        return 1

    for ptdfname in ptdfs:
        mode = os.stat(ptdfname)[stat.ST_MODE]

        # if not a directory, just process a single ptdf file
        if not stat.S_ISDIR(mode):
            ptds.storePTDFdata(ptdfname)
        # else a directory, process all ptdf files in directory
        else:
            files = glob(ptdfname + "/*.ptdf")
            files.sort()
            for ptdfname in files:
                ptds.storePTDFdata(ptdfname)

    #Transaction is commited at the end of access
    ptds.cache_info()
    ptds.closeDB()

    return 0

if __name__ == "__main__":
   sys.exit(main()) 
