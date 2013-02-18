#!/usr/bin/env python

# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information.

import sys
from PTds import PTdataStore

class PTdS_t4:

        def __init__(self, outFile):
                self.out = outFile

	def test4_1(self, testStore):
   	    """ Tests findFocusByName and findFocusByID, createFocus, findorCreateFocus
	
	    """
	    # NOTE: Currently does not test createFocus or findOrCreateFocus
	
	    no1 = " "
	    no2 = "/8/main.o/main"
	    
	    #testConnection = testStore.connectToDB(testStore.NO_DEBUG, dbname, dbpwd, dbfullname) # old Oracle
	    #testConnection = testStore.connectToDB(testStore.NO_DEBUG, dbhost, dbname, dbuser, dbpwd) # old Postgres
	    testConnection = testStore.connectToDB(testStore.NO_COMMIT)
	    # for now, can't continue with testing if no DB connection
	    if testConnection == False:
	        print "FAIL: test4: findResource:  unable to connect."
		self.out.write('Test 4.0 - FAIL - findResource unable to connect' + '\n')
	        return False
	    else:
	        #create some resources
	        focusId = 0 
	        reslist = []
	        reslist.append(testStore.createResource(14, 0, "execA", "execution"))
	        reslist.append(testStore.createResource(12, 0, "funcB", "environment/module/function"))
	        reslist.append(testStore.createResource(23, 0, "metricC", "metric"))
	        # create a focus 
	        try:
	            focusId = testStore.createFocus(reslist)
	            if (focusId == 0):
	                print "FAIL: createFocus: returned 0 with resource list:"
			self.out.write('Test 4.1 - FAIL - createFocus returned 0 with resource list.' + '\n')
	                print reslist
	                testStore.abortTransaction()
	                testStore.closeDB()
	                return False
	            else:
	                print "PASS: createFocus: returned %d with resource list:" % (focusId)
			self.out.write('Test 4.1 - PASS - createFocus returned %d with resource list.' + '\n')
	                print reslist
	        except:
	            print "EXCEPTION CAUGHT: createFocus: with resource list:"
		    self.out.write('EXCEPTION CAUGHT: createFocus with resource list.' + '\n')
	            print reslist
	            testStore.abortTransaction()
	            testStore.closeDB()
	            return False


	        # Then find the focus created by name and by id
	        fid = testStore.findFocusByID(reslist)
	        if fid == 0:
	            print "FAIL: findFocusByID: could not find focus with resource ids:"
		    self.out.write('Test 4.2 - FAIL - findFocusByID could not find focus with resource ids.' + '\n')
	            print reslist
	        else:
	            print "PASS: findFocusByID: found focus %d using resource list" % (fid)
		    self.out.write('Test 4.2 - PASS - findFocusByID found focus %d using resource list' + '\n')
	 

	        fid2 = testStore.findFocusByName("funcB,execA,metricC")
	        if fid2 == 0:
	            print "FAIL: findFocusByName: could not find focus with name: funcB,execA,metricC"
		    self.out.write('Test 4.3 - FAIL - findFocusByName could not find focus with name funcB,execA,metricC' + '\n')
	        else:
	            print "PASS: findFocusByName: found focus %d using focus name" % (fid2) 
		    self.out.write('Test 4.3 - PASS - findFocusByName found focus %d using focus name.\n')
	        if fid != fid2:
	            print "FAIL: IDs returned by findFocusByName and findFocusByID are different"
		    self.out.write('Test 4.4 - FAIL - IDs returned by findFocusByName and findFocusByID are different.\n')
	        else:
	            print "PASS: IDs returned by findFocusByName and findFocusByID are the same" 
		    self.out.write('Test 4.4 - PASS - IDs returned by findFocusByName and findFocusByID are the same.\n')
	
	        # Test findOrCreateFocus
	        fid3 = testStore.findOrCreateFocus(reslist)
	        if fid3 == fid:
	            print "PASS: findOrCreateFocus: found existing focus"
		    self.out.write('Test 4.5 - PASS - findOrCreateFocus found existing focus.\n')
	        elif fid3 == 0:
	            print "FAIL: findOrCreateFocus: returned 0 with resource list of existing focus"
		    self.out.write('Test 4.5 - FAIL - findOrCreateFocus returned 0 with a list of existing focus.\n')
	        else:
	            print "FAIL: findOrCreateFocus: returned incorrect focus id for existing focus"
		    self.out.write('Test 4.5 - FAIL - findOrCreateFocus returned incorrect focus id for existing focus.\n')
	        reslist2 = []
	        reslist2.append(testStore.createResource(14, 0, "execAA", "execution"))
	        reslist2.append(testStore.createResource(12, 0, "funcBB", "environment/module/function"))
	        reslist2.append(testStore.createResource(23, 0, "metricCC", "metric")) 
	        sql = "select MAX(id) from focus"
	        testStore.dbapi.execute(testStore.cursor, sql)
	        maxid, = testStore.dbapi.fetchone(testStore.cursor)
	        print "Max focus id before creating new focus is %d" % maxid
	        fid4 = testStore.findOrCreateFocus(reslist2)
	        if fid4 > maxid:
	            print "PASS: findOrCreateFocus: created new focus with resource list"
		    self.out.write('Test 4.6 - PASS - findOrCreateFocus created new focus with resource list.\n')
	        else:
	            print "FAIL: findOrCreateFocus: did not create new focus with resource list"
		    self.out.write('Test 4.6 - FAIL - findOrCreatefocus did not create new focus with resource list.\n')
	        
	
	        answer3 = testStore.findFocusByName(no1)
	        if answer3 == 0:
	            print "PASS: findFocusByName can't find no1"
		    self.out.write('Test 4.7 - PASS - findFocusByName can not find no1.\n')
	        else:
	            print "FAIL: findFocusByName returns " + str(answer3) + "for no1"
		    self.out.write('Test 4.7 - FAIL - findFocusByName returns ' + str(answer3) + ' for no1.\n')
	        answer4 = testStore.findFocusByName(no2)
	        if answer4 == 0:
	            print "PASS: findFocusByName can't find no2"
		    self.out.write('Test 4.8 - PASS - findFocusByName can not find no2.\n')
	        else:
	            print "FAIL: findFocusByName returns " + str(answer4) + "for no2"
		    self.out.write('Test 4.8 - FAIL - findFocusByName returns ' + str(answer4) + ' for no2.\n')
	
	        # better safe than...    
	        testStore.abortTransaction()
	        testStore.closeDB()        
