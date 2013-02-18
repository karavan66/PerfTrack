#!/usr/bin/env python

import os, sys
from PTds import PTdataStore
from Resource import Resource
from ResourceIndex import ResourceIndex



class PTdS_t8:

	def test1(self, ptds):
	    out = open('results', 'a')
	    # Falls under TEST 6
	    # test retrieval of simple performance results by context. 
	    # retrieve ancestors and descendants
	    # Assumes that there are executions with names: 
	    # /irs-15 /irs-2 /irs-6 /sppm-2  in the database
	    # the ptdfs for these are in /pperfdb/development/kathryn/perftrack/local_data/testData/smallBin/reference
	    execs = [("/irs-15","execution",1504),("/irs-2","execution",1414),
	             ("/irs-6","execution",1454),("/sppm-2","execution",66)]
	    # yes ancestors, yes descendants, simple only
	    for ex,t,pr_count in execs:
	        reses = ptds.getPerfResultsByContext([(ex,t)], anc=True, desc=True, \
				combined=False)
		print "%s" %(reses)
	        if len(reses) != pr_count:
	           print "FAIL: for %s. Got %s, expected %s" %(ex,len(reses),pr_count)
		   out.write('Test 8.1 - FAIL: for %s.  Got %s, expected %s.\n')
	        else:
	           print "PASS"
		   out.write('Test 8.1 - PASS\n')
	        
	        
	def test2(self, ptds):
	    out = open('results', 'a')

	    # Falls under TEST 6
	    # test retrieval of simple performance results by context. 
	    # retrieve ancestors, but not descendants
	    # Assumes that there are executions with names: 
	    # /irs-15 /irs-2 /irs-6 /sppm-2  in the database
	    # the ptdfs for these are in /pperfdb/development/kathryn/perftrack/local_data/testData/smallBin/reference
	    reses = [("/irs-15","execution",794),("/irs-2","execution",784),
	             ("/irs-6","execution",794),("/sppm-2","execution",0),
	             ("/irs-15/Process-3","execution/process",829)]
	    # yes ancestors, yes descendants, simple only
	    for r,t,pr_count in reses:
	        results = ptds.getPerfResultsByContext([(r,t)], anc=True, desc=False, \
	                     combined=False)
		print "%s" %(reses)
        	if len(results) != pr_count:
        	   print "FAIL: for %s. Got %s, expected %s" \
        	         % (r,len(results),pr_count)
		   out.write('Test 8.2 - FAIL: for %s.  Got %s, expected %s \n')
	        else:
	           print "PASS"
		   out.write('Test 8.2 -PASS\n')
	        
    
	def test3(self, ptds):
	    out = open('results', 'a')
	    # Falls under TEST 6
	    # test retrieval of simple performance results by context. 
	    # retrieve descendants, but not ancestors 
	    # Assumes that there are executions with names: 
	    # /irs-15 /irs-2 /irs-6 /sppm-2  in the database
	    # the ptdfs for these are in /pperfdb/development/kathryn/perftrack/local_data/testData/smallBin/reference
	    reses = [("/irs-15","execution",1504),("/irs-2","execution",1414),
	             ("/irs-6","execution",1454),("/sppm-2","execution",66)]
	    # yes ancestors, yes descendants, simple only
	    for r,t,pr_count in reses:
	        results = ptds.getPerfResultsByContext([(r,t)], anc=False, desc=True, \
	                     combined=False)
	        if len(results) != pr_count:
	           print "FAIL: for %s. Got %s, expected %s" \
	                 % (r,len(results),pr_count)
		   out.write('Test 8.3 - FAIL: For %s.  Got %s, expected %s.\n')
	        else:
	           print "PASS"
		   out.write('Test 8.3 - PASS.\n')
	
	def test4(self, ptds):
	    out = open('results', 'a')
	    # Falls under TEST 6
	    # test retrieval of performance results by context specifying combined, 
	    # when they are simple perf reses
	    # retrieve ancestors and descendants
	    # Assumes that there are executions with names: 
	    # /irs-15 /irs-2 /irs-6 /sppm-2  in the database
	    # the ptdfs for these are in /pperfdb/development/kathryn/perftrack/local_data/testData/smallBin/reference
	    execs = [("/irs-15","execution",0),("/irs-2","execution",0),
	             ("/irs-6","execution",0),("/sppm-2","execution",0)]
	    # yes ancestors, yes descendants, combined only
	    for ex,t,pr_count in execs:
	        reses = ptds.getPerfResultsByContext([(ex,t)], anc=True, desc=True, \
	                     combined=True)
	        if len(reses) != pr_count:
	           print "FAIL: for %s. Got %s, expected %s" %(ex,len(reses),pr_count)
		   out.write('Test 8.4 - FAIL: for %s.  Got %s, expected %s.\n')
	        else:
	           print "PASS"
		   out.write('Test 8.4 - PASS.\n')
	        
	def test5(self, ptds):
	    out = open('results', 'a')
	    # Falls under TEST 6
	    # test retrieval of performance results by label 
	    # when they are simple perf reses
	    # retrieve ancestors and descendants
	    # Assumes that there are executions with names: 
	    # /irs-15 /irs-2 /irs-6 /sppm-2  in the database
	    # the ptdfs for these are in /pperfdb/development/kathryn/perftrack/local_data/testData/smallBin/reference
	
	    # our test data has no labels, so make some
	    testLabel = "superExtraFancyLabel"
	    rets = ptds.getPerfResultsByContext([("/sppm-2","execution")],anc=True,desc=True,combined=False)
	    for id,m,v,u,s,e,f,l,c in rets: 
	       sql = "update performance_result set label='%s' where id='%s'" \
	           % (testLabel,id)
	       ptds.cursor.execute(sql)
	    
	    # yes ancestors, yes descendants, simple only
	    pr_count = 66
	    ex = '/sppm-2'
	    reses = ptds.getPerfResultsByLabel(testLabel, combined=False)
	    if len(reses) != pr_count:
	       	print "FAIL: for %s. Got %s, expected %s" %(ex,len(reses),pr_count)
		out.write('Test 8.5 - FAIL: for %s.  Got %s, expected %s.\n')
	    else:
	       print "PASS"
	       out.write('Test 8.5 - PASS.\n')
		 
	def test6(self, ptds):
	    out = open('results', 'a')
	    # Falls under TEST 4
	    # test create combined context
	    # retrieves several contexts from the db and creates a combined context
	    # from them
	    # Assumes that there are executions with names: 
	    # /irs-15 /irs-2 /irs-6 /sppm-2  in the database
	    # the ptdfs for these are in /pperfdb/development/kathryn/perftrack/local_data/testData/smallBin/reference
	  
	    # get information for one Process
	    # the time step metrics are "TSTEP-HYD cpu time" and "TSTEP-HYD wall time"
	    prs = ptds.getPerfResultsByContext([("/sppm-2/Process-0","execution/process")],combined=False)
	    #print prs
	    ts_cpu = []
	    ts_wall = []
	    for p in prs: 
	       id,met,val,units,st,et,fid,lab,comb = p
	       if met == "/TSTEP-HYD cpu time":
	          ts_cpu.append(p)
	       elif met == "/TSTEP-HYD wall time":
	          ts_wall.append(p)
	
	    expectedContext = "/sppm,/build,/mpiicc-8.0 Version 8.0,/mpiifort-8.0 Version 8.0,/env,/sppm-2/Process-0,/SingleMachineMCR/MCR,/inputdeck,/iq.h,/Linux #1 SMP Mon Sep 27 13:51:13 PDT 2004 2.4.21-p4smp-71.3chaos,/Linux #1 SMP Wed Sep 1 16:37:16 PDT 2004 2.4.21-p4smp-71chaos,/fpp,/m4,/whole execution/10,/whole execution/12,/whole execution/14,/whole execution/16,/whole execution/18,/whole execution/2,/whole execution/20,/whole execution/4,/whole execution/6,/whole execution/8"
	    fids = [] 
	    for id,met,val,units,st,et,fid,lab,comb in ts_cpu:
	        fids.append(fid)
	    newCntxt = ptds.createCombinedContext(fids)    
	    if newCntxt == expectedContext:
	       print "PASS"
	       out.write('Test 8.6 - PASS.\n')
	    else:
	       print "FAIL: unexpected context for TSTEP-HYD cpu time"
	       out.write('Test 8.6 - FAIL: Unexpected context for TSTEP-HYD cpu time.\n')
	    fids = [] 
	    for id,met,val,units,st,et,fid,lab,comb in ts_wall:
	        fids.append(fid)
	    newCntxt = ptds.createCombinedContext(fids)    
	    if newCntxt == expectedContext:
	       print "PASS"
	       out.write('Test 8.7 - PASS.\n')
	    else:
	       print "FAIL: unexpected context for TSTEP-HYD wall time"
	       out.write('Test 8.7 - FAIL: Unexpected context for TSET-HYD wall time.\n')
	
	def test7(self, ptds):
	    out = open('results', 'a')
	    # Falls under TEST 4
	    # test create combined perf result 
	    # retrieves several simple prs from the db and creates a combined pr  
	    # from them
	    # Assumes that there are executions with names: 
	    # /irs-15 /irs-2 /irs-6 /sppm-2  in the database
	    # the ptdfs for these are in /pperfdb/development/kathryn/perftrack/local_data/testData/smallBin/reference
	
	    # get information for one Process
	    # we'll take the results for each time step and average it
	    # the time step metrics are "TSTEP-HYD cpu time" and "TSTEP-HYD wall time"
	    prs = ptds.getPerfResultsByContext([("/sppm-2/Process-0","execution/process")],combined=False)
	    #print prs
	    ts_cpu = []
	    ts_wall = []
	    for p in prs:
	       id,met,val,units,st,et,fid,lab,comb = p
	       if met == "/TSTEP-HYD cpu time":
	          ts_cpu.append(p)
	       elif met == "/TSTEP-HYD wall time":
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
	    newVal = totVal/len(ts_cpu)
	    newCntxt = ptds.createCombinedContext(fids)
	    ret = ptds.addResource("/Average TSTEP-HYD cpu time", "metric")
	    if ret == 0:
	       print "FAIL: adding metric 'Average TSTEP-HYD cpu time' failed"
	       out.write('Test 8.8 - FAIL: Adding metric "average TSTEP=HYD cpu time" failed.\n')
	    cprid = ptds.addCombinedPerfResult(newCntxt, "/Average TSTEP-HYD cpu time", newVal, "seconds", "noValue", "noValue", prIds, label=newLabel)
	    if cprid == 0:
	       print "FAIL: addCombinedPerfResult failed for Average TSTEP-HYD cpu time"
	       out.write('Test 8.8 - FAIL: addCombinedPerfResult failed for Average TSTEP-HYD cpu time.\n')
	    cpr = ptds.getPerfResultsByLabel(newLabel, combined=True)
	    if len(cpr) != 1:
	       print "FAIL: wrong number of results in db for label=%s for Average TSTEP-HYD cpu time" % newLabel
	       out.write('Test 8.8 - FAIL: wrong number of results in db for label for average TSTEP-HYD cpu time.\n')
	    expectedContext = "/sppm,/build,/mpiicc-8.0 Version 8.0,/mpiifort-8.0 Version 8.0,/env,/sppm-2/Process-0,/SingleMachineMCR/MCR,/inputdeck,/iq.h,/Linux #1 SMP Mon Sep 27 13:51:13 PDT 2004 2.4.21-p4smp-71.3chaos,/Linux #1 SMP Wed Sep 1 16:37:16 PDT 2004 2.4.21-p4smp-71chaos,/fpp,/m4,/whole execution/10,/whole execution/12,/whole execution/14,/whole execution/16,/whole execution/18,/whole execution/2,/whole execution/20,/whole execution/4,/whole execution/6,/whole execution/8"
	    # extract the focus id from the combined perf res we made above
	    id,met,val,units,st,et,fid,lab,comb = cpr[0]
	    # check to see that there's a new focus for our new perf result
	    fidFromDb = ptds.findFocusByName(expectedContext)
	    if fidFromDb != fid:
	       print "FAIL: wrong context entered for Average TSTEP-HYD cpu time"
	       out.write('Test 8.8 - FAIL: Wrong context entered for Average TSTEP-HYD cpu time.\n')
	    ret = ptds.getCombinedPerfResultSourceData(cprid)
	    if len(ret) != len(ts_cpu):
	       print "FAIL: wrong number of source data prs in db for Average TSTEP-HYD cpu time" 
	       out.write('Test 8.8 - FAIL: Wrong number of source data prs in db for Average TSTEP-HYD cpu time.\n')
	    else:
	       print "PASS"
	       out.write('Test 8.8 - PASS.\n')
	
	
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
	    ret = ptds.addResource("/Average TSTEP-HYD wall time", "metric")
	    if ret == 0:
	       print "FAIL: adding metric 'Average TSTEP-HYD wall time' failed"
	       out.write('Test 8.9 - FAIL: adding metric "Average TSTEP-HYD wall time" failed.\n')
	    cprid = ptds.addCombinedPerfResult(newCntxt, "/Average TSTEP-HYD wall time", newVal, "seconds", "noValue", "noValue", prIds, label=newLabel)
	    if cprid == 0:
	      print "FAIL: addCombinedPerfResult failed for Average TSTEP-HYD wall time"
	      out.write('Test 8.9 - FAIL: addCombinedPerfResult failed for Average TSTEP-HYD wall time.\n')
	    ret = ptds.getPerfResultsByLabel(newLabel, combined=True)
	    if len(ret) != 2:
	       print "FAIL: wrong number of results in db for label=%s for Average TSTEP-HYD wall time" % newLabel
	       out.write('Test 8.9 - FAIL: Wrong number of results in db for label for average TSTEP-HYD wall time.\n')
	    ret = ptds.getCombinedPerfResultSourceData(cprid)
	    if len(ret) != len(ts_wall):
	       print "FAIL: wrong number of source data prs in db for Average TSTEP-HYD wall time" 
	       out.write('Test 8.9 - FAIL: Wrong number of source data prs in db for Average TSTEP-HYD wall time.\n')
	    else:
	       print "PASS"
	       out.write('Test 8.9 - PASS.\n')
	
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
	    ret = ptds.addResource("/Average of TSTEP-HYD wall and cpu time", "metric")
	    if ret == 0:
	       print "FAIL: adding metric 'Average of TSTEP-HYD wall and cpu time failed"
	       out.write('Test 8.10 - FAIL: Adding metric "Average of TSTEP-HYD" wall and cpu time failed.\n')
	    cprid = ptds.addCombinedPerfResult(newCntxt, "/Average of TSTEP-HYD wall and cpu time", newVal, "seconds", "noValue", "noValue", prIds, label=newLabel)
	    if cprid == 0:
	      print "FAIL: addCombinedPerfResult failed for Average of TSTEP-HYD wall and cpu time"
	      out.write('Test 8.10 - FAIL: addCombinedPerfResult failed for Average of TSTEP-HYD wall and cpu time.\n')
	    ret = ptds.getPerfResultsByLabel(newLabel, combined=True)
	    if len(ret) != 3:
	       print "FAIL: wrong number of results in db for label=%s for Average of TSTEP-HYD wall  and cpu time" % newLabel
	       out.write('Test 8.10 - FAIL: Wrong number of results in db for label for average of TSTEP-HYD wall and cpu time.\n')
	    ret = ptds.getCombinedPerfResultSourceData(cprid)
	    if len(ret) != len(prs):
	       print "FAIL: wrong number of source data prs in db for Average of TSTEP-HYD wall and cpu time" 
	       out.write('Test 8.10 - FAIL: Wrong number of source data prs in db for Average of TSTEP-Hyd wall and cpu time.\n')
	    else:
	       print "PASS"
	       out.write('Test 8.10 - PASS.\n')
  	 

	def test8(self, ptds):
	    out = open('results', 'a')
	    # Falls under TEST 4
	    # test delete combined perf result 
	    # retrieves combined prs from the db and tries to delete them
	    # Assumes that test7 has been run already
	    # Assumes that there are executions with names: 
	    # /irs-15 /irs-2 /irs-6 /sppm-2  in the database
	    # the ptdfs for these are in /pperfdb/development/kathryn/perftrack/local_data/testData/smallBin/reference
	  
	    newLabel = 'sppm-2'
	    ret = ptds.getPerfResultsByLabel(newLabel, combined=True)
	    if not ret:
	       print "FAIL: perhaps test7 wasn't run yet? the expected data is not in the database"
	       out.write('Test 8.11 - FAIL: Perhaps test7 was not run yet?  The expected tat is not in the database.\n')
	    numStarted = len(ret)
	    numDeleted = 0
	    idsNotDeleted = []
	    for id,met,val,units,st,et,fid,lab,comb in ret:
	        ret,list = ptds.deleteCombinedPerfResult(id)
	        if ret == 1 and len(list) > 0:
	           print "FAIL: deleted comb perf rest with dependencies"
		   out.write('Test 8.11 - FAIL: Deleted comb perf rest with dependencies.\n')
	        elif ret == 1 and len(list) == 0:
	           numDeleted += 1
	        elif ret == 0 and len(list) > 0:
	           # this is good, means pr that has dependency didn't get removed
	           idsNotDeleted.append((id,fid))
	        else:
	           print "FAIL: unexpected return value from deleteCombinedPerfResult"
		   out.write('Test 8.11 - FAIL: Unexpected return value from deleteCombPerfResult.\n')
	    ret = ptds.getPerfResultsByLabel(newLabel, combined=True)
	    if len(ret) != (numStarted-numDeleted):
	       print "FAIL: retrieve unexpected number of prs after deletion." 
	       out.write('Test 8.11 - FAIL: Retrieved unexpected number of prs after deletion.\n')
	  
	    # the list idsNotDeleted contains 2 combined perf reses that share a 
	    # context (from test7). 
	    #we'll delete one, and make sure the context is still there, and then
	    # delete the other and make sure the context is gone
	    expectedContext = "/sppm,/build,/mpiicc-8.0 Version 8.0,/mpiifort-8.0 Version 8.0,/env,/sppm-2/Process-0,/SingleMachineMCR/MCR,/inputdeck,/iq.h,/Linux #1 SMP Mon Sep 27 13:51:13 PDT 2004 2.4.21-p4smp-71.3chaos,/Linux #1 SMP Wed Sep 1 16:37:16 PDT 2004 2.4.21-p4smp-71chaos,/fpp,/m4,/whole execution/10,/whole execution/12,/whole execution/14,/whole execution/16,/whole execution/18,/whole execution/2,/whole execution/20,/whole execution/4,/whole execution/6,/whole execution/8"
	    id,fid = idsNotDeleted[0]
	    ret,list = ptds.deleteCombinedPerfResult(id) 
	    if ret!=0 and len(list) != 0:
	       print "FAIL: did not delete pr with no dependencies, #1"
	       out.write('Test 8.11 - FAIL: Did not delete pr with no dependencies, #1.\n')
	    fidFromDB = ptds.findFocusByName(expectedContext)
	    if fidFromDB != fid:
	       print "FAIL: expected to find context but it was gone"
	       out.write('Test 8.11 - FAIL: Expected to find context but it was gone.\n')
	    id,fid = idsNotDeleted[1]
	    ret,list = ptds.deleteCombinedPerfResult(id) 
	    if ret!=0 and len(list) != 0:
	       print "FAIL: did not delete pr with no dependencies, #2"
	       out.write('Test 8.11 - FAIL: Did not delete pr with no dependencies, #2.\n')
	    fidFromDB = ptds.findFocusByName(expectedContext)
	    if fidFromDB == fid:
	       print "FAIL: found context when it should be gone"
	       out.write('Test 8.11 - FAIL: found context when it should be gone.')
	    
	    else:
	       print "PASS"
	       out.write('Test 8.11 - PASS.\n')
	
		    
	def main():
	
	    ptds = PTdataStore()
	    connected = ptds.connectToDB(False)
	    if not connected:
	       print "could not connect to DB"
	       sys.exit(0)
	
	    tests = [test1,test2,test3,test4,test5,test6,test7,test8]
	
	    for test in tests: 
		        test(ptds)
		
	if __name__ == "__main__":
	   sys.exit(main())
