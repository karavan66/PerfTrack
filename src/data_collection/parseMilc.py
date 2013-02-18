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
   
    if app.name.lower() == ("su3_rmd"):
       processSu3_rmd(resIdx, fnames)

   





def processSu3_rmd(resIdx, fname ): 


    # expect only one execution and one application in resIdx
    [exe] = resIdx.findResourcesByType("execution")
    [app] = resIdx.findResourcesByType("application")

    # open the data file
    try:
       [file] = fname
       f = open(file, 'r')
    except:
       raise PTexception("Perf.processSu3_rmd: could not open performance data "\
                         "file:%s" % fname)

    terminationSeen = False
    #print 'processing: ' + file
    line = f.readline()
    
    avgCgIters = []
    timeLines = [] 
    totalItersLines = []
    while not terminationSeen:
        if line.startswith("exit:"):
           terminationSeen = True
           break
        elif line.startswith("RUNNING COMPLETED"):
           avgCgItersLine = f.readline()
           bigIterLine = f.readline()
           totalItersLine = f.readline()
           #average cg iters for step= 6.000000e+00 
           val = avgCgItersLine.split("=")[1].strip()
           avgCgIters.append(val)
           #Time = 2.016846e+01 seconds
           val = bigIterLine.split("=")[1].split()[0].strip()
           timeLines.append(val)
           #total_iters = 40
           val = totalItersLine.split("=")[1].strip()
           totalItersLines.append(val)
        line = f.readline()
    f.close() 
    #print avgCgIters
    #print timeLines
    #print totalItersLines

    vals = zip(avgCgIters, timeLines, totalItersLines)

    exe.setApplication(app)
    perfTool = Resource("self instrumentation", "performanceTool")
    resIdx.addResource(perfTool)

    cgIterMet = Resource("average cg iters for step","metric")
    resIdx.addResource(cgIterMet)
    timeMet = Resource("Time","metric")
    resIdx.addResource(timeMet)
    totalItersMet = Resource("total_iters","metric")
    resIdx.addResource(totalItersMet)

    topTimeLoc = resIdx.findOrCreateResource("whole execution", "time")
    resIdx.addResource(topTimeLoc)

    contextTemplate = resIdx.createContextTemplate()
    runMachs = resIdx.findResourcesByShortType("machine")
    if len(runMachs) > 1:
        raise PTexception("More than one machine resource associated with this execution. This case is not yet handled. Execution: %s" % exe.name)
    if runMachs != []:
       [hwLoc] = runMachs
       topContext = resIdx.addSpecificContextResource(contextTemplate,hwLoc)
    else:
       topContext = contextTemplate

    
    iterCount = 1
    for cgIter,timeLine,totalIters in vals:
       timeLoc = resIdx.findOrCreateResource("whole execution%smain loop iteration %d" % (Resource.resDelim,iterCount), "time%sinterval" % Resource.resDelim)
       context = resIdx.addSpecificContextResource(topContext, timeLoc)
       result = PerfResult(context, perfTool, cgIterMet, cgIter, "", "noValue", \
                "noValue") 
       exe.addPerfResult(result)
       result = PerfResult(context, perfTool, timeMet, timeLine, "seconds", \
                "noValue", "noValue") 
       exe.addPerfResult(result)
       result = PerfResult(context, perfTool, totalItersMet, totalIters, "", \
                "noValue", "noValue") 
       exe.addPerfResult(result)
       iterCount += 1


