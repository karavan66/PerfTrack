#!/usr/bin/env python

# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information. 

from PTds import PTdataStore
from PTexception import PTexception
import re
import sys
from ResourceIndex import ResourceIndex
from Resource import Resource
from AttrVal import AttrVal
from PTcommon import  StringToList, getMachineName

def getRunInfo(resIdx, filename, eInfo, ptds):


    process(resIdx, filename, eInfo, ptds)


def get_initial_run_info(resIdx, attrs, eInfo, ptds):
    """Parses the run data file and addes the information to the Execution
       object, exe."""

    runMachineArg = eInfo.machineName
    # expect only one execution resource in resIdx
    [exe] = resIdx.findResourcesByType("execution")
    (runMachine, runOS, exe, numberOfProcesses, threadsPerProcess)\
             =  getInitialAVs(resIdx, attrs, exe, runMachineArg, ptds)  


    envNewName = ptds.getNewResourceName("env")
    env = Resource(envNewName, "environment")   
    resIdx.addResource(env)
    if attrs.getCurrent()[0] != "RunDataEnd":
       (exe) =  getSubmission(resIdx, attrs, exe, ptds) 
    if attrs.getCurrent()[0] != "RunDataEnd":
       (exe) =  getFilesystems(resIdx, attrs, exe, ptds) 
    if attrs.getCurrent()[0] != "RunDataEnd":
       (env) =  getLibraries(resIdx, attrs, env, exe ) 
       #env.dump(recurse=True)
    if attrs.getCurrent()[0] != "RunDataEnd":
       (exe) = getInputDecks(resIdx, attrs, exe, ptds)
 
    # expect only one build resource in resIdx
    [build] = resIdx.findResourcesByType("build")

    # check to see if we figured out how many processes there were
    if numberOfProcesses != -1:
       # yes, so create resource entries for all processes and threads 
       i = 0
       while i < int(numberOfProcesses):
           process = Resource(exe.name+Resource.resDelim+"Process-" + str(i),"execution"+Resource.resDelim+"process")
           resIdx.addResource(process)
           process.addAttribute("environment",env.name,"resource")
           process.addAttribute("build",build.name,"resource")
           process.addAttribute("OS name", runOS.name,"resource")
           if runMachine:
              process.addAttribute("machine name",runMachine.name,"resource")
           j = 0
           while j < int(threadsPerProcess):
               thread = Resource(process.name+Resource.resDelim+"Thread-" + str(j), "execution"+Resource.resDelim+"process"+Resource.resDelim+"thread")
               resIdx.addResource(thread)
               j += 1
           i += 1
    # couldn't figure out number of processes, so link up resources with 
    # the execution resource
    else: 
       exe.addAttribute("environment", env.name, "resource")
       exe.addAttribute("build", build.name, "resource")
       exe.addAttribute("OS name", runOS.name, "resource")
       if runMachine:
          exe.addAttribute("machine name",runMachine.name,"resource")


   
def getInitialAVs(resIdx, attrs, exe, runMachineArg, ptds):
    """Parses the attribute value pairs and extracts the needed information.
    """
    runAVs = []
    runOSAVs = []
    runOSName = ""
    runOSVersion = ""
    runOSType = ""
    runMachine = ""
    numberOfProcesses = -1
    threadsPerProcess = -1


    for name,value,type in attrs:
        #print '(%s,%s)' % (name,value)   
        if name == "RunDataBegin":
           pass
        elif (name == "LibraryBegin") or (name == "InputDeckBegin") \
             or (name == "RunDataEnd") or (name == "SubmissionBegin"):
            break 
        #Get run specific data
        elif name == "RunMachine":
           runMachine = value
        elif name == "PageSize":
           pageSize = value
           runAVs.append((name,value,"string"))
        elif name == "NumberOfProcesses":
           numberOfProcesses = value
           runAVs.append((name,value,"string"))
        elif name == "ProcessesPerNode":
           processesPerNode = value
           runAVs.append((name,value,"string"))
        elif name == "ThreadsPerProcess":
           threadsPerProcess = value
           runAVs.append((name,value,"string"))
        elif name.startswith("Run") and not (name.find("RunOS") >= 0):
           if name == "RunEnv":
              RunEnv = [] # a list of attr value pairs
                   #where attr = "RunEnv"+ (enviroment variable name)
                   #and value is the environment variable's value
                   #e.g.  for PATH=/usr/bin:/usr/local/bin
                   # attr = RunEnvPATH
                   # value = /usr/bin:/usr/local/bin
              RunEnv = StringToList("Env_","@@@", value)
              for (n,v) in RunEnv:
                  if(v != ""):
                     runAVs.append((n,v,"string"))
           else:
              runAVs.append((name,value,"string"))
        elif name.startswith("RunOS"):
               if name == "RunOSName":
                  runOSName = value
               elif name == "RunOSReleaseVersion":
                  runOSVersion = value
               elif name == "RunOSReleaseType":
                  runOSType = value
               elif(value != ""):
                   runOSAVs.append((name,value,"string"))
         
        else:
             runAVs.append((name,value,"string"))

    if runOSName == "" or runOSName == None:
       raise PTexception("no operating system name given in run data file for"\
                         " execution:%s" % exe.name )
    if runOSVersion == "" or runOSVersion == None or \
       runOSType == "" or runOSType == None:
       raise PTexception("no operating system details given in run data file "\
                         "for execution:%s" % exe.name )

    if runMachine == "" or runMachine == None:
        raise PTexception("no run machine name given in data file "\
                         "for execution:%s" % exe.name )

    runOSNewName = ptds.getNewResourceName(runOSName+" "+runOSVersion+" "+\
                             runOSType)
    runOS = Resource(runOSNewName, "operatingSystem", runOSAVs)
    resIdx.addResource(runOS)
  
    # if the run data doesn't know the machine name, then see if the user
    # sent it in as an argument to PTdFgen
    if runMachine == "" or runMachine == None:
       runMachine = runMachineArg
    # if they didn't do that, then we still don't know the machine
    if runMachine == "" or runMachine == None:
       runMach = None
    else:
       fullname,type = getMachineName(ptds, runMachine, "machine")
       #print "machine is %s " % runMachine 
       runMach = Resource(fullname,type)
       resIdx.addResource(runMach)
    exe.addAttributes(runAVs)
  
    if threadsPerProcess < 0:
       raise PTexception("ThreadsPerProcess attribute not given in run data "\
                             "file for execution:%s" % exe.name )

    if numberOfProcesses < 0:
       raise PTexception("NumberOfProcesses attribute not given in run data "\
                             "file for execution:%s" % exe.name )
    return  (runMach, runOS, exe, numberOfProcesses, \
            threadsPerProcess)



def getLibraries(resIdx, attrs, env, exe ):
    """Extracts information for library Resources"""   
    libraryAVs = []
    libraryIDList = [] 

    itsLibraryTime = False
    name = ""
    value = ""
    LibraryName = "" 

    n,v,t = attrs.getCurrent() 
    if n != "LibraryBegin":
        return (env)
    itsLibraryTime = True
    name,value,type = attrs.getNext()
    try:
        while(itsLibraryTime):
            while(name != "LibraryEnd"):
                    if name == "LibraryBegin":
                        LibraryName = "" # reset
                    elif(name == "LibraryName"):
                        LibraryName = value
                    else:
                        if(value != ""):
                          if name == "LibraryPath":
                            libraryAVs.append(("Path",value,"string"))
                          elif name == "LibraryMemberObject":
                            libraryAVs.append(("MemberObject",value,"string"))
                          elif name == "LibraryType":
                            libraryAVs.append(("Type",value,"string"))
                          elif name == "LibraryVersion":
                            libraryAVs.append(("Version",value,"string"))
                          elif name == "LibrarySize":
                            libraryAVs.append(("Size",value,"string"))
                          elif name == "LibraryTimestamp":
                            libraryAVs.append(("Timestamp",value,"string"))
                          else:
                            libraryAVs.append((name,value,"string"))
                    #get next attr value/pair or begin/end marker       
                    name,value,type = attrs.getNext()
                    #print '(%s,%s)' % (name,value)   

            #print 'done with one library' 
            if LibraryName == "" or LibraryName == None:
               raise PTexception("missing LibraryName attribute in run data "\
                                 "file for execution:%s. "  % exe.name)
            lib = Resource(env.name+Resource.resDelim+LibraryName, "environment"+Resource.resDelim+"module",\
                           libraryAVs)
            resIdx.addResource(lib)
            libraryAVs = []
            #print 'added library' + str(lib_id)

            if(name == "LibraryEnd"):
                    name,value,type = attrs.getNext()
            if name == None or (name.find("Library") < 0 ): #next name is not a library 
                    #print 'done with library'
                    itsLibraryTime = False
            #else:
                #print 'I think a library' + str(name)
    except:
        print "ERROR"
        raise
    else:
        return (env)
 
def getInputDecks(resIdx, attrs, exe, ptds):
    """Extracts information for inputDeck resources"""
    inputDeckAVs= []
    inputDeckIDList = []

    itsInputDeckTime = False
    name = ""
    value = ""

    name,value,t = attrs.getCurrent()
    #print '(%s,%s)' % (name,value)   
    try:
        if(name == "InputDeckBegin"):
               #print 'begin inputDecks'
               InputDeckName = ""
               itsInputDeckTime = True

        while(itsInputDeckTime):
            while(name != "InputDeckEnd"):
                    if name == "InputDeckBegin":
                        InputDeckName = "" # reset
                    elif(name == "InputDeckName"):
                        if value.find("/") >= 0:
                           parts = value.split("/") 
                           InputDeckName = parts[len(parts)-1]
                           inputDeckAVs.append(("Path",value,"string"))
                        else:
                           InputDeckName = value
                    else:
                        if(value != ""):
                            if name == "InputDeckModTime":
                               inputDeckAVs.append(("Modification Time",value,"string"))
                            else:
                               inputDeckAVs.append((name,value,"string"))
                    #get next attr value/pair or begin/end marker       
                    name, value,type = attrs.getNext()
                    #print '(%s,%s)' % (name,value)   

            #print 'done with one input deck' 
            if InputDeckName == "" or InputDeckName == None:
               raise PTexception("missing InputDeckName attribute in run data "\
                                 "file for execution:%s" % exe.name)
            #inDeck = Resource(Resource.resDelim+InputDeckName, "inputDeck", inputDeckAVs)
            InputDeckNewName = ptds.getNewResourceName(InputDeckName)
            inDeck = Resource(InputDeckNewName, "inputDeck", inputDeckAVs)
            resIdx.addResource(inDeck)

            inputDeckAVs = []
            #print 'added inputDeck' + str(inDeck_id)

            if(name == "InputDeckEnd"):
                    name,value,type = attrs.getNext()
            if name == None or (name.find("InputDeck") < 0): 
               #next name is not an input file
                    #print 'done with input file'
                    itsInputDeckTime = False
            #else:
                #print 'I think an input deck' + str(name)
    except:
        print "ERROR"
        raise
    else:
        return (exe)

def getSubmission(resIdx, attrs, exe, ptds):
    """Extracts information for the submission resource"""
    submissionAVs= []
    submissionIDList = []

    itsSubmissionTime = False
    name = ""
    value = ""

    name,value,type = attrs.getCurrent()
    #print '(%s,%s)' % (name,value)
    try:
        if(name == "SubmissionBegin"):
               #print 'begin submission'
               submissionName = ""
               itsSubmissionTime = True

        while(itsSubmissionTime):
            while(name != "SubmissionEnd"):
                    if name == "SubmissionBegin":
                        submissionName = "" # reset
                    elif(name == "jobName"):
                        newE = ptds.getNewResourceName(value) 
                        exe.setName(newE)
                    else:
                        if(value != ""):
                            submissionAVs.append((name,value,"string"))
                    #get next attr value/pair or begin/end marker
                    name, value,type = attrs.getNext()
                    #print '(%s,%s)' % (name,value)

            submissionNewName = ptds.getNewResourceName("submission")
            sub = Resource(submissionNewName, "submission", submissionAVs)
            resIdx.addResource(sub)


            if(name == "SubmissionEnd"):
                    name,value,type = attrs.getNext()
            itsSubmissionTime = False
    except:
        print "ERROR"
        raise
    else:
        return (exe)


def getFilesystems(resIdx, attrs, exe, ptds):
    """Extracts information for filesystem resources"""
    fileSystemAVs= []
    fileSystemIDList = []

    itsFileSystemTime = False
    name = ""
    value = ""

    name,value,t = attrs.getCurrent()
    #print '(%s,%s)' % (name,value)   
    try:
        if(name == "FileSystemBegin"):
               #print 'begin fileSystems'
               FileSystemName = ""
               itsFileSystemTime = True

        while(itsFileSystemTime):
            while(name != "FileSystemEnd"):
                    if name == "FileSystemBegin":
                        FileSystemName = "" # reset
                        devices = []
                    elif(name == "Name"):
                        FileSystemName = value
                    else:
                        if name == "DeviceBegin":
                           deviceName,deviceAVs = getFileSystemDeviceInfo(attrs)
                           devices.append((deviceName,deviceAVs))
                        elif value != "" :
                           fileSystemAVs.append((name,value,"string"))
                    #get next attr value/pair or begin/end marker       
                    name, value,type = attrs.getNext()
                    #print '(%s,%s)' % (name,value)   

            #print 'done with one filesystem' 
            if FileSystemName == "" or FileSystemName == None:
               raise PTexception("missing FileSystemName attribute in run data "\
                                 "file for execution:%s" % exe.name)
            FileSystemNewName = ptds.getNewResourceName(FileSystemName)
            fs = Resource(FileSystemNewName, "fileSystem", fileSystemAVs)
            resIdx.addResource(fs)

            for dname,dAVs in devices:
               d = Resource(fs.name + Resource.resDelim + dname, fs.type + Resource.resDelim + "device", dAVs)
               resIdx.addResource(d)

            fileSystemAVs = []
            #print 'added fileSystem' + str(inDeck_id)

            if(name == "FileSystemEnd"):
                    name,value,type = attrs.getNext()
            if name == None or (name.find("FileSystem") < 0):
               #next name is not a file system
                    #print 'done with file systems'
                    itsFileSystemTime = False
    except:
        print "ERROR"
        raise
    else:
        return (exe)


def getFileSystemDeviceInfo(attrs):
   
    # assumes current line is "DeviceBegin"
    deviceAVs = []
    name,value,t = attrs.getNext()
    while name != "DeviceEnd":
       if name == "Name":
          deviceName = value
       else:
          if value != "":
             deviceAVs.append((name,value,"string")) 
       name,value,t = attrs.getNext()
    #print "%s %s" % (deviceName, deviceAVs)
    return (deviceName,deviceAVs)

def parsePBSoutput(resIdx, runfilename, ptds):
    # parse the stdout and stderr of PBS to get additional run information
    # we expect there to be a files called jobprefix.pbs.out and 
    # jobprefix.pbs.err where jobprefix
    # is the same prefix as the .run file parsed in process()
    fileprefix = runfilename.rstrip('.run')
    pbsstdout = fileprefix + ".pbs.out"
    pbsstderr = fileprefix + ".pbs.err"
    try:
       f = open(pbsstdout,'r')
    except:
       raise PTexception("Run.parsePBSoutput could not open pbs stdout file: %s" % pbsstdout)

    [exe] = resIdx.findResourcesByType("execution")

    lines = f.readlines()

    for line in lines:
        if line.startswith("Job startup at"):
           jobStartTime = line.strip("Job startup at").strip()
           if jobStartTime != "":
              exe.addAttribute("jobStartTime",jobStartTime,"string")
        elif line.startswith("Jobs exit status"):
           jobExitStatus = line.strip("Jobs exit status code is ").strip()
           if jobExitStatus != "":
              exe.addAttribute("jobExitStatus",jobExitStatus,"string")
        elif line.find("completed ") >= 0:
           jobCompletionTime = ""
           for w in line.split()[3:]:
                jobCompletionTime += "%s " % w 
           if jobCompletionTime.strip() != "":
              exe.addAttribute("jobCompletionTime",jobCompletionTime,"string")
        elif line.startswith("Nodes used"):
           jobNodes = line.strip("Nodes used: ").strip()
           if jobNodes != "":
              exe.addAttribute("jobNodes",jobNodes,"string")
              nodes = jobNodes.split()
              count = 1
              for node in nodes:
                  fullname,type = getMachineName(ptds, node, "node")
                  if fullname != "":
                     exe.addAttribute("run node_%d" % count, fullname, "resource")
                  count += 1
        elif line.startswith("Job Resources used"):
           jobResources = line.strip("Job Resources used: ").strip()
           if jobResources != "":
              exe.addAttribute("jobResourcesUsed",jobResources,"string")
    f.close()

    # look though stderr file
    try: 
       f = open (pbsstderr,'r')
    except:
       raise PTexception("Run.parsePBSoutput could not open pbs stderr file: %s" % pbsstderr)
    lines = f.readlines()
    count = 1
    for line in lines:
       runError = line.strip()
       if runError != "":
          exe.addAttribute("RunErrorMsg_%d" % count, runError, "string")
       count += 1

    f.close()


       
            
            
        
def process(resIdx, arg, eInfo, ptds):

    if not ptds:
       raise PTexception("Run.process: expect to be connected to database, but am not.")

    # open the data file
    try:
       f = open(arg, 'r')
    except:
       raise PTexception("Run.process: could not open run data file:%s" % arg)

    attrs = AttrVal()

    line = f.readline()
    while line != '' :
        # get this value
        nvlist = re.split('=', line, 1)
        if len(nvlist) == 1:
           [n] = nvlist
           attrs.addPair(n)
        else:
           [n,v] = nvlist
           attrs.addPair(n,v)
        line = f.readline()

    if attrs.getFirst()[0] != "RunDataBegin":
       raise PTexception("Missing RunDataBegin in run data file %s" % arg)
    if attrs.getLast()[0] != "RunDataEnd":
       raise PTexception("Missing RunDataEnd in run data file %s" % arg)

    get_initial_run_info(resIdx, attrs, eInfo, ptds)

    if eInfo.pbsOut:
       parsePBSoutput(resIdx, arg, ptds)
	
    f.close()



