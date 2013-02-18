#!/usr/bin/env python


import sys,re,datetime
from optparse import OptionParser, SUPPRESS_HELP
from AttrVal import AttrVal
from PTcommon import  StringToList,fixListFormat
from PTexception import PTexception
from PERIxml import PERIxml

def main(argv=sys.argv):

    options = checkInputs(argv)
    if not options:
       return -1

    if options.runFile:
       runFile = options.runFile
       if not options.runXML:
          runXML = "%s.xml" % runFile
       else:
          runXML = options.runXML
       translateRun(runFile,runXML)

    if options.buildFile:
       buildFile = options.buildFile
       if not options.buildXML:
          buildXML = "%s.xml" % buildFile
       else:
          buildXML = options.buildXML
       translateBuild(buildFile, buildXML)

    if options.machineFile:
       machineFile = options.machineFile
       if not options.machineXML:
          machineXML = "%s.xml" % machineFile
       else:
          machineXML = options.machineXML
         

def checkInputs(argv):
    """Parses command line arguments and returns their values"""

    usage = "usage: %prog [options]\nexecute '%prog --help' to see options"
    version = "%prog 1.0"
    parser = OptionParser(usage=usage,version=version)
    parser.add_option("-r","--run_input", dest="runFile",
                      help="the name of the run data file")
    parser.add_option("-m","--machine_input", dest="machineFile",
                      help="the name of the machine data file")
    parser.add_option("-b","--build_input", dest="buildFile",
                      help="the name of the build data file")
    parser.add_option("-R","--run_output", dest="runXML",
                      help="the name of the output XML file for run data. The default is the input name with .xml appended to it.")
    parser.add_option("-M","--machine_output", dest="machineXML",
                      help="the name of the output XML file for machine data. The default is the input name with .xml appended to it.")
    parser.add_option("-B","--build_output", dest="buildXML",
                      help="the name of the output XML file for build data. The defalt is the input name with .xml appended to it.")

    (options, args) = parser.parse_args(argv[1:])


    return options


def translateBuild(buildFile, buildXML):
    try:
       iF = open(buildFile,'r')
    except:
       print "in transateBuild: Unable to open %s for reading." % buildFile
       return

    attrs = AttrVal()

    # get the attribute value pairs
    line = iF.readline()
    while line != '':
        # get this value
        nvlist = re.split('=', line, 1)
        if len(nvlist) == 1:
           [n] = nvlist
           attrs.addPair(n)
        else:
           [n,v] = nvlist
           attrs.addPair(n,v)
        line = iF.readline()

    iF.close()

    if attrs.getFirst()[0] != "BuildDataBegin":
       raise PTexception("Missing BuildDataBegin in build data file: %s" % buildFile) 
    if attrs.getLast()[0] != "BuildDataEnd":
       raise PTexception("Missing BuildDataEnd in build data file: %s" % buildFile)

    # create a peri object
    peri = PERIxml()

    # create the build 
    build = peri.createBuild()

    getBuildData(attrs, build, peri)
    if attrs.getCurrent()[0] != "BuildDataEnd":
       getCompilerData(attrs, peri)
    if attrs.getCurrent()[0] != "BuildDataEnd":
       getLibraries(attrs, peri, build)

    peri.writeData(buildXML)
    

def translateRun(runFile, runXML):
    try:
       iF = open(runFile,'r')
    except:
       print "in transateRun: Unable to open %s for reading." % runFile
       return

    attrs = AttrVal()

    # get the attribute value pairs
    line = iF.readline()
    while line != '':
        # get this value
        nvlist = re.split('=', line, 1)
        if len(nvlist) == 1:
           [n] = nvlist
           attrs.addPair(n)
        else:
           [n,v] = nvlist
           attrs.addPair(n,v)
        line = iF.readline()

    iF.close()

    if attrs.getFirst()[0] != "RunDataBegin":
       raise PTexception("Missing RunDataBegin in run data file for: %s" % runFile)
    if attrs.getLast()[0] != "RunDataEnd":
       raise PTexception("Missing RunDataEnd in run data file for: %s" % runFile) 
    # make a peri object
    peri = PERIxml()

    # create the run
    run = peri.createRun()

    getRunData(attrs, peri, run)
    if attrs.getCurrent()[0] != "RunDataEnd":
       getSubmissionData(attrs, peri, run)
    if attrs.getCurrent()[0] != "RunDataEnd":
       getFileSystems(attrs, peri, run)
    if attrs.getCurrent()[0] != "RunDataEnd":
       getLibraries(attrs, peri, run)
    if attrs.getCurrent()[0] != "RunDataEnd":
       getInputDecks(attrs, peri, run)

    peri.writeData(runXML)


def getBuildData(attrs, build, peri):

    executableAVs = []
    buildAVs = []
    AppName = ""
    AppConcurrency = ""
    AppLanguages = ""
    BuildMachine = ""
    BuildOSName = ""
    BuildOSVersion = ""
    BuildOSType = ""

    userName = ""
    BuildDateTime = ""
    buildEnvs = []

    # regular expressions for parsing


    for name,value,type in attrs:
        if name == "BuildDataBegin":
           pass
        elif name == "BuildDataEnd" or name.endswith("Begin"):
           # done with general attributes when we hit BuildDataEnd or
           # the Begin line for another resource, e.g. CompilerBegin
           break
        #Get executable specific data
        elif name == "ApplicationName":
           AppName = value
        elif name.startswith("Application"):
           if name  == "ApplicationLanguages":
              AppLanguages = fixListFormat(value)
           elif name == "ApplicationParadigms":
              AppConcurrency = fixListFormat(value)
           elif name == "ApplicationExeName":
              exeName = value
           # TODO at this time these attributes can't be represented in 
           # PERI XML
           #elif name == "ApplicationExeSize":
              #executableAVs.append(("Executable Size", value, "string"))
           #elif name == "ApplicationExePerms":
              #executableAVs.append(("Executable Permissions", value, "string"))
           #elif name == "ApplicationExeUID":
              #executableAVs.append(("Executable UID", value, "string"))
           #elif name == "ApplicationExeGID":
              #executableAVs.append(("Executable GID", value, "string"))
           #elif name == "ApplicationExeTimestamp":
              #executableAVs.append(("Executable Timestamp", value, "string"))
           elif name == "ApplicationExeUsername":
              userName = value
        # get Build specific data
        elif name.startswith("Build") and not (name.find("BuildOS") >= 0):
           if name == "BuildEnv":
              BuildEnv = [] # a list of attr value pairs
                   #where attr = "BuildEnv"+ (enviroment variable name)
                   #and value is the environment variable's value
                   #e.g.  for PATH=/usr/bin:/usr/local/bin
                   # attr = BuildEnvPATH
                   # value = /usr/bin:/usr/local/bin
              BuildEnv = StringToList("Env_","@@@", value)
              for (n,v) in BuildEnv:
                  if(v != ""):
                     buildEnvs.append((n,v))
           else:
              if name == "BuildNode" or name == "BuildMachine":
                 BuildMachine = value
              if name == "BuildDateTime":
                 BuildDateTime = value
        #get Build operating system  specific data
        elif name.startswith("BuildOS"):
               if name == "BuildOSName":
                  BuildOSName = value
               elif name == "BuildOSReleaseVersion":
                  BuildOSVersion = value
               elif name == "BuildOSReleaseType":
                  BuildOSType = value

    if BuildDateTime != "":
        peri.createTime(BuildDateTime, build)

    if AppName != "":
         #peri.createApplication(AppName, AppLanguages, AppConcurrency, build)
         app = peri.createApplication(AppName, build)
         peri.setApplicationAttribute(app, "languages", AppLanguages)
         peri.setApplicationAttribute(app, "concurrency", AppConcurrency)

    if userName != "":
       peri.createPerson(userName, build)

    # add the environment variables
    if len(buildEnvs) > 0:
       env = peri.createEnvironment(None,build)
    for nme,val in buildEnvs:
       peri.setEnvironmentAttribute(env, nme, val)

    if  exeName != "": 
        # model the executable as a file in the output set
        # can't express file attributes such as size, permissions, etc.
        peri.createExecutable(exeName, build)

    if BuildMachine != "":
        peri.createMachineNode(BuildMachine, build)

    if BuildOSName != "":
        os = peri.createOperatingSystem(BuildOSName, build)
        peri.setOperatingSystemAttribute(os, "version", BuildOSVersion)
        peri.setOperatingSystemAttribute(os, "release type", BuildOSType)


def getRunData(attrs, peri, run):
  
    appName = ""
    userName = ""
    runAVs = []
    runOSAVs = []
    runOSName = ""
    runOSVersion = ""
    runOSType = ""
    envVars = []

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
        elif name == "ApplicationName":
           appName = value
        elif name == "UserName":
           userName = value
        elif name == "RunDateTime" or name == "LaunchDateTime":
           peri.createTime(value, run)
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
                     envVars.append((n,v))
           else:
              runAVs.append((name,value))
        elif name.startswith("RunOS"):
               if name == "RunOSName":
                  runOSName = value
               elif name == "RunOSReleaseVersion":
                  runOSVersion = value
               elif name == "RunOSReleaseType":
                  runOSType = value
               elif(value != ""):
                   runOSAVs.append((name,value))

        else:
             runAVs.append((name,value))

    # application
    # this is required, so if unknown, say so
    if appName == "":
       appName = "unknown"
    app = peri.createProgram(appName, run)
    peri.setProgramAttribute(app, "version", "")

    # person
    if userName != "":
       peri.createPerson(userName, run)

    #operating system
    if runOSName != "":
        os = peri.createOperatingSystem(runOSName, run)
        peri.setOperatingSystemAttribute(os, "version", runOSVersion)
        peri.setOperatingSystemAttribute(os, "release type", runOSType)

    #environment variables
    if len(envVars) > 0:
       env = peri.createEnvironment(None, run)
       for name,value in envVars:
          peri.setEnvironmentAttribute(env, name,value)


def getCompilerData(attrs, peri):

    compilerAVs = []

    itsCompilerTime = False
    name,value,t = attrs.getCurrent()
    #print '(%s,%s)' % (name,value)
    try:
        if(name.startswith("Compiler")):
               #print 'begin compiler'
               CompilerName = ""
               CompilerVersion = ""
               itsCompilerTime = True

        while(itsCompilerTime):
            while(name != "CompilerEnd"):
                    if name == "CompilerBegin":
                        CompilerName = "" # reset
                        CompilerVersion = ""
                    elif(name == "CompilerName"):
                        CompilerName = value
                    elif value != "" :
                        if value.startswith("["):
                           value = fixListFormat(value)
                        if value != "":
                           compilerAVs.append((name,value))
                    #get next attr value/pair or begin/end marker
                    name, value,type = attrs.getNext()
                    #print '(%s,%s)' % (name,value)

            #print 'done with one compiler'
            if CompilerName == "" or CompilerName == None:
               raise PTexception("missing CompilerName attribute in build data"\
                                 " file ")

            compiler = peri.createCompiler(CompilerName)
            #peri.setCompilerName(compiler, CompilerName)
           
            for nme,val in compilerAVs:
                 peri.setCompilerAttribute(compiler, nme, val)

            compilerAVs = []

            if(name == "CompilerEnd"):
                    name,value,type = attrs.getNext()
            if name == None or (name.find("Compiler") < 0):
               #next name is not a compiler
                    #print 'done with compilers'
                    itsCompilerTime = False

    except:
        print "ERROR"
        raise



def getSubmissionData(attrs, peri, run):
    """Extracts information for the submission resource"""
    submissionAVs= []
    submissionIDList = []
    qEntries = []
    launcher = ""
    launcherVersion = ""
    batchAVs = []
    batchName = ""

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
                    elif name == "launcher":
                        launcher = value
                    elif name == "launcherVersion":
                        launcherVersion = value
                    elif name.startswith("batchQueueEntry"):
                        qEntries.append(value)
                    elif name == "batchFile":
                        batchName = value
                    elif name == "jobName" or name == "pbsResources" or\
                       name == "lcrmResources" or name.startswith("#PBS_") or\
                       name.startswith("#PSUB") or name.startswith("batchCmd") or\
                       name.startswith("runCmd") or name == "batchFileDateTime" \
                       or name.startswith("envVar"): 
                        if name.startswith("#PBS"):
                           name = "pbsDirective"
                        elif name.startswith("#PSUB"):
                           name = "lcrmDirective"
                        elif name.startswith("runCmd") or name.startswith("batchCmd") or name.startswith("envVar"):
                           # these attributes have _X, where X is an int 
                           # appended to them, strip it off, they are there
                           # so that they are unique in the perftrack database
                           # not needed here
                           name = name.split("_")[0]
                        if value != "":
                           batchAVs.append((name,value))
                    else:
                        if(value != ""):
                            submissionAVs.append((name,value))
                    #get next attr value/pair or begin/end marker
                    name, value,type = attrs.getNext()
                    #print '(%s,%s)' % (name,value)
            if(name == "SubmissionEnd"):
                    name,value,type = attrs.getNext()
            itsSubmissionTime = False

            sched = peri.createScheduler(launcher, run)
            peri.setSchedulerAttribute(sched, "version", launcherVersion)
        
            # batch queue entries
            queue = peri.createQueue(None,sched)
            #queue = doc.createElement("peri:queueContents")
            for qe in qEntries:
               if launcher == "pbs":
                  jobId,progName,userName,hoursRun,status,jobQueue= qe.split()
               elif self.launcher == "lcrm":
                  jobId,progName,userName,hoursRun,status,host= qe.split()
               else:
                  #TODO fix me
                  print "unsupported launcher: get queue contents"
                  break
               job = peri.createSchedulerJob(None, queue)
               peri.setSchedulerJobAttribute(job, "jobid", jobId)
               peri.setSchedulerJobAttribute(job, "programName", progName)
               peri.setSchedulerJobAttribute(job, "hoursRunning", hoursRun)
               peri.setSchedulerJobAttribute(job, "status", status)

        
        
            if batchName != "":
                batch = peri.createBatchFile(batchName, run)
                for name,value in batchAVs:
                   peri.setBatchFileAttribute(batch, name, value)

    except:
        print "ERROR"
        raise


def getFileSystems(attrs, peri, run):
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
               FileSystemVersion = ""
               itsFileSystemTime = True
               # file systems modeled as resources
               fsSet = peri.createFileSystemSet(None, run)

        while(itsFileSystemTime):
            while(name != "FileSystemEnd"):
                    if name == "FileSystemBegin":
                        FileSystemName = "" # reset
                        FileSystemVersion = ""
                        devices = []
                    elif(name == "Name"):
                        FileSystemName = value
                    elif name == "Version":
                        FileSystemVersion = value
                    else:
                        if name == "DeviceBegin":
                           deviceName,deviceAVs = getFileSystemDeviceInfo(attrs)
                           devices.append((deviceName,deviceAVs))
                        elif value != "" :
                           fileSystemAVs.append((name,value))
                    #get next attr value/pair or begin/end marker       
                    name, value,type = attrs.getNext()
                    #print '(%s,%s)' % (name,value)   

            #print 'done with one filesystem' 
            if FileSystemName == "" or FileSystemName == None:
               raise PTexception("missing FileSystemName attribute in run data "\
                                 "file for execution:%s" % exe.name)
            fs = peri.createFileSystem(FileSystemName, fsSet)
            peri.setFileSystemAttribute(fs, "version", FileSystemVersion)

            for dname,dAVs in devices:
               dev = peri.createDevice(dname, fs)
               for nme,val in dAVs:
                  if nme.find("%") >= 0:
                     nme = nme.replace("%","Percent")
                  peri.addDeviceAttribute(dev,nme, val)

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


def getFileSystemDeviceInfo(attrs):

    # assumes current line is "DeviceBegin"
    deviceAVs = []
    name,value,t = attrs.getNext()
    while name != "DeviceEnd":
       if name == "Name":
          deviceName = value
       else:
          if value != "":
             deviceAVs.append((name,value))
       name,value,t = attrs.getNext()
    #print "%s %s" % (deviceName, deviceAVs)
    return (deviceName,deviceAVs)

def getLibraries(attrs, peri, parent):
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
    libs = peri.createLibrarySet(None, parent)
    name,value,type = attrs.getNext()
    try:
        while(itsLibraryTime):
            while(name != "LibraryEnd"):
                    if name == "LibraryBegin":
                        LibraryName = "" # reset
                        LibraryPath = ""
                    elif(name == "LibraryName"):
                        LibraryName = value
                    else:
                        if(value != ""):
                          if name == "LibraryPath":
                            LibraryPath = value
                          #TODO figure out how to express these in PERI xml
                          #elif name == "LibraryMemberObject":
                            #libraryAVs.append(("MemberObject",value,"string"))
                          #elif name == "LibraryType":
                            #libraryAVs.append(("Type",value,"string"))
                          #elif name == "LibraryVersion":
                            #libraryAVs.append(("Version",value,"string"))
                          #elif name == "LibrarySize":
                            #libraryAVs.append(("Size",value,"string"))
                          #elif name == "LibraryTimestamp":
                            #libraryAVs.append(("Timestamp",value,"string"))
                          #else:
                            #libraryAVs.append((name,value,"string"))
                    #get next attr value/pair or begin/end marker       
                    name,value,type = attrs.getNext()
                    #print '(%s,%s)' % (name,value)   

            #print 'done with one library' 
            if LibraryName == "" or LibraryName == None:
               raise PTexception("missing LibraryName attribute in data "\
                                 "file for execution:%s. "  % exe.name)
            #peri.createLibrary(libs,LibraryName, LibraryPath, phaseName)
            lib = peri.createLibrary(LibraryPath, libs)
            if parent == peri.getBuild():
               peri.setLibraryAttribute(lib, "type", "static")
            else:
               peri.setLibraryAttribute(lib, "type", "dynamic")

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

def getInputDecks(attrs, peri, run):
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
               iset = peri.createInputs(None,run)

        while(itsInputDeckTime):
            while(name != "InputDeckEnd"):
                    if name == "InputDeckBegin":
                        InputDeckName = "" # reset
                        fullName = ""
                    elif(name == "InputDeckName"):
                        InputDeckName = value
                    # TODO figure out how to express these details in PERI
                    #else:
                        #if(value != ""):
                            #if name == "InputDeckModTime":
                               #inputDeckAVs.append(("Modification Time",value,"string"))
                            #else:
                               #inputDeckAVs.append((name,value,"string"))
                    #get next attr value/pair or begin/end marker       
                    name, value,type = attrs.getNext()
                    #print '(%s,%s)' % (name,value)   

            #print 'done with one input deck' 
            if InputDeckName == "" or InputDeckName == None:
               raise PTexception("missing InputDeckName attribute in run data "\
                                 "file for execution:%s" % exe.name)

            # input decks are input set?
            # again, no way to keep track of file details, version ,timestamp...
            peri.createFile(InputDeckName, iset)

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



if __name__ == "__main__":
   sys.exit(main())
