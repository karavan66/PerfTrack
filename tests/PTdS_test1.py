#!/usr/bin/env python

# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information.

import sys
from PTds import PTdataStore

class PTdS_t1:

	def __init__ (self, outFile):
		self.out = outFile

	def test1 (self, testStore, dbh, dbn, dbu, dbp):
   	 """Tests connect and close
	
   	 return values:  0 = all connects fail
         	          1 = debug works, db fails
                          2 = debug fails, db works
                  	  3 = all connects work
  	  """
  	 testConnection = testStore.connectToDB(testStore.NO_COMMIT)
   	 if testConnection:
         	print "PASS:  connectToDB passed using DB"
        	testStore.closeDB()
        	self.out.write('Test 1 - PASS' + '\n')
	 else:
	        print "FAIL:  connectToDB failed using DB"
	        self.out.write('Test 1 - FAIL' + '\n')
	 testConnection = testStore.connectToDB(testStore.NO_COMMIT)
	 if testConnection:
	        print "connectToDB passed using debug"
	        testStore.closeDB()
	        self.out.write('Test 1 - PASS - Connected using debug' + '\n')
	 else:
	        print "FAIL:  connectToDB failed using debug"
	        self.out.write('Test 1 - FAIL - Failed using debug' + '\n')
	
	def test1_2 (self, testStore):
	    """Tests connectToDB with only one arguments
	    """
	    ##out = open('results', 'a')
	    testConnection = testStore.connectToDB(testStore.NO_COMMIT)
	    if testConnection:
	        print "PASS:  connectToDB passed using DB"
	        testStore.closeDB()
	        self.out.write('Test 1.2 - PASS - Connected using DB' + '\n')
	    else:
	        print "FAIL:  connectToDB failed using DB"
	        self.out.write('Test 1.2 - FAIL - Failed to connect using DB' + '\n')

	def test1_3 (self, testStore):
	    """Tests connectToDB with five arguments, the last 4 are ignored
	    """
	    ##out = open('results', 'a')
	    testConnection = testStore.connectToDB(testStore.NO_COMMIT)
	    if testConnection:
	        print "PASS:  connectToDB passed using DB"
	        testStore.closeDB()
	        self.out.write('Test 1.3 - PASS - Connected using DB' + '\n')
	    else:
	        print "FAIL:  connectToDB failed using DB"
	        self.out.write('Test 1.3 - FAIL - Failed to connect using DB' + '\n')
		
