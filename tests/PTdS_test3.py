#!/usr/bin/env python

# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information.

import sys
from PTds import PTdataStore

class PTdS_t3:

	def __init__(self, outFile):
		self.out = outFile

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
	        print "FAIL: test3: getResource: unable to connect."
		self.out.write('Test 3.0 - FAIL - getResource unable to connect' + '\n')
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
	            print "FAIL: createResource returned invalid resource_item id"
                    self.out.write('Test 3.1 - FAIL - createResource retunred invalid resource_item id' + '\n')
	            returnFlag = False
	        else:
	            print "PASS: resource id returned from createResource: %d" % (noParentId)
	            self.out.write('Test 3.1 - PASS - Resource id returned from createResource: %d' + '\n')
	            #find resource just added
	            #use getResourceName, getResourceType
	            resourcename = testStore.getResourceName(noParentId)
	            print "name of resource: %s" % (resourcename)
	            if (resourcename != "test3A"):
	                print "FAIL: getResourceName: name is not expected"
			self.out.write('Test 3.2 - FAIL - getResourceName - Name is not expected' + '\n')
	                returnFlag = False
	            else:
	                print "PASS: getResourceName: name is expected" 
			self.out.write('Test 3.2 - PASS - getResourceName - Name is expected' + '\n')
	                parentname = resourcename
	                restype = testStore.getResourceType(noParentId)
	                print "type of resource: %s" % (restype)
	                if (restype != "execution"):
	                    print "FAIL: getResourceType: type is not expected"
			    self.out.write('Test 3.3 - FAIL - getResourceType - Type is not expected' + '\n')
	                    returnFlag = False
	                else:
	                    print "PASS: getResourceType: type is expected" 
			    self.out.write('Test 3.3 - PASS - getResourceType - Type is expected' + '\n')
	                    parenttype = restype
	                    parId = testStore.getParentResource (noParentId)
	                    print "parent_id of resource: " + str(parId)
	                    if (parId != None):
	                        print "FAIL: getResourceParent: parent_id of resource without parent is not expected"
				self.out.write('Test 3.4 - FAIL - getResourceParent - parent_id of resource without parent is not expected' + '\n')
	                        returnFlag = False
	                    else:
	                        print "PASS: getResourceParent: parent_id of resource without parent is expected"
				self.out.write('Test 3.4 - PASS - getResourceParent - parent_id of resource without parent is expected' + '\n')
	                        parentparentid = parId
	                        parent_res_id = testStore.findResourceByName (resourcename)
	                        if (parent_res_id != noParentId):
	                            print "FAIL: findResourceByName did not return expected id of resource"
				    self.out.write('Test 3.5 - FAIL - findResourceByName did not return expected id of resource' + '\n')
	                            print "      expected: %d" % (noParentId)
	                            print "      returned: " + str(parent_res_id)
	                            returnFlag = False
	                        else:
	                            print "PASS: findResourceByName returned correct id of resource"
				    self.out.write('Test 3.5 - PASS - findResourceByName returned correct id of resource' + '\n')

#	def test3_2(self, testStore): 
	        #Add a resource who is a child of a known parent
	        print "\n3.2: add a resource who is a child of known parent."
	        print "     Test createResource() with getResourceName, getResourceType,"
	        print "     and getParentResource"
	        if (parent_res_id == -1):    #create child of resource created above
	            print "FAIL: problem with parent resource created earlier"
		    self.out.write('Test 3.6 - FAIL - Problem with parent resource created earlier' + '\n')
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
	                print "FAIL: getResourceName: child name is not expected: %s" % cname
			self.out.write('Test 3.7 - FAIL - getResourceName - Child name is not expected' + '\n')
	                returnFlag = False
	            else:
	                print "PASS: getResourceName: child name is expected"
			self.out.write('Test 3.7 - PASS - getResourceName - Child name is expected' + '\n')
	                childname = cname
	                ctype = testStore.getResourceType(child1Id)
	                print "type of child1Id: %s" % (ctype)
	                if (ctype != "execution/process"):
	                    print "FAIL: getResourceType: child type is not expected"
			    self.out.write('Test 3.8 - FAIL - getResourceType - Child type is not expected' + '\n')
	                    returnFlag = False
	                else:
	                    print "PASS: getResourceType: child type is expected"
			    self.out.write('Test 3.8 - PASS - getResourceType - Child type is expected' + '\n')
	                    childtype = ctype
	                    cparId = testStore.getParentResource (child1Id)
	                    print "parent_id of child1Id: %d" % (cparId)
	                    if (cparId != parent_res_id):
	                        print "FAIL: getParentResource: parent_id of child1Id is not expected"
				self.out.write('Test 3.9 - FAIL - getParentResource - parent_id of child1Id is not expected' + '\n')
	                        returnFlag = False
	                    else:
	                        print "PASS: getParentResource: parent_id of child1Id is expected"
				self.out.write('Test 3.9 - PASS - getParentresource - parent_id of child1Id is expected' + '\n')
	                        childparentid = cparId
	                        res_id = testStore.findResourceByName (cname)
	                        if (res_id != child1Id):
	                            print "FAIL: findResourceByName did not return expected id of child resource"
				    self.out.write('Test 3.10 - FAIL - findResourceByName did not return expected id of child resource' + '\n')
	                            print "      expected: %d returned: %d" % (child1Id, res_id)
	                            returnFlag = False
	                        else:
	                            print "PASS: findResourceByName returned correct id of child resource"
				    self.out.write('Test 3.10 - PASS - findResourceByName returned correct id of child resource' + '\n')
	

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
	        #    print "FAIL: getResourceId: invalid type should cause failure"
	        #    returnFlag = False
	        #else:
	        #    print "PASS: getResourceId: invalid type caused failure"
	        ## getResourceId -- bad name 
	        #bad2 = testStore.getResourceId (childtype, "badname", childparentid)
	        #if (bad2 != 0):
	        #    print "FAIL: getResourceId: invalid name should cause failure"
	        #    returnFlag = False
	        #else:
	        #    print "PASS: getResourceId: invalid name caused failure"
	        ## getResourceId -- bad parentid 
	        #bad3 = testStore.getResourceId (childtype, childname, 0)
	        #if (bad3 != 0):
	        #    print "FAIL: getResourceId: invalid parent_id should cause failure"
	        #    returnFlag = False
	        #else:
	        #    print "PASS: getResourceId: invalid parent_id caused failure"
	
	
	        # getResourceName -- bad id 0 
	        bad4 = testStore.getResourceName (0)
	        if (bad4 != ""):
	            print "FAIL: getResourceName: invalid id of 0 should cause failure"
		    self.out.write('Test 3.11 - FAIL - getResourceName - Invalid id of 0 should cause failure' + '\n')
	            returnFlag = False
	        else:
	            print "PASS: getResourceName: invalid id of 0 caused failure"
		    self.out.write('Test 3.11 - PASS - getResourceName - Invalid id of 0 caused expected failure' + '\n')
	
	        # getResourceName -- bad id None 
	        bad5 = testStore.getResourceName (None)
	        if (bad5 != ""):
	            print "FAIL: getResourceName: invalid id of None should return empty string"
		    self.out.write('Test 3.12 - FAIL - getResourceName - Invalid id of None should return empty string' + '\n')
	            returnFlag = False
	        else:
	            print "PASS: getResourceName: invalid id of None returned empty string"
		    self.out.write('Test 3.12 - PASS - getResourceName - Invalid id of None returned expected empty string' + '\n')
	
	
	        # getResourceName -- Id does not exist in resource_item
	        sql = "select MAX(id) from resource_item"
	        #testStore.cursor.execute(sql)
	        testStore.dbapi.execute(testStore.cursor, sql) 
	        #maxid, = testStore.cursor.fetchone()
	        maxid, = testStore.dbapi.fetchone(testStore.cursor)
	        print "Max resource_item id is %d" % maxid
	
	        try: 
	            bad10 = testStore.getResourceName (maxid + 100)
	            if (bad10 != ""):
	                print "FAIL: getResourceName: id %d does not exist; should cause exception" %(maxid+100)
			self.out.write('Test 3.13 - FAIL - getResourceName - id does not exist; should cause exception' + '\n')
	                returnFlag = False
	            else:
	                print "FAIL: getResourceName: id %d does not exist; should cause exception," %(maxid+100)
	                print "      but the empty string was returned"
			self.out.write('Test 3.13 - FAIL - getResourceName - id does not exist; should cause exception, but the empty string was returned' + '\n')
	        except:
	            print "PASS: EXCEPTION CAUGHT: getResourceName: id %d does not exist" %(maxid+100) 
		    self.out.write('Test 3.13 - PASS - Exception caught, id does not exist' + '\n')
	
	        # getResourceType 
	        bad6 = testStore.getResourceType (0)
	        if (bad6 != ""):
	            print "FAIL: getResourceType: invalid id of 0 should cause failure"
		    self.out.write('Test 3.14 - FAIL - getResourceType - Invalid id of 0 should cause failure' + '\n')
	            returnFlag = False
	        else:
	            print "PASS: getResourceType: invalid id of 0 caused failure"
		    self.out.write('Test 3.14 - PASS - getResourceType - Invalid id of 0 caused expected failure' + '\n')
	
	        # getResourceType -- bad id None 
	        bad7 = testStore.getResourceType (None)
	        if (bad7 != ""):
	            print "FAIL: getResourceType: invalid id of None should cause failure"
		    self.out.write('Test 3.15 - FAIL - getResourceType - Invalid id of None should cause failure' + '\n')
	            returnFlag = False
	        else:
	            print "PASS: getResourceType: invalid id of None caused failure"
		    self.out.write('Test 3.15 - PASS - getResourceType - Invalid id of None caused expected failure' + '\n')
	
	        # getParentResource -- bad id 0
	        try:   
	            bad8 = testStore.getParentResource (0)
	            if (bad8 != None):
	                print "FAIL: getParentResource: invalid childId of 0 should cause failure"
			self.out.write('Test 3.16 - FAIL - getParentResource - Invalid childId of 0 should cause failure' + '\n')
	                returnFlag = False
	            else:
	                print "PASS: getParentResource: invalid childId of 0 caused failure"
			self.out.write('Test 3.16 - PASS - getParentResource - Invalid childId of 0 caused failure' + '\n')
	        except:
	            print "EXCEPTION CAUGHT: getParentResource: invalid childId of O raised an exception" 
		    self.out.write('EXCEPTION CAUGHT - get ParentResource - Invalid childId of 0 raised an exception' + '\n')
	        
	        # getParentResource -- bad id None 
	        try:
	            bad9 = testStore.getParentResource (None)
	            if (bad9 != None):
	                print "FAIL: getParentResource: invalid childId of None should cause failure"
			self.out.write('Test 3.17 - FAIL - getParentResource - Invalid childId of None should cause failure' + '\n')
	                returnFlag = False
	            else:
	                print "PASS: getParentResource: invalid childId of None caused failure"
			self.out.write('Test 3.17 - PASS - getParentResource - Invalid childId of None caused expected failure' + '\n')
	        except:
	            print "EXCEPTION CAUGHT: getParentResource: invalid childId of None raised an exception"
		    self.out.write('EXCEPTION CAUGHT - getParentReasource - Invalid childId of None raised an exception' + '\n')
	
	    	testStore.abortTransaction()
	    	testStore.closeDB()
	    	return returnFlag
