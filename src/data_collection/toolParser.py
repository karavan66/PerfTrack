#/usr/bin/env python

# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information. 

from glob import glob
from PTexception import PTexception
from Resource import Resource
from ResourceIndex import ResourceIndex
from Execution import Execution
from PerfResult import PerfResult
from PTcommon import isIP,mapIPtoNode
from PTds import PTdataStore
import socket

def getPerfInfo(resIdx, fnames, toolname, ptds=None):
    if toolname.lower() == ("mpip"):
       [f] = fnames
       mpipParse(resIdx, f)

    #elif toolname.lower() == ("sysmpi"):
    #   [dirname] = fnames
    #   sysmpiParse(resIdx, dirname, ptds)

    elif toolname.lower() == ("pmapi"):
       [f] = fnames
       pmapiParse(resIdx, f)
    
    elif toolname.lower() == ("paradyn"):
       [dirname] = fnames
       paradynParse(resIdx, dirname, ptds)
    elif toolname.lower() == ("gprof"):
       [f] = fnames
       gprofParse(resIdx, f)


def gprofParse(resIdx, fName, ptds):
    # parses a single text file created by "gprof exeName gmon.out"
    # only works for non-bsd format gprof files
    # currently only parses the flat profile portion
    # currently only works for C and Fortran programs, i.e. no C++
    
    perfTool = resIdx.findOrCreateResource("gprof", "performanceTool")

    # expect only one app and execution in resIdx
    [app] = resIdx.findResourcesByType("application")
    [exe] = resIdx.findResourcesByType("execution")
    exe.setApplication(app)

    machs = resIdx.findResourcesByShortType("machine")
    if len(machs) > 1:
       raise PTexception("More than one machine found for execution. This is not yet supported. Execution: %s" % exe.name)
    if machs != []:
        [machine] = machs
    else:
        machine = None 
    
    builds = resIdx.findResourcesByType("build")
    if len(builds) > 1:
       raise PTexception("More than one build found for execution. This is not supported. Execution: %s" % exe.name)
    if builds != []:  # if there's already a build resource, use that
       [build] = builds
    else:    # else create a new, placeholder one.
       buildName = ptds.getNewResourceName("build")
       build = resIdx.findOrCreateResource(buildName, "build")

    # create default context
    topContext = resIdx.createContextTemplate()

    # open the data file
    try:
       f = open(fName)
    except:
       raise PTexception("toolParser.gprofParse: could not open " + fName)

    # now extract which process generated this file. If the filename ends in .gprof
    # then we assume the data is for the whole execution
    # if the filename ends in .gprof.X, where X is an integer, we assume the integer
    # refers to the rank of the process
    if fName.endswith(".gprof"):
       procRes = None # the easy case!
    else:
       fNamePts = fName.split(".")
       processNum = fNamePts[len(fNamePts)-1]
       procRes = resIdx.findOrCreateResource(exe.name+Resource.resDelim+"Process-"+processNum,  "execution"+Resource.resDelim+"process")

    # if we know the particular resources, add them to the context
    if machine:
       topContext = resIdx.addSpecificContextResource(topContext,machine)
    if build:
       topContext = resIdx.addSpecificContextResource(topContext,build)
    if procRes:
       topContext = resIdx.addSpecificContextResource(topContext,procRes)

    # parse the flat profile 
    gprofParseFlatProfile(resIdx, f, topContext, exe, build, perfTool)

def gprofParseFlatProfile(resIdx, f, topContext, exe, build, perfTool):
    # parses the flat profile portion of gprof text output
 

    # auxiliary function for finding func resources in list of reses. 
    # this is used below when parsing the perf results
    # TODO can be optimized if is bottleneck
    def findFunc(fList, fName):
        # returns resource if "short name" matches fname
        # otherwise returns None
        for f in fList:
            if f.name.endswith(Resource.resDelim+fName):
               return f
        return None

    # look for start of flat profile 
    line = f.readline()
    while line and line.lower().find("flat profile") < 0:
          line = f.readline()

    # there's no flat profile data in this file
    if not line:
       return
    
    GNU = False 
    if line.find("Flat") >= 0: 
       #GNU gprof starts with "Flat profile"
       GNU = True
    #else assume AIX gprof, starts with "flat profile" 
   
    # try to find metrics  
    line = f.readline()
    if GNU:
       while line.find("%") < 0:
            line = f.readline() # expect this to be first metric line
    else: 
       while line.find("ngranularity") < 0:
            line = f.readline()
       line = f.readline() # eat blank line
       line = f.readline() # read first metric line


    # metric lines look like:
    # %    cumulative   self           self    total
    # time  seconds    seconds  calls  s/call  s/call   name
    metFirstRow = line.split()  # should have length of 5
    metSecondRow = f.readline().split() # should have length of 7
   
    # list of metric (resource,unit) pairs
    metrics =  []
    # there are 5 metrics and a function name
    i = 0 # second row iterator
    j = 0 # first row iterator - need another b/c there's a blank in 1st row
    while i < 6:
        if i != 3:
           metricName = metFirstRow[j] + " " + metSecondRow[i]
           j += 1
        else:
           metricName = metSecondRow[i] 
        if metricName.find("/") >= 0: # since we use / for hierarchical names,
                                  # it's confusing if they are part of the name
                                      # replace with "per" e.g. calls/sec => 
                                      # calls per sec
            metricName = metricName.replace("/"," per ")  
        #print "metricName is: " + metricName 
        metric = resIdx.findOrCreateResource(metricName, "metric")
        metrics.append((metric,metSecondRow[i]))
        i += 1
   
    # now read in actual data
	perfReses = []
    line = f.readline()
    while line.strip() != "":  # until we reach a blank line
        perfReses.append(line)  
        line = f.readline()

    # get a list of the functions that we already know about in the program
    # if the function is already known, then we use that one
    # otherwise, we have no idea to what code the function belongs to. e.g. is 
    # it part of the source code (build hierarchy), 
    # part of a library (env hier)?
    # if we don't know where it belongs, we add it to the build in module 
    # "unknownModule"
    # I am not using findResourceByName here because I have no knowledge of 
    # the module name for the function.
    fList = resIdx.findResourcesByShortType("function")
    
    # if needed, we will create a placeholder build/module called unknownModule
    # to hold these functions.  
    unkModule = None

    # for each perfRes
    for ps in perfReses:
        prs = ps.split()
        missingInfo = False  # if "calls" has value of 0, gprof doesn't print the data
                             # in the last three data columns
        
        if len(prs) >= 7:
           function = prs[6]  # extract function name
        else:
           function = prs[3] # extract function name
           missingInfo = True
        
        #if not GNU:
           #function = function.rstrip("()")
        fRes = findFunc(fList, function)
        if fRes == None: # dne, so create
           if not unkModule:  # dne, so create
              unkModule = resIdx.findOrCreateResource(build.name + Resource.resDelim+ "unknownModule",  "build"+Resource.resDelim+"module")
           fRes = resIdx.findOrCreateResource(unkModule.name + Resource.resDelim + function,  "build"+Resource.resDelim+"module"+Resource.resDelim+"function")
        context = resIdx.addSpecificContextResource(topContext,fRes)
        i = 0
        # make perfReses for % time, cum secs, self secs
        while i < 3:  
           value = prs[i]
           (met,units) = metrics[i]
           result = PerfResult(context, perfTool, met, value, units,\
               "noValue", "noValue")
           exe.addPerfResult(result)
           i += 1
        # if there's data, make perfReses for calls, self s/call,total s/call
        if not missingInfo:  
           while i < 6:
              value = prs[i]
              (met,units) = metrics[i]
              result = PerfResult(context, perfTool, met, value, units,\
                  "noValue", "noValue")
              exe.addPerfResult(result)
              i += 1
 
     
     
def paradynParse(resIdx, execName, dirName, ptds):
    # parses data from the Paradyn Parallel Performance tool
    # parses the resources file (named execName.resources)
    # and any histogram files (named execName.hist_*)

    perfTool = Resource("Paradyn", "performanceTool")
    resIdx.addResource(perfTool)
    metrics = []

    # expect only one app and execution in resIdx
    [app] = resIdx.findResourcesByType("application")
    [exe] = resIdx.findResourcesByType("execution")

    machs = resIdx.findResourcesByShortType("machine")
    if len(machs) > 1:
       raise PTexception("More than one machine found for execution. This is not yet supported. Execution: %s" % exe.name)
    if machs != []:
        [machine] = machs
    else:
       raise PTexception("Need machine resource for parsing Paradyn data.")

    # parse the resources file, which is a list of all the resources in the 
    # application that Paradyn knows about - very many
    try:
      f = open(dirName+"/" + execName + ".resources")
    except:
       raise PTexception("toolParser.paradynParse: could not open "\
                         "resource list file:%s" % dirName+"/resources")
    # need to replace names generated by bld and run processing scripts 
    # for processes and threads to Paradyn names. That's what the var
    # processCount is for
    # TODO need to support the same sort of thing for threads
    processCount = 0
    syncObj = None
    line = f.readline()
    while line != '':

        print "processing line: %s" % line.strip()
        (syncObj, res) = ParadynConvertRes(line.strip(), resIdx, exe, machine,  syncObj, ptds, "alwaysCreate", processCount)

        if res.type.endswith("process"):
           processCount += 1
        line = f.readline()
    f.close()
    globalPhaseName = ptds.getNewResourceName("globalPhase") 
    globalPhase = Resource(globalPhaseName, "time")
    resIdx.addResource(globalPhase)
    
    # expect only one application in resIdx
    [app] = resIdx.findResourcesByType("application")
    exe.setApplication(app)

    contextTemplate = resIdx.createContextTemplate()
    topContext = resIdx.addSpecificContextResource(contextTemplate,machine)

    hists = glob(dirName+"/" + execName + ".hist_*")
    for hist in hists:
       print "processing: %s" % hist
       try:
          f = open(hist) 
       except:
          raise PTexception("toolParser.paradynParse: could not open "\
                         "histogram file:%s" % hist)
       ParadynParseHist(f,topContext,resIdx,exe, machine,perfTool, syncObj,globalPhase) 
       f.close()
    #TODO are there paradyn histogram files that are not named hist_* ?
    # I believe it's possible for a user to generate a histogram file and
    # give it any name they want. This case is not handled here yet.

def ParadynParseHist(f, topContext, resIdx, exe, machine, perfTool, syncObj,globalPhase):
    # parses a single Paradyn Histogram file of the format generated by
    # the "Export" button on the main Paradyn GUI window or from the "File/Save"
    # menu option on a histogram visualization
    #   A paradyn data file may contain one or more histogram tables
    #  This function calls ParadynParseOneHist for each histogram table
    # in a histogram file. Each histogram table has a header and some
    # number of data values, one per line.  
 
    # This expects f to be an open file handle
    # we'll read a line of the file. It will either be the beginning of a 
    # header (a line of ################) or the empty string because it's 
    # EOF and we're done with this file
    line = f.readline().strip()
    while line:
       ParadynParseOneHist(f, topContext, resIdx, exe, machine, perfTool, syncObj,globalPhase)
       line = f.readline().strip() # is there another histogram table?


def ParadynParseOneHist(f, topContext, resIdx, exe, machine, perfTool, syncObj, globalPhase):
    # parses a single Paradyn Histogram table 
    # expects f to be an open file handle
    # expects first line of header (line of ######) to be already read
 
    #   Each paradyn histogram table has the following format
    #
    #   ######################################
    #   #     Paradyn Resource Histogram Table
    #   #     ==================================
    #   #
    #   #     Metric: <metric name> (units, metricType)
    #   #     NumEntries: <number of entries for this histogram>
    #   #     Granularity: <length of time each entry represents> <units>
    #   #     StartTime: <time measurements for this histogram started> <units>
    #   #     Phase: <phase name>
    #   #     Focus: <focus name>
    #   ######################################
    #   nan
    #   nan
    #   ...... NumEntries data values separated by new lines

    line = f.readline()  # eat title line
    line = f.readline() # eat line of ========
    line = f.readline() # eat blank line

    # next line gives metric information
    #   #     Metric: <metric name> (units, metricType)
    # metInfo equals  metname("units",type)
    line = f.readline()
    metInfo = line.split()[2]
    metName = metInfo.split('(')[0]
    metUnits = metInfo.split('(')[1].split(',')[0].rstrip('"').lstrip('"')   
    metType = metInfo.split('(')[1].split(',')[1].rstrip(')')
    metric = resIdx.findOrCreateResource(metName, "metric")

    # next line is number of entries
    #   #     NumEntries: <number of entries for this histogram>
    line = f.readline().strip()
    numEntries = int(line.split()[2])

    # next line is Granularity of measurements, aka "bucket size"
    #   #     Granularity: <length of time each entry represents> <units>
    line = f.readline().strip()
    bucketSize = float(line.split()[2]) 
    bucketUnits = line.split()[3]

    # next line is starting time of measurements
    #   #     StartTime: <time measurements for this histogram started> <units>
    line = f.readline().strip()
    startTime = float(line.split()[2])
    timeUnits = line.split()[3]
   
    # next line is phase name
    #   #     Phase: <phase name>
    line = f.readline().strip()
    phaseName = line.split()[2]
    thisPhase = None
    if phaseName == "Global":
       # this is whole execution data
       pass
    else:
       thisPhase = resIdx.findOrCreateResource(globalPhase.name+Resource.resDelim  +phaseName,"time"+Resource.resDelim+"interval" )

    # next line is the context - list of resources 
    #   #     Focus: <focus name>
    line = f.readline().strip()
    focusName = line.split()[2] 
    reses = ParadynParseFocus(focusName, topContext, resIdx, exe, machine, syncObj)
    #print line
    #print reses
    node = None
    for r in reses:
        # if we have a process resource in the focus, then we want to add the
        # data we have about what machine the process ran on to the context 
        if r.type.endswith("process"):
           (runMach,runMachName,attrType) = r.getAttributeByName("run machine")
           if runMachName != None:
              node = resIdx.findResourceByName(runMachName)
           break        
    # if we found a specific machine resource, add it to the context
    if node:
       reses.append(node)
    context = resIdx.addSpecificContextResources(topContext,reses)

    # eat header ending line ( line of #############)
    line = f.readline().strip()

    # expect one execution resource in resIdx
    [exe] = resIdx.findResourcesByType("execution")
  
    endTime = startTime + bucketSize 
    # we will put the time information in both the start_time, end_time fields
    # of the performance result table as well as in the time hierarchy
    # until we figure out which is best
    # whole execution time = "global_phase"
    # these histogram time intervals are children of the global phase. 
    # Attributes of
    # the interval will be the start time and end time of the measurement
    # other phases will also be children  of the global phase with 
    # start time and end time attributes
    timeInterval = 0 # keep track of the time interval 'name'
    
    while timeInterval < numEntries:
       line = f.readline().strip()
       if line == 'nan': # no value gathered for this time interval
          pass
       else:
          value = line
          if thisPhase:
             timeRes = resIdx.findOrCreateResource(thisPhase.name +Resource.resDelim+'bin_'+str(timeInterval), "time"+Resource.resDelim+"interval"+Resource.resDelim+"subinterval")
          else:
             timeRes = resIdx.findOrCreateResource(globalPhase.name +Resource.resDelim+'bin_'+str(timeInterval), "time"+Resource.resDelim+"interval")
          timeRes.addAttributes([("startTime",str(startTime),"string"),\
                                 ("endTime",str(endTime),"string"), \
                                 ("units", timeUnits,"string")])
          thisContext = resIdx.addSpecificContextResource(context,timeRes)
          result = PerfResult(thisContext, perfTool, metric, value, \
                 metUnits, str(startTime), str(endTime))
          exe.addPerfResult(result)

       startTime = endTime
       endTime = startTime + bucketSize 
       timeInterval += 1


def ParadynParseFocus(measContext, topContext, resIdx, exe, machine, syncObj):
    # this function parses the focus from a paradyn histogram file and returns
    # the list of resources that are in the focus. We add this list 
    # of resources to the context for the performance result
    pdReses = measContext.split(',')
    specificContextReses = []
    for pdRes in pdReses:
        if pdRes.count('/') == 1:
           # top level context - don't need to do anything. It's already in
           # topContext
           pass
        else:
           (syncObj, res) = ParadynConvertRes(pdRes, resIdx, \
                       exe, machine,  syncObj)
           specificContextReses.append(res)
    return (specificContextReses)
      
     
def ParadynConvertRes(pdRes, resIdx, exe, machine, syncObj, ptds=None, \
                      method="findOrCreate", processCount=-1 ):

    # converts paradyn resource names into the default PT resource hierarchy
 
    # to cut down on the time it takes to parse the resources file
    # adding the option to just create all the resources instead of looking 
    # to see if they exist first.
    if method == "findOrCreate":
       resourceFunc = resIdx.findOrCreateResource
    elif method == "alwaysCreate":
       resourceFunc = Resource
    else:
       raise PTexception("Unsupported method type in " \
                         "toolParser.ParadynConvertRes: %s" % method) 

    rnames = pdRes.strip('/').split('/') # get individual resource names
    hierType = rnames[0]
    res = None # the PT resource that was created or found
    if hierType == "Machine":
       # machine hierarchy goes like so
       # /Machine/nodeName/process/thread, thread is optional
       nodeName = rnames[1]
       if len(rnames) > 2:
          processName = rnames[2]
       else:
          processName = ""
       if len(rnames) > 3:
          threadName = rnames[3]
       else:
          threadName = ""
       # paradyn sometimes writes the IP address of the node out instead of
       # its hostname
       if isIP(nodeName):
          nodeName = mapIPtoNode(nodeName)
       # the resources in the database are not the fully-qualified names of
       # the nodes. e.g. node13 as opposed to node13.myplace.gov
       # so strip off just the node name
       if nodeName.find('.'):
          nodeName = nodeName.split('.')[0]
       hw = resourceFunc(machine.name+Resource.resDelim+"batch"+Resource.resDelim+nodeName,  "grid"+Resource.resDelim+"machine"+Resource.resDelim+"partition"+Resource.resDelim+"node")
       resIdx.addResource(hw)
       res = hw
       if processName != "":
          # need to replace names like Process-0, Process-1 with Paradyn
          # process names, e.g. Process-exeName{pid}
          # TODO : somehow make this more robust.
          if processCount >= 0:
             oldNameProcess = resIdx.findResourceByName(exe.name+Resource.resDelim+"Process-" + str(processCount))
             if oldNameProcess:
                des = resIdx.getResourceDescendants(oldNameProcess)
                for d in des:
                    oldName = d.name
                    print oldName
                    resNames = oldName.split(Resource.resDelim)
                    print resNames
                    idx = resNames.index("Process-"+str(processCount))
                    resNames[idx] = "Process-" + processName
                    newName = ""
                    for r in resNames:
                        if newName == "":
                           newName = r
                        else:
                           newName += Resource.resDelim + r
                    print "change old:%s to new:%s" % (oldName, newName)
                    resIdx.updateResourceName(d,newName)
                newName = exe.name+Resource.resDelim+"Process-" +processName
                resIdx.updateResourceName(oldNameProcess,newName)
             process = oldNameProcess
          if processCount == -1 : #then we just do it the old way
             process = resourceFunc(exe.name+Resource.resDelim+"Process-" +\
                     processName, "execution"+Resource.resDelim+"process")
             resIdx.addResource(process)
          process.addAttribute("run machine",hw.name, "resource")
          res = process
       if threadName != "":
          thread = resourceFunc(process.name+Resource.resDelim+"Thread-" + threadName, "execution"+Resource.resDelim+"process"+Resource.resDelim+"thread")
          resIdx.addResource(thread)
          res = thread
    elif hierType == "Code": 
       # code hierarchy goes like so
       # /Code/moduleName/functionName/loopName, loop is optional
       moduleName = rnames[1]
       functionName = rnames[2]
       if len(rnames) > 3:
          loopName = rnames[3]
       else:
          loopName = ""
       # attempt to determine if module goes in environment or build...
       # currently, this defaults to the build hierarchy
       dynamic = False
       if moduleName.find(".so") >= 0:
          dynamic = True
       if moduleName.find(".a") >= 0: # for AIX
          env = resIdx.findResourcesByType("environment")
          if resIdx.findResourcesByName(env.name+Resource.resDelim+moduleName):
             dynamic = True

       if dynamic:
          [hier] = resIdx.findResourcesByType("environment")
       else:
          [hier] = resIdx.findResourcesByType("build")
       module = resourceFunc(hier.name+Resource.resDelim+moduleName, \
                   hier.type+Resource.resDelim+"module")
       resIdx.addResource(module)
       function = resourceFunc(module.name+Resource.resDelim+functionName, \
                       module.type+Resource.resDelim+"function")
       resIdx.addResource(function)
       res = function
       if loopName != "":
          loop = resourceFunc(function.name+Resource.resDelim+loopName, \
                   function.type+Resource.resDelim+"codeBlock")
          resIdx.addResource(loop)
          res = loop
    elif hierType == "SyncObject": 
       
       syncType = rnames[1]
       if syncObj:
          topSync = syncObj
       else:
          allSyncName = ptds.getNewResourceName("all_sync_objects")
          topSync = resourceFunc(allSyncName, "syncObject")
          syncObj = topSync
          resIdx.addResource(topSync)
       if syncType == "Message": 
          # Message hierarchy goes like so
          # /SyncObject/Message/communicator/messageTag, communicator, 
          # messageTag optional
          message = resourceFunc(topSync.name+Resource.resDelim+"Message", \
                    "syncObject"+Resource.resDelim+"Message")
          resIdx.addResource(message)
          res = message
          if len(rnames) > 2:
             commName = rnames[2]
             communicator = resourceFunc(res.name+Resource.resDelim+commName, "syncObject"+Resource.resDelim+"Message"+Resource.resDelim+"communicator")
             resIdx.addResource(communicator) 
             res = communicator
          if len(rnames) > 3:
             tagName = rnames[3]
             tag = resourceFunc(res.name+Resource.resDelim+tagName, \
                       res.type+Resource.resDelim+"messageTag")
             resIdx.addResource(tag)
             res = tag
       elif syncType == "Semaphore": 
          res = resourceFunc(topSync.name+Resource.resDelim+"Semaphore", \
                     "syncObject"+Resource.resDelim+"Semaphore")
          resIdx.addResource(res)
          if len(rnames) > 2:
             raise PTexception("Semaphore not implemented yet in "\
                            "toolParser.paradynParse")
          else:
             pass
       elif syncType == "Barrier": 
          res = resourceFunc(topSync.name+Resource.resDelim+"Barrier", \
                     "syncObject"+Resource.resDelim+"Barrier" )
          resIdx.addResource(res)
          if len(rnames) > 2:
             raise PTexception("Barrier not implemented yet in "\
                            "toolParser.paradynParse")
          else:
             pass
       elif syncType == "SpinLock": 
          res = resourceFunc(topSync.name+Resource.resDelim+"SpinLock", \
                     "syncObject"+Resource.resDelim+"SpinLock")
          resIdx.addResource(res)
          if len(rnames) > 2:
             raise PTexception("SpinLock not implemented yet in "\
                            "toolParser.paradynParse")
          else:
             pass
       elif syncType == "Window": 
          res = resourceFunc(topSync.name+Resource.resDelim+"Window", \
                 "syncObject"+Resource.resDelim+"Windows")
          resIdx.addResource(res)
          if len(rnames) > 2:
             winName = rnames[2]
             window = resourceFunc(res.name+Resource.resDelim+winName, "syncObject"+Resource.resDelim+"Windows"+Resource.resDelim+"window")
             resIdx.addResource(window)
             res = window

    return (syncObj, res)

def pmapiParse(resIdx, fname):

    try:
       f = open(fname,'r')
    except:
       raise PTexception("toolParser.pmtoolkitParse: could not open "\
                         "performance data file:%s" % fname)


    perfTool = Resource("PMAPI", "performanceTool")
    resIdx.addResource(perfTool)
    metrics = []
   
    # expect one execution resource in resIdx 
    [exe] = resIdx.findResourcesByType("execution") 
    [app] = resIdx.findResourcesByType("application") 
    
    exe.setApplication(app) 
    contextTemplate = resIdx.createContextTemplate()
    line = f.readline()
    while line != '':
       if line.find("PM_COUNTER") >= 0:
          rank = line[:line.index(":")].strip()
          [x,y,counter,value]= line.split()
          metric = resIdx.findOrCreateResource(counter.strip(), "metric")
          resIdx.addResource(metric)
          metric.addAttribute("performanceTool",perfTool.name,"resource")
          process = resIdx.findOrCreateResource(exe.name+Resource.resDelim+"Process-" + rank, "execution"+Resource.resDelim+"process")
          # the machine that the process ran on is an attribute of the process
          (runMach,runMachName,attrType) = \
                   process.getAttributeByName("run machine")      
          if runMachName != None:
             mach = resIdx.findResourceByName(runMachName)
          if mach == None:
             raise PTexception("Couldn't get process/node map")
          context = resIdx.addSpecificContextResources(contextTemplate,[process,mach])
          result = PerfResult(context, perfTool, metric, value, \
                 "noValue", "noValue", "noValue")
          exe.addPerfResult(result)

       line = f.readline() 

    f.close()
       
def sysmpiParse(resIdx, dirName, ptds, execName=None):
    perfTool = Resource("sysMPI", "performanceTool")
    #print "toolParser.sysmpiParse: tool name: %s" % perfTool.name
    resIdx.addResource(perfTool)
    metrics = []

    if execName is None:
       print "toolParser.sysmpiParse: parsing system data ..."
       sysmpiParseSys(resIdx, dirName, ptds, perfTool, metrics)
       print "toolParser.sysmpiParse: system data parsing complete."
    else:
       print "toolParser.sysmpiParse: parse for application data ..."
       sysmpiParseApp(resIdx, dirName, ptds, execName, perfTool, metrics)
       print "toolParser.sysmpiParse: application parsing complete."

def sysmpiParseSys(resIdx, dirName, ptds, perfTool, metrics):
    machs = resIdx.findResourcesByShortType("machine")
    if len(machs) > 1:
       raise PTexception("toolParser.sysmpiParseSys: More than one machine " \
                            "found. This is not yet supported.")
    if machs != []:
       [machine] = machs
       #print "Machine name: %s" % machine.getName()
    else:
       machine = None
       #print "Machine name not coming through ..."

    reports = glob(dirName+"/*.sysmpi.rpt")
    repName = reports[0]
    try:
       report = open(repName)
    except:
       raise PTexception("toolParser.sysmpiParseSys: could not open performance "\
                     "data file:%s" % repName)
    ## Begin Parse
    ## read report. Retrieve start time, end time, and System Metrics data
    ## The way I am reading this is awkward.  I think it could be streamlined
    stTime = ""
    endTime = ""
    tiDict = {}
    line = report.readline()
    if not line:
       raise PTexception("toolParser.sysmpiParseSys: corrupt report file")
    words = line.split()
    if words[0] == "Start:":
       partition = line.partition("Start: ")
       #print partition
       stTime = partition[2].strip(' \"\n')
       #print stTime
    else:
       raise PTexception("toolParser.sysmpiParseSys: corrupt report "\
                         "file - does not begin with Start time")
    line = report.readline()
    words = line.split()
    if words[0] == "End:":
       partition = line.partition("End: ")
       #print partition
       endTime = partition[2].strip(' \"\n')
       #print endTime
    else:
       raise PTexception("toolParser.sysmpiParseSys: corrupt report "\
                         "file - does not have with End time")

    sysLine = report.readline()
    while (sysLine.strip() != "System Metrics:"):
       #print sysLine.strip()
       sysLine = report.readline()
       if not sysLine:
          raise PTexception("toolParser.sysmpiParseSys: corrupt report "\
                            "file - no System Metrics header")
    metLine = report.readline()
    if not metLine:
       raise PTexception("toolParser.sysmpiParseSys: corrupt report "\
                         "file - no System Metrics section")
    elif metLine.strip() == "Total Interrupts By Node:":
       sysMetName = "Total Interrupts"
       sysMetRes = Resource(sysMetName, "metric")
       #sysMetRes = resIdx.findOrCreateResource(sysMetName, "metric")
       resIdx.addResource(sysMetRes)
       ##create a constraint from metric to tool -
       ## this doesn't look obvious since we are calling addAttribute, but
       ## the type 'resource' indicates that it is a ResourceConstraint; if
       ## type is 'string', then addAttribute creates a ResourceAttribute
       sysMetRes.addAttribute("performanceTool",perfTool.name,"resource")

       metValLine = report.readline()
       while (metValLine.strip() != "Application Metrics:"):
          strpMetVal = metValLine.strip()
          nodeVal = strpMetVal.split()
          #print "node %s val %s" % (nodeVal[0], nodeVal[1])
          if tiDict.has_key(nodeVal[0]):
             val = tiDict[nodeVal[0]]
             if (long(val) < long(nodeVal[1])):
                tiDict[nodeVal[0]] = nodeVal[1]
          else:
             tiDict[nodeVal[0]] = nodeVal[1]
          metValLine = report.readline()
          if not metLine:
             break
       #print "Contents of %s Dict" % sysMetName
       #for node in tiDict.keys():
       #   print node +  " " + tiDict[node]

    report.close()
    ## end parse
    contextTemplate = resIdx.createContextTemplate()
    if machine:
       topContext = resIdx.addSpecificContextResource(contextTemplate, machine)
    else:
       topContext = contextTemplate

    for node in tiDict.keys():
       ##findOrCreateResource for the node
       nodeRes = resIdx.findOrCreateResource(machine.name+Resource.resDelim+"batch"+Resource.resDelim+node, "grid"+Resource.resDelim+"machine"+Resource.resDelim+"partition"+Resource.resDelim+"node")

       #print "toolParser.sysmpiParseSys: node name: %s" % nodeRes.name
       nodeResName = nodeRes.name

       ##addSpecificContextResource (the node)
       context = resIdx.addSpecificContextResource(topContext,nodeRes)

       ##Create Result
       result = PerfResult(context, perfTool, sysMetRes , \
                           tiDict[node], "noValue", stTime, endTime)
       #print "toolParser.sysmpiParseSys: created result: %s" % result.PTdF(nodeResName)

       ##Add Result
       nodeRes.addPerfResult(result)

def sysmpiParseApp(resIdx, dirName, ptds, execName, perfTool, metrics):
   class Report:
      pass
   class CallHx:
      pass

   rpt = None
   chx = None

   funcDict = {"MPI_Allgather":0,
               "MPI_Allreduce":1,
               "MPI_Barrier":2,
               "MPI_Bcast":3,
               "MPI_Irecv":4,
               "MPI_Isend":5,
               "MPI_Recv":6,
               "MPI_Reduce":7,
               "MPI_Send":8,
               "MPI_Wait":8,
               "MPI_Waitall":10}

   ##Parse the report file
   rpt = Report()
   sysmpiReadReport (rpt, funcDict, dirName)
   """
   print "contents of total inclusive time dict:"
   for rank in rpt.processTotIncTimeDict.keys():
      tlist = rpt.processTotIncTimeDict[rank]
      print tlist

   print "contents of function call count dict:"
   for rank in rpt.processFunCallCntDict.keys():
      tlist = rpt.processFunCallCntDict[rank]
      print tlist

   print "contents of max inclusive time dict:"
   for fn in rpt.funMaxIncTimeDict.keys():
      mlist = rpt.funMaxIncTimeDict[fn]
      print mlist
   """

   ##Parse the call histories
   chx = CallHx()
   sysmpiReadCallHx(chx, funcDict, dirName)
   #for rank in chx.callHx.keys():
   #   print rank
   #   valList = chx.callHx[rank]
   #   print valList[0]

   ##Process the data
   sysmpiProcessData(resIdx, rpt, chx, perfTool, metrics, funcDict)

def sysmpiProcessData(resIdx, rptObj, chxObj, tool, metList, funcDict):
   machs = resIdx.findResourcesByShortType("machine")
   if len(machs) > 1:
      raise PTexception("toolParser.sysmpiParseApp: More than one machine " \
                           "found. This is not yet supported.")
   if machs != []:
      [machine] = machs
      #print "Machine name: %s" % machine.getName()
   else:
      machine = None
      #print "Machine name not coming through ..."


   [exe] = resIdx.findResourcesByType("execution")
   [app] = resIdx.findResourcesByType("application")

   ## Add Constraint from Process to Node
   for rank in rptObj.processNodeDict.keys():
      process = resIdx.findOrCreateResource(exe.name + Resource.resDelim + \
                             "Process-" + rank, "execution" + \
                             Resource.resDelim + "process")
      hw = resIdx.findOrCreateResource(machine.name + Resource.resDelim + \
                             "batch" + Resource.resDelim + \
                             rptObj.processNodeDict[rank],
                             "grid" + Resource.resDelim + "machine" + \
                             Resource.resDelim + "partition" + \
                             Resource.resDelim + "node")
      process.addAttribute("run machine",hw.name,"resource")
      #print "%s on %s" % (process.name, hw.name)

   ## Add Metrics
   wcTimeMet = Resource("Wallclock Time", "metric")
   resIdx.addResource(wcTimeMet)
   wcTimeMet.addAttribute("performanceTool",tool.name,"resource")

   totIncTimeMetDict = {}
   for fn in funcDict.keys():
      metName = fn + " Total Inclusive Time"
      #print metName
      newMet = Resource(metName, "metric")
      resIdx.addResource(newMet)
      newMet.addAttribute("performanceTool", tool.name, "resource")
      totIncTimeMetDict[fn] = newMet

   callCntMetDict = {}
   for fn in funcDict.keys():
      metName = fn + " Call Count"
      #print metName
      newMet = Resource(metName, "metric")
      resIdx.addResource(newMet)
      newMet.addAttribute("performanceTool", tool.name, "resource")
      callCntMetDict[fn] = newMet

   maxIncTimeMetDict = {}
   for fn in funcDict.keys():
      metName = fn + " Max Inclusive Time"
      #print metName
      newMet = Resource(metName, "metric")
      resIdx.addResource(newMet)
      newMet.addAttribute("performanceTool", tool.name, "resource")
      maxIncTimeMetDict[fn] = newMet

   incTimeMetDict = {}
   for fn in funcDict.keys():
      metName = fn + " Inclusive Time"
      newMet = Resource(metName, "metric")
      resIdx.addResource(newMet)
      newMet.addAttribute("performanceTool", tool.name, "resource")
      incTimeMetDict[fn] = newMet

   ## Find or create whole exec time resource
   timeLoc = resIdx.findOrCreateResource("whole execution", "time")

   ## Create the context
   exe.setApplication(app)
   contextTemplate = resIdx.createContextTemplate()
   if machine:
      topContext = resIdx.addSpecificContextResource(contextTemplate, machine)
   else:
      topContext = contextTemplate

   ## Add Whole Execution Results
   context = topContext
   result = PerfResult(context, tool, wcTimeMet, rptObj.wcTime, \
                rptObj.wcUnits, rptObj.stTime, rptObj.endTime)
   exe.addPerfResult(result)

   ## Per Process Results
   ## Total Inclusive Time
   for rank in rptObj.processTotIncTimeDict.keys():
      fnList = rptObj.processTotIncTimeDict[rank]
      for pair in fnList:
        fname = pair[0]
        val   = pair[1]
        metRes = totIncTimeMetDict[fname]
        hwLoc = resIdx.findOrCreateResource(machine.name+Resource.resDelim + \
                "batch"+Resource.resDelim+rptObj.processNodeDict[rank], \
                "grid"+Resource.resDelim+"machine"+Resource.resDelim + \
                "partition"+Resource.resDelim+"node")
        procLoc = resIdx.findOrCreateResource(exe.name+Resource.resDelim + \
                "Process-" + rank, "execution"+Resource.resDelim+"process")
        context = resIdx.addSpecificContextResources(topContext,[hwLoc,procLoc])

        result = PerfResult(context, tool, metRes, val, "seconds",
                            rptObj.stTime, rptObj.endTime)
        exe.addPerfResult(result)
  ## Call Count
   for rank in rptObj.processFunCallCntDict.keys():
      fnList = rptObj.processFunCallCntDict[rank]
      for pair in fnList:
        fname = pair[0]
        val   = pair[1]
        metRes = callCntMetDict[fname]
        hwLoc = resIdx.findOrCreateResource(machine.name+Resource.resDelim + \
                "batch"+Resource.resDelim+rptObj.processNodeDict[rank], \
                "grid"+Resource.resDelim+"machine"+Resource.resDelim + \
                "partition"+Resource.resDelim+"node")
        procLoc = resIdx.findOrCreateResource(exe.name+Resource.resDelim + \
                "Process-" + rank, "execution"+Resource.resDelim+"process")
        context = resIdx.addSpecificContextResources(topContext,[hwLoc,procLoc])

        result = PerfResult(context, tool, metRes, val, "noValue",
                            rptObj.stTime, rptObj.endTime)
        exe.addPerfResult(result)

   ## Per Function Results
   ## Max Inclusive Time
   for fn in rptObj.funMaxIncTimeDict.keys():
      mitList = rptObj.funMaxIncTimeDict[fn]
      rank = mitList[0]
      val = mitList[1]
      metRes = maxIncTimeMetDict[fn]
      hwLoc = resIdx.findOrCreateResource(machine.name+Resource.resDelim + \
                "batch"+Resource.resDelim+rptObj.processNodeDict[rank], \
                "grid"+Resource.resDelim+"machine"+Resource.resDelim + \
                "partition"+Resource.resDelim+"node")
      procLoc = resIdx.findOrCreateResource(exe.name+Resource.resDelim + \
                 "Process-" + rank, "execution"+Resource.resDelim+"process")

      reses = resIdx.findResourcesByShortType("module")
      for res in reses:
         if res.getName().find("libmpi") >= 0:
            modName = res.name
            # if lib found in build hierarchy, then static
            # if found in environment, then dynamic
            if res.getType().find("build") >= 0:
               dynamic = False
            else:
               dynamic = True
            break
      if modName == "":
         raise PTexception("toolParser:sysmpiProcessData: " \
                           "Module libmpi not found")
      if not dynamic:
         modLoc = resIdx.findOrCreateResource(modName,"build" + \
                                              Resource.resDelim + "module")
         mpiLoc = resIdx.findOrCreateResource(modName + Resource.resDelim + fn,
                                             "build"  + Resource.resDelim + \
                                             "module" + Resource.resDelim + \
                                             "function")
      else:
         env_id = None
         envs = resIdx.findResourcesByType("environment")
         if len(envs) > 1:
            raise PTexception("toolParser:sysmpiProcessData: " \
                              "More than one environment found for " \
                              "execution. This is not yet supported. " \
                              "Execution: %s" % exe.name)

         [env] = envs
         modLoc = resIdx.findOrCreateResource(modName,"environment" + \
                                              Resource.resDelim + "module")
         mpiLoc = resIdx.findOrCreateResource(modName+Resource.resDelim + fn,
                                              "environment" + \
                                              Resource.resDelim + "module" + \
                                              Resource.resDelim + "function")
      [build] = resIdx.findResourcesByType("build")

      #print hwLoc.name, procLoc.name, modLoc.name, mpiLoc.name
      context = resIdx.addSpecificContextResources(topContext,
                                         [hwLoc,procLoc,mpiLoc])

      result = PerfResult(context, tool, metRes, val, "seconds",
                            rptObj.stTime, rptObj.endTime)
      exe.addPerfResult(result)


   ## Add the Call History Results
   ## NOTE: There may not be any call history results included in the fileset
   ## for each rank in callHxDict, there is a list of calls
   ##    each one is a result for the process, function
   for rank in chxObj.callHxDict.keys():
      rnkCallList = chxObj.callHxDict[rank]

      #metRes = maxIncTimeMetDict[fn]
      hwLoc = resIdx.findOrCreateResource(machine.name + Resource.resDelim + \
                "batch" + Resource.resDelim + rptObj.processNodeDict[rank], \
                "grid" + Resource.resDelim + "machine" + Resource.resDelim + \
                "partition" + Resource.resDelim + "node")
      procLoc = resIdx.findOrCreateResource(exe.name + Resource.resDelim + \
                 "Process-" + rank, "execution" + Resource.resDelim + \
                 "process")

      reses = resIdx.findResourcesByShortType("module")
      for res in reses:
         if res.getName().find("libmpi") >= 0:
            modName = res.name
            # if lib found in build hierarchy, then static
            # if found in environment, then dynamic
            if res.getType().find("build") >= 0:
               dynamic = False
            else:
               dynamic = True
            break
      if modName == "":
         raise PTexception("toolParser:sysmpiProcessData: " \
                           "Module libmpi not found")
      if not dynamic:
         modLoc = resIdx.findOrCreateResource(modName,"build" + \
                                              Resource.resDelim + "module")
         for callInfo in rnkCallList:
            #print rank, callInfo
            mpiLoc = resIdx.findOrCreateResource(modName + \
                                 Resource.resDelim + callInfo[0],
                                 "build"  + Resource.resDelim + \
                                 "module" + Resource.resDelim + "function")
            [build] = resIdx.findResourcesByType("build")
            context = resIdx.addSpecificContextResources(topContext,
                                 [hwLoc,procLoc,mpiLoc])
            metRes = incTimeMetDict[callInfo[0]]
            result = PerfResult(context, tool, metRes, callInfo[3], "seconds",
                            callInfo[1].strip('\"'), callInfo[2].strip('\"'))
            exe.addPerfResult(result)


      else:
         env_id = None
         envs = resIdx.findResourcesByType("environment")
         if len(envs) > 1:
            raise PTexception("toolParser:sysmpiProcessData: " \
                              "More than one environment found for " \
                              "execution. This is not yet supported. " \
                              "Execution: %s" % exe.name)

         [env] = envs
         modLoc = resIdx.findOrCreateResource(modName,"environment" + \
                                              Resource.resDelim + "module")
         for callInfo in rnkCallList:
            #print rank, callInfo
            mpiLoc = resIdx.findOrCreateResource(modName + \
                                 Resource.resDelim + callInfo[0],
                                 "environment" + Resource.resDelim + \
                                 "module" + Resource.resDelim + "function")
            [build] = resIdx.findResourcesByType("build")
            context = resIdx.addSpecificContextResources(topContext,
                                [hwLoc,procLoc,mpiLoc])
            metRes = incTimeMetDict[callInfo[0]]
            result = PerfResult(context, tool, metRes, callInfo[3], "seconds",
                                callInfo[1], callInfo[2])
            exe.addPerfResult(result)


def sysmpiReadReport (rptObj, funcDict, dirName):
   rptObj.processNodeDict = {}
   rptObj.processTotIncTimeDict = {}
   rptObj.processFunCallCntDict = {}
   rptObj.funMaxIncTimeDict = {}
   rptObj.stTime = ""
   rptObj.endTime = ""
   rptObj.wcTime = ""
   rptObj.wcUnits = ""
   rptObj.mpiProcesses = 0


   reports = glob(dirName+"/*.sysmpi.rpt")
   repName = reports[0]
   try:
      report = open(repName)
   except:
      raise PTexception("toolParser.sysmpiReadReport: could not open performance "\
                    "data file:%s" % repName)
   ## Read report. Retrieve start time, end time, wallclock time, processes,
   ## process-node map, and Application Metrics

   ## start time
   line = report.readline()
   if not line:
      raise PTexception("toolParser.sysmpiReadReport: corrupt report file")
   words = line.split()
   if words[0] == "Start:":
      partition = line.partition("Start: ")
      #print partition
      rptObj.stTime = partition[2].strip(' \"\n')
      #print "start " + rptObj.stTime
   else:
      raise PTexception("toolParser.sysmpiReadReport: corrupt report "\
                        "file - does not begin with Start time")

   ## end time
   line = report.readline()
   words = line.split()
   if words[0] == "End:":
      partition = line.partition("End: ")
      #print partition
      rptObj.endTime = partition[2].strip(' \"\n')
      #print "end " + rptObj.endTime
   else:
      raise PTexception("toolParser.sysmpiReadReport: corrupt report "\
                        "file - does not have End time")

   ## wall clock time
   line = report.readline()
   words = line.split()
   if words[0] == "Wallclock:":
      partition = line.partition("Wallclock:")
      #print partition
      parts = partition[2].split()
      rptObj.wcTime = parts[0]
      rptObj.wcUnits = parts[1]
      #print "wctime %s %s" % (rptObj.wcTime, rptObj.wcUnits)
   else:
     raise PTexception("toolParser.sysmpiReadReport: corrupt report "\
                        "file - no Wallclock time")

   ## mpi processes
   line = report.readline()
   if line.startswith("MPI Processes:"):
      words = line.split()
      rptObj.mpiProcesses = long(words[2])
      #print "MPI Processes %ld" % rptObj.mpiProcesses
   else:
     raise PTexception("toolParser.sysmpiReadReport: corrupt report "\
                        "file - MPI Processes line")

   ## process to node map
   line = report.readline()
   if line.startswith("MPI Process to Machine Map"):
      line = report.readline()
      while line.startswith("System Metrics:") != True:
         words = line.split()
         #print "found map process %s to node %s" % (words[0], words[1])
         rptObj.processNodeDict[words[0]] = words[1]
         rptObj.processTotIncTimeDict[words[0]] = []
         rptObj.processFunCallCntDict[words[0]] = []
         line = report.readline()
      #print "Process to Node Map:"
      #for rank in rptObj.processNodeDict.keys():
      #   print "%s:%s" % (rank, rptObj.processNodeDict[rank])
   else:
      raise PTexception("toolParser.sysmpiReadReport: corrupt report "\
                        "file - MPI Process to Machine Map section")

   ## skip to Application section
   line = report.readline()
   while line.startswith("Application Metrics:") != True:
      line = report.readline()

   ## process function data
   if line.startswith("Application Metrics:"):
      line = report.readline()
      strp = line.strip()
      while strp.startswith("Max Inclusive Time By Function") != True:
         #print line
         if strp.startswith("Rank"):
            words = strp.split()
            rank = words[1]
            if rptObj.processNodeDict.has_key(rank):
               if strp.endswith("Total Inclusive Time By Function:"):
                  valList = rptObj.processTotIncTimeDict[rank]
                  line = report.readline()
                  strp = line.strip()
                  #print line
                  while ((strp.startswith("Rank") != True) and \
                         (strp.startswith("Max Inclusive Time By Function") != True)):
                     words = strp.split()
                     fnName = words[0]
                     if funcDict.has_key(fnName) == False:
                        raise PTexception("toolParser.sysmpiReadReport: corrupt "\
                           "report file Total Inclusive Time for rank " + \
                           rank + " and function " + fnName)
                     if rptObj.funMaxIncTimeDict.has_key(fnName) == False:
                        rptObj.funMaxIncTimeDict[fnName] = []
                     val = words[1]
                     valList.append((fnName,val))
                     line = report.readline()
                     strp = line.strip()
                     #print line
                  rptObj.processTotIncTimeDict[rank] = valList
                  #print valList
               elif strp.endswith("Function Call Count By Function:"):
                  valList = rptObj.processFunCallCntDict[rank]
                  line = report.readline()
                  strp = line.strip()
                  #print line
                  while 1:
                     if ((strp.startswith("Rank") == True) or \
                         (strp.startswith("Max Inclusive Time By Function") == True)):
                        #print "debug: breaking on line: %s" % line
                        break
                     words = strp.split()
                     fnName = words[0]
                     if funcDict.has_key(fnName) == False:
                        raise PTexception("toolParser.sysmpiReadReport: corrupt "\
                           "report file Total Inclusive Time for rank " + \
                           rank + " and function " + fnName)
                     if rptObj.funMaxIncTimeDict.has_key(fnName) == False:
                        rptObj.funMaxIncTimeDict[fnName] = []
                     val = words[1]
                     valList.append((fnName,val))
                     line = report.readline()
                     strp = line.strip()
                     #print line
                  rptObj.processFunCallCntDict[rank] = valList

               else:
                 raise PTexception("toolParser.sysmpiReadReport: corrupt "\
                      "report file - App. Metrics Section. bad line: " + line)
            else:
              raise PTexception("toolParser.sysmpiReadReport: corrupt report "\
                              "file - App. Metrics Section. rank " + rank + \
                              "not registered in process to node map.")

         else:
            raise PTexception("toolParser.sysmpiReadReport: corrupt report "\
                              "file -Application Metrics section")
      ## end while
      line = report.readline()
      strp = line.strip()
      while (strp.startswith("Error Report") != True):
         #print line
         words = strp.split()
         fnName = words[0]
         if rptObj.funMaxIncTimeDict.has_key(fnName):
            valList = rptObj.funMaxIncTimeDict[fnName]
            valList.append(words[1])
            valList.append(words[2])
            rptObj.funMaxIncTimeDict[fnName] = valList
         else:
            raise PTexception("toolParser.sysmpiReadReport: corrupt report " \
                        "file - Max Inclusive Time By Function section - " \
                        "function " + fnName + " is not registered")
         line = report.readline()
         strp = line.strip()

      #print "last line read: %s" % line
   else:
      raise PTexception("toolParser.sysmpiReadReport: corrupt report "\
                        "file -Application Metrics section")
   report.close()

def sysmpiReadCallHx(chxObj, funcDict, dirName):
   print "toolParser.sysmpiReadCallHx ..."
   chxObj.callHxDict = {}

   hxFiles = glob(dirName+"/*.sysmpi.*.cg")
   if len(hxFiles) > 0:
      for hxName in hxFiles:
         try:
            print "toolParser:sysmpiReadCallHx: open %s" % hxName
            hxf = open(hxName)
         except:
            raise PTexception("toolParser.sysmpiReadCallHx: could not open performance "\
                       "data file:%s" % hxName)

         ## Read call hx. first line specifies the process; the remaining lines
         ## are calls in this format: fnName, start, end, duration

         ## get rank
         line = hxf.readline()
         words = line.split()
         if words[0] != "Rank":
            raise PTexception("toolParser.sysmpiReadCallHx: "\
                              "first line does not start with \'Rank\'")
         else:
            rank = words[1]

         ## read everything else
         print "Rank %s" % rank
         line = hxf.readline()
         callList = []
         oneCall = []
         while line:
            strpLine = line.strip()
            words = strpLine.split()
            fun = words[0]
            dur = words[5]
            start = words[1] + " " + words[2]
            end = words[3] + " " + words[4]
            oneCall = [fun,start,end,dur]
            callList.append(oneCall)
            oneCall = []
            line = hxf.readline()
         hxf.close()
         chxObj.callHxDict[rank] = callList
   else:
      print "toolParser:sysmpiReadCallHx: no call history files to read"

def mpipParse(resIdx, fname ):

    try:
       f = open(fname,'r')
    except:
       raise PTexception("toolParser.mpipParse: could not open performance "\
                         "data file:%s" % fname)
 
    # expect one resource of application, execution in resIdx
    [app] = resIdx.findResourcesByType("application")
    [exe] = resIdx.findResourcesByType("execution")

    mpiPAVs = [] # holds the attribute,value pairs for perf Tool mpiP
    processMap = {}  # hold rank to node mapping
    mpiTime = [] # list of tuples, indexed by rank: (appTime, mpiTime, MPI%)
    totalMpiTime = None  # a tuple with mpiTime for whole program

    # the following are for holding data for the various mpiP categories
    CS = []  # holds the callsite information
    class callSite:
        def __init__(self,args):
          if len(args) != 5:
             raise PTexception("error in parsing file")
          [self.id,self.lev,self.fileAddr,self.parentFun,self.MPIcall] = args
    AT = []
    class aggTime: # hold the Aggregate Time measurements
        def __init__(self,args):
          if len(args) != 5:
             raise PTexception("error in parsing file")
          [self.call,self.site,self.time,self.app,self.MPI] = args
    AS = []
    class aggSent: # holds the Aggregate Sent Message Size measurements
        def __init__(self,args):
          if len(args) != 6:
             raise PTexception("error in parsing file")
          [self.call,self.site,self.count,self.total,self.avg,self.sent] = args
    CT = [] # for rank-specific data
    CTW = [] # for aggregate data
    class callsiteTime: # holds the Callsite Time statistics measurements
        def __init__(self,args):
          if len(args) != 9:
             raise PTexception("error in parsing file:%d" % len(args))
          [self.name,self.site,self.rank,self.count,self.max,self.mean,\
           self.min, self.app,self.MPI] = args
    CM = [] # for rank-specific data
    CMW = [] # for aggregate data
    class callsiteMsg: # holds the Callsite Message statistics 
        def __init__(self,args):
          if len(args) != 8:
             raise PTexception("error in parsing file:%d" % len(args))
          [self.name,self.site,self.rank,self.count,self.max,self.mean,\
           self.min, self.sum] = args

  
    # begin parsing
    terminationSeen = False 
    machs = resIdx.findResourcesByShortType("machine")
    if len(machs) > 1:
       raise PTexception("More than one machine found for execution. This is not yet supported. Execution: %s" % exe.name)
    if machs != []:
        [machine] = machs


    line = f.readline()
 
    while line != '':
       if line.find("@ Command") >= 0:
          runCmd = line[line.index(":")+1:].strip()
          if runCmd != '':
             exe.addAttribute("runCmd",runCmd)
       elif line.find("@ Version") >= 0:
          mpiPVersion = line[line.index(":")+1:].strip()
          if mpiPVersion != '':
             mpiPAVs.append(("mpiPVersion", mpiPVersion,"string"))
       elif line.find("@ MPIP Build Date") >= 0:
          mpiPBuildDate = line[line.index(":")+1:].strip() 
          if mpiPBuildDate != '':
             mpiPAVs.append(("mpiPBuildDate", mpiPBuildDate,"string"))
       elif line.find("@ Start Time") >= 0:
          runStart = line[line.index(":")+1:].strip() 
          if runStart != '':
             exe.addAttribute("runStartTime",runStart)
       elif line.find("@ Stop Time") >= 0:
          runStop = line[line.index(":")+1:].strip() 
          if runStop != '':
             exe.addAttribute("runStopTime",runStop)
       elif line.find("@ MPIP env var") >= 0:
          mpiPEnvVar = line[line.index(":")+1:].strip() 
          if mpiPEnvVar != '':
             mpiPAVs.append(("mpiPEnvVar", mpiPEnvVar,"string"))
       elif line.find("@ Collector Rank") >= 0:
          mpiPCollectorRank = line[line.index(":")+1:].strip() 
          if mpiPCollectorRank != '':
             mpiPAVs.append(("mpiPCollectorRank", mpiPCollectorRank,"string"))
       elif line.find("@ Collector PID") >= 0:
          mpiPCollectorPID = line[line.index(":")+1:].strip() 
          if mpiPCollectorPID != '':
             mpiPAVs.append(("mpiPCollectorPID", mpiPCollectorPID,"string"))
       elif line.find("@ Final Output Dir") >= 0:
          mpiPOutputDir = line[line.index(":")+1:].strip() 
          if mpiPOutputDir != '':
             mpiPAVs.append(("mpiPOutputDir", mpiPOutputDir,"string"))
       elif line.find("@ MPI Task Assignment") >= 0:
          temp = line[line.index(":")+1:].strip() 
          info = temp.split()
          processMap[int(info[0])] = info[1]
          process = resIdx.findOrCreateResource(exe.name+Resource.resDelim+"Process-" + info[0], "execution"+Resource.resDelim+"process")
          hw = resIdx.findOrCreateResource(machine.name+Resource.resDelim+"batch"+Resource.resDelim+info[1], "grid"+Resource.resDelim+"machine"+Resource.resDelim+"partition"+Resource.resDelim+"node")
          process.addAttribute("run machine",hw.name,"resource")

       elif line.find("@--- MPI Time") >= 0:
          f.readline() # skip ---------
          f.readline() # skip header line
          line = f.readline()
          while line.find("  *") < 0:
             parts = line.split()
             #  (appTime, mpiTime, MPI%)
             #print "parts is " + str(parts)
             mpiTime.append((parts[1].strip(), parts[2].strip(), \
                             parts[3].strip()))
             line = f.readline() 
          parts = line.split()
          totalMpiTime = (parts[1].strip(),parts[2].strip(),parts[3].strip())
       elif line.find("@--- Callsites:") >= 0:
          f.readline() # skip ---------
          f.readline() # skip header line
          line = f.readline()
          while line.find("-----") < 0:
             parts = line.split()
             c = callSite(parts)
             CS.append(c)
             line = f.readline()
       elif line.find("@--- Aggregate Time") >= 0:
          f.readline() # skip ---------
          f.readline() # skip header line
          line = f.readline()
          while line.find("-----") < 0:
             parts = line.split()
             a = aggTime(parts)
             AT.append(a)
             line = f.readline()
       elif line.find("@--- Aggregate Sent") >= 0:
          f.readline() # skip ---------
          f.readline() # skip header line
          line = f.readline()
          while line.find("-----") < 0:
             parts = line.split()
             a = aggSent(parts)
             AS.append(a)
             line = f.readline()
       elif line.find("@--- Callsite Time") >= 0:
          f.readline() # skip ---------
          f.readline() # skip header line
          line = f.readline()
          while line.find("-----") < 0:
             if line.strip() == "": # skip blank line
                line = f.readline()
             parts = line.split()
             c = callsiteTime(parts)
             if line.find("  *") >= 0:
                CTW.append(c) 
             else:
                CT.append(c)
             line = f.readline()
       elif line.find("@--- Callsite Message") >= 0:
          f.readline() # skip ---------
          f.readline() # skip header line
          line = f.readline()
          while line.find("-----") < 0:
             if line.strip() == "": # skip blank line
                line = f.readline()
             parts = line.split()
             c = callsiteMsg(parts)
             if line.find("  *") >= 0:
                CMW.append(c) 
             else:
                CM.append(c)
             line = f.readline()
       elif line.find("@--- End of Report") >= 0:
            terminationSeen = True  

       line = f.readline()
 
    # end parsing file
    f.close()
    if not terminationSeen:
       raise PTexception("toolParser.mpipParse: incomplete mpiP data file:%s"\
                         % fname)


    # process data 
    perfTool = Resource("mpiP", "performanceTool", mpiPAVs)
    resIdx.addResource(perfTool) 
     
    appTimeMet = Resource("AppTime", "metric")
    resIdx.addResource(appTimeMet)
    appTimeMet.addAttribute("performanceTool",perfTool.name,"resource")
    MPITimeMet = Resource("MPITime", "metric")
    resIdx.addResource(MPITimeMet)
    MPITimeMet.addAttribute("performanceTool",perfTool.name,"resource")
    MPIPercentMet = Resource("MPI%", "metric")
    resIdx.addResource(MPIPercentMet)
    MPIPercentMet.addAttribute("performanceTool",perfTool.name,"resource")
    aggTimeMet = Resource("Aggregate Time", "metric")
    resIdx.addResource(aggTimeMet)
    aggTimeMet.addAttribute("performanceTool",perfTool.name,"resource")
    aggAppPercentMet = Resource("Aggregate App%", "metric")
    resIdx.addResource(aggAppPercentMet)
    aggAppPercentMet.addAttribute("performanceTool",perfTool.name,"resource")
    aggMPIPercentMet = Resource("Aggregate MPI%", "metric")
    resIdx.addResource(aggMPIPercentMet)
    aggMPIPercentMet.addAttribute("performanceTool",perfTool.name,"resource")
    aggSentMsgCountMet = Resource("Aggregate Sent Message Count", "metric")
    resIdx.addResource(aggSentMsgCountMet)
    aggSentMsgCountMet.addAttribute("performanceTool",perfTool.name,"resource")
    aggSentMsgTotalMet = Resource("Aggregate Sent Message Total", "metric")
    resIdx.addResource(aggSentMsgTotalMet)
    aggSentMsgTotalMet.addAttribute("performanceTool",perfTool.name,"resource")
    aggSentMsgAvrgMet = Resource("Aggregate Sent Message Avrg", "metric")
    resIdx.addResource(aggSentMsgAvrgMet)
    aggSentMsgAvrgMet.addAttribute("performanceTool",perfTool.name,"resource")
    aggSentMsgPrcntMet = Resource("Aggregate Sent Message Sent%", "metric")
    resIdx.addResource(aggSentMsgPrcntMet)
    aggSentMsgPrcntMet.addAttribute("performanceTool",perfTool.name,"resource")
    callTimeCountMet = Resource("Callsite Time Count", "metric")
    resIdx.addResource(callTimeCountMet)
    callTimeCountMet.addAttribute("performanceTool",perfTool.name,"resource")
    callTimeMaxMet = Resource("Callsite Time Max", "metric")
    resIdx.addResource(callTimeMaxMet)
    callTimeMaxMet.addAttribute("performanceTool",perfTool.name,"resource")
    callTimeMeanMet = Resource("Callsite Time Mean", "metric")
    resIdx.addResource(callTimeMeanMet)
    callTimeMeanMet.addAttribute("performanceTool",perfTool.name,"resource")
    callTimeMinMet = Resource("Callsite Time Min", "metric")
    resIdx.addResource(callTimeMinMet)
    callTimeMinMet.addAttribute("performanceTool",perfTool.name,"resource")
    callTimeAppPrcntMet = Resource("Callsite Time App%", "metric")
    resIdx.addResource(callTimeAppPrcntMet)
    callTimeAppPrcntMet.addAttribute("performanceTool",perfTool.name,"resource")
    callTimeMPIPrcntMet = Resource("Callsite Time MPI%", "metric")
    resIdx.addResource(callTimeMPIPrcntMet)
    callTimeMPIPrcntMet.addAttribute("performanceTool",perfTool.name,"resource")
    callMsgCountMet = Resource("Callsite Message Sent Count", "metric")
    resIdx.addResource(callMsgCountMet)
    callMsgCountMet.addAttribute("performanceTool",perfTool.name,"resource")
    callMsgMaxMet = Resource("Callsite Message Sent Max", "metric")
    resIdx.addResource(callMsgMaxMet)
    callMsgMaxMet.addAttribute("performanceTool",perfTool.name,"resource")
    callMsgMeanMet = Resource("Callsite Message Sent Mean", "metric")
    resIdx.addResource(callMsgMeanMet)
    callMsgMeanMet.addAttribute("performanceTool",perfTool.name,"resource")
    callMsgMinMet = Resource("Callsite Message Sent Min", "metric")
    resIdx.addResource(callMsgMinMet)
    callMsgMinMet.addAttribute("performanceTool",perfTool.name,"resource")
    callMsgSumMet = Resource("Callsite Message Sent Sum", "metric")
    resIdx.addResource(callMsgSumMet)
    callMsgSumMet.addAttribute("performanceTool",perfTool.name,"resource")

    timeLoc = resIdx.findOrCreateResource("whole execution", "time")

    exe.setApplication(app)
    contextTemplate = resIdx.createContextTemplate()
    if machine:
       topContext = resIdx.addSpecificContextResource(contextTemplate, machine)
    else:
       topContext = contextTemplate 

    # add per process MPI timings 
    i = 0
    for appTime,mpiTime,mpiPercent in mpiTime:
       hwLoc = resIdx.findOrCreateResource(machine.name+Resource.resDelim+"batch"+Resource.resDelim+processMap[i], "grid"+Resource.resDelim+"machine"+Resource.resDelim+"partition"+Resource.resDelim+"node")
       procLoc = resIdx.findOrCreateResource(exe.name+Resource.resDelim+"Process-" + str(i), "execution"+Resource.resDelim+"process")
       context = resIdx.addSpecificContextResources(topContext,[hwLoc,procLoc])
       result = PerfResult(context, perfTool, appTimeMet,appTime,"seconds",\
                "noValue", "noValue")
       exe.addPerfResult(result) 
       result = PerfResult(context, perfTool, MPITimeMet,mpiTime,"seconds",\
                "noValue", "noValue")
       exe.addPerfResult(result) 
       result = PerfResult(context, perfTool, MPIPercentMet, mpiPercent, \
                "noValue", "noValue", "noValue")
       exe.addPerfResult(result) 
       i += 1
    
    # add MPI timings for whole execution	
    context = topContext
    result = PerfResult(context, perfTool, appTimeMet, totalMpiTime[0], \
                 "seconds", "noValue", "noValue")
    exe.addPerfResult(result)
    result = PerfResult(context, perfTool, MPITimeMet, totalMpiTime[1], \
                 "seconds", "noValue", "noValue")
    exe.addPerfResult(result)
    result = PerfResult(context, perfTool, MPIPercentMet, totalMpiTime[2], \
                 "noValue", "noValue", "noValue")
    exe.addPerfResult(result)


    # add Aggregate Time  measurements
    i = 0
    hwLoc = machine
    procLoc = exe
    reses = resIdx.findResourcesByShortType("module")
    for res in reses:
       if res.getName().find("libmpi") >= 0:
          modName = res.name
          # if lib found in build hierarchy, then static
          # if found in environment, then dynamic
          if res.getType().find("build") >= 0:
             dynamic = False
          else:
             dynamic = True
          break
    if modName == "":
       raise PTexception("toolParser: Module not found" +\
                         " for function:%s" % "libmpi")
    if not dynamic:
       modLoc = resIdx.findOrCreateResource(modName,"build"+Resource.resDelim+"module")
    else:
       env_id = None
       envs = resIdx.findResourcesByType("environment")
       if len(envs) > 1:
          raise PTexception("More than one environment found for execution. This is not yet supported. Execution: %s" % exe.name)
       [env] = envs
       modLoc = resIdx.findOrCreateResource(modName,"environment"+Resource.resDelim+"module")

    # expect one build resource in resIdx
    [build] = resIdx.findResourcesByType("build") 

    for a in AT: 
       cs = CS[int(a.site)-1]
       if cs.parentFun == "[unknown]": # don't have module/fun information
          mod = resIdx.findOrCreateResource(build.name+Resource.resDelim+"mod"+cs.fileAddr,  "build"+Resource.resDelim+"module")
          fun = resIdx.findOrCreateResource(mod.name+Resource.resDelim+"fun"+cs.fileAddr, "build"+Resource.resDelim+"module"+Resource.resDelim+"function")
          codeLoc = resIdx.findOrCreateResource(fun.name+Resource.resDelim+cs.fileAddr, "build"+Resource.resDelim+"module"+Resource.resDelim+"function"+Resource.resDelim+"codeBlock")
       else:
          modLoc  = resIdx.findOrCreateResource(build.name+Resource.resDelim+cs.fileAddr, "build"+Resource.resDelim+"module")
          codeLoc  = resIdx.findOrCreateResource(modLoc.name+Resource.resDelim+cs.parentFun, "build"+Resource.resDelim+"module"+Resource.resDelim+"function")
       if not dynamic:
           mpiLoc = resIdx.findOrCreateResource(modName+Resource.resDelim + "MPI_"+a.call, "build"+Resource.resDelim+"module"+Resource.resDelim+"function")
       else:
           mpiLoc = resIdx.findOrCreateResource(modName+Resource.resDelim+ "MPI_"+a.call, "environment"+Resource.resDelim+"module"+Resource.resDelim+"function")
 
       primaryContext = (resIdx.addSpecificContextResource(topContext,mpiLoc),"primary")
       parentContext = (resIdx.addSpecificContextResource(topContext,codeLoc),"parent")
       
       result = PerfResult([primaryContext,parentContext], perfTool, aggTimeMet,\
                         a.time, "milliseconds", "noValue", "noValue")
       exe.addPerfResult(result)
       result = PerfResult([primaryContext,parentContext], perfTool,\
                          aggAppPercentMet, a.app, "noValue", "noValue", \
                          "noValue")
       exe.addPerfResult(result)
       result = PerfResult([primaryContext,parentContext], perfTool,\
                          aggMPIPercentMet, a.MPI, "noValue", "noValue",\
                          "noValue")
       exe.addPerfResult(result)

   
    # add Aggregate Sent Message Size measurements
    for a in AS:
       cs = CS[int(a.site)-1]
       if cs.parentFun == "[unknown]": # don't have module/fun information
          mod = resIdx.findOrCreateResource(build.name+Resource.resDelim+"mod"+cs.fileAddr, "build"+Resource.resDelim+"module")
          fun = resIdx.findOrCreateResource(mod.name+Resource.resDelim+"fun"+cs.fileAddr, "build"+Resource.resDelim+"module"+Resource.resDelim+"function")
          codeLoc = resIdx.findOrCreateResource(fun.name+Resource.resDelim+cs.fileAddr, "build"+Resource.resDelim+"module"+Resource.resDelim+"function"+Resource.resDelim+"codeBlock")
       else:
          modLoc  = resIdx.findOrCreateResource(build.name+Resource.resDelim+cs.fileAddr, "build"+Resource.resDelim+"module")
          codeLoc  = resIdx.findOrCreateResource(modLoc.name+Resource.resDelim+ cs.parentFun,"build"+Resource.resDelim+"module"+Resource.resDelim+"function")
       if not dynamic:
           mpiLoc = resIdx.findOrCreateResource(modName+Resource.resDelim + "MPI_"+a.call, "build"+Resource.resDelim+"module"+Resource.resDelim+"function")
       else:
           mpiLoc = resIdx.findOrCreateResource(modName+Resource.resDelim+ "MPI_"+a.call, "environment"+Resource.resDelim+"module"+Resource.resDelim+"function")

       primaryContext = (resIdx.addSpecificContextResource(topContext,mpiLoc),"primary")
       parentContext = (resIdx.addSpecificContextResource(topContext,codeLoc),"parent")
       
       result = PerfResult([primaryContext,parentContext], perfTool, \
                         aggSentMsgCountMet, a.count, "noValue", "noValue", \
                         "noValue")
       exe.addPerfResult(result)
       result = PerfResult([primaryContext,parentContext], perfTool,\
                          aggSentMsgTotalMet, a.total, "bytes", "noValue", \
                          "noValue")
       exe.addPerfResult(result)
       result = PerfResult([primaryContext,parentContext], perfTool,\
                          aggSentMsgAvrgMet, a.avg, "bytes", "noValue",\
                          "noValue")
       exe.addPerfResult(result)
       result = PerfResult([primaryContext,parentContext], perfTool,\
                          aggSentMsgPrcntMet, a.sent, "noValue", "noValue",\
                          "noValue")
       exe.addPerfResult(result)


    # add Callsite Time statistics measurements
    for c in CT:
       cs = CS[int(c.site)-1]
       if cs.parentFun == "[unknown]": # don't have module/fun information
          mod = resIdx.findOrCreateResource(build.name+Resource.resDelim+"mod"+cs.fileAddr,  "build"+Resource.resDelim+"module")
          fun = resIdx.findOrCreateResource(mod.name+Resource.resDelim+"fun"+cs.fileAddr, "build"+Resource.resDelim+"module"+Resource.resDelim+"function")
          codeLoc = resIdx.findOrCreateResource(fun.name+Resource.resDelim+cs.fileAddr, "build"+Resource.resDelim+"module"+Resource.resDelim+"function"+Resource.resDelim+"codeBlock")
       else:
          modLoc  = resIdx.findOrCreateResource(build.name+Resource.resDelim+cs.fileAddr, "build"+Resource.resDelim+"module")
          codeLoc  = resIdx.findOrCreateResource(modLoc.name+Resource.resDelim+ cs.parentFun, "build"+Resource.resDelim+"module"+Resource.resDelim+"function")

       if not dynamic:
           mpiLoc = resIdx.findOrCreateResource(modName+Resource.resDelim + "MPI_"+c.name, "build"+Resource.resDelim+"module"+Resource.resDelim+"function")
       else:
           mpiLoc = resIdx.findOrCreateResource(modName+Resource.resDelim+ "MPI_"+c.name, "environment"+Resource.resDelim+"module"+Resource.resDelim+"function")
       procLoc = resIdx.findOrCreateResource(exe.name+Resource.resDelim+"Process-" + c.rank, "execution"+Resource.resDelim+"process")
       primaryContext = (resIdx.addSpecificContextResources(topContext,\
                      [mpiLoc,procLoc]),"primary")
       parentContext = (resIdx.addSpecificContextResources(topContext,\
                      [codeLoc,procLoc]),"parent")

       result = PerfResult([primaryContext,parentContext], perfTool, \
                         callTimeCountMet, c.count, "noValue", "noValue", \
                         "noValue")
       exe.addPerfResult(result)
       result = PerfResult([primaryContext,parentContext], perfTool,\
                          callTimeMaxMet, c.max, "milliseconds", "noValue", \
                          "noValue")
       exe.addPerfResult(result)
       result = PerfResult([primaryContext,parentContext], perfTool,\
                          callTimeMeanMet, c.mean, "milliseconds", "noValue",\
                          "noValue")
       exe.addPerfResult(result)
       result = PerfResult([primaryContext,parentContext], perfTool,\
                          callTimeMinMet, c.min, "milliseconds", "noValue",\
                          "noValue")
       exe.addPerfResult(result)
       result = PerfResult([primaryContext,parentContext], perfTool,\
                          callTimeAppPrcntMet, c.app, "noValue", "noValue",\
                          "noValue")
       exe.addPerfResult(result)
       result = PerfResult([primaryContext,parentContext], perfTool,\
                          callTimeMPIPrcntMet, c.MPI, "noValue", "noValue",\
                          "noValue")
       exe.addPerfResult(result)

    # the Callsite statistics that aren't specific to a particular rank
    for c in CTW:
       cs = CS[int(c.site)-1]
       if cs.parentFun == "[unknown]": # don't have module/fun information
          mod = resIdx.findOrCreateResource(build.name+Resource.resDelim+"mod"+cs.fileAddr, "build"+Resource.resDelim+"module")
          fun = resIdx.findOrCreateResource(mod.name+Resource.resDelim+"fun"+cs.fileAddr, "build"+Resource.resDelim+"module"+Resource.resDelim+"function")
          codeLoc = resIdx.findOrCreateResource(fun.name+Resource.resDelim+cs.fileAddr, "build"+Resource.resDelim+"module"+Resource.resDelim+"function"+Resource.resDelim+"codeBlock")
       else:
          modLoc  = resIdx.findOrCreateResource(build.name+Resource.resDelim+cs.fileAddr, "build"+Resource.resDelim+"module")
          codeLoc  = resIdx.findOrCreateResource(modLoc.name+Resource.resDelim+ cs.parentFun, "build"+Resource.resDelim+"module"+Resource.resDelim+"function")

       if not dynamic:
           mpiLoc = resIdx.findOrCreateResource(modName+Resource.resDelim + "MPI_"+c.name, "build"+Resource.resDelim+"module"+Resource.resDelim+"function")
       else:
           mpiLoc = resIdx.findOrCreateResource(modName+Resource.resDelim+ "MPI_"+c.name, "environment"+Resource.resDelim+"module"+Resource.resDelim+"function")
       procLoc = exe
       primaryContext = (resIdx.addSpecificContextResource(topContext,mpiLoc),"primary")
       parentContext = (resIdx.addSpecificContextResource(topContext,codeLoc),"parent")

       result = PerfResult([primaryContext,parentContext], perfTool, \
                         callTimeCountMet, c.count, "noValue", "noValue", \
                         "noValue")
       exe.addPerfResult(result)
       result = PerfResult([primaryContext,parentContext], perfTool,\
                          callTimeMaxMet, c.max, "milliseconds", "noValue", \
                          "noValue")
       exe.addPerfResult(result)
       result = PerfResult([primaryContext,parentContext], perfTool,\
                          callTimeMeanMet, c.mean, "milliseconds", "noValue",\
                          "noValue")
       exe.addPerfResult(result)
       result = PerfResult([primaryContext,parentContext], perfTool,\
                          callTimeMinMet, c.min, "milliseconds", "noValue",\
                          "noValue")
       exe.addPerfResult(result)
       result = PerfResult([primaryContext,parentContext], perfTool,\
                          callTimeAppPrcntMet, c.app, "noValue", "noValue",\
                          "noValue")
       exe.addPerfResult(result)
       result = PerfResult([primaryContext,parentContext], perfTool,\
                          callTimeMPIPrcntMet, c.MPI, "noValue", "noValue",\
                          "noValue")
       exe.addPerfResult(result)

    # add Callsite Message statistics measurements
    for c in CM:
       cs = CS[int(c.site)-1]
       if cs.parentFun == "[unknown]": # don't have module/fun information
          mod = resIdx.findOrCreateResource(build.name+Resource.resDelim+"mod"+cs.fileAddr, "build"+Resource.resDelim+"module")
          fun = resIdx.findOrCreateResource(mod.name+Resource.resDelim+"fun"+cs.fileAddr, "build"+Resource.resDelim+"module"+Resource.resDelim+"function")
          codeLoc = resIdx.findOrCreateResource(fun.name+Resource.resDelim+cs.fileAddr, "build"+Resource.resDelim+"module"+Resource.resDelim+"function"+Resource.resDelim+"codeBlock")
       else:
          modLoc  = resIdx.findOrCreateResource(build.name+Resource.resDelim+cs.fileAddr,  "build"+Resource.resDelim+"module")
          codeLoc  = resIdx.findOrCreateResource(modLoc.name+Resource.resDelim+ cs.parentFun, "build"+Resource.resDelim+"module"+Resource.resDelim+"function")

       if not dynamic:
           mpiLoc = resIdx.findOrCreateResource(modName+Resource.resDelim + "MPI_"+c.name, "build"+Resource.resDelim+"module"+Resource.resDelim+"function")
       else:
           mpiLoc = resIdx.findOrCreateResource(modName+Resource.resDelim+  "MPI_"+c.name, "environment"+Resource.resDelim+"module"+Resource.resDelim+"function")
       procLoc = resIdx.findOrCreateResource(exe.name+Resource.resDelim+"Process-" + c.rank, "execution"+Resource.resDelim+"process")
       primaryContext = (resIdx.addSpecificContextResources(topContext,\
                      [mpiLoc,procLoc]),"primary")
       parentContext = (resIdx.addSpecificContextResources(topContext,\
                      [codeLoc,procLoc]),"parent")

       result = PerfResult([primaryContext,parentContext], perfTool, \
                         callMsgCountMet, c.count, "noValue", "noValue", \
                         "noValue")
       exe.addPerfResult(result)
       result = PerfResult([primaryContext,parentContext], perfTool,\
                          callMsgMaxMet, c.max, "bytes", "noValue", \
                          "noValue")
       exe.addPerfResult(result)
       result = PerfResult([primaryContext,parentContext], perfTool,\
                          callMsgMeanMet, c.mean, "bytes", "noValue",\
                          "noValue")
       exe.addPerfResult(result)
       result = PerfResult([primaryContext,parentContext], perfTool,\
                          callMsgMinMet, c.min, "bytes", "noValue",\
                          "noValue")
       exe.addPerfResult(result)
       result = PerfResult([primaryContext,parentContext], perfTool,\
                          callMsgSumMet, c.sum, "bytes", "noValue",\
                          "noValue")
       exe.addPerfResult(result)

    # add aggregate Callsite Message statistics measurements
    for c in CMW:
       cs = CS[int(c.site)-1]
       if cs.parentFun == "[unknown]": # don't have module/fun information
          mod = resIdx.findOrCreateResource(build.name+Resource.resDelim+"mod"+cs.fileAddr,  "build"+Resource.resDelim+"module")
          fun = resIdx.findOrCreateResource(mod.name+Resource.resDelim+"fun"+cs.fileAddr,  "build"+Resource.resDelim+"module"+Resource.resDelim+"function") 
    # add aggregate Callsite Message statistics measurements
    for c in CMW:
       cs = CS[int(c.site)-1]
       if cs.parentFun == "[unknown]": # don't have module/fun information
          mod = resIdx.findOrCreateResource(build.name+Resource.resDelim+"mod"+cs.fileAddr,  "build"+Resource.resDelim+"module")
          fun = resIdx.findOrCreateResource(mod.name+Resource.resDelim+"fun"+cs.fileAddr, "build"+Resource.resDelim+"module"+Resource.resDelim+"function")
          codeLoc = resIdx.findOrCreateResource(fun.name+Resource.resDelim+cs.fileAddr, "build"+Resource.resDelim+"module"+Resource.resDelim+"function"+Resource.resDelim+"codeBlock")
       else:
          modLoc  = resIdx.findOrCreateResource(build.name+Resource.resDelim+cs.fileAddr,  "build"+Resource.resDelim+"module")
          codeLoc  = resIdx.findOrCreateResource(modLoc.name+Resource.resDelim+ cs.parentFun, "build"+Resource.resDelim+"module"+Resource.resDelim+"function")

       if not dynamic:
           mpiLoc = resIdx.findOrCreateResource(modName+Resource.resDelim  + "MPI_"+c.name, "build"+Resource.resDelim+"module"+Resource.resDelim+"function")
       else:
           mpiLoc = resIdx.findOrCreateResource(modName+Resource.resDelim+  "MPI_"+c.name, "environment"+Resource.resDelim+"module"+Resource.resDelim+"function")
       procLoc = exe
       primaryContext = (resIdx.addSpecificContextResources(topContext,\
                      [mpiLoc,procLoc]),"primary")
       parentContext = (resIdx.addSpecificContextResources(topContext,\
                      [codeLoc,procLoc]),"parent")

       result = PerfResult([primaryContext,parentContext], perfTool, \
                         callMsgCountMet, c.count, "noValue", "noValue", \
                         "noValue")
       exe.addPerfResult(result)
       result = PerfResult([primaryContext,parentContext], perfTool,\
                          callMsgMaxMet, c.max, "bytes", "noValue", \
                          "noValue")
       exe.addPerfResult(result)
       result = PerfResult([primaryContext,parentContext], perfTool,\
                          callMsgMeanMet, c.mean, "bytes", "noValue",\
                          "noValue")
       exe.addPerfResult(result)
       result = PerfResult([primaryContext,parentContext], perfTool,\
                          callMsgMinMet, c.min, "bytes", "noValue",\
                          "noValue")
       exe.addPerfResult(result)
       result = PerfResult([primaryContext,parentContext], perfTool,\
                          callMsgSumMet, c.sum, "bytes", "noValue",\
                          "noValue")
       exe.addPerfResult(result)



