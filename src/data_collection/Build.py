#!/usr/bin/env python

# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information. 

from PTds import PTdataStore
from ResourceIndex import ResourceIndex
from Execution import Execution
from Resource import Resource
from PTexception import PTexception
from AttrVal import AttrVal
from PTcommon import  fixListFormat,getMachineName, StringToList
import re
import sys

def getBuildInfo(resIdx, filename, exeName, ptds):

  process(resIdx, filename, exeName,ptds)

 
def getInitialAVs(resIdx, attrs, exeName, ptds):
    """ Takes attrs, which is a list of name, value pairs, and builds
        a build Resource object and Execution object
    """

    executableAVs = []
    buildAVs = []
    buildOSAVs = []
    AppName = ""
    BuildMachType = ""
    BuildMachine = ""
    BuildOSName = ""
    BuildOSVersion = ""
    BuildOSType = ""

    # regular expressions for parsing


    for name,value,type in attrs:
        if name == "BuildDataBegin":
           pass
        elif name == "BuildDataEnd":
           break
	#Get executable specific data
        elif name == "ApplicationName":
           AppName = value 
        elif name == "ApplicationExeTrialName" or \
	     name == "ApplicationExeUserComment":
	   AppTrialName = value
        elif name.startswith("Application"):
           if name  == "ApplicationLanguages":
              value = fixListFormat(value)
              executableAVs.append(("Languages", value, "string"))
           elif name == "ApplicationParadigms":
              value = fixListFormat(value)
              executableAVs.append(("Concurrency", value, "string"))
           elif name == "ApplicationExeName":
              executableAVs.append(("Executable Name", value, "string"))
           elif name == "ApplicationExeSize":
              executableAVs.append(("Executable Size", value, "string"))
           elif name == "ApplicationExePerms":
              executableAVs.append(("Executable Permissions", value, "string"))
           elif name == "ApplicationExeUID":
              executableAVs.append(("Executable UID", value, "string"))
           elif name == "ApplicationExeGID":
              executableAVs.append(("Executable GID", value, "string"))
           elif name == "ApplicationExeTimestamp":
              executableAVs.append(("Executable Timestamp", value, "string"))
           elif name == "ApplicationExeUsername":
              executableAVs.append(("Username", value, "string"))
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
	             buildAVs.append((n,v,"string"))
           else:
	      if name == "BuildNode" or name == "BuildMachine":
                 BuildMachine = value
              if name == "BuildNode":
		 BuildMachType = 'node'
                 buildAVs.append(("Node Name",value,"string"))
              elif name == "BuildMachine":
		 BuildMachType = 'machine'
                 buildAVs.append(("Machine Name",value,"string"))
              if name == "BuildDateTime":
                 buildAVs.append(("DateTime",value,"string"))
        #get Build operating system  specific data
        elif name.startswith("BuildOS"):
	       if name == "BuildOSName":
	          BuildOSName = value
               elif name == "BuildOSReleaseVersion":
                  BuildOSVersion = value
               elif name == "BuildOSReleaseType":
                  BuildOSType = value

    if exeName == "" or exeName == None:
       raise PTexception("missing execution name in Build.getInitialAVs") 

    exeNewName = ptds.getNewResourceName(exeName)
    # ATTR CHANGE TODO
    # executableAVs should be attrs of build, not execution
    exe = Execution(exeNewName, executableAVs)
    resIdx.addResource(exe)

  
    newBuildName = ptds.getNewResourceName("build") 
    build = Resource(newBuildName, "build", buildAVs)
    resIdx.addResource(build)
    
    if BuildMachine == "" or BuildMachine == None:
       raise PTexception("missing build machine name in build data file for "
                         " execution:%s" % exeName)

    if BuildMachType == "node":
        fullname,type = getMachineName(ptds, BuildMachine, BuildMachType)
        #print fullname
        buildMachine = Resource(fullname,type)
    else: # machine
        fullname,type = getMachineName(ptds, BuildMachine, BuildMachType)
        buildMachine = Resource(fullname,type)

    if BuildOSName == "" or BuildOSName == None:
       raise PTexception("missing build operating system name for execution"\
                         "execution:%s" % exeName)
    if BuildOSVersion == "" or BuildOSVersion == None or \
       BuildOSType == "" or BuildOSType == None: 
       raise PTexception("missing build operating system details for execution"\
                         "execution:%s" % exeName)
    buildOSNewName = ptds.getNewResourceName(BuildOSName+" "+BuildOSVersion+\
                              " "+BuildOSType)
    buildOS = Resource(buildOSNewName, "operatingSystem", buildOSAVs)
    resIdx.addResources([buildOS,buildMachine])
    build.addAttribute("Node Name", buildMachine.name, "resource")
    build.addAttribute("OS Name", buildOS.name, "resource")


    return(build,exe)
    



def get_rest_of_build_info(resIdx, exe, build, attrs, exeName,ptds):
    """This parses out the rest of the build information 
       The rest of the information is the compilers, preprocessors,
       and static libraries. This information is added to the build attributes"""

    compilerAVs = []
    compCount = 0
    preprocessorAVs = []
    preprocCount = 0
    libraryAVs = []
    
    itsCompilerTime = False
    itsPreprocessorTime = False
    itsLibraryTime = False
    name = ""
    value = ""
    CompilerName = ""
    CompilerVersion = ""

    name,value,type = attrs.getNext()
    #print '(%s,%s)' % (name,value)   

    if(name == "CompilerBegin"):
        itsCompilerTime = True

    try: 
        while(itsCompilerTime):
            while  (name != "CompilerEnd"):
                   if name == "CompilerBegin":
                       CompilerName = ""
                       CompilerVersion = ""
                   elif(name == "CompilerName"):
		            CompilerName = value
                   elif(name == "CompilerVersion"):
                       CompilerVersion = value
                   else:
                       if(not (name.endswith("Path") or \
                               name.endswith("Vendor"))): 
		                value = fixListFormat(value)
                       if(value != ""):
                          if name == "CompilerPath":
	                     compilerAVs.append(("Path",value,"string"))
                          elif name == "CompilerVendor":
	                     compilerAVs.append(("Vendor",value,"string"))
                          elif name == "CompilerCompileFlags":
	                     compilerAVs.append(("CompileFlags",value,"string"))
                          elif name == "CompilerLibraries":
	                     compilerAVs.append(("Libraries",value,"string"))
                          elif name == "CompilerIncludePaths":
	                     compilerAVs.append(("IncludePaths",value,"string"))
                          elif name == "CompilerLibraryPaths":
	                     compilerAVs.append(("LibraryPaths",value,"string"))
                          elif name == "mpiScriptCompilerName":
	                     compilerAVs.append(("mpiScriptName",value,"string"))
                          elif name == "mpiScriptCompilerPath":
	                     compilerAVs.append(("mpiScriptPath",value,"string"))
                          else:
	                     compilerAVs.append((name,value,"string"))
                   name,value,type = attrs.getNext()
                   #print '(%s,%s)' % (name,value)   
                
    

            if CompilerName == "" or CompilerName == None:
                raise PTexception("missing compiler name for execution:%s"\
                      % exeName)
            if CompilerVersion == "" or CompilerVersion == None:
               compilerNewName = ptds.getNewResourceName(CompilerName)
            else:
               compilerNewName = ptds.getNewResourceName(CompilerName+" "+\
                                   CompilerVersion )
	    comp = Resource(compilerNewName, "compiler", compilerAVs)
            resIdx.addResource(comp)
            # associate the build with the compilers 
            build.addAttribute("compiler"+str(compCount), comp.name, "resource")
            compCount += 1
            compilerAVs = []
            
            if(name == "CompilerEnd"):
                     name,value,type = attrs.getNext()
            if name == None or (not (name.startswith("Compiler") \
               or name.startswith("mpiScript"))): #next name is not a compiler
	            #print 'done with compilers'
	            itsCompilerTime = False
        compilerAVs = []
    
        if (name == "PreprocessorBegin"):
	       #print 'begin preprocessors '
               itsPreprocessorTime = True
        
        while(itsPreprocessorTime):
	    while name != None and (name != "PreprocessorEnd"):
                    if name == "PreprocessorBegin":
	                pass
                    elif(name == "PreprocessorName"):
		        PreProcName = value
                    else:
                        if(not (name.endswith("Path") or \
                                name.endswith("Vendor"))): 
		            value = fixListFormat(value)
                        if(value != ""):
                          if name == "PreprocessorPath":
	                    preprocessorAVs.append(("Path",value,"string"))
                          elif name == "PreprocessorVendor":
	                    preprocessorAVs.append(("Vendor",value,"string"))
                          elif name == "PreprocessorVersion":
	                    preprocessorAVs.append(("Version",value,"string"))
                          elif name == "PreprocessorFlags":
	                    preprocessorAVs.append(("Flags",value,"string"))
                          else:
	                    preprocessorAVs.append((name,value,"string"))
	            #get next attr value/pair or begin/end marker	
                    name,value,type = attrs.getNext()
    
            PreProcNewName = ptds.getNewResourceName(PreProcName)
	    preproc = Resource(PreProcNewName, "preprocessor", preprocessorAVs)
            resIdx.addResource(preproc)
            build.addAttribute("preprocessor"+str(preprocCount),preproc.name, \
                               "resource")
            preprocCount += 1
	    preprocessorAVs = []
    
            if(name == "PreprocessorEnd"):
                    name,value,type = attrs.getNext()
            if name == None or (name.find("Preprocessor") < 0): #next name is not a preprocessor
	#            print 'done with preprocessors'
	            itsPreprocessorTime = False
        # associate the build with the preprocessors
        preprocessorAVs = []
        
        if (name == "LibraryBegin"):
	       #print 'begin libraries'
               itsLibraryTime = True
        
        while(itsLibraryTime):
	    while name != None and (name != "LibraryEnd"):
                    if name == "LibraryBegin":
	                pass
                    # ATTR CHANGE TODO
	            # I think that we will want to have this attribute when
                    # we move libraries out of /build and /env and into /code
                    elif name == "LibraryDynamic":
		        #we are only looking at static libraries here anyway
	                pass 
                    elif(name == "LibraryName"):
		        LibraryName = value
		    else:	 
                        #elif(name == "LibraryVersion"):
		                #LibraryVersion = value
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
    
	    # static libraries are children of build
	    lib = Resource(build.name+Resource.resDelim+LibraryName, "build"+Resource.resDelim+"module",  libraryAVs)
            resIdx.addResource(lib)
	    libraryAVs = []
    
            if(name == "LibraryEnd"):
                    (name,value,type) = attrs.getNext()
            if name == None or (name.find("Library") < 0): #next name is not a library 
	            #print 'done with library'
	            itsLibraryTime = False
    except:
        print "ERROR"
        raise
    else:
        return ( exe, build)


def process(resIdx, arg, exeName, ptds=None):

    if not ptds: 
       raise PTexception("Build.process: expect to already be connected to database, but am not.")

    # open the data file
    try:
       f = open(arg, 'r')
    except:
       raise PTexception("Build.process: could not open build data file:%s."\
                         % arg)

    attrs = AttrVal()

    line = f.readline() # eat BuildDataBegin
    line = f.readline()
    while line != '' and not (line.strip().endswith("Begin") or line.strip() == "BuildDataEnd"):
        # get this value
        nvlist = re.split('=', line, 1) 
        if len(nvlist) == 1:
            [n]  = nvlist
            attrs.addPair(n)
        else:
            [n,v] = nvlist
            attrs.addPair(n,v)
        line = f.readline()

    (Build, Exe) = getInitialAVs(resIdx, attrs,exeName, ptds)
    attrs_rest = AttrVal()
    
    while line != '' and line.strip() != "BuildDataEnd":
        # get this value
        nvlist = re.split('=', line, 1)
        if len(nvlist) == 1:
           [n] = nvlist
           attrs_rest.addPair(n)
        else:
           [n,v] = nvlist
           attrs_rest.addPair(n,v)
        line = f.readline()
    
    if line.strip() != "BuildDataEnd":
       print "line is:" + line
       raise PTexception("missing BuildDataEnd in build data file for "
                         "execution:%s" % Exe.name)
    if attrs_rest.getLength() != 0:
       (Exe,Build) = get_rest_of_build_info(resIdx, Exe, Build, \
                            attrs_rest, exeName,ptds)
                              

    f.close()
    return (Build, Exe)


