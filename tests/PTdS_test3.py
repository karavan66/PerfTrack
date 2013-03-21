#!/usr/bin/env python

# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information.

import sys
from PTds import PTdataStore

class PTdS_t3:

	def __init__(self, pf):
		self.pf = pf

	def test3_1(self, testStore):
	    """Tests getResourceId, getResourceName, getResourceType, getParentResource
	       Returns True if all tests pass, False if any fail
	
	       getResourceId -- deprecated - use findResourceByName or 
	                        findResourceByShortNameAndType 
	    """
	    parent_res_id = -1
	    childname = ""
	    childtype = ""
	    childparentid = None
	    parentname = ""
	    parenttype = ""
	    parentparentid = None
	    returnFlag = True
	    #testConnection = testStore.connectToDB(testStore.NO_COMMIT, dbname, dbpwd, dbfullname) # old Oracle
	    #testConnection = testStore.connectToDB(testStore.NO_COMMIT, dbhost, dbname, dbuser, dbpwd) #old Postgres
	    testConnection = testStore.connectToDB(testStore.NO_COMMIT) 
	    if testConnection == False:
	        self.pf.failed("test3: getResource: unable to connect.")
		self.pf.failed("Test 3.0 - getResource unable to connect" + '\n')
	        return False
	    else:
	        # add some data to db using PTdataStore methods (this will not be committed to db)
	        # createResource only adds resource if focus_frame_id is None
	        print "\n3.1: add a resource that does not have a parent id."
	        print "     Test createResource() with getResourceName, getResourceType,"
	        print "     and getParentResource"
	
	        noParentId = 0
	        noParentId = testStore.createResource(None, None, "test3A", "execution")
	        print "id of resource without a parent_id: " + str(noParentId)  
	        if (noParentId == None): 
	            self.pf.failed("createResource returned invalid resource_item id")
                    self.pf.failed("Test 3.1 - createResource retunred invalid resource_item id" + '\n')
	            returnFlag = False
	        else:
	            self.pf.passed("resource id returned from createResource: %d" % (noParentId))
	            self.pf.passed("Test 3.1 - Resource id returned from createResource: %d" + '\n')
	            #find resource just added
	            #use getResourceName, getResourceType
	            resourcename = testStore.getResourceName(noParentId)
	            print "name of resource: %s" % (resourcename)
	            if (resourcename != "test3A"):
	                self.pf.failed("getResourceName: name is not expected")
			self.pf.failed("Test 3.2 - getResourceName - Name is not expected" + '\n')
	                returnFlag = False
	            else:
	                self.pf.passed("getResourceName: name is expected" )
			self.pf.passed("Test 3.2 - getResourceName - Name is expected" + '\n')
	                parentname = resourcename
	                restype = testStore.getResourceType(noParentId)
	                print "type of resource: %s" % (restype)
	                if (restype != "execution"):
	                    self.pf.failed("getResourceType: type is not expected")
			    self.pf.failed("Test 3.3 - getResourceType - Type is not expected" + '\n')
	                    returnFlag = False
	                else:
	                    self.pf.passed("getResourceType: type is expected" )
			    self.pf.passed("Test 3.3 - getResourceType - Type is expected" + '\n')
	                    parenttype = restype
	                    parId = testStore.getParentResource (noParentId)
	                    print "parent_id of resource: " + str(parId)
	                    if (parId != None):
	                        self.pf.failed("getResourceParent: parent_id of resource without parent is not expected")
				self.pf.failed("Test 3.4 - getResourceParent - parent_id of resource without parent is not expected" + '\n')
	                        returnFlag = False
	                    else:
	                        self.pf.passed("getResourceParent: parent_id of resource without parent is expected")
				self.pf.passed("Test 3.4 - getResourceParent - parent_id of resource without parent is expected" + '\n')
	                        parentparentid = parId
	                        parent_res_id = testStore.findResourceByName (resourcename)
	                        if (parent_res_id != noParentId):
	                            self.pf.failed("findResourceByName did not return expected id of resource")
				    self.pf.failed("Test 3.5 - findResourceByName did not return expected id of resource" + '\n')
	                            print "      expected: %d" % (noParentId)
	                            print "      returned: " + str(parent_res_id)
	                            returnFlag = False
	                        else:
	                            self.pf.passed("findResourceByName returned correct id of resource")
				    self.pf.passed("Test 3.5 - findResourceByName returned correct id of resource" + '\n')

#	def test3_2(self, testStore): 
	        #Add a resource who is a child of a known parent
	        print "\n3.2: add a resource who is a child of known parent."
	        print "     Test createResource() with getResourceName, getResourceType,"
	        print "     and getParentResource"
	        if (parent_res_id == -1):    #create child of resource created above
	            self.pf.failed("problem with parent resource created earlier")
		    self.pf.failed("Test 3.6 - Problem with parent resource created earlier" + '\n')
	            returnFlag = False
	        else:
	            child1Id = testStore.createResource(None, parent_res_id, "test3A/test3A-child1", "execution/process")
	            if (child1Id != None and child1Id > 0):
	                print "child1Id returned from createResource: %d" % (child1Id)
	            else:
	                print "ERROR: test3: createResource returned invalid resource_item id"
			self.out.write('Test 3.6 - ERROR - createResource returned invalid resource_item id' + '\n')
	                testStore.abortTransaction()
	                testStore.closeDB()
	                return returnFlag
	            #find resource just added
	            #use getResourceName, getResourcType
	            cname = testStore.getResourceName(child1Id)
	            pname = testStore.getResourceName(parent_res_id)
	            print "name of child1Id: %s name of parent: %s" % (cname, pname)
	            if (cname != pname + "/test3A-child1"):
	                self.pf.failed("getResourceName: child name is not expected: %s" % cname)
			self.pf.failed("Test 3.7 - getResourceName - Child name is not expected" + '\n')
	                returnFlag = False
	            else:
	                self.pf.passed("getResourceName: child name is expected")
			self.pf.passed("Test 3.7 - getResourceName - Child name is expected" + '\n')
	                childname = cname
	                ctype = testStore.getResourceType(child1Id)
	                print "type of child1Id: %s" % (ctype)
	                if (ctype != "execution/process"):
	                    self.pf.failed("getResourceType: child type is not expected")
			    self.pf.failed("Test 3.8 - getResourceType - Child type is not expected" + '\n')
	                    returnFlag = False
	                else:
	                    self.pf.passed("getResourceType: child type is expected")
			    self.pf.passed("Test 3.8 - getResourceType - Child type is expected" + '\n')
	                    childtype = ctype
	                    cparId = testStore.getParentResource (child1Id)
	                    print "parent_id of child1Id: %d" % (cparId)
	                    if (cparId != parent_res_id):
	                        self.pf.failed("getParentResource: parent_id of child1Id is not expected")
				self.pf.failed("Test 3.9 - getParentResource - parent_id of child1Id is not expected" + '\n')
	                        returnFlag = False
	                    else:
	                        self.pf.passed("getParentResource: parent_id of child1Id is expected")
				self.pf.passed("Test 3.9 - getParentresource - parent_id of child1Id is expected" + '\n')
	                        childparentid = cparId
	                        res_id = testStore.findResourceByName (cname)
	                        if (res_id != child1Id):
	                            self.pf.failed("findResourceByName did not return expected id of child resource")
				    self.pf.failed("Test 3.10 - findResourceByName did not return expected id of child resource" + '\n')
	                            print "      expected: %d returned: %d" % (child1Id, res_id)
	                            returnFlag = False
	                        else:
	                            self.pf.passed("findResourceByName returned correct id of child resource")
				    self.pf.passed("Test 3.10 - findResourceByName returned correct id of child resource" + '\n')
	

#	def test3_3(self, testStore):	
	        # Test getResourceName, getResourceType, getParentResource with bad parameters.  Use
	        # resource ids of parent and child created above in some of tests
	        print "\n3.3: Test getResourceName, getResourceType, "
	        print "     getParentResource with bad parameters." 
	        # 9-1-05 -- getResourceId is deprecated; instead use findResourceByName or 
	        #           findResourceByShortNameAndType. These are tested in test2 
	        ## getResourceId -- bad type
	        #bad1 = testStore.getResourceId ("badtype", childname, childparentid) 
	        #if (bad1 != 0):
	        #    self.pf.failed("getResourceId: invalid type should cause failure")
	        #    returnFlag = False
	        #else:
	        #    self.pf.passed("getResourceId: invalid type caused failure")
	        ## getResourceId -- bad name 
	        #bad2 = testStore.getResourceId (childtype, "badname", childparentid)
	        #if (bad2 != 0):
	        #    self.pf.failed("getResourceId: invalid name should cause failure")
	        #    returnFlag = False
	        #else:
	        #    self.pf.passed("getResourceId: invalid name caused failure")
	        ## getResourceId -- bad parentid 
	        #bad3 = testStore.getResourceId (childtype, childname, 0)
	        #if (bad3 != 0):
	        #    self.pf.failed("getResourceId: invalid parent_id should cause failure")
	        #    returnFlag = False
	        #else:
	        #    self.pf.passed("getResourceId: invalid parent_id caused failure")
	
	
	        # getResourceName -- bad id 0 
	        bad4 = testStore.getResourceName (0)
	        if (bad4 != ""):
	            self.pf.failed("getResourceName: invalid id of 0 should cause failure")
		    self.pf.failed("Test 3.11 - getResourceName - Invalid id of 0 should cause failure" + '\n')
	            returnFlag = False
	        else:
	            self.pf.passed("getResourceName: invalid id of 0 caused failure")
		    self.pf.passed("Test 3.11 - getResourceName - Invalid id of 0 caused expected failure" + '\n')
	
	        # getResourceName -- bad id None 
	        bad5 = testStore.getResourceName (None)
	        if (bad5 != ""):
	            self.pf.failed("getResourceName: invalid id of None should return empty string")
		    self.pf.failed("Test 3.12 - getResourceName - Invalid id of None should return empty string" + '\n')
	            returnFlag = False
	        else:
	            self.pf.passed("getResourceName: invalid id of None returned empty string")
		    self.pf.passed("Test 3.12 - getResourceName - Invalid id of None returned expected empty string" + '\n')
	
	
	        # getResourceName -- Id does not exist in resource_item
	        sql = "select MAX(id) from resource_item"
	        #testStore.cursor.execute(sql)
	        testStore.dbapi.execute(testStore.cursor, sql) 
	        #maxid, = testStore.cursor.fetchone()
	        maxid, = testStore.dbapi.fetchone(testStore.cursor)
	        print "Max resource_item id is %d" % maxid

	        # getResourceType 
	        bad6 = testStore.getResourceType (0)
	        if (bad6 != ""):
	            self.pf.failed("getResourceType: invalid id of 0 should cause failure")
		    self.pf.failed("Test 3.14 - getResourceType - Invalid id of 0 should cause failure" + '\n')
	            returnFlag = False
	        else:
	            self.pf.passed("getResourceType: invalid id of 0 caused failure")
		    self.pf.passed("Test 3.14 - getResourceType - Invalid id of 0 caused expected failure" + '\n')
	
	        # getResourceType -- bad id None 
	        bad7 = testStore.getResourceType (None)
	        if (bad7 != ""):
	            self.pf.failed("getResourceType: invalid id of None should cause failure")
		    self.pf.failed("Test 3.15 - getResourceType - Invalid id of None should cause failure" + '\n')
	            returnFlag = False
	        else:
	            self.pf.passed("getResourceType: invalid id of None caused failure")
		    self.pf.passed("Test 3.15 - getResourceType - Invalid id of None caused expected failure" + '\n')
	
	        # getParentResource -- bad id 0
	        try:   
	            bad8 = testStore.getParentResource (0)
	            if (bad8 != None):
	                self.pf.failed("getParentResource: invalid childId of 0 should cause failure")
			self.pf.failed("Test 3.16 - getParentResource - Invalid childId of 0 should cause failure" + '\n')
	                returnFlag = False
	            else:
	                self.pf.passed("getParentResource: invalid childId of 0 caused failure")
			self.pf.passed("Test 3.16 - getParentResource - Invalid childId of 0 caused failure" + '\n')
	        except:
	            print "EXCEPTION CAUGHT: getParentResource: invalid childId of O raised an exception" 
		    self.out.write('EXCEPTION CAUGHT - get ParentResource - Invalid childId of 0 raised an exception' + '\n')
	        
	        # getParentResource -- bad id None 
	        try:
	            bad9 = testStore.getParentResource (None)
	            if (bad9 != None):
	                self.pf.failed("getParentResource: invalid childId of None should cause failure")
			self.pf.failed("Test 3.17 - getParentResource - Invalid childId of None should cause failure" + '\n')
	                returnFlag = False
	            else:
	                self.pf.passed("getParentResource: invalid childId of None caused failure")
			self.pf.passed("Test 3.17 - getParentResource - Invalid childId of None caused expected failure" + '\n')
	        except:
	            print "EXCEPTION CAUGHT: getParentResource: invalid childId of None raised an exception"
		    self.out.write('EXCEPTION CAUGHT - getParentReasource - Invalid childId of None raised an exception' + '\n')
	
	    	testStore.abortTransaction()
	    	testStore.closeDB()
	    	return returnFlag
