#!/usr/bin/env python

# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information. 

import sys,os
from getpass import getpass
from optparse import OptionParser, SUPPRESS_HELP
from PTds import PTdataStore
from ResourceIndex import ResourceIndex
from Application import Application
from Resource import Resource
from PerfResult import PerfResult
from PTexception import PTexception
from PTcommon import  StringToList, getMachineName
import parsePerf
import Hardware
import Build
import Run

class ExecInfo:
    pass

class SystemInfo:
    pass

class MachineInfo:
    pass

class TestInfo:
    pass


def write_files(dir_name, execName, writeLst, split):
    if (not split):
        ptdfname = dir_name + "/" + execName + ".ptdf"
        f = open(ptdfname,'w')
        for w in writeLst:
            f.write(w)
        f.close()
    else:
        fileCounter = 1
        lineCounter = 0
        fileCtrName = "00" + str(fileCounter)
        ptdfname = dir_name + "/" + execName + "_" + fileCtrName + ".ptdf"
        f = open(ptdfname,'w')
        for w in writeLst:
            lines = w.splitlines(True)
            for line in lines:
               f.write(line)
               lineCounter = lineCounter + 1
               if lineCounter == 250000:
                  f.close()
                  fileCounter = fileCounter + 1
                  if fileCounter < 10:
                     fileCtrName = "00" + str(fileCounter)
                  elif fileCounter < 99:
                     fileCtrName = "0" + str(fileCounter)
                  else:
                     fileCtrName = str(fileCounter)
                  ptdfname = dir_name + "/" + execName + "_" + \
                             fileCtrName + ".ptdf"
                  f = open(ptdfname,'w')
                  lineCounter = 0
        if f:
            f.close()

def main(argv=sys.argv):
    
    options = checkInputs(argv)
    if not options:
       return -1

    eInfo = None
    mInfo = None
    sInfo = None
    tInfo = None
    verbose = False

    if options.executions:
       eInfo = ExecInfo() 
       eInfo.dataDir = options.dataDir
       # turn the comma separated string of tools into list of tools 
       eInfo.perfTools = options.perfTools.split(",")
       eInfo.machineName = options.machineName
       eInfo.pbsOut = options.pbsOut
    else:
       eInfo = None

    if options.system:
       sInfo = SystemInfo()
       sInfo.dataDir = options.dataDir
       sInfo.perfTools = options.perfTools.split(",")
       sInfo.machineName = options.machineName
    else:
       sInfo = None

    if options.machines:
       mInfo = MachineInfo()
       if options.dataDir:
          mInfo.machineFile = options.dataDir + "/" +options.machineFile
          mInfo.machinePTdF = options.dataDir + "/" +options.machinePTdF
       else:
          mInfo.machineFile = options.machineFile
          mInfo.machinePTdF = options.machinePTdF
    else:
       mInfo = None

    if options.PTdFtestMode:
       tInfo = TestInfo()
       tInfo.testRunIndex = options.testRunIndex
    else:
       tInfo = None
    
    verbose = options.verbose

    processData(eInfo, mInfo, sInfo, tInfo, verbose, opt = options)

def processData(eInfo, mInfo, sInfo, testMode, verbose, opt = None):
    if mInfo:
       try:
         resIdx = ResourceIndex()
         Hardware.getHardwareInfo(resIdx, mInfo.machineFile)

         writeList = resIdx.PTdF()
         f = open(mInfo.machinePTdF,'w')
         for w in writeList:
            f.write(w)
         f.close()
         print "PTDF machine data generation complete."
       except PTexception, a:
           raise
           if testMode:
              print a
              raise PTexception(a)
           else:
              print a.value
              return -1

    if sInfo:
       ptds = None
       try:
          resIdx = ResourceIndex()
          ptds = connectToDB(testMode, opt)
          ## set the machine name from command line arg:
          fullname,type = getMachineName(ptds, sInfo.machineName, "machine")
          mach = Resource(fullname, type)
          resIdx.addResource(mach)

          parsePerf.getSysPerfInfo(resIdx, sInfo.dataDir, sInfo.perfTools, ptds)
          ptdfname = sInfo.dataDir + "/sys.ptdf"
          f = open(ptdfname,'w')
          # ResourceIndex.PTdF returns a list of strings to write
          writeLst = resIdx.PTdF()
          for w in writeLst:
             f.write(w)
          f.close()
          print "PTDF system data generation complete."
       except PTexception, a:
          if testMode:
             print a.value
             raise PTexception(a)
          else:
             print a.value
             return -1
       else:
          ptds.closeDB()

    if eInfo:
       ptds = None # database object, not currently needed for 
                   # processing machine data
       try:
          (execs,apps) = getRuns(eInfo, testMode)
          ptds = connectToDB(testMode, opt)
           
          for e in execs:
             # We are creating a new ResourceIndex object for each
             # execution. This way it's easy to dump a separate PTdF 
             # file for each execution. 
      
             resIdx = ResourceIndex()

             app = Application(e['appName'])
             resIdx.addResource(app)
      
             execName = e['execName']
             if verbose:
                print "now processing files for execution:%s" % execName
             concurrency = e['concurrency']
             if (concurrency.find("PTHREADS") >= 0) or \
                (concurrency.find("OPENMP") >= 0):
                threaded = True
             else:
                threaded = False
      
             buildFile = eInfo.dataDir + "/" + execName + ".bld"
             # creates build and execution resources
             Build.getBuildInfo(resIdx, buildFile, execName, ptds)
      
             runFile = eInfo.dataDir + "/" + execName + ".run"
             #  uses build and execution resources in resIdx
             Run.getRunInfo(resIdx, runFile, eInfo, ptds)
            
             [execution] = resIdx.findResourcesByType("execution")  
             app.addExecution(execution)
             
             parsePerf.getPerfInfo(resIdx, execName, \
                            eInfo.dataDir, eInfo.perfTools,  \
                            threaded, ptds)
             writeLst = resIdx.PTdF()
             write_files(eInfo.dataDir, execName, writeLst, opt.split)
             print "PTDF execution data generation complete."
       except PTexception, a:
           if testMode:
              print a.value
              raise PTexception(a)
           else:
              print a.value
              return -1
       else:
           ptds.closeDB()

         
def connectToDB(testMode, opt = None):
    ptds = PTdataStore()  #create PTdataStore object
    if testMode:
       debugLevel = ptds.NO_WRITE
    else:
       debugLevel = ptds.NO_DEBUG

    if opt == None:
        connected = ptds.connectToDB(debugLevel)
    else:
        connected = ptds.connectToDB(debugLevel,
                                     ctb_db = opt.database,
                                     ctb_host = opt.host,
                                     ctb_pwd = opt.password,
                                     ctb_user = opt.user)

    if not connected:
        raise PTexception("Build.process: could not connect to database")

    return ptds


         
      
def getRuns(eInfo, testMode):
    
    execs = []
    apps = {}

    if testMode:
       fname = eInfo.dataDir + "/" + testMode.testRunIndex
    else:
       fname = eInfo.dataDir +"/PTrunIndex.txt"
    try:
       f = open(fname,'r')
    except:
       raise PTexception("getRuns: Could not open file: %s." % fname)

    lineno = 1
    try:
       line = f.readline()
       while line != '':
           temp =  {}
           parts = line.split()
           if len(parts) > 7:
               raise PTexception("getRuns: Problem parsing %s. Offending "\
                                     "line: %d" % (fname, lineno))
           temp['execName'] = parts[0]         
           temp['appName'] = parts[1]         
           apps['appName'] = None
           temp['concurrency'] = parts[2]         
           temp['numProcesses'] = parts[3]         
           temp['threadsPerProcess'] = parts[4]         
           if len(parts) > 5:
             temp['buildTimeStamp'] = parts[5]         
             temp['runTimeStamp'] = parts[6]         
           execs.append(temp)
           lineno += 1
           line = f.readline()

    except:
       raise PTexception("getRuns: Problem parsing %s. Offending line: %d" % (fname, lineno))
    for dict in execs:
      num = dict["numProcesses"]
      #print "PTdFgen:getRuns: number of processes: %s" % (num)  
    return (execs,apps) 


def checkInputs(argv):
    """Parses command line arguments and returns their values"""

    usage = "usage: %prog [options]\nexecute '%prog --help' to see options"
    version = "%prog 1.0"
    parser = OptionParser(usage=usage,version=version)
    parser.add_option("-d","--data_dir", dest="dataDir", 
                      help="the name of the data directory")
    parser.add_option("-m","--machine_data", dest="machines", 
                      action="store_true", default=False,
                      help="use this flag to parse machine data.")
    parser.add_option("--machine_file", dest="machineFile", 
                      help="the name of the machine data file")
    parser.add_option("--machine_out", dest="machinePTdF", 
                      help="the name of the output PTdF file for machine data")
    parser.add_option("-e","--exec_data", dest="executions", 
                      action="store_true", default=False,
                      help="use this flag to parse execution data.") 
    parser.add_option("-s", "--sys_data", dest="system",
                      action="store_true", default=False,
                      help="use this flag to parse non-execution system performance data.")
    parser.add_option("-p","--perfTools", dest="perfTools", 
                      default="self instrumentation",
                      help="use this flag to specify the performance tools "\
                      "used. Expects a comma separated list of tools. " \
                      "Defaults to self instrumentation.") 
    parser.add_option("-M","--machineName", dest="machineName",
                      help="The name of the machine on which data was " \
                           "collected. When parsing system data, this " \
                           "option is required; When parsing execution " \
                           "data, the option is necessary only if the " \
                           "run data collection scripts can't determine " \
                           "this information automatically.")
    parser.add_option("-P", "--pbsOut", dest="pbsOut", action="store_true", 
                      help="specify that the script should look for files "\
                      "that end in .pbs.out and pbs.err that will contain " \
                      "the messages output to stdout and stderr by PBS",
                       default=False)                 
    parser.add_option("-v","--verbose", dest="verbose", action="store_true",
                      default=False,
                      help="use this flag to get verbose output.") 
    parser.add_option("--testMode", dest="PTdFtestMode", action="store_true",
                      default=False, help=SUPPRESS_HELP)
    parser.add_option("--split", dest="split", action="store_true",
                  default=False, help=SUPPRESS_HELP)
    parser.add_option("--testRunIndex", dest="testRunIndex",help=SUPPRESS_HELP)
    parser.add_option("-D", "--dbname", dest = "database",
                      help = "name of the database to connect too")
    parser.add_option("-H", "--host", dest = "host",
                      help = "hostname of the database server")
    parser.add_option("-U", "--username", dest =  "user",
                      help = "database user name")
    parser.add_option("-w", "--password", dest = "password",
                      help = "user's database password")
    (options, args) = parser.parse_args(argv[1:])

    if (options.executions == True) and (options.dataDir == None):
       parser.print_help()
       print "\nYou must give the name of the data directory that "\
             + " contains " \
             + "execution data files with the --data_dir <dirName> option.\n"
       return None

    if (options.system == True) and  (options.dataDir == None):
       parser.print_help()
       print "\nYou must give the name of the data directory that "\
             + " contains " \
             + "system data files with the --data_dir <dirName> option.\n"
       return None

    if (options.system == True) and (options.machineName == None):
       parser.print_help()
       print "\nYou must also use the machine name option when using the " \
             "-s option:  -s -M <machName>\n"
       return None

    if(options.machines == True) and (options.machineFile == None):
       parser.print_help()
       print "\nYou must give the name of the input machine data file"\
             + " with the --machine_file <filename> "\
             + "option.\n"
       return None

    if(options.machines == True) and (options.machinePTdF == None):
       parser.print_help()
       print "\nYou must give the name of the output file (PTdF file) "\
             + " for the machine data with the --machine_out <ptdf_file> "\
             + "option.\n"
       return None

    if(options.machines == False) and (options.executions == False):
      parser.print_help()
      print "\nYou must specify --machine_data to parse machine data files "\
            "or --exec_data to parse execution data files.\n"
      return None


    return options

if __name__ == "__main__":
   sys.exit(main())
