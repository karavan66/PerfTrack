#!/usr/bin/env python

# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information. 

import os, sys, re, commands, stat, time, string, datetime, glob
from optparse import OptionParser
from submission import Submission
from filesystem import fsInfo
from PTcommon import my_exec2,StringToList

global OS_name

def main(argv=None):
  
    if not argv:
       argv = sys.argv
    options = checkInputs(argv)
    if options.input_decks:
       iDs = options.input_decks.split(',')
       inputDecks = []
       for deck in iDs:
           inputDecks.append(deck.rstrip("\"").lstrip("\""))
              #input decks are a comma separated list
              # of file names (e.g. -i "file1,file2")
    else:
       inputDecks = [] 

    format = "old"
    if options.PERIxml:
       format = "PERIxml"

    filename = getData(options.exename, options.launcher, options.path, \
                       options.batchFile,\
                       inputDecks, options.usesMPI, options.usesOMP, \
                       options.usesPthreads,options.appName,format, options.CNLfixUp ,options.ptDataDir,options.exportEnvAtLaunch)
 
    return filename

def getData(exename, launcher, path=None, batchFile = "", \
            inputDecks=[], usesMPI=False, \
            usesOpenMP=False, usesPthreads=False, appname=None, format="old",CNLfixUp=False, ptDataDir="",exportEnvAtLaunch=False):

    uname_res = os.uname()
    run_OS_name = uname_res[0]
    run_OS_release_type = uname_res[2]
    run_OS_release_version = uname_res[3]
    globals()["OS_name"] = run_OS_name

    #what user is running this command
    userName = os.getenv('USER')

    # things we are expecting to get from parsing the launch command
    # or batch file:
    # machine name
    # number of processes, number of threads, processes per node,
    # partition job run on
    sub = Submission()
    okay = sub.getInfo(launcher,batchFile)
    if not okay:
       print "parsing of submission information failed"
       sys.exit(0)

    run_machine = sub.getRunMachine()
    numberOfProcesses = sub.getNumberOfProcesses()
    processesPerNode = sub.getProcessesPerNode()
    numberOfThreads = sub.getNumberOfThreads()
    numberOfNodes  = sub.getNumberOfNodes()
    if numberOfThreads == -1 and usesOpenMP == True:
       # default OMP_NUM_THREADS is number of cpus per node
       numberOfThreads = sub.getCpusPerNode() 
    elif numberOfThreads == -1:
       numberOfThreads = 1
       
       

    #print "runmachine="+str(run_machine)+ " usesMPI="+str(usesMPI) +" usesOpenMP="+ str(usesOpenMP) + " usesPthreads="+ str(usesPthreads) +" numberOfProcesses=" +str(numberOfProcesses) + " numberOfThreads="+ str(numberOfThreads) 

    #print "runmachine="+str(run_machine)
    #print " usesMPI="+str(usesMPI) 
    #print " usesOpenMP="+ str(usesOpenMP) 
    #print  " usesPthreads="+ str(usesPthreads) 
    #print " numberOfProcesses=" +str(numberOfProcesses) 
    #print  " numberOfThreads="+ str(numberOfThreads) 
           

    # Grab env vars to put in DB => runEnv
    (result, output) = commands.getstatusoutput('env')
    if (result != 0):
        print  'environment (\'env\') command failed with error: ' + str(result)
        print output
        sys.exit(2)
    # for simplicity, runEnvVars is a string of (envVar=value) separated by
    # '@@@'  e.g. envVar1=value1@@@envVar2=value2@@@envVar3=value3
    runEnvVars = output.replace("\n","@@@")

    page_size = os.sysconf('SC_PAGESIZE') #TODO double check this size has consistent units across platforms.
    if(path): 
       dynLibs = getDynamicLibs([path])
    else:
       dynLibs = getDynamicLibs([exename])


    # this gets file system information
    fs = fsInfo() 
    fs.getInfo()


    # if we're running on a Cray XT machine, the compute nodes may be running
    # compute node linux, while the login nodes are running regular  linux
    # we want to add some commands to the batch file to get some data 
    # directly from the compute nodes
    if(CNLfixUp):
       tmpBatch = "%s.ptBatch" % batchFile
       cmds = ""
       cmds += "aprun -n 1 uname -s > %s/out.uname ;" % ptDataDir
       cmds += "aprun -n 1 uname -r >> %s/out.uname ;" % ptDataDir
       cmds += "aprun -n 1 uname -v >> %s/out.uname ;" % ptDataDir
       cmds += "aprun -n 1 env > %s/out.env ;" % ptDataDir
       cmds += "ptCNLfix.py %s" % ptDataDir
       #sedcmd = "'s/PERFTRACK_CMDS/%s/g' %s > %s" % (cmds,batchFile,tmpBatch)
       my_exec2("cp %s %s" % (batchFile,tmpBatch), "")
       my_exec2('echo "%s" >>' % cmds, tmpBatch)
       batchFile = tmpBatch


    # get the current date and time in ISO format 
    launchTime = string.split(str(datetime.datetime.isoformat( \
                                     datetime.datetime.now())), '.')[0]


    # get input deck information
    # TODO fix this so that we can get the relevant information out from
    # the input decks - somehow. perhaps provide an interface to enter
    # name, value pairs for important input information, such as x=192 or 
    # weather=cloudy
    # for now, we are just recording the names of the files and their 
    # modification date.
    # oh, and we expect the input files to exist in the current working 
    # directory , or be given a complete path to the file
    
    iDecks= getInputDecks(inputDecks)

    # launch the job
    if launcher == "lcrm":
      (out, err, retval) = my_exec2("psub", batchFile)
      print out
      print err
    elif launcher == "pbs":
      #print "NOT LAUNCHING"
      if (CNLfixUp or exportEnvAtLaunch):
        (out, err, retval) = my_exec2("qsub -V", batchFile)
      else:
        (out, err, retval) = my_exec2("qsub", batchFile)
      print out
      print err 

    elif launcher == "mpirun":
      mpirunArgs = sub.getLauncherArgs()
      (out, err, retval) = my_exec2("mpirun", mpirunArgs)
      print out
      print err 
        

    # output data 
    if format == "PERIxml":
        filename = "perftrack_run_" + exename + "_" \
               + launchTime.replace(" ","") + "." + run_machine+ ".xml"

        if path:
           exeName = path
        else:
           exeName = exename
        printInPERIformat(filename,launchTime, userName, appname, exeName,run_machine, run_OS_name, run_OS_release_version, run_OS_release_type, runEnvVars, page_size, str(numberOfNodes), str(numberOfProcesses), str(processesPerNode), str(numberOfThreads), str(usesMPI), str(usesOpenMP), str(usesPthreads), sub, fs, dynLibs, iDecks ) 
        return filename

    if(exename == None):
       print "no exeName specified. Error"  
       sys.exit(1)
    filename = "perftrack_run_" + exename + "_" + launchTime.replace(" ","") \
               + "." + run_machine+ ".txt"
    file = open(filename,'w')
    file.write("RunDataBegin\n")
    file.write("LaunchDateTime=" + launchTime +"\n") 
    file.write("UserName=" + userName + "\n")
    if appname:
       file.write("ApplicationName=" + appname + "\n")
    if path:
       file.write("ExecutableName=" + path + "\n")
    else:
       file.write("ExecutableName=" + exename + "\n")
    file.write("RunMachine=" + run_machine + "\n")
    file.write("RunOSName=" + run_OS_name + "\n")
    file.write("RunOSReleaseVersion=" + run_OS_release_version + "\n" )
    file.write("RunOSReleaseType=" + run_OS_release_type + "\n")
    file.write("RunEnv="+ runEnvVars + "\n") 
    file.write("PageSize=" + str(page_size) + "\n") 
    if numberOfNodes != -1:
      file.write("NumberOfNodes=" + str(numberOfNodes) + "\n")
    if numberOfProcesses != -1:
      file.write("NumberOfProcesses=" + str(numberOfProcesses) + "\n")
    if processesPerNode != -1: # sometimes we can't figure it out
      file.write("ProcessesPerNode=" + str(processesPerNode) + "\n")
    if (usesOpenMP or usesPthreads) and numberOfThreads != -1:
      file.write("ThreadsPerProcess=" + str(numberOfThreads) + "\n")
    file.write("UsesMPI=" + str(usesMPI) +"\n")
    file.write("UsesOpenMP=" + str(usesOpenMP) + "\n")
    file.write("UsesPthreads=" + str(usesPthreads) +"\n")
    file.write(sub.printData())
    file.write(fs.printData())
    for l in dynLibs:
       file.write(l.printData())
    for (f,mt) in iDecks:
       file.write("InputDeckBegin\n")
       file.write("InputDeckName=" + f + "\n")
       file.write("InputDeckModTime=" + mt + "\n")
       file.write("InputDeckEnd\n")
    file.write("RunDataEnd\n")
    file.close()

 
    return filename


def checkInputs(argv):
    exename = None
    path = None
    input_decks = None
    batchFile = None
 
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("--appName", dest="appName",
                      help="specify the name of the application")
    parser.add_option("--exeName", dest="exename",
                      help="specify the name of the executable")
    parser.add_option("--pathToExe", dest="path",
                      help="specify the path to the executable")
    parser.add_option("--inputDecks", dest="input_decks",
                      help="specify the names of the input decks")
    parser.add_option("--batchFile", dest="batchFile",
                      help="specify the name of the batch file")
    parser.add_option("--mpi", dest="usesMPI", action="store_true",
                      help="the program uses MPI",default=False)
    parser.add_option("--openmp", dest="usesOMP", action="store_true",
                      help="the program uses OpenMP",default=False)
    parser.add_option("--pthreads", dest="usesPthreads", action="store_true",
                      help="the program uses pthreads",default=False)
    parser.add_option("--launcher", dest="launcher", default="pbs",
                      help="name of job launcher: lcrm,pbs; default = pbs")
    parser.add_option("--peri", dest="PERIxml", action="store_true",
                      help="output to PERI xml format",default=False)
    parser.add_option("--ptDataDir", dest="ptDataDir",default="", 
                      help="data directory containing perftrack data")
    parser.add_option("--CNL", dest="CNLfixUp", action="store_true",
                      help="will add extra cmds to batch file to execute on compute nodes", default = False)
    parser.add_option("--exportEnv", dest="exportEnvAtLaunch", action="store_true",
                      help="for PBS, will add flag to qsub to export environment to the job, -V", default = False)
    (options,args) = parser.parse_args(argv[1:])

    if not options.exename:
        print "You need to specify the name of the executable with the --exeName argument."
        sys.exit(0)

    return  options


def getDynamicLibs(Executables):
    """Gathers the libraries loaded by executables with ldd, 
       gets basic information about the libraries, and returns a 
       list of libraries
    """
    #gather libs from ldd output
    dynamic_libraries = []
    for exe in Executables:
       # in future, need to parse the batch script file to make sure
       # that any env vars that are set there are set here before we
       # call ldd (search for export, setenv, source, ...)
       # and get the right dynamic libs
       
       (output,stderr, retval) = my_exec2("ldd", exe)
       
       if (retval != 0) :
          print "\nCannot run ldd on " + exe + "!! No library information obtained !!"
          print output
          return []
       lines = output.split("\n")
       for line in lines:
          newLib = library()
          if (globals()["OS_name"] == "AIX"):
             #format: /full/path/to/lib/libname.a(objfilename.o)
             exename = exe.split('/')
             exename.reverse()  #get just the exe name
             words = line.split('(')  #split at the objfilename
             libname = words[0].split('/') #get just the lib name
             libname.reverse()
             if(exename[0] != libname[0]): #don't put the exe in the libs list
                newLib.name = libname[0]
                newLib.fullname = words[0]  #full path and name
                #In AIX land there are libs that don't end in .a and don't
                #have member objs
                #check to see if this is one of those
                if (libname[0].find(".a") != -1):
                   newLib.memberObject = words[1].rstrip(')')
             else:
                continue #skip the exe line
          else: #assume if not AIX then it's Linux for now
             #format: libname => /full/path/to/lib/libname (address)
             if line.startswith("linux-gate.so.1"):
                 # skip non-existant virtual library for linux 2.6
                 continue
             words = line.split()
             #is there path info in libname?
             if (words[0].find("/") != -1):
                 w = words[0].split("/") #extract out lib name
                 w.reverse()
                 newLib.name = w[0]
                 newLib.fullname = words[0]
             else:
                 newLib.name = words[0]
                 newLib.fullname = words[2].strip()
          (retval,stat) = statFile(newLib.fullname)
          if (retval == 0):
             newLib.size = str(stat.size)
             newLib.timestamp =  str(stat.mtime)
             newLib.version  = "" #TODO
             newLib.type = getLibraryType(newLib.name)
             newLib.dynamic = "True"
             dynamic_libraries.insert(0,newLib)
          else:
             print 'Error: could not stat ' + newLib.fullname
    return dynamic_libraries

def getLibraryType(libName):
    """Attempts to determine a type of the library based on it's name.  For
       example -lmpi would be an MPI library.
       returns a string typename
    """
    if(libName.find("mpi") != -1):
       return "MPI"
    elif(libName.find("elan") != -1):
       return "Network"
    elif(libName.find("thread") != -1):
       return "Thread"
    else:
       return ""

#def my_exec(cmd1,cmd2):
     #"""Executes cmd1 and gives it arguments in cmd2 (cmd2 is just a string
        #containing the arguments)
        #Returns stdout and the return status of cmd1
     #"""
     #Cmd = cmd1.strip() + ' ' + cmd2
     ##print "Cmd is " + Cmd
     #x = popen2.Popen3(Cmd, True)
     #x.tochild.close()
     #output = x.fromchild.read().strip()
     #retval = x.wait()
     #status = os.WEXITSTATUS(retval)
     ##if (status != 0):
        ##print "exec failed for " + Cmd
     #return (output, retval)

def statFile(file):
    theStat = Stat()
    try:
       mode = os.stat(file)
       theStat.perms = oct(mode[stat.ST_MODE]  & 0777)
       theStat.size = mode.st_size  #in bytes
       #theStat.mtime = mode.st_mtime
       theStat.mtime = datetime.datetime.fromtimestamp( \
                           mode[stat.ST_MTIME]).isoformat()
       return (0, theStat)
    except OSError, e:
       print  'Cannot stat ' + file + ' with error: ' + e.strerror
       return (-1, None)


class Stat:
   def __init__(self):
      self.perms = ""
      self.size = ""
      self.mtime = ""

class library:
  def __init__(self):
      self.name = ""
      self.fullname = ""
      self.memberObject = "" #for AIX, target obj in lib archive
      self.type = ""
      self.version = ""
      self.size = ""
      self.timestamp = ""
      self.dynamic = "True"
  def findL(self, listL):
      for L in listL:
         if(self.name == L.name and self.fullname == L.fullname):
            return L  #already in the list
      listL.insert(0,self)
      return self
  def printL(self):
      print '(name=' + self.name + ', fullname=' + self.fullname + \
            ', memberObject=' + self.memberObject + \
            ', type=' + self.type + ', version=' + self.version + \
            ', size=' + self.size + ', timestamp=' + self.timestamp + \
            ', dynamic=' + self.dynamic +')'
  def printData(self):
      return 'LibraryBegin\n' \
            + 'LibraryName=' + self.name + \
            '\nLibraryPath=' + self.fullname + \
            '\nLibraryMemberObject=' + self.memberObject + \
            '\nLibraryType=' + self.type + \
            '\nLibraryVersion=' + self.version+ \
            '\nLibrarySize=' + self.size + \
            '\nLibraryTimestamp=' + self.timestamp + \
            '\nLibraryDynamic=' + self.dynamic \
            + '\nLibraryEnd\n'

  def PERIformat(self, peri, parent):
       lib = peri.createLibrary(self.fullname, parent)
       peri.setLibraryAttribute(lib, "type", "dynamic")



def getInputDecks(inputDecks):
    # returns a list of tuples (f, mt)
    # f = input deck name,  mt =  modification time of file
    # allows elements of inputDecks to be contain wildcards * for searching
    # for the file with glob (e.g. zrad.* would match zrad.0008)
    # currently, only one file is matched for each filename in the list.
    # if glob returns multiple matches, we only take the first one
    list_o_file_info = []
    for inFile in inputDecks:
        #print "first file is : " + inFile
        if inFile.find("*") >= 0:
           infile = glob.glob(inFile)[0]
           #print "File is : " + infile
        else:
           infile = inFile 
           #print "File is : " + infile
        (res, stat) = statFile(infile)     
        list_o_file_info.append((infile, stat.mtime)) 

    return list_o_file_info

def printInPERIformat(filename, launchTime, userName, appname, exeName,run_machine, run_OS_name, run_OS_release_version, run_OS_release_type, runEnvVars, page_size, numberOfNodes, numberOfProcesses, processesPerNode, numberOfThreads, usesMPI, usesOpenMP, usesPthreads, sub, fs, dynLibs, iDecks ):

    from PERIxml import PERIxml

    peri = PERIxml()
    run = peri.createRun()
    peri.createTime(launchTime, run)

    # application
    # this is required, so if unknown, say so
    if appname == "":
       appname = "unknown"
    app = peri.createProgram(appname, run)
    peri.setProgramAttribute(app, "version", "")

    # person
    if userName != "":
       peri.createPerson(userName, run)

    #operating system
    if run_OS_name != "":
        os = peri.createOperatingSystem(run_OS_name, run)
        peri.setOperatingSystemAttribute(os, "version", run_OS_release_version) 
        peri.setOperatingSystemAttribute(os, "release type", run_OS_release_type) 

    #environment variables
    RunEnv = [] # hold the environment vars, (name, value) tuple list
    RunEnv = StringToList("","@@@", runEnvVars)
    if len(RunEnv) > 0:
       env = peri.createEnvironment(None, run)
    for nme,val in RunEnv:
       peri.setEnvironmentAttribute(env, nme, val)

    # other attributes of execution are ignored for now because they
    # can't be expressed in PERI xml
    # page_size, numberOfNodes, numberOfProcesses, processesPerNode, numberOfThreads, usesMPI, usesOpenMP, usesPthreads

    # call the submission object, ask it to add to the xml
    sub.PERIformat(peri, run)

    # call the filesystems object, ask it to add to the xml
    fs.PERIformat(peri, run)

    # get library info
    if len(dynLibs) > 0:
       libs = peri.createLibrarySet(None,run)
    for lib in dynLibs:
       lib.PERIformat(peri,libs)

    # get input deck info
    if len(iDecks) > 0:
       iset = peri.createInputs(None,run)
    for (f,mt) in iDecks:
       peri.createFile(f, iset)

    peri.writeData(filename)



if __name__ == "__main__":
      main()
