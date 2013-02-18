
# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information.

import sys
from PTds import PTdataStore

class PTdS_t5:

	def __init__(self, outFile):
	    self.out = outFile

	def test5_1(self, testStore):
	    """ Tests addResourceAttribute, lookupAttributes, lookupAttribute
	        Returns true if all tests pass; false if some fail
	        9-1-05 -- lookupAttribute, lookupAttributes deprecated
	    """
	    # 7-13-05: add testing for addResourceAttribute.  enterResourceAVs may be 
	    # deprecated at this time; it is not used by storePTDFdata.
	    # 9-1-05: enterResourceAVs is deprecated
	    # 9-4-05: TODO: need to rewrite most of test; for now comment out what is
	    #               deprecated
	    returnFlag = True
	    #testConnection = testStore.connectToDB(testStore.NO_DEBUG, dbname, dbpwd, dbfullname) #old Oracle
	    #testConnection = testStore.connectToDB(testStore.NO_COMMIT, dbhost, dbname, dbuser, dbpwd) #old PG
	    testConnection = testStore.connectToDB(testStore.NO_COMMIT)
	
	    # for now, can't continue with testing if no DB connection
	    if testConnection == False:
	        print "FAIL: test5:  unable to connect."
		self.out.write('Test 5.1 - FAIL - Unable to connect.\n')
	        return False
	    print "PASS: test5: able to connect."
	    self.out.write('Test 5.1 - PASS - Able to connect.\n')
	
	    #add resources to db, then enter attribute-value pairs in resource_attribute 
	    p1 = testStore.createResource (None, None, "ParentA", "ParentA-type")
	    p2 = testStore.createResource (None, None, "ParentB", "ParentB-type")
	    if (p1 == None or p2 == None):
	        print "ERROR: test5: unable to create resource(s) for test"
		self.out.write('Test 5 - ERROR - Unable to create resource(s) for test.\n')
	        returnFlag = False
	        testStore.abortTransaction()
	        testStore.closeDB()
	        return returnFlag
	    c1 = testStore.createResource (None, p1, "ChildA", "ChildA-type")
	    c2 = testStore.createResource (None, p1, "ChildB", "ChildB-type")
	    c3 = testStore.createResource (None, p1, "ChildC", "ChildC-type")
	    if (c1 == None or c2 == None or c3 == None): 
	        print "Error: test5: unable to create resource(s) for test"
		self.out.write('Test 5 - ERROR - Unable to create resource(s) for test.\n')
	        returnFlag = False
	        testStore.abortTransaction()
	        testStore.closeDB()
	        return returnFlag
	
	    # create some dictionaries
	    d1 = {"name": "name1", "value": "value1"}
	    d2 = {"name": "name2", "value": "value2"}
	    d3 = {"name": "name3", "value": "value3"}
	    d4 = {"name": "name4", "value": "value4"}
	    noValue = {"name": "nameWithNoValue"}
	    noName= {"value": "valueWithNoName"}
	    numbers = {"name": 1, "value": 2} 
	
	    # create attribute names, values, and types for entering with addResourceAttribute()
	    a5name = "name5"
	    a6name = "name6"
	    a7name = "name7"
	    a8name = "name8"
	    a5val  = "val5"
	    a6val  = "val6"
	    a7val  = "val7"
	    a8val  = "val8"
	    type   = "string"
	
	    d5 = {"name": "name5", "value": "val5"}
	    d6 = {"name": "name6", "value": "val6"}
	    d7 = {"name": "name7", "value": "val7"}
	    d8 = {"name": "name8", "value": "val8"}
	
	 
	    #test: enter valid resource_attribute entries using addResourceAttribute
	    print "5.2: Enter resource_attribute entries for valid resources using addResourceAttribute"
	
	    rv = 0
	    try:
	        rv = testStore.addResourceAttribute("ParentA", a5name, a5val, type)
	    except:
	        if not rv:
	            print "FAIL-EXCEPTION RAISED: addResourceAttribute: (ParentA, %s, %s, %s): ParentA is valid resource," %(a5name, a5val, type)
	            print "    but attribute not added"
		    self.out.write('Test 5.2 - FAIL - EXCEPTION RAISED - addResourceAttributes - ParentA is valid resource, but attribute not added.\n')
	        else:
	            print "PASS-EXCEPTION RAISED: addResourceAttribute: (ParentA, %s, %s, %s): ParentA is valid resource;" %(a5name, a5val, type)
	            print "    attribute added"
		    self.out.write('Test 5.2 - PASS - EXCEPTION RAISED - addResourceAttributes - ParentA is valid resource, attribute added.')
	    else:
	        if not rv:
	            print "FAIL: addResourceAttribute: (ParentA, %s, %s, %s): ParentA is valid resource," %(a5name, a5val, type)
	            print "    but attribute not added"
		    self.out.write('Test 5.2 - FAIL - addResourceAttribute - ParentA is valid resource, but attribute not added.')
	        else:
	            print "PASS: addResourceAttribute: (ParentA, %s, %s, %s): ParentA is valid resource;" %(a5name, a5val, type)
	            print "    attribute added"
		    self.out.write('Test 5.2 - PASS - addResourceAttribute - ParentA is valid resource, attribute added.\n')
	    rv = 0
	    try:
	        rv = testStore.addResourceAttribute("ParentA", a6name, a6val, type)
	    except:
	        if not rv:
	            print "FAIL-EXCEPTION RAISED: addResourceAttribute: (ParentA, %s, %s, %s): ParentA is valid resource," %(a6name, a6val, type) 
	            print "    but attribute not added"
		    self.out.write('Test 5.3 - FAIL - EXCEPTION RAISED - addResourceAttribute - ParentA is valid resource, but attribute not added.\n')
	        else:
	            print "PASS-EXCEPTION RAISED: addResource Attribute: (ParentA, %s, %s, %s): ParentA is valid resource;" %(a6name, a6val, type)
	            print "    attribute added"
		    self.out.write('Test 5.3 - PASS - EXCEPTION RAISED - addResourceAttribute - ParentA is valid resource; attribute added.\n')
	    else:
	        if not rv:
	            print "FAIL: addResourceAttribute: (ParentA, %s, %s, %s): ParentA is valid resource," %(a6name, a6val, type)
	            print "    but attribute not added"
		    self.out.write('Test 5.3 - FAIL - addResourceAttribute - ParentA is valid resource, but attribute not added.\n')
	        else:
       	     	    print "PASS: addResourceAttribute: (ParentA, %s, %s, %s): ParentA is valid resource;" %(a6name, a6val, type)
       	     	    print "    attribute added"
		    self.out.write('Test 5.3 - PASS - addResourceAttribute - ParentA is valid resource; attribute added.\n')
	
	    rv = 0
	    try:
	        rv = testStore.addResourceAttribute("ParentB", a7name, a7val, type)
	    except:
	        if not rv:
	            print "FAIL-EXCEPTION RAISED: addResourceAttribute: (ParentB , %s, %s, %s): ParentB is valid resource," %(a7name, a7val, type)  
	            print "    but attribute not added"
		    self.out.write('Test 5.4 - FAIL - EXCEPTION RAISED - addResourceAttribute - ParentB is valid resource, but attribute not added.\n')
	        else:
	            print "PASS-EXCEPTION RASISE: addResource Attribute: (ParentB, %s, %s, %s): ParentB is valid resource;" %(a7name, a7val, type)
	            print "    attribute added"
		    self.out.write('Test 5.4 - PASS - EXCEPTION RAISED  addResourceAttribute - ParentB is valid resource; attribute added.\n')
	    else:
	        if not rv:
	            print "FAIL: addResourceAttribute: (ParentB, %s, %s, %s): ParentB is valid resource," %(a7name, a7val, type)
	            print "    but attribute not added"
		    self.out.write('Test 5.4 - FAIL - addResourceAttribute - ParentB is valid resource, but attribute not added.\n')
	        else:
	            print "PASS: addResourceAttribute: (ParentB, %s, %s, %s): ParentB is valid resource;" %(a7name, a7val, type)
	            print "    attribute added"
		    self.out.write('Test 5.4 - PASS - addResourceAttribute - ParentB is valid resource; attribute added.\n')

	
	    ##test: lookup attributes created in above test with lookupAttribute()
	    #if not testStore.lookupAttribute (p1, a5name, a5val):
	    #    print "FAIL: lookupAttribute: valid (%s, %s) entered for resource %d" % (a5name, a5val, p1)
	    #    print "      not found"
	    #    returnFlag = False
	    #else:
	    #    print "PASS: lookupAttribute: found (%s, %s) entered for resource %d" % (a5name, a5val, p1)
	
	    #if not testStore.lookupAttribute (p1, a6name, a6val):
	    #    print "FAIL: lookupAttribute: valid (%s, %s) entered for resource %d" % (a6name, a6val, p1)
	    #    print "      not found"
	    #    returnFlag = False
	    #else:
	    #    print "PASS: lookupAttribute: found (%s, %s) entered for resource %d" % (a6name, a6val, p1)
	
	    #if not testStore.lookupAttribute (p2, a7name, a7val):
	    #    print "FAIL: lookupAttribute: valid (%s, %s) entered for resource %d" % (a7name, a7val, p2)
	    #    print "      not found"
	    #    returnFlag = False
	    #else:
	    #    print "PASS: lookupAttribute: found (%s, %s) entered for resource %d" % (a7name, a7val, p2)
	
	
	    ##test: lookup attributes created above with lookupAttributes()
	    #if not testStore.lookupAttributes (p1, [(d5["name"],d5["value"])]):
	    #    print "FAIL: lookupAttributes: valid (%s, %s) entered for resource %d" % (d5["name"], d5["value"], p1)
	    #    print "      not found"
	    #    returnFlag = False
	    #else:
	    #    print "PASS: lookupAttributes: found (%s, %s) entered for resource %d" % (d5["name"], d5["value"], p1)
	
	    #if not testStore.lookupAttributes (p1, [(d5["name"],d5["value"]),(d6["name"],d6["value"])]):
	    #    print "FAIL: lookupAttributes: valid (%s, %s), (%s, %s) list entered for resource %d" %  (d5["name"], d5["value"], d6["name"], d6["value"], p1)
	    #    print "      not found"
	    #    returnFlag = False
	    #else:
	    #    print "PASS: lookupAttributes: found (%s, %s), (%s, %s) entered for resource %d" % (d5["name"], d5["value"], d6["name"], d6["value"], p1)
	
	    #if not testStore.lookupAttributes (p1, [(a5name,a5val),(a6name,a6val)]):
	    #    print "FAIL: lookupAttributes: valid (%s, %s), (%s, %s) list entered for resource %d" % (a5name, a5val, a6name, a6val, p1)
	    #    print "      not found"
	    #    returnFlag = False
	    #else:
	    #    print "PASS: lookupAttributes: found (%s, %s), (%s,%s) entered for resource %d" % (a5name,a5val, a6name, a6val,p1)
	
	    #if not testStore.lookupAttributes (p2, [(d7["name"],d7["value"])]):
	    #    print "FAIL: lookupAttributes: valid (%s, %s) list entered for resource %d not found" % (d7["name"], d7["value"],p2)
	    #    returnFlag = False
	    #else:
	    #    print "PASS: lookupAttributes: found list (%s,%s) entered for resource %d" % (d7["name"], d7["value"], p2)
	
	
	    #test: enter some invalid resource_attibute (name,value) pairs for invalid resources
	    print "\n6.2: Test addResourceAttribute, lookupAttribute, lookupAttributes "
	    print "     Enter valid and invalid (attribute,value) pairs for invalid resources."
	    #sql = "select MAX(id) from resource_item"
	    ##testStore.cursor.execute(sql)
	    #testStore.dbapi.execute(testStore.cursor, sql)
	    ##maxid, = testStore.cursor.fetchone()
	    #maxid, = testStore.dbapi.fetchone (testStore.cursor)
	    #sql = "select MAX(resource_id) from resource_attribute"
	    ##testStore.cursor.execute(sql)
	    #testStore.dbapi.execute (testStore.cursor, sql)
	    ##maxresid, = testStore.cursor.fetchone()
	    #maxresid, = testStore.dbapi.fetchone (testStore.cursor) 
	    #print "Max resource_item id is %d" % (maxid)
	    #print "Max resource_attribute resource_id is %d" % (maxresid) 
	
	    #invalid resource ids
	    badName1 = "ThisIsANameThatDoesNotExist"
	    badName2 = "ThisNameDoesNotExistEither" 
	    rv = 0
	    try:
	        rv = testStore.addResourceAttribute(badName1, a5name, a5val, type)
	    except:
	        if not rv:
	            print "PASS-EXCEPTION RAISED: addResourceAttribute: resource does not exist; attribute not added"
		    self.out.write('Test 5.5 - PASS - EXCEPTION RAISED - addResourceAttribute - resource does not exist; attribute not added.\n')
	        else:
	            print "FAIL-EXCEPTION RAISED: addResourceAttribute: resource does not exist, but attribue was added"
		    self.out.write('Test 5.5 - FAIL - EXCEPTION RAISED - addResourceAttribute - resource does not exist, but attribute was added.\n')
	    else:
	        if not rv:
	            print "PASS: addResourceAttribute: resource does not exist; attribute not added"
		    self.out.write('Test 5.5 - PASS - addResourceAttribute - resource does not exist; attribute added.\n')
	        else:
	            print "FAIL: addResourceAttribute: resource does not exist, but attribue was added"
		    self.out.write('Test 5.5 - FAIL - addResourceAttribute - resource does not exist, but attribute was added.\n')
	        returnFlag = False 
	
	    ## test: lookupAttribute with invalid resource_id
	    #if testStore.lookupAttribute (maxid+300, d4["name"], d4["value"] ):
	    #    print "FAIL: lookupAttribute: invalid resource_id of %d should cause lookupAttribute to fail" % (maxid+300)
	    #    sql = "select count(*) from resource_attribute where resource_id = " + str(maxid+300)
	    #    print "    Execute following query: " + sql
	    #    #testStore.cursor.execute(sql)
	    #    testStore.dbapi.execute(testStore.cursor, sql)
	    #    #cnt, = testStore.cursor.fetchone()
	    #    cnt, = testStore.dbapi.fetchone(testStore.cursor)
	    #    if cnt != 0:
	    #       print "??HUH?? the query works & says count = " + str(cnt) + "! How can this be?"
	    #    else:
	    #       print "the query says count = " + str(cnt) 
	    #    returnFlag = False
	    #else:
	    #    print "PASS: lookupAttribute: invalid resource_id caused lookupAttribute to fail"
	
	    ##test: lookupAttribute with valid resource_item id that is not a resource_attribute resource_id
	    #rangelist = range(1,maxid+1)
	    #doesNotExist = 0
	    #for x in rangelist:
	    #    sql = "select count(*) from resource_attribute where resource_id = " + str(x)
	    #    #testStore.cursor.execute(sql)
	    #    testStore.dbapi.execute (testStore.cursor, sql)
	    #    #cnt, = testStore.cursor.fetchone()
	    #    cnt, = testStore.dbapi.fetchone(testStore.cursor)
	    #    if cnt == 0:
	    #        doesNotExist = x
	    #        break    
	    #if testStore.lookupAttribute (doesNotExist, d4["name"], d4["value"] ):
	    #    print "FAIL: lookupAttribute: resource_id %d does not exist in resource_attribute." % (doesNotExist)
	    #    print "      This should cause lookupAttribute to fail"
	    #    returnFlag = False
	    #else:
	    #    print "PASS: lookupAttribute: valid resource_item id %d which is an invalid" % (doesNotExist)
	    #    print "      resource_attribute resource_id caused lookupAttribute to fail"
	
	    ##test: lookup attribute with invalid name or value
	    #if testStore.lookupAttribute (p1, "Not a Name", "Not a Value"):
	    #    print "FAIL: (name,value) of (Not a Name, Not a Value) is not a valid"
	    #    print "      name,value pair and should cause lookupAttribute to fail"
	    #    returnFlag = False
		    #else:
	    #    print "PASS: (name,value) of (Not a Name, Not a Value) caused lookupAttribute to fail"
	    #if testStore.lookupAttribute (p1, "Not a Name", d1["value"]):
	    #    print "FAIL: (name,value) of (Not a Name, " + str(d1["value"]) + ") has invalid name"
	    #    print "      and should cause lookupAttribute to fail"
	    #    returnFlag = False
	    #else:
	    #    print "PASS: (name,value) of (Not a Name, " + str(d1["value"]) + ") caused lookupAttribute to fail"
	    #if testStore.lookupAttribute (p1, d1["name"], "Not a Value"):
	    #    print "FAIL: (name,value) of (" + str(d1["name"]) + ", Not a Value) has invalid value"
	    #    print "      and should cause lookupAttribute to fail"
	    #    returnFlag = False
	    #else:
	    #    print "PASS: (name,value) of (" + str(d1["name"]) + ", Not a Value) caused lookupAttribute to fail"
	
	    ##test: lookupAttributes with invalid resource_id
	    #if testStore.lookupAttributes (maxid+400, [(d1["name"],d1["value"])]):
	    #    print "FAIL: lookupAttributes: resource_id %d does not exist in resource_attribute" % (maxid+400)
	    #    print "      and should cause lookup attributes to fail"
	    #    returnFlag = False
	    #else:
	    #    print "PASS: lookupAttributes: resource_id %d does not exist in resource_attribute" % (maxid+400)
	    #    print "      and caused lookupAttributes to fail"
	    #if testStore.lookupAttributes (doesNotExist, [(d1["name"],d1["value"])]):   
	    #    print "FAIL: lookupAttributes: resource_id %d does not exist in resource_attribute." % (doesNotExist)
	    #    print "      This should cause lookupAttributes to fail"
	
	    #else:
	    #    print "PASS: lookupAttributes: valid resource_item id %d which is an invalid" % (doesNotExist)
	    #    print "      resource_attribute resource_id caused lookupAttributes to fail"
 

	    ##test: lookupAttributes with invalid (name,value) list

	    testStore.abortTransaction()
	    testStore.closeDB()
	    return returnFlag
