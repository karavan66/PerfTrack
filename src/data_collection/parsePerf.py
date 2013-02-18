#!/usr/bin/env python

# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information. 

import sys
import parsePurple
import parseMilc
import toolParser
from Resource import Resource
from PTds import PTdataStore
from glob import glob


def main(argv=sys.argv):
    print "exiting"
    return 0

def getSysPerfInfo(resIdx,dataDir,tools,ptds):
    for tool in tools:
       if tool.upper() == "SYSMPI":
           #print "SYSMPI sys perf data tool parser"
           toolParser.sysmpiParse(resIdx, dataDir, ptds)
       else:
          print "parsePerf:getSysPerfInfo: no system performance parser for \'%s\'" % tool

def getPerfInfo(resIdx, execName, dataDir, tools, threaded, ptds):
    # expect one application in resIdx
    [app] = resIdx.findResourcesByType("application")

    for tool in tools:      
       #print "processing tool %s for app %s and exe %s" % (tool, app.name ,execName)
       if tool == "self instrumentation":
           if app.name.lower() == ("sppm"):
              dataFiles = [dataDir + "/" + execName + ".output*"]
              parsePurple.getPerfInfo(resIdx, dataFiles, threaded)
           elif app.name.lower() == ("irs"):
              dataFiles = []
              dataFiles.append(dataDir + "/" + execName + ".hsp")
              dataFiles.append(dataDir + "/" + execName + ".tmr")
              dataFiles.append(dataDir + "/" + execName + ".hst")
              parsePurple.getPerfInfo(resIdx, dataFiles, threaded)
           elif app.name.lower() == ("smg2000"):
              dataFiles = [dataDir + "/" + execName + ".smg"]
              parsePurple.getPerfInfo(resIdx, dataFiles, threaded)
           elif app.name.lower() == ("amg2006"):
              dataFiles = [dataDir + "/" + execName + ".amg"]
              parsePurple.getPerfInfo(resIdx, dataFiles, threaded)
           elif app.name.lower() == ("umt2k"):
              dataFiles = [dataDir + "/" + execName + ".rtout"]
              parsePurple.getPerfInfo(resIdx, dataFiles, threaded)
           elif app.name.lower() == ("su3_rmd"):
              dataFiles = [dataDir + "/" + execName + ".su3_rmd"]
              parseMilc.getPerfInfo(resIdx, dataFiles, threaded)
           elif app.name.lower() == ("gtc"):
              dataFiles = [dataDir + "/" + execName + ".gtc"]
              parsePurple.getPerfInfo(resIdx, dataFiles, threaded)
           #elif app.name.lower() == ("nwchem-5.1"):
           #   dataFiles = [dataDir + "/" + execName + ".nwchem"]
           #   parsePurple.getPerfInfo(resIdx, dataFiles, threaded)
           else:
              print "WARNING: no performance data parser for application:%s" % app.name
       elif tool.upper() == "PARADYN":
           if not ptds:
               raise PTexception("parsePerf.getPerfInfo: expect to be already connected to the database, but am not.")

           toolParser.paradynParse(resIdx, execName,  dataDir,  ptds)             

       elif tool.upper() == "MPIP":
           files = glob(dataDir+"/*.mpiP")
           for f in files:
              toolParser.mpipParse(resIdx, f)

       elif tool.upper() == "SYSMPI":
           #files = glob(dataDir+"/*.sysmpi.*")
           #for f in files:
           toolParser.sysmpiParse(resIdx, dataDir, execName, ptds)

       elif tool.upper() == "PMAPI":
           raise PTexception("PMAPI data not supported through this execution "\
                      "path currently.")
           #(execution, resTypes) = toolParser.pmapiParse(dataFiles, build, \
                        #execution, resTypes)
       elif tool.upper() == "GPROF":
           if not ptds:
               raise PTexception("parsePerf.getPerfInfo: expect to be already connected to the database, but am not.")
           files = glob(dataDir+"/*.gprof*")
           for f in files:
               toolParser.gprofParse(resIdx, f, ptds)

       else:
           print "parsePerf:getPerfInfo: no application performance parser for \'%s\'" % tool

if __name__ == "__main__":
   sys.exit(main())
