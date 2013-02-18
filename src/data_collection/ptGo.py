#!/usr/bin/env python

# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information. 

from optparse import OptionParser
import sys, os, datetime, string, shutil, ptbuild, ptrun

HIGH = 2
MEDIUM = 1

global runParadigms 

def main():
    options = checkInputs()
   
    dataFileDir = makeDataDirectory() 
    
    if options.verbosity >= MEDIUM:
       if options.buildDataFile:
          print "Copying build data file %s to temp data directory." % \
                options.buildDataFile
       else:
          print "Generating build data with ptbuild.py"   
    data_gen(options, build=True, file=options.buildDataFile, \
             dataDir=dataFileDir)
    if options.buildOnly:
       return
    if options.verbosity >= MEDIUM:
       if options.runDataFile:
          print "Copying run data file %s to temp data directory." % \
                options.runDataFile
       else:
          print "Generating run data with ptrun.py"   
    data_gen(options, run=True, file=options.runDataFile, dataDir=dataFileDir)
    #if options.verbosity >= MEDIUM:
       #if options.perfDataFile:
          #print "Copying performance data file %s to temp data directory." % \
                #options.perfDataFile
       #else:
       #   print "Generating perf data with %s." % options.perfParser   
    #data_gen(options,perf=True, file=options.perfDataFile, dataDir=dataFileDir)

    print 'DATAFILE DIRECTORY=' + str(dataFileDir)


def data_gen(options=None, build=False, run=False, perf=False, file=None,\
             dataDir=None):

    global runParadigms

    if options.verbosity == HIGH: 
       print "build %s, run %s, perf %s, file %s, dataDir %s." % \
             (build,run,perf,file,dataDir)

    if build:
       if file:  # they gave us a build file to use
          try:
             shutil.copy(file, dataDir) 
             runParadigms = getBuildInfo(file)
             buildFile = file
          except:
             print "Could not copy build data file %s to %s." % (file, dataDir)
             sys.exit(1)
       else:     # we need to generate the build
          (buildFile, runParadigms) = genBuild(options, dataDir)
          shutil.move(buildFile, dataDir)          
    if run:
       if file: # they gave us a run file to use
          try:
             shutil.copy(file, dataDir) 
          except:
             print "Could not copy run data file %s to %s." % (file, dataDir)
             sys.exit(1)
       else:
          runFile = genRun(options, dataDir, runParadigms)
          shutil.move(runFile, dataDir)          
          

def genBuild(options, dataDir):

    args = parseBuildOptions(options)
    if options.verbosity == HIGH:
       print "Arg list to ptbuild: " + str(args)
    try:
       (buildFile, runParadigms) = ptbuild.main(args)
    except:
       print "build failed"
       raise
       sys.exit(1)
    return (buildFile,runParadigms)

def getBuildInfo(file):
    paradigms = []
    f = open(file)
    data = f.readlines()
    for d in data:
       if d.find("ApplicationParadigms") == 0:
          temp = d.split('=')[1].strip()   # break off attr name
          pds = temp.strip('[').strip(']').split(',') # make list 
          for p in pds:
             paradigms.append(p.strip().lstrip('\'').rstrip('\''))
          break
    f.close()
    return paradigms      
    
def genRun(options, dataDir, runParadigms):
    args = parseRunOptions(options, runParadigms)
    if(options.CNLfixes):
       args.append("--ptDataDir")
       args.append(dataDir)
       args.append("--CNL")
    runFile = ""
    if options.verbosity == HIGH:
       print "Arg list to ptrun: " + str(args)
    try:
       runFile = ptrun.main(args)
    except:
       print "run failed"
       raise
       sys.exit(1)
    return runFile

def parseRunOptions(options, runParadigms):
    args = []
    args.append("ptrun.py")
    if options.appName:
       args.append("--appName")
       args.append(options.appName)
    if options.exeName:
       args.append("--exeName")
       args.append(options.exeName)
    if options.pathToExe:
       args.append("--pathToExe")
       args.append(options.pathToExe)
    if options.batchFile:
       args.append("--batchFile")
       args.append(options.batchFile)
    if options.exportEnvAtLaunch:
       args.append("--exportEnv")
    # let's move this over to ptrun to decide whether it needs a batch file or not
    #else:
       #print " You need to give the name of the batch file to run your program. Use the --batchFile option."
       #sys.exit(0)
    if options.launcher:
       args.append("--launcher")
       args.append(options.launcher)
    if options.inputDecks:
       args.append("--inputDecks")
       args.append("\""+options.inputDecks+"\"")
    if options.PERIxml:
       args.append("--peri")
    for rp in runParadigms:
       if rp == "MPI":
          args.append("--mpi")  
       elif rp == "OpenMP":
          args.append("--openmp")
       elif rp == "pthreads":
          args.append("--pthreads")
    return args
 
def parseBuildOptions(options):
    args = []
    args.append("ptbuild.py")
    if options.appName:
       args.append("-a")
       args.append(options.appName)
    if options.CVSproj:
       args.append("-p")
       args.append(options.CVSproj)
    if options.trialName:
       args.append("-c")
       args.append(options.trialName)
    if options.makeCmd:
       args.append("-M")
       args.append(options.makeCmd)
    if options.makefile:
       args.append("-m")
       args.append(options.makefile)
    if options.makeFlags:
       args.append("-f")
       args.append(options.makeFlags)
    if options.pathToExe:
       args.append("-x")
       args.append(options.pathToExe)
    if options.srcDir:
       args.append("-n")
       args.append(options.srcDir)
    if options.PTdf:
       args.append("-e")
    if options.PERIxml:
       args.append("-P")
    if not options.srcDir and not options.CVSproj:
       print "You must specify either the name of the CVS project to check out or the name of the directory that contains the Makefile. Use the --CVSproj or --srcDir options."
       sys.exit(0)
    if options.verbosity == HIGH:
       args.append("-v")
    return args
    
  
def makeDataDirectory():
    timeStamp = string.split(str(datetime.datetime.isoformat( \
                                     datetime.datetime.now())), '.')[0]
    dirName = "perfTrackData_" + timeStamp
    try:
       os.mkdir(dirName)
    except:
       print "failed to make data directory: " + dirName
       sys.exit(1)
    return dirName

def checkInputs():
    """Parses command line arguments and returns their values"""

    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("--build_only", dest="buildOnly", action="store_true",
                      default=False,
                      help="you only want to build the executable.") 
    parser.add_option("--build_file", dest="buildDataFile",
                      help="you supply the build data file")
    parser.add_option("--app", dest="appName",
                      help="the name of the application")
    parser.add_option("--CVSproj", dest="CVSproj",
                      help="the name of the CVS project to check out")
    parser.add_option("--trial", dest="trialName",
                      help="the name you want to give this trial")
    parser.add_option("--makeCmd", dest="makeCmd",
                      help="specify the name of the make command to use")
    parser.add_option("--makefile", dest="makefile",
                      help="specify the name of the makefile to use")
    parser.add_option("--makeFlags", dest="makeFlags",
                      help="specify the flags to give to make")
    parser.add_option("--exeName", dest="exeName",
                      help="specify the name of the executable")
    parser.add_option("--srcDir", dest="srcDir",
                      help="specify the directory of the source files,default = .",
                      default=".")
    parser.add_option("--buildHelp", dest="buildHelp", action="store_true",
                      help="print options for building and exit")
 
   
    parser.add_option("--run_file", dest="runDataFile",
                      help="you supply the run data file")
    parser.add_option("--runHelp", dest="runHelp", action="store_true",
                      help="print options for running and exit")
    parser.add_option("--launcher", dest="launcher", default="pbs",
                      help="name of job launcher: lcrm,pbs,mpirun; default = pbs; for command line launchers, e.g. mpirun, the arguments to the command should be in the file given to the --batchFile argument")
                      # soon want to support all of these launchers
                      #help="name of job launcher: lcrm,pbs,loadleveler,mpirun,mpiexec; default = pbs")
    parser.add_option("--batchFile", dest="batchFile", 
                      help="specify the name of the batch file")
    parser.add_option("--inputDecks", dest="inputDecks",
                      help="a comma separated list of input decks")
    parser.add_option("--pathToExe", dest="pathToExe",
                      help="specify the path to the executable, default= /current/working/directory/ + name specified to --exeName option")

    parser.add_option("--CNL", dest="CNLfixes", action="store_true",
                      help="update batch file to gather information from compute nodes directly", default=False)

    parser.add_option("--exportEnv", dest="exportEnvAtLaunch", action="store_true",
                      help="for PBS, add flag to qsub to export environment variables to the job, -V", default=False)
    # The intention is that later this script will process performance
    # information also
    # Currently, it does not.
    #parser.add_option("--perf_file", dest="perfDataFile",
    #                  help="you supply the performance data file")
    #parser.add_option("--perfHelp", dest="perfHelp", action="store_true",
    #                  help="print options for performance data and exit")

    #parser.add_option("--perf_parser", dest="perfParser",
    #                  help="the performance data parser to run")

    parser.add_option("-v", "--verbose", action="store_const", 
                      dest="verbosity", const=1, help="be a little verbose")
    parser.add_option("-V", "--very_verbose", action="store_const", 
                      dest="verbosity", const=2, help="be more verbose")
    parser.add_option("-q", "--quiet", const=0,
                      action="store_const", dest="verbose", help="be quiet")
    parser.add_option("--ptdf", dest="PTdf", help="output to PTdf format",
                      action="store_true", default=False)
    parser.add_option("--peri", dest="PERIxml",help="output to PERI xml format",
                      action="store_true", default=False)
    (options, args) = parser.parse_args()

    if options.verbosity == HIGH:
        print "buildDataFile: %s " % options.buildDataFile
        print "runDataFile: %s " % options.runDataFile
        #print "perfDataFile: %s " % options.perfDataFile
        #print "perfParser: %s " % options.perfParser
  
    #if options.buildHelp or options.runHelp or options.perfHelp:
    if options.buildHelp or options.runHelp :
       if options.buildHelp:
          buildOptions()
       if options.runHelp:
          runOptions()
       sys.exit(0)

    if not options.appName:
       print "You must specify the name of the application you are building with the --app flag."
       sys.exit(0)

    if not options.pathToExe:
       options.pathToExe = os.getcwd()+"/" + options.appName

    return options

def buildOptions():
          print """
The following options are for building: 
--app, --CVSproj, --trial, --makeCmd, --makefile, --makeFlags, --exeName,
--srcDir""" 

def runOptions():
          print """
The following options are for running:
--app, --trial, --batchFile, --inputDecks, --pathToExe --launcher --CNL --exportEnv"""

if __name__ == "__main__":
    main()

