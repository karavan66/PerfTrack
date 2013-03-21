#!/usr/bin/env python

# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information.

import sys
from PTds import PTdataStore

class PTdS_t2:

        def __init__ (self, pf):
                self.pf = pf


	def test2_1(self, testStore):
    	 """Tests findOrCreateResource/createResource/findResource/findResourcebyShortNameAndType/
       	 findResourceByName

       	 NOTE -- 9-1-05:
       	 findOrCreateResource - deprecated
       	 findResource - deprecated
       
   	 returns True if all tests pass, False if some fail  
    	 """

    	 #testConnection = testStore.connectToDB(testStore.NO_COMMIT, dbhost, dbname, dbuser, dbpwd)
    	 #testConnection = testStore.connectToDB(testStore.NO_DEBUG, dbname, dbpwd, dbfullname)
    	 testConnection = testStore.connectToDB(testStore.NO_COMMIT)
    	 # for now, can't continue with testing if no DB connection
    	 if testConnection == False:
	         self.pf.failed("test2:  unable to connect.")
	 	 return False
		 self.pf.failed("Test 2.1 - unable to connect" + '\n')
    	 else:
         	improbableResource = testStore.findResourceByName("test1999")
         	if improbableResource != 0:
            	 print "improbableResource set to %d" % (improbableResource)
            	 self.pf.failed("improbableResource:  resource name test1999 in use")
	    	 self.pf.failed("Test 2.1 - Resource name in use" + '\n')
            	 return False
         	else:
            	 self.pf.passed("improbableResource not found")
            	 self.pf.passed("Test 2.1 - improbableResource not found" + '\n')
	
	def test2_2(self, testStore):
         improbableResource2 = testStore.findResourceByName("test2000")
         if improbableResource2 != 0:
               	 print "improbableResource2 set to %d" % (improbableResource2)
            	 self.pf.failed("improbableResource2: resource name test2000 in use")
	     	 self.pf.failed("Test 2.2 - Resource name in use" + '\n')
             	 return False
         else:
            	 self.pf.passed("improbableResource2 not found")
	     	 self.pf.passed("Test 2.2 - improbableResource2 not found" + '\n')

	def test2_3(self, testStore):
         newResID = 0
         newResID = testStore.createResource(14, 0, "testerA", "execution")
         print "createResource returns: %d" %(newResID)

         # 9-1-05 Deprecated -- use findResourceByName and createResource instead: 
         #newResID = testStore.findOrCreateResource(0, "execution", "testerB", "execution")
         #print "findOrCreateResource returns: %d" % newResID
         newResId = testStore.findResourceByName("testerB")
         if newResId == 0: # resource not found
             newResId = testStore.createResource(14, 0, "testerB", "execution")    
 
         # non-existent resource short name
         type = "grid|machine|partition|node"
         sname = "mcr999999"
         id = testStore.findResourceByShortNameAndType(type, sname)
         if id == None:
             self.pf.passed("looking for non-existent short name")
 	     self.pf.passed("Test 2.3 - Looking for non-existant short name" + '\n')
         elif id == -1:
             self.pf.failed("found multiple entries for non-existent resource")
 	     self.pf.failed("Test 2.3 - Found multipe entries for non-existant resource" + '\n')
         else:
             self.pf.failed("looking for non-existent short name. Got " + str(id))
             self.pf.failed("Test 2.3 - Looking for non-existant short name.  Got " + str(id) + '\n')

	def test2_4(self, testStore): 
         # existing resource shortname that could partially overlap another name
         # mcr9 is contained in mcr99
         type = "grid|machine|partition|node"
         sname = "mcr9"
         id = testStore.findResourceByShortNameAndType(type, sname)
         if id == None:
             self.pf.failed("did not find existing resource " + sname)
	     self.pf.failed("Test 2.4 - Did not find existing resource " + sname + '\n')
         elif id == -1:
             self.pf.failed("found multiple entries for existing resource " + sname)
 	     self.pf.failed("Test 2.4 - Found multiple entries for existing resource " + sname + '\n')
         else:
             self.pf.passed("found one id for existing resource " + sname)
 	     self.pf.passed("Test 2.4 - Found one ID for existing resource " + sname + '\n')
 
	def test2_5(self, testStore):
         # non-existent type name
         type = "grid|machine|partition|mode"
         sname = "mcr9"
         id = testStore.findResourceByShortNameAndType(type, sname)
         if id == None:
             self.pf.passed("looking for non-existent type name")
 	     self.pf.passed("Test 2.5 - Looking for non-existant type name" + '\n')
         elif id == -1:
             self.pf.failed("found multiple entries for non-existent type")
             self.pf.failed("Test 2.5 - Found multiple entries for non-existant type" + '\n')
         else:
             self.pf.failed("looking for non-existent type name. Got " + str(id))
 	     self.pf.failed("Test 2.5 - Looking for non-existant type name.  Got " + str(id) + '\n')
 
	def test2_6(self, testStore):
         # missing type argument
         type = None
         sname = "mcr9"
         id = testStore.findResourceByShortNameAndType(type, sname)
         if id == None:
            self.pf.passed("looking for None type name")
 	    self.pf.passed("Test 2.6 - Looking for None type name" + '\n')
         elif id == -1:
             self.pf.failed("found multiple entries for None type name")
  	     self.pf.failed("Test 2.6 - Found multiple entries for None type name" + '\n')
         else:
             self.pf.failed("looking for None type name. Got " + str(id))
 	     self.pf.failed("Test 2.6 - Looking for None type name.  Got " + str(id) + '\n')
 
	def test2_7(self, testStore):
         # missing sname argument
         type = "grid|machine|partition|mode"
         sname = None
         id = testStore.findResourceByShortNameAndType(type, sname)
         if id == None:
             self.pf.passed("looking for None short name")
 	     self.pf.passed("Test 2.7 - Looking for None short name" + '\n')
         elif id == -1:
             self.pf.failed("found multiple entries for None short name ")
 	     self.pf.failed("Test 2.7 - Found multiple entries for None short name" + '\n')
         else:
             self.pf.failed("looking for None short name. Got " + str(id))
 	     self.pf.failed("Test 2 - Looking for None short name.  Got " + str(id) + '\n')
         #better safe than...
         testStore.abortTransaction()
