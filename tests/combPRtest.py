#!/usr/bin/env python

import os, sys
from PTds import PTdataStore
from Resource import Resource
from ResourceIndex import ResourceIndex
from PassFail import PassFail

def test1(ptds, pf):
    # test retrieval of simple performance results by context. 
    # retrieve ancestors and descendants
    # Assumes that there are executions with names: 
    # /irs-15 /irs-2 /irs-6 /sppm-2  in the database
    # the ptdfs for these are in /pperfdb/development/kathryn/perftrack/local_data/testData/smallBin/reference
    execs = [("irs-15","execution",1504),("irs-2","execution",1414),
             ("irs-6","execution",1454),("sppm-2","execution",66)]
    # yes ancestors, yes descendants, simple only
    for ex,t,pr_count in execs:
        reses = ptds.getPerfResultsByContext([(ex,t)], anc=True, desc=True, \
                     combined=False)
        if len(reses) != pr_count:
            pf.failed("for %s. Got %s, expected %s" %(ex,len(reses),pr_count))
        else:
            pf.passed()
        
        
def test2(ptds, pf):
    # test retrieval of simple performance results by context. 
    # retrieve ancestors, but not descendants
    # Assumes that there are executions with names: 
    # /irs-15 /irs-2 /irs-6 /sppm-2  in the database
    # the ptdfs for these are in /pperfdb/development/kathryn/perftrack/local_data/testData/smallBin/reference
    reses = [("irs-15","execution",794),("irs-2","execution",784),
             ("irs-6","execution",794),("sppm-2","execution",0),
             ("irs-15|Process-3","execution|process",829)]
    # yes ancestors, yes descendants, simple only
    for r,t,pr_count in reses:
        results = ptds.getPerfResultsByContext([(r,t)], anc=True, desc=False, \
                     combined=False)
        if len(results) != pr_count:
            pf.failed("For %s. Got %s, expected %s" % (r,len(results),pr_count))
                
        else:
            pf.passed()
        
    
def test3(ptds, pf):
    # test retrieval of simple performance results by context. 
    # retrieve descendants, but not ancestors 
    # Assumes that there are executions with names: 
    # /irs-15 /irs-2 /irs-6 /sppm-2  in the database
    # the ptdfs for these are in /pperfdb/development/kathryn/perftrack/local_data/testData/smallBin/reference
    reses = [("irs-15","execution",1504),("irs-2","execution",1414),
             ("irs-6","execution",1454),("sppm-2","execution",66)]
    # yes ancestors, yes descendants, simple only
    for r,t,pr_count in reses:
        results = ptds.getPerfResultsByContext([(r,t)], anc=False, desc=True, \
                     combined=False)
        if len(results) != pr_count:
            pf.failed("for %s. Got %s, expected %s" % (r,len(results),pr_count))
        else:
            pf.passed()

def test4(ptds, pf):
    # test retrieval of performance results by context specifying combined, 
    # when they are simple perf reses
    # retrieve ancestors and descendants
    # Assumes that there are executions with names: 
    # /irs-15 /irs-2 /irs-6 /sppm-2  in the database
    # the ptdfs for these are in /pperfdb/development/kathryn/perftrack/local_data/testData/smallBin/reference
    execs = [("irs-15","execution",0),("irs-2","execution",0),
             ("irs-6","execution",0),("sppm-2","execution",0)]
    # yes ancestors, yes descendants, combined only
    for ex,t,pr_count in execs:
        reses = ptds.getPerfResultsByContext([(ex,t)], anc=True, desc=True, \
                     combined=True)
        if len(reses) != pr_count:
            pf.failed("for %s. Got %s, expected %s" %(ex,len(reses),pr_count))
        else:
            pf.passed()
        
def test5(ptds, pf):
    # test retrieval of performance results by label 
    # when they are simple perf reses
    # retrieve ancestors and descendants
    # Assumes that there are executions with names: 
    # /irs-15 /irs-2 /irs-6 /sppm-2  in the database
    # the ptdfs for these are in /pperfdb/development/kathryn/perftrack/local_data/testData/smallBin/reference

    # our test data has no labels, so make some
    testLabel = "superExtraFancyLabel"
    rets = ptds.getPerfResultsByContext([("sppm-2","execution")],anc=True,desc=True,combined=False)
    for id,m,v,u,s,e,f,l,c in rets: 
       sql = "update performance_result set label='%s' where id='%s'" \
           % (testLabel,id)
       ptds.cursor.execute(sql)
    
    # yes ancestors, yes descendants, simple only
    pr_count = 66
    ex = 'sppm-2'
    reses = ptds.getPerfResultsByLabel(testLabel, combined=False)
    if len(reses) != pr_count:
        pf.failed("For %s Got %s, expected %s" %(ex,len(reses),pr_count))
    else:
        pf.passed()
 
def test6(ptds, pf):
    # test create combined context
    # retrieves several contexts from the db and creates a combined context
    # from them
    # Assumes that there are executions with names: 
    # /irs-15 /irs-2 /irs-6 /sppm-2  in the database
    # the ptdfs for these are in /pperfdb/development/kathryn/perftrack/local_data/testData/smallBin/reference
  
    # get information for one Process
    # the time step metrics are "TSTEP-HYD cpu time" and "TSTEP-HYD wall time"
    prs = ptds.getPerfResultsByContext([("sppm-2|Process-0","execution|process")],combined=False)
    #print prs
    ts_cpu = []
    ts_wall = []
    for p in prs: 
       id,met,val,units,st,et,fid,lab,comb = p
       if met == "TSTEP-HYD cpu time":
          ts_cpu.append(p)
       elif met == "TSTEP-HYD wall time":
          ts_wall.append(p)

    expectedContext = "sppm,build,mpiicc-8.0 Version 8.0,mpiifort-8.0 Version 8.0,env,sppm-2|Process-0,SingleMachineMCR|MCR,inputdeck,iq.h,Linux #1 SMP Mon Sep 27 13:51:13 PDT 2004 2.4.21-p4smp-71.3chaos,Linux #1 SMP Wed Sep 1 16:37:16 PDT 2004 2.4.21-p4smp-71chaos,fpp,m4,whole execution|10,whole execution|12,whole execution|14,whole execution|16,whole execution|18,whole execution|2,whole execution|20,whole execution|4,whole execution|6,whole execution|8"
    fids = [] 
    for id,met,val,units,st,et,fid,lab,comb in ts_cpu:
        fids.append(fid)
    newCntxt = ptds.createCombinedContext(fids)    
    if newCntxt == expectedContext:
        pf.passed()
    else:
        pf.failed("unexpected context for TSTEP-HYD cpu")

    fids = [] 
    for id,met,val,units,st,et,fid,lab,comb in ts_wall:
        fids.append(fid)
    newCntxt = ptds.createCombinedContext(fids)    
    if newCntxt == expectedContext:
        pf.passed()
    else:
        pf.failed("unexpected context for TSTEP-HYD wall time")

def test7(ptds, pf):
    # test create combined perf result 
    # retrieves several simple prs from the db and creates a combined pr  
    # from them
    # Assumes that there are executions with names: 
    # /irs-15 /irs-2 /irs-6 /sppm-2  in the database
    # the ptdfs for these are in /pperfdb/development/kathryn/perftrack/local_data/testData/smallBin/reference

    # get information for one Process
    # we'll take the results for each time step and average it
    # the time step metrics are "TSTEP-HYD cpu time" and "TSTEP-HYD wall time"
    prs = ptds.getPerfResultsByContext([("sppm-2|Process-0","execution|process")],combined=False)
    #print prs
    ts_cpu = []
    ts_wall = []
    for p in prs:
       id,met,val,units,st,et,fid,lab,comb = p
       if met == "TSTEP-HYD cpu time":
          ts_cpu.append(p)
       elif met == "TSTEP-HYD wall time":
          ts_wall.append(p)

    newLabel = "sppm-2"

    # average the values of TSTEP-HYD cpu time
    fids = []
    totVal = 0
    prIds = []
    for id,met,val,units,st,et,fid,lab,comb in ts_cpu:
        fids.append(fid)
        prIds.append(id)
        totVal += val
    if len(ts_cpu) == 0:
        pf.failed("TS CPU has no length")
        return

    newVal = totVal/len(ts_cpu)
    newCntxt = ptds.createCombinedContext(fids)
    ret = ptds.addResource("Average TSTEP-HYD cpu time", "metric")
    cprid = ptds.addCombinedPerfResult(newCntxt, "Average TSTEP-HYD cpu time", newVal, "seconds", "noValue", "noValue", prIds, label=newLabel)
    if cprid == 0:
        pf.failed("addCombinedPerfResult failed for Average TSTEP-HYD cpu time")
    cpr = ptds.getPerfResultsByLabel(newLabel, combined=True)
    if len(cpr) != 1:
        pf.failed("wrong number of results in db for label=%s for Average TSTEP-HYD cpu time" % newLabel)
    expectedContext = "sppm,build,mpiicc-8.0 Version 8.0,mpiifort-8.0 Version 8.0,env,sppm-2|Process-0,SingleMachineMCR|MCR,inputdeck,iq.h,Linux #1 SMP Mon Sep 27 13:51:13 PDT 2004 2.4.21-p4smp-71.3chaos,Linux #1 SMP Wed Sep 1 16:37:16 PDT 2004 2.4.21-p4smp-71chaos,fpp,m4,whole execution|10,whole execution|12,whole execution|14,whole execution|16,whole execution|18,whole execution|2,whole execution|20,whole execution|4,whole execution|6,whole execution|8"
    # extract the focus id from the combined perf res we made above
    id,met,val,units,st,et,fid,lab,comb = cpr[0]
    # check to see that there's a new focus for our new perf result
    fidFromDb = ptds.findFocusByName(expectedContext)
    if fidFromDb != fid:
        pf.failed("wrong context entered for Average TSTEP-HYD cpu time")
    ret = ptds.getCombinedPerfResultSourceData(cprid)
    if len(ret) != len(ts_cpu):
        pf.failed("wrong number of source data prs in db for Average TSTEP-HYD cpu time")
    else:
        pf.passed()


    # average the values of TSTEP-HYD wall time
    fids = []
    totVal = 0
    prIds = []
    for id,met,val,units,st,et,fid,lab,comb in ts_wall:
        fids.append(fid)
        prIds.append(id)
        totVal += val
    newVal = totVal/len(ts_cpu)
    newCntxt = ptds.createCombinedContext(fids)
    ret = ptds.addResource("Average TSTEP-HYD wall time", "metric")
    if ret == 0:
       pf.failed("adding metric 'Average TSTEP-HYD wall time' failed")
    cprid = ptds.addCombinedPerfResult(newCntxt, "Average TSTEP-HYD wall time", newVal, "seconds", "noValue", "noValue", prIds, label=newLabel)
    if cprid == 0:
        pf.failed("addCombinedPerfResult failed for Average TSTEP-HYD wall time")
    ret = ptds.getPerfResultsByLabel(newLabel, combined=True)
    if len(ret) != 2:
       pf.failed("wrong number of results in db for label=%s for Average TSTEP-HYD wall time" % newLabel)
    ret = ptds.getCombinedPerfResultSourceData(cprid)
    if len(ret) != len(ts_wall):
        pf.failed("wrong number of source data prs in db for Average TSTEP-HYD wall time")
    else:
        pf.passed()

    # now to test creating a combined res from combined reses
    # please note: this actual combination of averaging cpu and wall time
    # makes no sense - it's just a test case, people. 
    # get the combined reses we just made
    prs = ptds.getPerfResultsByLabel(newLabel, combined=True)
    fids = []
    totVal = 0
    prIds = []
    for id,met,val,units,st,et,fid,lab,comb in prs:
        fids.append(fid)
        prIds.append(id)
        totVal += val
    newVal = totVal/len(prs)
    newCntxt = ptds.createCombinedContext(fids)
    ret = ptds.addResource("Average of TSTEP-HYD wall and cpu time", "metric")
    if ret == 0:
       pf.failed("adding metric 'Average of TSTEP-HYD wall and cpu time' failed")
    cprid = ptds.addCombinedPerfResult(newCntxt, "Average of TSTEP-HYD wall and cpu time", newVal, "seconds", "noValue", "noValue", prIds, label=newLabel)
    if cprid == 0:
        pf.failed("addCombinedPerfResult failed for Average of TSTEP-HYD wall and cpu time")
    ret = ptds.getPerfResultsByLabel(newLabel, combined=True)
    if len(ret) != 3:
        pf.failed("wrong number of results in db for label=%s for Average of TSTEP-HYD wall  and cpu time" % newLabel)
    ret = ptds.getCombinedPerfResultSourceData(cprid)
    if len(ret) != len(prs):
        pf.failed("wrong number of source data prs in db for Average of TSTEP-HYD wall and cpu time")
    else:
        pf.passed()
   

def test8(ptds,pf):
    # test delete combined perf result 
    # retrieves combined prs from the db and tries to delete them
    # Assumes that test7 has been run already
    # Assumes that there are executions with names: 
    # /irs-15 /irs-2 /irs-6 /sppm-2  in the database
    # the ptdfs for these are in /pperfdb/development/kathryn/perftrack/local_data/testData/smallBin/reference
  
    newLabel = 'sppm-2'
    ret = ptds.getPerfResultsByLabel(newLabel, combined=True)
    if not ret:
       pf.failed("perhaps test7 wasn't run yet? the expected data is not in the database")
    numStarted = len(ret)
    numDeleted = 0
    idsNotDeleted = []
    for id,met,val,units,st,et,fid,lab,comb in ret:
        ret,list = ptds.deleteCombinedPerfResult(id)
        if ret == 1 and len(list) > 0:
            pf.failed("deleted comb perf rest with dependencies")
        elif ret == 1 and len(list) == 0:
           numDeleted += 1
        elif ret == 0 and len(list) > 0:
           # this is good, means pr that has dependency didn't get removed
           idsNotDeleted.append((id,fid))
        else:
           print "FAIL: unexpected return value from deleteCombinedPerfResult"
    ret = ptds.getPerfResultsByLabel(newLabel, combined=True)
    if len(ret) != (numStarted-numDeleted):
        pf.failed("retrieve unexpected number of prs after deletion.")
  
    # the list idsNotDeleted contains 2 combined perf reses that share a 
    # context (from test7). 
    #we'll delete one, and make sure the context is still there, and then
    # delete the other and make sure the context is gone
    expectedContext = "sppm,build,mpiicc-8.0 Version 8.0,mpiifort-8.0 Version 8.0,env,sppm-2|Process-0,SingleMachineMCR|MCR,inputdeck,iq.h,Linux #1 SMP Mon Sep 27 13:51:13 PDT 2004 2.4.21-p4smp-71.3chaos,Linux #1 SMP Wed Sep 1 16:37:16 PDT 2004 2.4.21-p4smp-71chaos,fpp,m4,whole execution|10,whole execution|12,whole execution|14,whole execution|16,whole execution|18,whole execution|2,whole execution|20,whole execution|4,whole execution|6,whole execution|8"
    if (len(idsNotDeleted) == 0):
        pf.failed("Missing idsNotDeleted")
        return

    id,fid = idsNotDeleted[0]
    ret,list = ptds.deleteCombinedPerfResult(id) 
    if ret!=0 and len(list) != 0:
        pf.failed("did not delete pr with no dependencies, #1")
    fidFromDB = ptds.findFocusByName(expectedContext)
    if fidFromDB != fid:
        pf.failed("expected to find context but it was gone")
    id,fid = idsNotDeleted[1]
    ret,list = ptds.deleteCombinedPerfResult(id) 
    if ret!=0 and len(list) != 0:
        pf.failed("did not delete pr with no dependencies, #2")
    fidFromDB = ptds.findFocusByName(expectedContext)
    if fidFromDB == fid:
        pf.failed("found context when it should be gone")
    else:
        pf.passed()

    
def main():

    ptds = PTdataStore()
    connected = ptds.connectToDB(False)
    if not connected:
       print "could not connect to DB"
       sys.exit(0)

    tests = [test1,test2,test3,test4,test5,test6,test7,test8]

    pf = PassFail()
    for test in tests: 
        test(ptds, pf)

    pf.test_info()
    return pf.failed_count > 0

if __name__ == "__main__":
   sys.exit(main())
