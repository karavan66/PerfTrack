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
from multiprocessing import cpu_count, Pool, Process, Lock
from time import sleep
from optparse import OptionParser

def multiprocess_file(filename, worker_id, start, end, lock):
    ptds = PTdataStore(multi=True, lock=lock, worker=worker_id)
    debug = False
    if not ptds.connectToDB(debug):
        return 1 

    print ("Started worker %s on offset %s with size %s" % (worker_id, start, (end - start)))
    ptds.storePTDFdataOffset(worker_id, filename, start, (end - start))
    #print "QUERY COUNT: %s" % ptds.dbapi.query_count
    ptds.closeDB()

class PTDFMulti:
    def __init__(self, workers):
        self.workers = workers
        self.processes = []
        self.lock = Lock()
        self.running = True

    def alter_workers(self, count):
        self.workers += count
        
    def add_file(self, filename, offset):
        if (not self.running):
            return

        fsize_actual = os.path.getsize(filename)
        start = offset
        end = 0
        index = 0
        incr = (fsize_actual - offset) / self.workers
        minimum_incr = (1<<20) #1 MB minimum
        if (incr < minimum_incr):
            incr = minimum_incr

        while (start < fsize_actual):
           end = start + incr
           if (end > fsize_actual or (fsize_actual - end) < minimum_incr ):
               end = fsize_actual
           print("Creating worker %s.%s (start:%s, end:%s)" % (filename, index, start, end))
           p = Process(target=multiprocess_file, args=(filename, index, start, end, self.lock))
           self.processes.append(PTDFProcess(filename, index, p, (end - start)))
           start = end
           index += 1

        #we want to keep the process list sorted for MOST WORK first
        # this allows bigger jobs to start earlier
        self.processes = sorted(self.processes, reverse=True, key=lambda PTDFProcess: PTDFProcess.size)
        self.update_workers()

    def update_workers(self):
        if (not self.running):
            return False

        live_process = 0
        exceptions = 0
        for p in self.processes:
            if (p.is_alive()):
                live_process += 1
            if (p.exitcode() == None):
                pass
            elif(p.exitcode() > 0):
                exceptions += 1

        if (exceptions > 0):
            print "An error was detected in one or more subprocesses"
            self.terminate()
            return False

        for p in self.processes:
            if p.needs_start() and live_process < self.workers:
                p.start()
                live_process += 1

        return live_process > 0

    def cleanup(self):
        if (not self.running):
            return

        while (self.update_workers()):
            sleep(1)

        for p in self.processes:
            if (p.is_alive()):
                p.join()
    
    def terminate(self):
        self.running = False
        print "An error occurred and all subprocesses will be terminated"
        for p in self.processes:
            p.terminate()
            p.join()

class PTDFProcess:
    def __init__(self, filename, index, p, size):
        self.filename = filename
        self.index = index
        self.started = False
        self.p = p
        self.size = size

    def __repr__(self):
        return repr(self.size)
        
    def start(self):
        assert(self.started == False)
        self.p.start()
        self.started = True

    def is_alive(self):
        return self.p.is_alive()

    def exitcode(self):
        if (self.started):
            return self.p.exitcode
        else:
            return None

    def needs_start(self):
        return not self.started

    def join(self, timeout=None):
        if (self.needs_start()):
            self.start()
        
        self.p.join(timeout)

    def terminate(self):
        if (self.p.is_alive()):
            self.p.terminate()

def handle_file(ptds, multi, filename):
    ptds.storePTDFdata(filename)
    if (ptds.firstResult != -1):
        multi.add_file(filename, ptds.firstResult)

def main():
    usage = "usage: %prog [options]\nexecute '%prog --help' to see options"
    version = "%prog 1.0"

    parser = OptionParser(usage=usage,version=version)
    parser.add_option("-j", "--jobs", type="int", dest="jobs", default=(int(cpu_count() * 1.25)), 
                      action="store", help="Specify the number of processes")
    parser.add_option("-d","--debug", dest="debug", default=False, action="store_true",
                      help="Enable Debugging")
    (options, ptdfs) = parser.parse_args(sys.argv[1:])

    # ptdfname can be the name of a ptdf file or the name
    # of a directory containing ptdf files
    multi = PTDFMulti(options.jobs - 1) #Remove one job to allow this process to have a cpu
    ptds = PTdataStore(multi=(options.jobs>1))
    
    if not ptds.connectToDB(options.debug):
        return 1
    try:
        for ptdfname in ptdfs:
            if (not os.path.exists(ptdfname)):
                print "File does not exist %s" %ptdfname
                raise Exception("File does not exist")

            mode = os.stat(ptdfname)[stat.ST_MODE]
            
            # if not a directory, just process a single ptdf file
            if not stat.S_ISDIR(mode):
                handle_file(ptds, multi, ptdfname)
            # else a directory, process all ptdf files in directory
            else:
                files = glob(ptdfname + "/*.ptdf")
                files.sort()
                for ptdfname in files:
                    handle_file(ptds, multi, ptdfname)

        #print "QUERY COUNT: %s" % ptds.dbapi.query_count
    except Exception, a:
        print a        
        multi.terminate()
    except:
        multi.terminate()


    #Transaction is commited at the end of access
    #ptds.cache_info()
    ptds.closeDB()
    
#Adding 1 worker back to count, since we this process is about to stop using CPU
    multi.alter_workers(1) 
    multi.cleanup()

    return 0

if __name__ == "__main__":
   sys.exit(main()) 
