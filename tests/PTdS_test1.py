#!/usr/bin/env python

# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information.

import sys
from PTds import PTdataStore

class PTdS_t1:

	def __init__ (self, pf):
		self.pf = pf

	def test1 (self, testStore, dbh, dbn, dbu, dbp):
   	 """Tests connect and close
	
   	 return values:  0 = all connects fail
         	          1 = debug works, db fails
                          2 = debug fails, db works
                  	  3 = all connects work
  	  """
  	 testConnection = testStore.connectToDB(testStore.NO_COMMIT)
   	 if testConnection:
         	self.pf.passed("connectToDB passed using DB")
        	testStore.closeDB()
        	self.pf.passed("Test 1" + '\n')
	 else:
	        self.pf.failed("connectToDB failed using DB")
	        self.pf.failed("Test 1" + '\n')
	 testConnection = testStore.connectToDB(testStore.NO_COMMIT)
	 if testConnection:
	        print "connectToDB passed using debug"
	        testStore.closeDB()
	        self.pf.passed("Test 1 - Connected using debug" + '\n')
	 else:
	        self.pf.failed("connectToDB failed using debug")
	        self.pf.failed("Test 1 - Failed using debug" + '\n')
	
	def test1_2 (self, testStore):
	    """Tests connectToDB with only one arguments
	    """
	    ##out = open('results', 'a')
	    testConnection = testStore.connectToDB(testStore.NO_COMMIT)
	    if testConnection:
	        self.pf.passed("connectToDB passed using DB")
	        testStore.closeDB()
	        self.pf.passed("Test 1.2 - Connected using DB" + '\n')
	    else:
	        self.pf.failed("connectToDB failed using DB")
	        self.pf.failed("Test 1.2 - Failed to connect using DB" + '\n')

	def test1_3 (self, testStore):
	    """Tests connectToDB with five arguments, the last 4 are ignored
	    """
	    ##out = open('results', 'a')
	    testConnection = testStore.connectToDB(testStore.NO_COMMIT)
	    if testConnection:
	        self.pf.passed("connectToDB passed using DB")
	        testStore.closeDB()
	        self.pf.passed("Test 1.3 - Connected using DB" + '\n')
	    else:
	        self.pf.failed("connectToDB failed using DB")
	        self.pf.failed("Test 1.3 - Failed to connect using DB" + '\n')
		
