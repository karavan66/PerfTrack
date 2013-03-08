#!/usr/bin/python
"""
This is an example script that shows how to use PerfTrack to load
PTDF data files into a PerfTrack database.
"""
import os, sys
import stat
from multiprocessing import cpu_count, Pool, Process, Lock
from glob import glob
from PTds import PTdataStore
from getpass import getpass

def process_file(filename, worker_id, fsize, workers, lock):
    ptds = PTdataStore(multi=True, lock=lock, worker=worker_id)
    debug = False
    if not ptds.connectToDB(debug):
        return 1    
    size = (fsize / workers)
    offset = size * worker_id
    print ("Started worker %s on offset %s with size %s" % (worker_id, offset, size))
    ptds.storePTDFdataOffset(worker_id, filename, offset, size)
    #ptds.cache_info()
    ptds.closeDB()

def main():
    if len(sys.argv) < 2:
       print("usage: progname ptdfnames")
       return 1
    # ptdfname can be the name of a ptdf file or the name
    # of a directory containing ptdf files
    ptdfs = sys.argv[1:]
    workers = cpu_count()
    #workers = 1
    mylock = Lock()
    for ptdfname in ptdfs:

        mode = os.stat(ptdfname)[stat.ST_MODE]

        # if not a directory, just process a single ptdf file
        if not stat.S_ISDIR(mode):
            fsize = os.path.getsize(ptdfname)
            processes = []
            for id in range(workers):
                print("Spawning worker %s" % id)
                p = Process(target=process_file, args=(ptdfname, id, fsize, workers, mylock))
                p.start()
                processes.append(p)

            print("waiting for processes")
            for p in processes:
                p.join()

            #pool.close()
            #pool.join()
        # else a directory, process all ptdf files in directory
#        else:
#            files = glob(ptdfname + "/*.ptdf")
#            files.sort()
#            for ptdfname in files:
#                ptds.storePTDFdata(ptdfname)

    #Transaction is commited at the end of access
    return 0

if __name__ == "__main__":
   sys.exit(main()) 
