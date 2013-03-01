#!/usr/bin/env python

# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information. 

import re, glob
from PerfResult import PerfResult
from PTexception import PTexception
from ResourceIndex import ResourceIndex
from Resource import Resource
from Execution import Execution

def getPerfInfo(resIdx, fnames, threaded=False):
    
    # expect one application resource in resIdx
    [app] = resIdx.findResourcesByType("application")
   
    if app.name.lower() == ("sppm"):
       [f] = fnames
       files = glob.glob(f) 
       files.sort()
       if len(files) == 0:
          print "no performance data files found for execution: %s" % exe.name
       for fname in files:
          if fname.find("output") >= 0:
             processSppm(resIdx, fname, f.rstrip('*'))

    elif app.name.lower() == ("irs"):
       [hspFile, tmrFile, hostFile] = fnames
       processIRS(resIdx, hspFile, tmrFile, hostFile, threaded)

    elif app.name.lower() == ("smg2000"):
       processSMG(resIdx, fnames)

    elif app.name.lower() == ("amg2006"):
       processAMG(resIdx, fnames)

    elif app.name.lower() == ("umt2k"):
       processUMT(resIdx,fnames)

    elif app.name.lower() == ("gtc"):
       processGtc(resIdx, fnames)

    #elif app.name.lower() == ("nwchem-5.1"):
    #   processNWC(resIdx, fnames)

def processSppm(resIdx, fname, f):

    # lists
    timeStepInfo = {}
    # this gets process number information from file extension
    procNum = fname.split(f)[1] #name like output0, output1, where
                              #number indicates the process number
    
    # open the data file
    try:
       f = open(fname, 'r')
    except:
       raise PTexception("Perf.processSppm: could not open performance data "\
                         "file:%s" % fname)

    terminationSeen = False	 # have we seen the "Finished Calculation"
                            # string that signifies that the run completed?

    
    # cycle through the file
    line = f.readline()

    while line != '':
        if line.find("Finished Calculation") >= 0:
           terminationSeen = True

        # record which double timestep we're on
        if line.find("Begin Double Timestep") >= 0:
            # extract the timestep number
            l = line.replace("=","").strip().strip(">").strip("<").strip()
            theTimeStepNumber = l.split("Begin Double Timestep")[1].strip() 
            # create an empty dictionary for this time step
            thisTimeStepInfo = {}

        # look for x bndry lines
        if line.find("Finished X bdrys") >= 0:
            # extract the numbers cpu, wall, and ratio
            vals = line.split("Finished X bdrys")[0].split(":")[1].split()
            if thisTimeStepInfo.has_key('xbndry'):
                thisTimeStepInfo['xbndry'][0] = float(thisTimeStepInfo['xbndry'][0])+float(vals[0])
                thisTimeStepInfo['xbndry'][1] = float(thisTimeStepInfo['xbndry'][1])+float(vals[1])
            else:
                thisTimeStepInfo['xbndry'] = [vals[0],vals[1]]
            
        # look for x sweep lines
        if line.find("Finished X sweep") >= 0:
            vals = line.split("Finished X sweep")[0].split(":")[1].split()
            if thisTimeStepInfo.has_key('xsweep'):
                thisTimeStepInfo['xsweep'][0] = float(thisTimeStepInfo['xsweep'][0])+float(vals[0])
                thisTimeStepInfo['xsweep'][1] = float(thisTimeStepInfo['xsweep'][1])+float(vals[1])
            else:
                thisTimeStepInfo['xsweep'] = [vals[0],vals[1]]
            
        # look for y bndry lines
        if line.find("Finished Y bdrys") >= 0:
            vals = line.split("Finished Y bdrys")[0].split(":")[1].split()
            if thisTimeStepInfo.has_key('ybndry'):
                thisTimeStepInfo['ybndry'][0] = float(thisTimeStepInfo['ybndry'][0])+float(vals[0])
                thisTimeStepInfo['ybndry'][1] = float(thisTimeStepInfo['ybndry'][1])+float(vals[1])
            else:
                thisTimeStepInfo['ybndry'] = [vals[0],vals[1]]
            
        # look for y sweep lines
        if line.find("Finished Y sweep") >= 0:
            vals = line.split("Finished Y sweep")[0].split(":")[1].split()
            if thisTimeStepInfo.has_key('ysweep'):
                thisTimeStepInfo['ysweep'][0] = float(thisTimeStepInfo['ysweep'][0])+float(vals[0])
                thisTimeStepInfo['ysweep'][1] = float(thisTimeStepInfo['ysweep'][1])+float(vals[1])
            else:
                thisTimeStepInfo['ysweep'] = [vals[0],vals[1]]
            
        # look for z bndry lines
        if line.find("Finished Z bdrys") >= 0:
            vals = line.split("Finished Z bdrys")[0].split(":")[1].split()
            if thisTimeStepInfo.has_key('zbndry'):
                thisTimeStepInfo['zbndry'][0] = float(thisTimeStepInfo['zbndry'][0])+float(vals[0])
                thisTimeStepInfo['zbndry'][1] = float(thisTimeStepInfo['zbndry'][1])+float(vals[1])
            else:
                thisTimeStepInfo['zbndry'] = [vals[0],vals[1]]
            
        # look for z sweep lines
        if line.find("Finished Z sweep") >= 0:
            vals = line.split("Finished Z sweep")[0].split(":")[1].split()
            if thisTimeStepInfo.has_key('zsweep'):
                thisTimeStepInfo['zsweep'][0] = float(thisTimeStepInfo['zsweep'][0])+float(vals[0])
                thisTimeStepInfo['zsweep'][1] = float(thisTimeStepInfo['zsweep'][1])+float(vals[1])
            else:
                thisTimeStepInfo['zsweep'] = [vals[0],vals[1]]

        # look for the physical data at the end of the time step
        if line.find("nstep Time") >= 0:
            line = f.readline()
            # separate out the values
            vals = line.strip().split()
            thisTimeStepInfo['physdata'] = vals
        
        # find all the TSTEP-HYD lines
        if line.find("TSTEP-HYD") >= 0:
            # get values cpu, wall, ratio
            vals = line.split("Finished   double ")[0].split(":")[1].split() 
            thisTimeStepInfo['tstephyd'] = vals

        # find all the TOTAL-HYD lines
        if line.find("TOTAL-HYD") >= 0:
            if line.find("Started Calculation") >= 0:
               pass # skip the Total-Hyd initialization line 
            else:
               # get values cpu, wall, ratio
               vals = line.split("Cumulative double")[0].split(":")[1].split() 
               thisTimeStepInfo['totalhyd'] = vals
               timeStepInfo[theTimeStepNumber] = thisTimeStepInfo

        line = f.readline()
    
    f.close()
    
    # expect one execution,app resource in resIdx
    [exe] = resIdx.findResourcesByType("execution")
    [app] = resIdx.findResourcesByType("application")

    if not terminationSeen:
       raise PTexception("Incomplete data file %s seen for execution:%s" \
                        % (fname, exe.name))
    #print timeStepInfo
    
    perfTool = Resource("self instrumentation", "performanceTool") 
    resIdx.addResource(perfTool)
    cpuTimeMet = Resource("TSTEP-HYD cpu time", "metric")
    resIdx.addResource(cpuTimeMet)
    cpuTimeMet.addAttribute("performanceTool",perfTool.name,"resource")
    wallTimeMet = Resource("TSTEP-HYD wall time", "metric")
    resIdx.addResource(wallTimeMet)
    wallTimeMet.addAttribute("performanceTool",perfTool.name,"resource")
    cpuwallratioMet = Resource("TSTEP-HYD cpu to wall time ratio", "metric") 
    resIdx.addResource(cpuwallratioMet)
    cpuwallratioMet.addAttribute("performanceTool",perfTool.name,"resource")
    totalcpuTimeMet = Resource("TOTAL-HYD cpu time", "metric")
    resIdx.addResource(totalcpuTimeMet)
    totalcpuTimeMet.addAttribute("performanceTool",perfTool.name,"resource")
    totalwallTimeMet = Resource("TOTAL-HYD wall time", "metric")
    resIdx.addResource(totalwallTimeMet)
    totalwallTimeMet.addAttribute("performanceTool",perfTool.name,"resource")
    totalcpuwallratioMet = Resource("TOTAL-HYD cpu to wall time ratio","metric")
    resIdx.addResource(totalcpuwallratioMet)
    totalcpuwallratioMet.addAttribute("performanceTool",perfTool.name,"resource")

    exe.setApplication(app)
    topTimeLoc = resIdx.findOrCreateResource("whole execution", "time")
    procLoc = resIdx.findOrCreateResource(exe.name+Resource.resDelim+"Process-"+procNum,  "execution"+Resource.resDelim+"process")

    contextTemplate = resIdx.createContextTemplate()

    runMachs = resIdx.findResourcesByShortType("machine") 
    if len(runMachs) > 1:
        raise PTexception("More than one machine resource associated with this execution. This case is not yet handled. Execution: %s" % exe.name)
    if runMachs  != []:
       [hwLoc] = runMachs
       tContext = resIdx.addSpecificContextResource(contextTemplate,hwLoc)
    else:
       tContext = contextTemplate

    # each sppm output file is specific to a process 
    topContext = resIdx.addSpecificContextResource(tContext,procLoc)

    highestTimeStep = 0
    for timeStep in timeStepInfo:
    #    print "tstephyd " + timeStep + " cputime: " + timeStepInfo[timeStep]["tstephyd"][0]
        if int(timeStep) > highestTimeStep:
           highestTimeStep = int(timeStep)
        # get per time step values
        timeLoc = resIdx.findOrCreateResource("whole execution"+Resource.resDelim+timeStep, "time"+Resource.resDelim+"interval")
        context = resIdx.addSpecificContextResource(topContext,timeLoc)
        cpuTime = timeStepInfo[timeStep]["tstephyd"][0]
        result = PerfResult(context, perfTool, cpuTimeMet, cpuTime, "seconds",\
                "noValue", "noValue")
        exe.addPerfResult(result)
        wallTime = timeStepInfo[timeStep]["tstephyd"][1]
        result = PerfResult(context, perfTool, wallTimeMet, wallTime, "seconds",\
                "noValue", "noValue")
        exe.addPerfResult(result)
        cpuwallRatio = timeStepInfo[timeStep]["tstephyd"][2]
        result = PerfResult(context, perfTool, cpuwallratioMet, cpuwallRatio,\
                 "noValue", "noValue", "noValue")
        exe.addPerfResult(result)
 
    # get total execution time for this process 
    context = topContext 
    cpuTime = timeStepInfo[str(highestTimeStep)]["totalhyd"][0]
    result = PerfResult(context, perfTool, totalcpuTimeMet, cpuTime, "seconds",\
            "noValue", "noValue")
    exe.addPerfResult(result)
    wallTime = timeStepInfo[str(highestTimeStep)]["totalhyd"][1]
    result = PerfResult(context, perfTool, totalwallTimeMet, wallTime, "seconds",\
            "noValue", "noValue")
    exe.addPerfResult(result)
    cpuwallRatio = timeStepInfo[str(highestTimeStep)]["totalhyd"][2]
    result = PerfResult(context, perfTool, totalcpuwallratioMet, cpuwallRatio,\
             "noValue", "noValue", "noValue")
    exe.addPerfResult(result)



def processIRS(resIdx, hspFile, tmrFile, hostFile, threaded):
    # open the *hsp data file - contains high level program performance measurements

    try:
       f = open(hspFile, 'r')
    except:
       raise PTexception("Perf.processIRS: could not open performance data "\
                         "file:%s" % hspFile)

    figureOfMerit = None
    wallTime = None
    cpuTime = None
    physicsTime = None

    # cycle through the hsp file
    line = f.readline()

    while line != '':
        if line.startswith("BENCHMARK microseconds"):
           figureOfMerit = line.split("=")[1].strip()
        elif line.startswith("wall        time"):
           wallTime = line.split(":")[1].split("seconds")[0].strip()
        elif line.startswith("total   cpu time"):
           cpuTime = line.split(":")[1].split("seconds")[0].strip()
        elif line.startswith("physics cpu time"):
           physicsTime = line.split(":")[1].split("seconds")[0].strip()
        line = f.readline()
    f.close()

    if not figureOfMerit:
       raise PTexception("Incomplete .hsp file %s" % hspFile)
    # see if there is process/host information
    processMap = {}
    if (hostFile):
       try:
          f = open(hostFile, 'r')
          i = 0
          line = f.readline()
          while line != '':
             if line.find("!") >= 0:
                pass
             else:
                processMap[str(i)] = line.split('.')[0].strip()
                i += 1
             line = f.readline()
          f.close()
       except:  # hostfile doesn't exist
           pass

#    print processMap

    try:
       f = open(tmrFile, 'r')
    except:
       raise PTexception("Perf.processIRS: could not open performance data " \
                         "file:%s" % tmrFile)

    numberOfProcesses = 0
    numberOfThreads = 0

    line = f.readline()
    started = False
    while not started:
       line = f.readline()
       if line.find("ROUTINE") >= 0:
          started = True
       elif line.find("Num of MPI Processes") >= 0:
          numberOfProcesses = int(line.split(":")[1].strip()) 
       elif line.find("Num of Domains") >= 0:
          numberOfThreads = int(line.split(":")[1].strip())
    f.readline()   # throw away "------" line

    if numberOfProcesses and numberOfThreads:
       threadsPerProcess = numberOfThreads/numberOfProcesses
    #   print 'threadsPerPRocess:' + str(type(threadsPerProcess))
    else:
       print 'Unable to determine number of processes or threads in parseIRS'

    funTimings = []

    line = f.readline() # should be first function
    #print line
    done = False
    while line != '' and not done:
       temp = {}
       if line.find("Aggregate") >= 0:
           # break up the line into individual words
           parts = line.split()
           # first word is the function name
           temp['functionName'] = parts[0]
           # fourth and up are numbers
           temp['aggregateMFLOPWS'] = parts[4]
           temp['aggregateFLOPS'] = parts[5]
           temp['aggregateCPUSECS'] = parts[6]
           temp['aggregateWALLSECS'] = parts[7]
           temp['aggregateNUMCALLS'] = parts[8]
       else:
           print 'off step'
           sys.exit(0)
       line = f.readline()
       #print line
       if line.find("Average") >= 0:
           # break up the line into individual words
           parts = line.split()
           # fourth word and up are numbers
           temp['averageMFLOPWS'] = parts[4]
           temp['averageFLOPS'] = parts[5]
           temp['averageCPUSECS'] = parts[6]
           temp['averageWALLSECS'] = parts[7]
           temp['averageNUMCALLS'] = parts[8]
       line = f.readline()
       #print line
       if line.find("Max") >= 0:
           # check to see if there is data
           if not (line.find("----         ----") >= 0):
               parts = line.split()
               # sometimes there is a (T) or (G) there, sometimes not
               if len(parts) == 11:
                  i = -1 # offset references down 1 
               else:
                  i = 0  # offsets will be what they are
               # does it specify a process number?
               if parts[i+5] == "Proc":
                  temp['maxPROCNUM'] = parts[i+6]
                  #print 'MAX proc determined : ' + temp['maxPROCNUM']
               # gives the thread number in terms of the total number of threads
               # we want the thread number in terms of its parent process
               # so extract out the process number and the respective thread
               # number
               # processNumber = threadNumber/threadsPerProcess (integer divide)
               # threadNumber = threadNumber % threadsPerProcess (mod)
               elif parts[i+5] == "Thread":
                  if(threaded):
                     a = int(parts[i+6])
                     temp['maxPROCNUM'] = str(a/threadsPerProcess)
                     temp['maxTHREADNUM'] = str(a % threadsPerProcess)
                  else:
                     temp['maxPROCNUM'] = parts[i+6]
                  #print 'MAX proc thread determined : ' + temp['maxPROCNUM']
               temp['maxHasData'] = True
               temp['maxMFLOPWS'] = parts[i+7]
               temp['maxFLOPS'] = parts[i+8]
               temp['maxCPUSECS'] = parts[i+9]
               temp['maxWALLSECS'] = parts[i+10]
               temp['maxNUMCALLS'] = parts[i+11]
           else:
               temp['maxHasData'] = False
       line = f.readline()
       #print line
       if line.find("Min") >= 0:
           # check to see if there is data
           if not (line.find("----         ----") >= 0):
               parts = line.split()
               # sometimes there is a (T) or (G) there, sometimes not
               if len(parts) == 11:
                  i = -1 # offset references down 1 
               else:
                  i = 0  # offsets will be what they are
               # does it specify a process number?
               if parts[i+5] == "Proc":
                  temp['minPROCNUM'] = parts[i+6]
                  #print 'MIN proc determined : ' + temp['minPROCNUM']
               # gives the thread number in terms of the total number of threads
               # we want the thread number in terms of its parent process
               # so extract out the process number and the respective thread
               # number
               # processNumber = threadNumber/threadsPerProcess (integer divide)
               # threadNumber = threadNumber % threadsPerProcess (mod)
               elif parts[i+5] == "Thread":
                  if(threaded):
                     a = int(parts[i+6])
                     temp['minPROCNUM'] = str(a/threadsPerProcess)
                     temp['minTHREADNUM'] = str(a % threadsPerProcess)
                  else:
                     temp['minPROCNUM'] = parts[i+6]
                  #print 'MIN proc thread determined : ' + temp['minPROCNUM']
               temp['minHasData'] = True
               temp['minMFLOPWS'] = parts[i+7]
               temp['minFLOPS'] = parts[i+8]
               temp['minCPUSECS'] = parts[i+9]
               temp['minWALLSECS'] = parts[i+10]
               temp['minNUMCALLS'] = parts[i+11]
           else:
               temp['minHasData'] = False

       funTimings.append(temp)
       line = f.readline()
       #print line
       while line == '\n':  # skip any blank lines
          #print 'line matches newline'
          line = f.readline()
          #print line
       if line.find("======") >= 0:  # end of file marked by a bunch
                                              # of ==== s
          done = True
    f.close()

    # expect one execution and one application and one buildin resIdx
    [exe] = resIdx.findResourcesByType("execution")
    [app] = resIdx.findResourcesByType("application")
    [build] =resIdx.findResourcesByType("build")
 
    if not done:
       raise PTexception("Incomplete .tmr file seen for execution:%s" \
                         % exe.name)

    exe.setApplication(app)

    perfTool = Resource("self instrumentation", "performanceTool")
    resIdx.addResource(perfTool)
   
    figOfMeritMet = Resource("Figure of Merit", "metric")
    resIdx.addResource(figOfMeritMet)
    figOfMeritMet.addAttribute("performanceTool",perfTool.name,"resource")
    wallTimeMet = Resource("Wall time used", "metric")
    resIdx.addResource(wallTimeMet)
    wallTimeMet.addAttribute("performanceTool",perfTool.name,"resource")
    cpuTimeMet = Resource("Total CPU time used", "metric")
    resIdx.addResource(cpuTimeMet)
    cpuTimeMet.addAttribute("performanceTool",perfTool.name,"resource")
    physTimeMet = Resource("Physics CPU time used", "metric")
    resIdx.addResource(physTimeMet)
    physTimeMet.addAttribute("performanceTool",perfTool.name,"resource")

    procLoc = exe  # the entire execution

    timeLoc = resIdx.findOrCreateResource("whole execution", "time")

    contextTemplate = resIdx.createContextTemplate()

    runMachs = resIdx.findResourcesByShortType("machine")
    if len(runMachs) > 1:
        raise PTexception("More than one machine resource associated with this execution. This case is not yet handled. Execution: %s" % exe.name)
    if runMachs != []:
       [hwLoc] = runMachs
       topContext = resIdx.addSpecificContextResource(contextTemplate,hwLoc)
    else:
       topContext = contextTemplate
    

    context = topContext
    result = PerfResult(context, perfTool, figOfMeritMet, figureOfMerit,\
             "microseconds per zone-iteration", "noValue", "noValue")
    exe.addPerfResult(result)
    result = PerfResult(context, perfTool, wallTimeMet, wallTime,\
             "seconds", "noValue", "noValue")
    exe.addPerfResult(result)
    result = PerfResult(context, perfTool, cpuTimeMet, cpuTime,\
             "seconds", "noValue", "noValue")
    exe.addPerfResult(result)
    result = PerfResult(context, perfTool, physTimeMet, physicsTime,\
             "seconds", "noValue", "noValue")
    exe.addPerfResult(result)

    aggMFLOPWSMet = Resource("Aggregate MFLOP per Wall sec", "metric")
    resIdx.addResource(aggMFLOPWSMet)
    aggMFLOPWSMet.addAttribute("performanceTool",perfTool.name,"resource")
    aggFLOPSMet = Resource("Aggregate FLOPS", "metric")
    resIdx.addResource(aggFLOPSMet)
    aggFLOPSMet.addAttribute("performanceTool",perfTool.name,"resource")
    aggCPUSECSMet = Resource("Aggregate CPU time", "metric")
    resIdx.addResource(aggCPUSECSMet)
    aggCPUSECSMet.addAttribute("performanceTool",perfTool.name,"resource")
    aggWALLSECSMet = Resource("Aggregate wall time", "metric")
    resIdx.addResource(aggWALLSECSMet)
    aggWALLSECSMet.addAttribute("performanceTool",perfTool.name,"resource")
    aggNUMCALLSMet = Resource("Aggregate num calls", "metric")
    resIdx.addResource(aggNUMCALLSMet)
    aggNUMCALLSMet.addAttribute("performanceTool",perfTool.name,"resource")
    avgMFLOPWSMet = Resource("Average MFLOP per Wall sec", "metric")
    resIdx.addResource(avgMFLOPWSMet)
    avgMFLOPWSMet.addAttribute("performanceTool",perfTool.name,"resource")
    avgFLOPSMet = Resource("Average FLOPS", "metric")
    resIdx.addResource(avgFLOPSMet)
    avgFLOPSMet.addAttribute("performanceTool",perfTool.name,"resource")
    avgCPUSECSMet = Resource("Average CPU time", "metric")
    resIdx.addResource(avgCPUSECSMet)
    avgCPUSECSMet.addAttribute("performanceTool",perfTool.name,"resource")
    avgWALLSECSMet = Resource("Average wall time", "metric")
    resIdx.addResource(avgWALLSECSMet)
    avgWALLSECSMet.addAttribute("performanceTool",perfTool.name,"resource")
    avgNUMCALLSMet = Resource("Average num calls", "metric")
    resIdx.addResource(avgNUMCALLSMet)
    avgNUMCALLSMet.addAttribute("performanceTool",perfTool.name,"resource")
    maxMFLOPWSMet = Resource("Maximum MFLOP per Wall sec", "metric")
    resIdx.addResource(maxMFLOPWSMet)
    maxMFLOPWSMet.addAttribute("performanceTool",perfTool.name,"resource")
    maxFLOPSMet = Resource("Maximum FLOPS", "metric")
    resIdx.addResource(maxFLOPSMet)
    maxFLOPSMet.addAttribute("performanceTool",perfTool.name,"resource")
    maxCPUSECSMet = Resource("Maximum CPU time", "metric")
    resIdx.addResource(maxCPUSECSMet)
    maxCPUSECSMet.addAttribute("performanceTool",perfTool.name,"resource")
    maxWALLSECSMet = Resource("Maximum wall time", "metric")
    resIdx.addResource(maxWALLSECSMet)
    maxWALLSECSMet.addAttribute("performanceTool",perfTool.name,"resource")
    maxNUMCALLSMet = Resource("Maximum num calls", "metric")
    resIdx.addResource(maxNUMCALLSMet)
    maxNUMCALLSMet.addAttribute("performanceTool",perfTool.name,"resource")
    minMFLOPWSMet = Resource("Minimum MFLOP per Wall sec", "metric")
    resIdx.addResource(minMFLOPWSMet)
    minMFLOPWSMet.addAttribute("performanceTool",perfTool.name,"resource")
    minFLOPSMet = Resource("Minimum FLOPS", "metric")
    resIdx.addResource(minFLOPSMet)
    minFLOPSMet.addAttribute("performanceTool",perfTool.name,"resource")
    minCPUSECSMet = Resource("Minimum CPU time", "metric")
    resIdx.addResource(minCPUSECSMet)
    minCPUSECSMet.addAttribute("performanceTool",perfTool.name,"resource")
    minWALLSECSMet = Resource("Minimum wall time", "metric")
    resIdx.addResource(minWALLSECSMet)
    minWALLSECSMet.addAttribute("performanceTool",perfTool.name,"resource")
    minNUMCALLSMet = Resource("Minimum num calls", "metric")
    resIdx.addResource(minNUMCALLSMet)
    minNUMCALLSMet.addAttribute("performanceTool",perfTool.name,"resource")

    for funTiming in funTimings:
        funName = funTiming['functionName']
        (modName,dynamic) = getFunctionParentIRS(funName, resIdx)
        #print modName
        aggMFLOPWS = funTiming['aggregateMFLOPWS']
        aggFLOPS = funTiming['aggregateFLOPS']
        aggCPUSECS = funTiming['aggregateCPUSECS']
        aggWALLSECS = funTiming['aggregateWALLSECS']
        aggNUMCALLS = funTiming['aggregateNUMCALLS']
        avgMFLOPWS = funTiming['averageMFLOPWS']
        avgFLOPS = funTiming['averageFLOPS']
        avgCPUSECS = funTiming['averageCPUSECS']
        avgWALLSECS = funTiming['averageWALLSECS']
        avgNUMCALLS = funTiming['averageNUMCALLS']

        if not dynamic:
           modLoc = resIdx.findOrCreateResource(build.name+Resource.resDelim+ \
                          modName, "build"+Resource.resDelim+"module")
           codeLoc = resIdx.findOrCreateResource(build.name+Resource.resDelim+modName+Resource.resDelim + funName, "build"+Resource.resDelim+"module"+Resource.resDelim+"function")
        else:
           env_id = None
           envs = resIdx.findResourcesByType("environment")
           if len(envs) > 1:
              raise PTexception("More than one environment found for execution. This is not yet supported. Execution: %s" % exe.name)
           [env] = envs
           modLoc = resIdx.findOrCreateResource(modName, "environment"+Resource.resDelim+"module")
           envLoc = resIdx.findOrCreateResource(modName+Resource.resDelim+ funName, "environment"+Resource.resDelim+"module"+Resource.resDelim+"function")
           codeLoc = envLoc
        procLoc = exe

        context = resIdx.addSpecificContextResource(topContext,codeLoc) 
        results = []
        results.append(PerfResult(context, perfTool, aggMFLOPWSMet, aggMFLOPWS,\
             "MFLOPS", "noValue", "noValue"))
        results.append(PerfResult(context, perfTool, aggFLOPSMet, aggFLOPS,\
             "FLOPS", "noValue", "noValue"))
        results.append(PerfResult(context, perfTool, aggCPUSECSMet, aggCPUSECS,\
             "seconds", "noValue", "noValue"))
        results.append(PerfResult(context, perfTool, aggWALLSECSMet, aggWALLSECS,\
             "seconds", "noValue", "noValue"))
        results.append(PerfResult(context, perfTool, aggNUMCALLSMet, aggNUMCALLS,\
             "calls", "noValue", "noValue"))
        results.append(PerfResult(context, perfTool, avgMFLOPWSMet, avgMFLOPWS,\
             "MFLOPS", "noValue", "noValue"))
        results.append(PerfResult(context, perfTool, avgFLOPSMet, avgFLOPS,\
             "FLOPS", "noValue", "noValue"))
        results.append(PerfResult(context, perfTool, avgCPUSECSMet, avgCPUSECS,\
             "seconds", "noValue", "noValue"))
        results.append(PerfResult(context, perfTool, avgWALLSECSMet, avgWALLSECS,\
             "seconds", "noValue", "noValue"))
        results.append(PerfResult(context, perfTool, avgNUMCALLSMet, avgNUMCALLS,\
             "calls", "noValue", "noValue"))
        exe.addPerfResults(results)

        if funTiming['maxHasData']:
            maxPROCNUM = funTiming['maxPROCNUM']
            if funTiming.has_key('maxTHREADNUM'):
               maxTHREADNUM = funTiming['maxTHREADNUM']
            else:
               maxTHREADNUM = None
            maxMFLOPWS = funTiming['maxMFLOPWS']
            maxFLOPS = funTiming['maxFLOPS']
            maxCPUSECS = funTiming['maxCPUSECS']
            maxWALLSECS = funTiming['maxWALLSECS']
            maxNUMCALLS = funTiming['maxNUMCALLS']
            if maxTHREADNUM:
               procLoc = resIdx.findOrCreateResource(exe.name+Resource.resDelim+"Process-" + maxPROCNUM+ Resource.resDelim+"Thread-"+maxTHREADNUM, "execution"+Resource.resDelim+"process"+Resource.resDelim+"thread")
            else:
               procLoc = resIdx.findOrCreateResource(exe.name+Resource.resDelim+"Process-" + maxPROCNUM, "execution"+Resource.resDelim+"process")
            if processMap.has_key(maxPROCNUM):
               maxHwLoc = resIdx.findOrCreateResource(hwLoc.name+Resource.resDelim+"batch"+Resource.resDelim + processMap[maxPROCNUM], "grid"+Resource.resDelim+"machine"+Resource.resDelim+"partition"+Resource.resDelim+"node")
            else:
               maxHwLoc = hwLoc

            context = resIdx.addSpecificContextResources(topContext,[codeLoc,procLoc,maxHwLoc])
            results = []
            results.append(PerfResult(context, perfTool, maxMFLOPWSMet, \
                 maxMFLOPWS, "MFLOPS", "noValue", "noValue"))
            results.append(PerfResult(context, perfTool, maxFLOPSMet, maxFLOPS,\
                 "FLOPS", "noValue", "noValue"))
            results.append(PerfResult(context, perfTool, maxCPUSECSMet, \
                 maxCPUSECS, "seconds", "noValue", "noValue"))
            results.append(PerfResult(context, perfTool, maxWALLSECSMet, \
                 maxWALLSECS, "seconds", "noValue", "noValue"))
            results.append(PerfResult(context, perfTool, maxNUMCALLSMet, \
                 maxNUMCALLS, "calls", "noValue", "noValue"))
            exe.addPerfResults(results)


        if funTiming['minHasData']:
            minPROCNUM = funTiming['minPROCNUM']
            if funTiming.has_key('minTHREADNUM'):
               minTHREADNUM = funTiming['minTHREADNUM']
            else:
               minTHREADNUM = None
            #print 'MIN proc num:' + str(minPROCNUM) + 'threadnum:'+str(minTHREADNUM)
            minMFLOPWS = funTiming['minMFLOPWS']
            minFLOPS = funTiming['minFLOPS']
            minCPUSECS = funTiming['minCPUSECS']
            minWALLSECS = funTiming['minWALLSECS']
            minNUMCALLS = funTiming['minNUMCALLS']
            if minTHREADNUM:
               procLoc = resIdx.findOrCreateResource(exe.name+Resource.resDelim+"Process-" + minPROCNUM+Resource.resDelim+"Thread-"+minTHREADNUM, "execution"+Resource.resDelim+"process"+Resource.resDelim+"thread")
            else:
               procLoc = resIdx.findOrCreateResource(exe.name+Resource.resDelim+"Process-" + minPROCNUM, "execution"+Resource.resDelim+"process")
            if processMap.has_key(minPROCNUM):
               #print 'minPROCNUM: %s processMap[minPROCNUM]: %s' % \
               #      (minPROCNUM, processMap[minPROCNUM])
               minHwLoc = resIdx.findOrCreateResource(hwLoc.name+Resource.resDelim+"batch" +Resource.resDelim + processMap[minPROCNUM], "grid"+Resource.resDelim+"machine"+Resource.resDelim+"partition"+Resource.resDelim+"node")
            else:
               minHwLoc = hwLoc
            #print 'min context:codeLoc: %s minHwLoc: %s procLoc: %s timeLoc: %s'\
               #% (str(codeLoc), str(minHwLoc), str(procLoc), str(timeLoc))
            context = resIdx.addSpecificContextResources(topContext,[codeLoc,procLoc,minHwLoc]) 
            results = []
            results.append(PerfResult(context, perfTool, minMFLOPWSMet, \
                 minMFLOPWS, "MFLOPS", "noValue", "noValue"))
            results.append(PerfResult(context, perfTool, minFLOPSMet, minFLOPS,\
                 "FLOPS", "noValue", "noValue"))
            results.append(PerfResult(context, perfTool, minCPUSECSMet, \
                 minCPUSECS, "seconds", "noValue", "noValue"))
            results.append(PerfResult(context, perfTool, minWALLSECSMet, \
                 minWALLSECS, "seconds", "noValue", "noValue"))
            results.append(PerfResult(context, perfTool, minNUMCALLSMet, \
                 minNUMCALLS, "calls", "noValue", "noValue"))
            exe.addPerfResults(results)



def getFunctionParentIRS(funName, resIdx):
    """Returns the name of the module in which the function can be found.
       It also returns True if the module is a dynamic library, and False
       if not.
       If searching for MPI functions, it is assumed that the MPI library has already
       been added to the build or environment of the Execution, exe.  If not, a 
       PTexception is thrown. If a matching library or module is not found, a 
       PTexception is raised.
       The form of the return value is (moduleName, Dynamic)
    """
    dynamic = False
    if funName.startswith("rdiff") or funName.startswith("tdiff") or \
       funName == "rmatmult3" or funName == "gtkappabnd" or \
       funName == "diagonal" or funName.startswith("update") or \
       funName == "volcal3d" or funName == "DensityEnergyMin" or \
       funName == "DivgradDriver" or funName == "dsrc" or \
       funName == "eos_init" or funName == "erate" or funName == "EosDriver" or\
       funName == "eosfm5" or funName == "esrc" or funName == "etaminchk" or \
       funName == "FluxLimiterDriver" or funName.startswith("getemat") or \
       funName == "getspeed2" or funName == "InitCycle" or \
       funName == "LengthScale" or funName == "opac2t" or \
       funName == "planck_opacity" or funName == "pminchk" or \
       funName == "PostSubcycle" or funName == "PreSubcycle" or \
       funName == "psrc" or funName.startswith("refnd3d") or \
       funName == "refzq" or funName == "stoplot" or funName == "tblkinit" or\
       funName == "tmsrc" or funName == "norml2" or \
       funName == "divgradpert3d" or funName.startswith("geteos") or \
       funName == "radinit" or funName == "retransfer" or \
       funName == "HydroDtControls" or funName == "regenrgy3d" or \
       funName == "rsrcbc3" or funName == "xirs" or funName == "zstarcal": 
     
       modName = funName + ".c"
    elif funName == "DtTempInitialize" or funName == "DtTempInitialze":
       modName = "DtTempInitialize.c"   # oops function name is mispelled in
                                        # output of benchmark. 
    elif funName.startswith("RadiationSource"):
       modName = "RadiationSourceBC.c"
    elif funName.startswith("MatrixSolve"):
       modName = "MatrixSolve.c"
    elif funName.startswith("ChemPot"):
       modName = "ChemPotCalc.c"
    elif funName.startswith("KrAnalytic_"):
       modName = "KrAnalytic.c"
    elif funName.startswith("KpAnalytic_"):
       modName = "KpAnalytic.c"
    elif funName.startswith("SetFaceTemperature"):
       modName = "SetFaceTemperature.c"
    elif funName.startswith("DiffCoef"):
       modName = "DiffCoef.c"
    elif funName == "FluxLimiterPert3d":
       modName = "FluxLimiter3d.c"
    elif funName == "EosGroup_check" or funName == "Region_check":
       modName = "Region.c"
    elif funName.startswith("CalcDt"):
       modName = "DtTempControls.c"
    elif funName.startswith("MPI_"):
       modName = ""
       reses = resIdx.findResourcesByShortType("module")
       for res in reses:
          if res.getName().find("libmpi") >= 0:
             modName = res.getName()
             # if lib found in build hierarchy, then static
             # if found in environment, then dynamic
             if res.getType().find("build") >= 0:
                dynamic = False
             else:
                dynamic = True
             break
       if modName == "":
           raise PTexception("parsePurple.getFunctionParentIRS: Module not found for function:%s"\
                             % funName) 
    else:
       raise PTexception("parsePurple.getFunctionParentIRS: Module not found for function:%s"\
                         % funName) 
    return (modName, dynamic)



def processSMG(resIdx, fname ): 

    terminationSeen = False

    # expect only one execution and one application in resIdx
    [exe] = resIdx.findResourcesByType("execution")
    [app] = resIdx.findResourcesByType("application")

    # open the data file
    try:
       [file] = fname
       f = open(file, 'r')
    except:
       raise PTexception("Perf.processSMG: could not open performance data "\
                         "file:%s" % fname)

    print 'processing: ' + file
    line = f.readline()
    while line != '':

        if line.find("Final Relative Residual") >= 0:
           terminationSeen = True
           parts = line.split("=")
           finalRelRes = parts[1].strip()
        elif line.find("Running with these driver parameters") >= 0:
           line = f.readline()
           while line.find("=====") < 0:
               parts = line.split("=")
               name = parts[0].split("0:")[1]
               exe.addAttribute(name.strip(),parts[1].strip())
               line = f.readline()
        elif line.find("Struct Interface") >= 0:
           f.readline()  # throw away ======
           f.readline()  # throw away next Struct Interface 
           line = f.readline() # get wall clock
           parts = line.split("=") 
           value_unit = parts[1].split()
           siWallTime = value_unit[0].strip()
           siWallTimeUnits = value_unit[1].strip()
           line = f.readline() # get cpu clock
           parts = line.split("=") 
           value_unit = parts[1].split()
           siCpuTime = value_unit[0].strip()
           siCpuTimeUnits = value_unit[1].strip()
        elif line.find("Setup phase time") >= 0:
           f.readline()  # throw away ======
           f.readline()  # throw away SMG Setup 
           line = f.readline() # get wall clock
           parts = line.split("=") 
           value_unit = parts[1].split()
           suWallTime = value_unit[0].strip()
           suWallTimeUnits = value_unit[1].strip()
           line = f.readline() # get cpu clock
           parts = line.split("=") 
           value_unit = parts[1].split()
           suCpuTime = value_unit[0].strip()
           suCpuTimeUnits = value_unit[1].strip()
        elif line.find("Solve phase time") >= 0:
           line = f.readline()  
           while line.find("wall clock") < 0:
                line = f.readline()
           parts = line.split("=") 
           #print file +": " + str(parts)
           value_unit = parts[1].split()
           soWallTime = value_unit[0].strip()
           soWallTimeUnits = value_unit[1].strip()
           line = f.readline() # get cpu clock
           parts = line.split("=") 
           value_unit = parts[1].split()
           soCpuTime = value_unit[0].strip()
           soCpuTimeUnits = value_unit[1].strip()
        elif line.find("Iterations") >= 0:
           parts = line.split("=")
           Iters = parts[1].strip()
        line = f.readline()

    f.close()

    [exe] = resIdx.findResourcesByType("execution")
    [app] = resIdx.findResourcesByType("application")

    exe.setApplication(app)
    perfTool = Resource("self instrumentation", "performanceTool")
    resIdx.addResource(perfTool)
    siwallTimeMet = Resource("Struct Interface: wall clock time", "metric")
    resIdx.addResource(siwallTimeMet)
    siwallTimeMet.addAttribute("performanceTool",perfTool.name,"resource")
    sicpuTimeMet = Resource("Struct Interface: cpu clock time", "metric")
    resIdx.addResource(sicpuTimeMet)
    sicpuTimeMet.addAttribute("performanceTool",perfTool.name,"resource")
    suwallTimeMet = Resource("SMG Setup: wall clock time", "metric")
    resIdx.addResource(suwallTimeMet)
    suwallTimeMet.addAttribute("performanceTool",perfTool.name,"resource")
    sucpuTimeMet = Resource("SMG Setup: cpu clock time", "metric")
    resIdx.addResource(sucpuTimeMet)
    sucpuTimeMet.addAttribute("performanceTool",perfTool.name,"resource")
    sowallTimeMet = Resource("SMG Solve: wall clock time", "metric")
    resIdx.addResource(sowallTimeMet)
    sowallTimeMet.addAttribute("performanceTool",perfTool.name,"resource")
    socpuTimeMet = Resource("SMG Solve: cpu clock time", "metric")
    resIdx.addResource(socpuTimeMet)
    socpuTimeMet.addAttribute("performanceTool",perfTool.name,"resource")
    iterMet = Resource("Iterations", "metric")
    resIdx.addResource(iterMet)
    iterMet.addAttribute("performanceTool",perfTool.name,"resource")
    finalRelResidualMet = Resource("Final Relative Residual Norm", "metric")
    resIdx.addResource(finalRelResidualMet)
    finalRelResidualMet.addAttribute("performanceTool",perfTool.name,"resource")

    timeLoc = resIdx.findOrCreateResource("whole execution", "time")
    resIdx.addResource(timeLoc)
    
    procLoc = exe
    contextTemplate = resIdx.createContextTemplate()
    runMachs = resIdx.findResourcesByShortType("machine")
    if len(runMachs) > 1:
        raise PTexception("More than one machine resource associated with this execution. This case is not yet handled. Execution: %s" % exe.name)
    if runMachs != []:
       [hwLoc] = runMachs
       topContext = resIdx.addSpecificContextResource(contextTemplate,hwLoc)
    else:
       topContext = contextTemplate


    context = topContext
    result = PerfResult(context, perfTool, siwallTimeMet, siWallTime, \
                       siWallTimeUnits, "noValue", "noValue")
    exe.addPerfResult(result)
    result = PerfResult(context, perfTool, sicpuTimeMet, siCpuTime, \
                       siCpuTimeUnits, "noValue", "noValue")
    exe.addPerfResult(result)
    result = PerfResult(context, perfTool, suwallTimeMet, suWallTime, \
                       suWallTimeUnits, "noValue", "noValue")
    exe.addPerfResult(result)
    result = PerfResult(context, perfTool, sucpuTimeMet, suCpuTime, \
                       suCpuTimeUnits, "noValue", "noValue")
    exe.addPerfResult(result)
    result = PerfResult(context, perfTool, sowallTimeMet, soWallTime, \
                       soWallTimeUnits, "noValue", "noValue")
    exe.addPerfResult(result)
    result = PerfResult(context, perfTool, socpuTimeMet, soCpuTime, \
                       soCpuTimeUnits, "noValue", "noValue")
    exe.addPerfResult(result)
    result = PerfResult(context, perfTool, iterMet, Iters, \
                       "noValue", "noValue", "noValue")
    exe.addPerfResult(result)
    result = PerfResult(context, perfTool, finalRelResidualMet, \
                       finalRelRes, "noValue", "noValue", "noValue")
    exe.addPerfResult(result)


def processAMG(resIdx, fname ):
    terminationSeen = False

    # expect only one execution and one application in resIdx
    [exe] = resIdx.findResourcesByType("execution")
    [app] = resIdx.findResourcesByType("application")

    # open the data file
    try:
       [file] = fname
       f = open(file, 'r')
    except:
       raise PTexception("Perf.processAMG: could not open performance data "\
                         "file:%s" % fname)

    print 'processing: ' + file
    while 1:
        line = f.readline()
        if not line:
           break

        #print line
        if line.find("Final Relative Residual") >= 0:
           #terminationSeen = True
           parts = line.split("=")
           finalRelRes = parts[1].strip()
        #elif line.find("Running with these driver parameters") >= 0:
        #   line = f.readline()
        #   while line.find("=====") < 0:
        #       parts = line.split("=")
        #       name = parts[0].split("0:")[1]
        #       exe.addAttribute(name.strip(),parts[1].strip())
        #       line = f.readline()
        elif line.find("SStruct Interface") >= 0:
           f.readline()  # throw away ======
           f.readline()  # throw away next Struct Interface 
           line = f.readline() # get wall clock
           parts = line.split("=")
           value_unit = parts[1].split()
           siWallTime = value_unit[0].strip()
           siWallTimeUnits = value_unit[1].strip()
           line = f.readline() # get cpu clock
           parts = line.split("=")
           value_unit = parts[1].split()
           siCpuTime = value_unit[0].strip()
           siCpuTimeUnits = value_unit[1].strip()
        elif line.find("Setup phase times") >= 0:
           f.readline()  # throw away ======
           f.readline()  # throw away PCG Setup 
           line = f.readline() # get wall clock
           parts = line.split("=")
           value_unit = parts[1].split()
           suWallTime = value_unit[0].strip()
           suWallTimeUnits = value_unit[1].strip()
           line = f.readline() # get cpu clock
           parts = line.split("=")
           value_unit = parts[1].split()
           suCpuTime = value_unit[0].strip()
           suCpuTimeUnits = value_unit[1].strip()
        elif line.find("Solve phase times") >= 0:
           f.readline()  # throw away ======
           f.readline()  # throw away PCG Solve
           line = f.readline() # get wall clock
           parts = line.split("=")
           #print file +": " + str(parts)
           value_unit = parts[1].split()
           soWallTime = value_unit[0].strip()
           soWallTimeUnits = value_unit[1].strip()
           line = f.readline() # get cpu clock
           parts = line.split("=")
           value_unit = parts[1].split()
           soCpuTime = value_unit[0].strip()
           soCpuTimeUnits = value_unit[1].strip()
        elif line.find("Iterations / Solve Phase Time") >= 0:
           #print "Found System Size Line!!!"
           #terminationSeen = True
           #System Size * Iterations / Solve Phase Time: 1.257195e+07
           parts = line.split(":")
           fom = parts[1].strip()
           #print "fom: " + fom
           break
        elif line.find("Iterations") >= 0:
           words = line.split()
           if words[0].strip() == "Iterations":
              parts = line.split("=")
              Iters = parts[1].strip()
        else:
           continue

    f.close()
    #print "Iters %s" % Iters
    #print "Solve CPU time %s" % soCpuTime
    #print "FOM %s" % fom

    [exe] = resIdx.findResourcesByType("execution")
    [app] = resIdx.findResourcesByType("application")

    exe.setApplication(app)

    perfTool = Resource("self instrumentation", "performanceTool")
    resIdx.addResource(perfTool)

    siwallTimeMet = Resource("SStruct Interface: wall clock time", "metric")
    resIdx.addResource(siwallTimeMet)
    siwallTimeMet.addAttribute("performanceTool",perfTool.name,"resource")


    sicpuTimeMet = Resource("SStruct Interface: cpu clock time", "metric")
    resIdx.addResource(sicpuTimeMet)
    sicpuTimeMet.addAttribute("performanceTool",perfTool.name,"resource")

    suwallTimeMet = Resource("PCG Setup: wall clock time", "metric")
    resIdx.addResource(suwallTimeMet)
    suwallTimeMet.addAttribute("performanceTool",perfTool.name,"resource")

    sucpuTimeMet = Resource("PCG Setup: cpu clock time", "metric")
    resIdx.addResource(sucpuTimeMet)
    sucpuTimeMet.addAttribute("performanceTool",perfTool.name,"resource")

    sowallTimeMet = Resource("PCG Solve: wall clock time", "metric")
    resIdx.addResource(sowallTimeMet)
    sowallTimeMet.addAttribute("performanceTool",perfTool.name,"resource")

    socpuTimeMet = Resource("PCG Solve: cpu clock time", "metric")
    resIdx.addResource(socpuTimeMet)
    socpuTimeMet.addAttribute("performanceTool",perfTool.name,"resource")

    iterMet = Resource("Iterations", "metric")
    resIdx.addResource(iterMet)
    iterMet.addAttribute("performanceTool",perfTool.name,"resource")

    fomMet = Resource("Figure of Merit", "metric")
    resIdx.addResource(fomMet)
    fomMet.addAttribute("performanceTool",perfTool.name,"resource")

    finalRelResidualMet = Resource("Final Relative Residual Norm", "metric")
    resIdx.addResource(finalRelResidualMet)
    finalRelResidualMet.addAttribute("performanceTool",perfTool.name,"resource")

    timeLoc = resIdx.findOrCreateResource("whole execution", "time")
    resIdx.addResource(timeLoc)

    procLoc = exe
    contextTemplate = resIdx.createContextTemplate()
    runMachs = resIdx.findResourcesByShortType("machine")
    if len(runMachs) > 1:
        raise PTexception("More than one machine resource associated with this execution. This case is not yet handled. Execution: %s" % exe.name)
    if runMachs != []:
       [hwLoc] = runMachs
       topContext = resIdx.addSpecificContextResource(contextTemplate,hwLoc)
    else:
       topContext = contextTemplate


    context = topContext
    result = PerfResult(context, perfTool, siwallTimeMet, siWallTime, \
                       siWallTimeUnits, "noValue", "noValue")
    exe.addPerfResult(result)

    result = PerfResult(context, perfTool, sicpuTimeMet, siCpuTime, \
                       siCpuTimeUnits, "noValue", "noValue")
    exe.addPerfResult(result)

    result = PerfResult(context, perfTool, suwallTimeMet, suWallTime, \
                       suWallTimeUnits, "noValue", "noValue")
    exe.addPerfResult(result)

    result = PerfResult(context, perfTool, sucpuTimeMet, suCpuTime, \
                       suCpuTimeUnits, "noValue", "noValue")
    exe.addPerfResult(result)

    result = PerfResult(context, perfTool, sowallTimeMet, soWallTime, \
                       soWallTimeUnits, "noValue", "noValue")
    exe.addPerfResult(result)

    result = PerfResult(context, perfTool, socpuTimeMet, soCpuTime, \
                       soCpuTimeUnits, "noValue", "noValue")
    exe.addPerfResult(result)

    result = PerfResult(context, perfTool, iterMet, Iters, \
                       "noValue", "noValue", "noValue")
    exe.addPerfResult(result)

    result = PerfResult(context, perfTool, fomMet, fom, "noValue", "noValue", "noValue")
    exe.addPerfResult(result)

    result = PerfResult(context, perfTool, finalRelResidualMet, \
                       finalRelRes, "noValue", "noValue", "noValue")
    exe.addPerfResult(result)


def processUMT(resIdx,fname):

    # expect only one execution and one application in resIdx
    [exe] = resIdx.findResourcesByType("execution")
    [app] = resIdx.findResourcesByType("application")

    # open the data file
    try:
       [file] = fname
       f = open(file, 'r')
    except:
       raise PTexception("Perf.processUMT: could not open performance data "\
                         "file:%s" % fname)

    print 'processing: ' + file
    line = f.readline()
    while line != '':
       if line.startswith("CPU time total"):
          parts = line.split("=")
          fp = parts[0].strip().split('(')
          cpuMetName = fp[0].strip()
          cpuTimeUnits = fp[1].strip(")")
          cpuTimeValue = parts[1].strip()
          #print "cpu MetName: %s Units: %s Value: %s" \
             #%(cpuMetName, cpuTimeUnits, cpuTimeValue)
       elif line.startswith("Wallclock time"):
          parts = line.split("=")
          fp = parts[0].strip().split('(')
          wallMetName = fp[0].strip()
          wallTimeUnits = fp[1].strip(")")
          wallTimeValue = parts[1].strip()
          #print "wall MetName: %s Units: %s Value: %s" \
             #%(wallMetName, wallTimeUnits, wallTimeValue)
       elif line.startswith("Angle-Loop-Only time"):
          parts = line.split("=")
          fp = parts[0].strip().split('(')
          angleLoopMetName = fp[0].strip()
          angleLoopTimeUnits = fp[1].strip(")")
          angleLoopTimeValue = parts[1].strip()
          #print "angleLoop MetName: %s Units: %s Value: %s" \
              #%(angleLoopMetName,angleLoopTimeUnits, angleLoopTimeValue)
       elif line.startswith("Communication time"):
          parts = line.split("=")
          fp = parts[0].strip().split('(')
          commMetName = fp[0].strip()
          commTimeUnits = fp[1].strip(")")
          commTimeValue = parts[1].strip()
          #print "comm MetName: %s Units: %s Value: %s" \
              #%(commMetName, commTimeUnits, commTimeValue)
       elif line.startswith("Convergence time"):
          parts = line.split("=")
          fp = parts[0].strip().split('(')
          convMetName = fp[0].strip()
          convTimeUnits = fp[1].strip(")")
          convTimeValue = parts[1].strip()
          #print "conv MetName: %s Units: %s Value: %s" \
              #%(convMetName, convTimeUnits, convTimeValue)
       line = f.readline()

    f.close()

    exe.setApplication(app)
    perfTool = Resource("self instrumentation", "performanceTool")
    resIdx.addResource(perfTool) 
    cpuMet = Resource(cpuMetName,"metric")
    resIdx.addResource(cpuMet)
    cpuMet.addAttribute("performanceTool",perfTool.name,"resource")
    wallMet = Resource(wallMetName,"metric")
    resIdx.addResource(wallMet)
    wallMet.addAttribute("performanceTool",perfTool.name,"resource")
    angleLoopMet = Resource(angleLoopMetName,"metric")
    resIdx.addResource(angleLoopMet)
    angleLoopMet.addAttribute("performanceTool",perfTool.name,"resource")
    commMet = Resource(commMetName,"metric")
    resIdx.addResource(commMet)
    commMet.addAttribute("performanceTool",perfTool.name,"resource")
    convMet = Resource(convMetName,"metric")
    resIdx.addResource(convMet)
    convMet.addAttribute("performanceTool",perfTool.name,"resource")

    timeLoc = resIdx.findOrCreateResource("whole execution", "time")
    resIdx.addResource(timeLoc)

    procLoc = exe
    contextTemplate = resIdx.createContextTemplate()
    runMachs = resIdx.findResourcesByShortType("machine")
    if len(runMachs) > 1:
        raise PTexception("More than one machine resource associated with this execution. This case is not yet handled. Execution: %s" % exe.name)
    if runMachs != []:
       [hwLoc] = runMachs
       topContext = resIdx.addSpecificContextResource(contextTemplate,hwLoc)
    else:
       topContext = contextTemplate

    context = topContext

    result = PerfResult(context, perfTool, cpuMet, cpuTimeValue, \
                       cpuTimeUnits, "noValue", "noValue")
    exe.addPerfResult(result)
    result = PerfResult(context, perfTool, wallMet, wallTimeValue, \
                       wallTimeUnits, "noValue", "noValue")
    exe.addPerfResult(result)
    result = PerfResult(context, perfTool, angleLoopMet, angleLoopTimeValue, \
                       angleLoopTimeUnits, "noValue", "noValue")
    exe.addPerfResult(result)
    result = PerfResult(context, perfTool, commMet, commTimeValue, \
                       commTimeUnits, "noValue", "noValue")
    exe.addPerfResult(result)
    result = PerfResult(context, perfTool, convMet, convTimeValue, \
                       convTimeUnits, "noValue", "noValue")
    exe.addPerfResult(result)

def processNWC(resIdx, fname):
    # expect only one execution and one application in resIdx
    [exe] = resIdx.findResourcesByType("execution")
    [app] = resIdx.findResourcesByType("application")

    # open the data file
    try:
       [file] = fname
       f = open(file, 'r')
    except:
       raise PTexception("Perf.processNWC: could not open performance data "\
                         "file:%s" % fname)

    print 'processing: ' + file
    line = f.readline()
    while line != '':
       if line.startswith("Wallclock Time"):
          parts = line.split()
          wcVal = parts[2].strip()
          wcMetName = "NWChem Wallclock Time"
          wcUnits = "seconds"
       line = f.readline()
    f.close()

    exe.setApplication(app)
    perfTool = Resource("self instrumentation", "performanceTool")
    resIdx.addResource(perfTool)
    wcMet = Resource(wcMetName,"metric")
    resIdx.addResource(wcMet)
    wcMet.addAttribute("performanceTool",perfTool.name,"resource")

    timeLoc = resIdx.findOrCreateResource("whole execution", "time")
    resIdx.addResource(timeLoc)

    procLoc = exe
    contextTemplate = resIdx.createContextTemplate()
    runMachs = resIdx.findResourcesByShortType("machine")
    if len(runMachs) > 1:
        raise PTexception("More than one machine resource associated with " \
                          "this execution. This case is not yet handled. " \
                          "Execution: %s" % exe.name)
    if runMachs != []:
       [hwLoc] = runMachs
       topContext = resIdx.addSpecificContextResource(contextTemplate,hwLoc)
    else:
       topContext = contextTemplate

    context = topContext

    result = PerfResult(context, perfTool, wcMet, wcVal, \
                       wcUnits, "noValue", "noValue")
    exe.addPerfResult(result)


def processGtc(resIdx, fname):
        ''' Parses the output of the GTC application and adds performance
            metrics to the resource index.

            input:
               resIdx - The resource index to add the performance metrics

               fname - Name of the file containing the output from GTC.

            output:
               no value is returned

            raises:
               PTexception if:
                  - fname can't be opened or opened. 
                  - there is an error parsing fname

            The metrics gathered are located at the end of the input file and
            include:
               - cpu time pusher
               - cpu time shift
               - cpu time charge
               - cpu time poisson
               - cpu time field
               - cpu time load
               - cpu time total
               - wall clock pusher
               - wall clock shift
               - wall clock charge
               - wall clock poisson
               - wall clock field
               - wall clock load
               - wall clock total
               - main loop time
               - total cpu time usage
               - total wall clock time
        '''

	# set verbose to True for verbose output to stdout during parsing
	verbose = False

	# only one execution and and one application is expeced in the
	# resource index
	[exe] = resIdx.findResourcesByType("execution")
	[app] = resIdx.findResourcesByType("application")

	# open the performance data file
	try:
		perfDataFile = open(fname[0], 'r')
	except:
		raise PTexception("parsePurple.parseGtc: unable to open "
			"performance data file " + fname[0])

	# read in the performance data file 
	try:
		perfData = perfDataFile.readlines()
	except:
		perfDataFile.close()
		raise PTexception("parsePurple.parseGtc: unable to read "
			"performance data file " + fname[0])
	perfDataFile.close()
		
	# Get the CPU time usage.
	# The values for CPU time usage are located on the third line after
	# the line containing " CPU TIME USAGE (in SEC):".  The CPU time
	# usage is recorded in the performance data file as a space
	# deliminated line containing a value, in seconds, for pusher,
	# shift, charge, poisson, smooth, field, load, and total, respectively.
	try:
		index = perfData.index(' CPU TIME USAGE (in SEC):\n')
	except:
		raise PTexception("parsePurple.parseGtc: incomplete performance"
			"data file, " + fname[0] + " ,could not find CPU TIME USAGE")
	index = index + 3
	line = perfData[index]
	line = line.split(" ")
	cpuTimePusherMetName = "CPU TIME USAGE pusher"
	cpuTimePusherTimeUnits = "sec"
	cpuTimePusherValue = line[1].strip()
	cpuTimeShiftMetName = "CPU TIME USAGE shift"
	cpuTimeShiftTimeUnits = "sec"
	cpuTimeShiftValue = line[2].strip()
	cpuTimeChargeMetName = "CPU TIME USAGE charge"
	cpuTimeChargeTimeUnits = "sec"
	cpuTimeChargeValue = line[3].strip()
	cpuTimePoissonMetName = "CPU TIME USAGE poisson"
	cpuTimePoissonTimeUnits = "sec"
	cpuTimePoissonValue = line[4].strip()
	cpuTimeSmoothMetName = "CPU TIME USAGE smooth"
	cpuTimeSmoothTimeUnits = "sec"
	cpuTimeSmoothValue = line[5].strip()
	cpuTimeFieldMetName = "CPU TIME USAGE field"
	cpuTimeFieldTimeUnits = "sec"
	cpuTimeFieldValue = line[6].strip()
	cpuTimeLoadMetName = "CPU TIME USAGE load"
	cpuTimeLoadTimeUnits = "sec"
	cpuTimeLoadValue = line[7].strip()
	cpuTimeTotalMetName = "CPU TIME USAGE total"
	cpuTimeTotalTimeUnits = "sec"
	cpuTimeTotalValue = line[8].strip()
	if verbose:
		print cpuTimePusherMetName + " " + cpuTimePusherTimeUnits + ": " +\
			cpuTimePusherValue 
		print cpuTimeShiftMetName + " " + cpuTimeShiftTimeUnits + ": " +\
			cpuTimeShiftValue 
		print cpuTimeChargeMetName + " " + cpuTimeChargeTimeUnits + ": " +\
			cpuTimeChargeValue 
		print cpuTimePoissonMetName + " " + cpuTimePoissonTimeUnits +\
			": " + cpuTimePoissonValue 
		print cpuTimeSmoothMetName + " " + cpuTimeSmoothTimeUnits + ": " +\
			cpuTimeSmoothValue 
		print cpuTimeFieldMetName + " " + cpuTimeFieldTimeUnits + ": " +\
			cpuTimeFieldValue 
		print cpuTimeLoadMetName + " " + cpuTimeLoadTimeUnits + ": " +\
			cpuTimeLoadValue 
		print cpuTimeTotalMetName + " " + cpuTimeTotalTimeUnits + ": " +\
			cpuTimeTotalValue 

	# Get the wall clock times.
	# The values for wall clock times are located on the fifth line after
	# the line containing the CPU time usage values.  Wall clock time 
	# is recorded in the performance data file as a space
	# deliminated line containing a value, in seconds, for pusher,
	# shift, charge, poisson, smooth, field, load, and total, respectively.
	index = index + 5
	line = perfData[index]
	line = line.split(" ")
	wallTimePusherMetName = "WALL CLOCK TIMES pusher"
	wallTimePusherTimeUnits = "sec"
	wallTimePusherValue = line[1].strip()
	wallTimeShiftMetName = "WALL CLOCK TIMES shift"
	wallTimeShiftTimeUnits = "sec"
	wallTimeShiftValue = line[2].strip()
	wallTimeChargeMetName = "WALL CLOCK TIMES charge"
	wallTimeChargeTimeUnits = "sec"
	wallTimeChargeValue = line[3].strip()
	wallTimePoissonMetName = "WALL CLOCK TIMES poisson"
	wallTimePoissonTimeUnits = "sec"
	wallTimePoissonValue = line[4].strip()
	wallTimeSmoothMetName = "WALL CLOCK TIMES smooth"
	wallTimeSmoothTimeUnits = "sec"
	wallTimeSmoothValue = line[5].strip()
	wallTimeFieldMetName = "WALL CLOCK TIMES field"
	wallTimeFieldTimeUnits = "sec"
	wallTimeFieldValue = line[6].strip()
	wallTimeLoadMetName = "WALL CLOCK TIMES load"
	wallTimeLoadTimeUnits = "sec"
	wallTimeLoadValue = line[7].strip()
	wallTimeTotalMetName = "WALL CLOCK TIMES total"
	wallTimeTotalTimeUnits = "sec"
	wallTimeTotalValue = line[8].strip()
	if verbose:
		print wallTimePusherMetName + " " + wallTimePusherTimeUnits +\
			": " + wallTimePusherValue 
		print wallTimeShiftMetName + " " + wallTimeShiftTimeUnits + ": " +\
			wallTimeShiftValue 
		print wallTimeChargeMetName + " " + wallTimeChargeTimeUnits +\
			": " + wallTimeChargeValue 
		print wallTimePoissonMetName + " " + wallTimePoissonTimeUnits +\
			": " + wallTimePoissonValue 
		print wallTimeSmoothMetName + " " + wallTimeSmoothTimeUnits +\
			": " + wallTimeSmoothValue 
		print wallTimeFieldMetName + " " + wallTimeFieldTimeUnits + ": " +\
			wallTimeFieldValue 
		print wallTimeLoadMetName + " " + wallTimeLoadTimeUnits + ": " +\
			wallTimeLoadValue 
		print wallTimeTotalMetName + " " + wallTimeTotalTimeUnits + ": " +\
			wallTimeTotalValue 

	# Get the main loop time.
	# The value for main loop time is located on the line after the wall
	# clock time values.  Main loop time is recorded on a single line
	# like, "MAIN LOOP TIME(SEC):     878.390"
	index = index + 1
	line = perfData[index]
	line = line.split(" ")
	mainLoopTimeMetName = "MAIN LOOP TIME"
	mainLoopTimeUnits = "sec"
	mainLoopTimeValue = line[len(line) - 1].strip()
	if verbose:
		print mainLoopTimeMetName + " " + mainLoopTimeUnits + " " +\
			mainLoopTimeValue

	# Get the total CPU time usage
	# The value for total CPU time usage is located on the line after the
	# main loop time.  Total CPU time usage is recorded on a single line
	# like, "TOTAL CPU TIME USAGE (SEC):     879.133"
	index = index + 1
	line = perfData[index]
	line = line.split(" ")
	totalCpuTimeUsageMetName = "TOTAL CPU TIME USAGE"
	totalCpuTimeUsageUnits = "sec"
	totalCpuTimeUsageValue = line[len(line) - 1].strip()
	if verbose:
		print totalCpuTimeUsageMetName + " " + totalCpuTimeUsageUnits +\
			" " + totalCpuTimeUsageValue

	# Get the total wall clock time
	# The value for total wall clock time is located on the line after the
	# total CPU time usage.  Total CPU time usage is recorded on a single
	# line like, "TOTAL WALL CLOCK TIME(SEC):     879.133"
	index = index + 1
	line = perfData[index]
	line = line.split(" ")
	totalWallClockMetName = "TOTAL WALL CLOCK TIME"
	totalWallClockUnits = "sec"
	totalWallClockValue = line[len(line) - 1].strip()
	if verbose:
		print totalWallClockMetName + " " + totalWallClockUnits +\
			" " + totalWallClockValue

	# Use the data gathered above to create resources and add the
	# resources to the resource index.	
	if verbose:
		print "Creating resources and adding them to the resource index."

	exe.setApplication(app)
	perfTool = Resource("self instrumentation", "performanceTool")
	resIdx.addResource(perfTool)
	
	cpuTimePusherMet = Resource(cpuTimePusherMetName, "metric")
	resIdx.addResource(cpuTimePusherMet)
	cpuTimePusherMet.addAttribute("performanceTool",perfTool.name,
		"resource")
	
	cpuTimeShiftMet = Resource(cpuTimeShiftMetName, "metric")
	resIdx.addResource(cpuTimeShiftMet)
	cpuTimeShiftMet.addAttribute("performanceTool",perfTool.name,
		"resource")

	cpuTimeChargeMet = Resource(cpuTimeChargeMetName, "metric")
	resIdx.addResource(cpuTimeChargeMet)
	cpuTimeChargeMet.addAttribute("performanceTool",perfTool.name,
		"resource")

	cpuTimePoissonMet = Resource(cpuTimePoissonMetName, "metric")
	resIdx.addResource(cpuTimePoissonMet)
	cpuTimePoissonMet.addAttribute("performanceTool",perfTool.name,
		"resource")

	cpuTimeSmoothMet = Resource(cpuTimeSmoothMetName, "metric")
	resIdx.addResource(cpuTimeSmoothMet)
	cpuTimeSmoothMet.addAttribute("performanceTool",perfTool.name,
		"resource")

	cpuTimeFieldMet = Resource(cpuTimeFieldMetName, "metric")
	resIdx.addResource(cpuTimeFieldMet)
	cpuTimeFieldMet.addAttribute("performanceTool",perfTool.name,
		"resource")

	cpuTimeLoadMet = Resource(cpuTimeLoadMetName, "metric")
	resIdx.addResource(cpuTimeLoadMet)
	cpuTimeLoadMet.addAttribute("performanceTool",perfTool.name,
		"resource")

	cpuTimeTotalMet = Resource(cpuTimeTotalMetName, "metric")
	resIdx.addResource(cpuTimeTotalMet)
	cpuTimeTotalMet.addAttribute("performanceTool",perfTool.name,
		"resource")

	wallTimePusherMet = Resource(wallTimePusherMetName, "metric")
	resIdx.addResource(wallTimePusherMet)
	wallTimePusherMet.addAttribute("performanceTool",perfTool.name,
		"resource")
	
	wallTimeShiftMet = Resource(wallTimeShiftMetName, "metric")
	resIdx.addResource(wallTimeShiftMet)
	wallTimeShiftMet.addAttribute("performanceTool",perfTool.name,
		"resource")

	wallTimeChargeMet = Resource(wallTimeChargeMetName, "metric")
	resIdx.addResource(wallTimeChargeMet)
	wallTimeChargeMet.addAttribute("performanceTool",perfTool.name,
		"resource")

	wallTimePoissonMet = Resource(wallTimePoissonMetName, "metric")
	resIdx.addResource(wallTimePoissonMet)
	wallTimePoissonMet.addAttribute("performanceTool",perfTool.name,
		"resource")

	wallTimeSmoothMet = Resource(wallTimeSmoothMetName, "metric")
	resIdx.addResource(wallTimeSmoothMet)
	wallTimeSmoothMet.addAttribute("performanceTool",perfTool.name,
		"resource")

	wallTimeFieldMet = Resource(wallTimeFieldMetName, "metric")
	resIdx.addResource(wallTimeFieldMet)
	wallTimeFieldMet.addAttribute("performanceTool",perfTool.name,
		"resource")

	wallTimeLoadMet = Resource(wallTimeLoadMetName, "metric")
	resIdx.addResource(wallTimeLoadMet)
	wallTimeLoadMet.addAttribute("performanceTool",perfTool.name,
		"resource")

	wallTimeTotalMet = Resource(wallTimeTotalMetName, "metric")
	resIdx.addResource(wallTimeTotalMet)
	wallTimeTotalMet.addAttribute("performanceTool",perfTool.name,
		"resource")

	mainLoopTimeMet = Resource(mainLoopTimeMetName, "metric")
	resIdx.addResource(mainLoopTimeMet)
	mainLoopTimeMet.addAttribute("performanceTool", perfTool.name,
		"resource")	

	totalCpuTimeUsageMet = Resource(totalCpuTimeUsageMetName, "metric")
	resIdx.addResource(totalCpuTimeUsageMet)
	totalCpuTimeUsageMet.addAttribute("performanceTool", perfTool.name,
		"resource")	

	totalWallClockMet = Resource(totalWallClockMetName, "metric")
	resIdx.addResource(totalWallClockMet)
	totalWallClockMet.addAttribute("performanceTool", perfTool.name,
		"resource")	

	# add a whole execution resource
	if verbose:
		print "Adding whole execution resource."
	timeLoc = resIdx.findOrCreateResource("whole execution", "time")
	resIdx.addResource(timeLoc)

	# create context
	if verbose:
		print "Creating context."
	procLoc = exe
	contextTemplate = resIdx.createContextTemplate()
	runMachs = resIdx.findResourcesByShortType("machine")
	if len(runMachs) > 1:
	    raise PTexception("parsePurple.processGtc: More than one machine"
			"resource associated with this execution. This case is not"
			"yet handled. Execution: %s" % exe.name)
	if runMachs != []:
	   [hwLoc] = runMachs
	   topContext = resIdx.addSpecificContextResource(contextTemplate,
			hwLoc)
	else:
	   topContext = contextTemplate
	
	context = topContext

	# add the performance results
	if verbose:
		print "Adding performance results."
	result = PerfResult(context, perfTool, cpuTimePusherMet,
		cpuTimePusherValue, cpuTimePusherTimeUnits, "noValue", "noValue")
	exe.addPerfResult(result)
	result = PerfResult(context, perfTool, cpuTimeShiftMet,
		cpuTimeShiftValue, cpuTimeShiftTimeUnits, "noValue", "noValue")
	exe.addPerfResult(result)
	result = PerfResult(context, perfTool, cpuTimeChargeMet,
		cpuTimeChargeValue, cpuTimeChargeTimeUnits, "noValue", "noValue")
	exe.addPerfResult(result)
	result = PerfResult(context, perfTool, cpuTimePoissonMet,
		cpuTimePoissonValue, cpuTimePoissonTimeUnits, "noValue", "noValue")
	exe.addPerfResult(result)
	result = PerfResult(context, perfTool, cpuTimeSmoothMet,
		cpuTimeSmoothValue, cpuTimeSmoothTimeUnits, "noValue", "noValue")
	exe.addPerfResult(result)
	result = PerfResult(context, perfTool, cpuTimeFieldMet,
		cpuTimeFieldValue, cpuTimeFieldTimeUnits, "noValue", "noValue")
	exe.addPerfResult(result)
	result = PerfResult(context, perfTool, cpuTimeLoadMet,
		cpuTimeLoadValue, cpuTimeLoadTimeUnits, "noValue", "noValue")
	exe.addPerfResult(result)
	result = PerfResult(context, perfTool, cpuTimeTotalMet,
		cpuTimeTotalValue, cpuTimeTotalTimeUnits, "noValue", "noValue")
	exe.addPerfResult(result)

	result = PerfResult(context, perfTool, wallTimePusherMet,
		wallTimePusherValue, wallTimePusherTimeUnits, "noValue", "noValue")
	exe.addPerfResult(result)
	result = PerfResult(context, perfTool, wallTimeShiftMet,
		wallTimeShiftValue, wallTimeShiftTimeUnits, "noValue", "noValue")
	exe.addPerfResult(result)
	result = PerfResult(context, perfTool, wallTimeChargeMet,
		wallTimeChargeValue, wallTimeChargeTimeUnits, "noValue", "noValue")
	exe.addPerfResult(result)
	result = PerfResult(context, perfTool, wallTimePoissonMet,
		wallTimePoissonValue, wallTimePoissonTimeUnits, "noValue",
			"noValue")
	exe.addPerfResult(result)
	result = PerfResult(context, perfTool, wallTimeSmoothMet,
		wallTimeSmoothValue, wallTimeSmoothTimeUnits, "noValue", "noValue")
	exe.addPerfResult(result)
	result = PerfResult(context, perfTool, wallTimeFieldMet,
		wallTimeFieldValue, wallTimeFieldTimeUnits, "noValue", "noValue")
	exe.addPerfResult(result)
	result = PerfResult(context, perfTool, wallTimeLoadMet,
		wallTimeLoadValue, wallTimeLoadTimeUnits, "noValue", "noValue")
	exe.addPerfResult(result)
	result = PerfResult(context, perfTool, wallTimeTotalMet,
		wallTimeTotalValue, wallTimeTotalTimeUnits, "noValue", "noValue")
	exe.addPerfResult(result)

	result = PerfResult(context, perfTool, mainLoopTimeMet,
		mainLoopTimeValue, mainLoopTimeUnits, "noValue", "noValue")
	exe.addPerfResult(result)

	result = PerfResult(context, perfTool, totalCpuTimeUsageMet,
		totalCpuTimeUsageValue, totalCpuTimeUsageUnits, "noValue",
		"noValue")
	exe.addPerfResult(result)

	result = PerfResult(context, perfTool, totalWallClockMet,
		totalWallClockValue, totalWallClockUnits, "noValue",
		"noValue")
	exe.addPerfResult(result)

