#!/usr/bin/env python

# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information.

import sys
from PTds import PTdataStore
#from getpass import getpass

# connect/close
#def test1 (testStore, dbh, dbn, dbu, dbp):
#    """Tests connect and close
#
#    return values:  0 = all connects fail
#                    1 = debug works, db fails
#                    2 = debug fails, db works
#                    3 = all connects work
#    """
#    testConnection = testStore.connectToDB(testStore.NO_WRITE, dbh, dbn, dbu, dbp)
#    if testConnection:
#        print "PASS:  connectToDB passed using DB"
#        testStore.closeDB()
#    else:
#        print "FAIL:  connectToDB failed using DB"
    #testConnection = testStore.connectToDB(testStore.NO_WRITE, "", "", "", "")
    #if testConnection:
    #    print "connectToDB passed using debug"
    #    testStore.closeDB()
    #else:
    #    print "FAIL:  connectToDB failed using debug"

def test1_2 (testStore):
    """Tests connectToDB with only one arguments
    """
    testConnection = testStore.connectToDB(testStore.NO_WRITE)
    if testConnection:
        print "PASS:  connectToDB passed using DB"
        testStore.closeDB()
    else:
        print "FAIL:  connectToDB failed using DB"

def test1_3 (testStore):
    """Tests connectToDB with five arguments, the last 4 are ignored 
    """
    testConnection = testStore.connectToDB(testStore.NO_WRITE, "blah", "blah", 
                                           "blah", "blah")
    if testConnection:
        print "PASS:  connectToDB passed using DB"
        testStore.closeDB()
    else:
        print "FAIL:  connectToDB failed using DB"

def test2(testStore):
    """Tests findOrCreateResource/createResource/findResource/findResourcebyShortNameAndType/
       findResourceByName

       NOTE -- 9-1-05:
       findOrCreateResource - deprecated
       findResource - deprecated
       
    returns True if all tests pass, False if some fail  
    """

    #testConnection = testStore.connectToDB(testStore.NO_COMMIT, dbhost, dbname, dbuser, dbpwd)
    #testConnection = testStore.connectToDB(testStore.NO_WRITE, dbname, dbpwd, dbfullname)
    testConnection = testStore.connectToDB(testStore.NO_COMMIT)
    # for now, can't continue with testing if no DB connection
    if testConnection == False:
        print "FAIL: test2:  unable to connect."
        return False
    else:
        improbableResource = testStore.findResourceByName("test1999")
        if improbableResource != 0:
            print "improbableResource set to %d" % (improbableResource)
            print "FAIL:  improbableResource:  resource name test1999 in use"
            return False
        else:
            print "PASS:  improbableResource not found"
            
        improbableResource2 = testStore.findResourceByName("test2000")
        if improbableResource2 != 0:
            print "improbableResource2 set to %d" % (improbableResource2)
            print "FAIL:  improbableResource2: resource name test2000 in use"
            return False
        else:
            print "PASS: improbableResource2 not found"

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
        type = "grid/machine/partition/node"
        sname = "mcr999999"
        id = testStore.findResourceByShortNameAndType(type, sname)
        if id == None:
            print "PASS: looking for non-existent short name"
        elif id == -1:
            print "FAIL: found multiple entries for non-existent resource"
        else:
            print "FAIL: looking for non-existent short name. Got " + str(id)

        # existing resource shortname that could partially overlap another name
        # mcr9 is contained in mcr99
        type = "grid/machine/partition/node"
        sname = "mcr9"
        type = "grid|machine|node"
        sname = "jaccn115"
        id = testStore.findResourceByShortNameAndType(type, sname)
        if id == None:
            print "FAIL: did not find existing resource " + sname
        elif id == -1:
            print "FAIL: found multiple entries for existing resource " + sname
        else:
            print "PASS: found one id for existing resource " + sname

        # non-existent type name
        type = "grid/machine/partition/mode"
        sname = "mcr9"
        id = testStore.findResourceByShortNameAndType(type, sname)
        if id == None:
            print "PASS: looking for non-existent type name"
        elif id == -1:
            print "FAIL: found multiple entries for non-existent type"
        else:
            print "FAIL: looking for non-existent type name. Got " + str(id)

        # missing type argument
        type = None
        sname = "mcr9"
        id = testStore.findResourceByShortNameAndType(type, sname)
        if id == None:
            print "PASS: looking for None type name"
        elif id == -1:
            print "FAIL: found multiple entries for None type name "
        else:
            print "FAIL: looking for None type name. Got " + str(id)

        # missing sname argument
        type = "grid/machine/partition/mode"
        sname = None
        id = testStore.findResourceByShortNameAndType(type, sname)
        if id == None:
            print "PASS: looking for None short name"
        elif id == -1:
            print "FAIL: found multiple entries for None short name "
        else:
            print "FAIL: looking for None short name. Got " + str(id)
        #better safe than...
        testStore.abortTransaction()

    
def test3(db):
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
            returnFlag = False
        else:
            print "PASS: resource id returned from createResource: %d" % (noParentId)
            #find resource just added
            #use getResourceName, getResourceType
            resourcename = testStore.getResourceName(noParentId)
            print "name of resource: %s" % (resourcename)
            if (resourcename != "test3A"):
                print "FAIL: getResourceName: name is not expected"
                returnFlag = False
            else:
                print "PASS: getResourceName: name is expected" 
                parentname = resourcename
                restype = testStore.getResourceType(noParentId)
                print "type of resource: %s" % (restype)
                if (restype != "execution"):
                    print "FAIL: getResourceType: type is not expected"
                    returnFlag = False
                else:
                    print "PASS: getResourceType: type is expected" 
                    parenttype = restype
                    parId = testStore.getParentResource (noParentId)
                    print "parent_id of resource: " + str(parId)
                    if (parId != None):
                        print "FAIL: getResourceParent: parent_id of resource without parent is not expected"
                        returnFlag = False
                    else:
                        print "PASS: getResourceParent: parent_id of resource without parent is expected"
                        parentparentid = parId
                        parent_res_id = testStore.findResourceByName (resourcename)
                        if (parent_res_id != noParentId):
                            print "FAIL: findResourceByName did not return expected id of resource"
                            print "      expected: %d" % (noParentId)
                            print "      returned: " + str(parent_res_id)
                            returnFlag = False
                        else:
                            print "PASS: findResourceByName returned correct id of resource"
 
        #Add a resource who is a child of a known parent
        print "\n3.2: add a resource who is a child of known parent."
        print "     Test createResource() with getResourceName, getResourceType,"
        print "     and getParentResource"
        if (parent_res_id == -1):    #create child of resource created above
            print "FAIL: problem with parent resource created earlier"
            returnFlag = False
        else:
            child1Id = testStore.createResource(None, parent_res_id, "test3A/test3A-child1", "execution/process")
            if (child1Id != None and child1Id > 0):
                print "child1Id returned from createResource: %d" % (child1Id)
            else:
                print "ERROR: test3: createResource returned invalid resource_item id"
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
                returnFlag = False
            else:
                print "PASS: getResourceName: child name is expected"
                childname = cname
                ctype = testStore.getResourceType(child1Id)
                print "type of child1Id: %s" % (ctype)
                if (ctype != "execution/process"):
                    print "FAIL: getResourceType: child type is not expected"
                    returnFlag = False
                else:
                    print "PASS: getResourceType: child type is expected"
                    childtype = ctype
                    cparId = testStore.getParentResource (child1Id)
                    print "parent_id of child1Id: %d" % (cparId)
                    if (cparId != parent_res_id):
                        print "FAIL: getParentResource: parent_id of child1Id is not expected"
                        returnFlag = False
                    else:
                        print "PASS: getParentResource: parent_id of child1Id is expected"
                        childparentid = cparId
                        res_id = testStore.findResourceByName (cname)
                        if (res_id != child1Id):
                            print "FAIL: findResourceByName did not return expected id of child resource"
                            print "      expected: %d returned: %d" % (child1Id, res_id)
                            returnFlag = False
                        else:
                            print "PASS: findResourceByName returned correct id of child resource"


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
            returnFlag = False
        else:
            print "PASS: getResourceName: invalid id of 0 caused failure"

        # getResourceName -- bad id None 
        bad5 = testStore.getResourceName (None)
        if (bad5 != ""):
            print "FAIL: getResourceName: invalid id of None should return empty string"
            returnFlag = False
        else:
            print "PASS: getResourceName: invalid id of None returned empty string"


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
                returnFlag = False
            else:
                print "FAIL: getResourceName: id %d does not exist; should cause exception," %(maxid+100)
                print "      but the empty string was returned"
        except:
            print "PASS: EXCEPTION CAUGHT: getResourceName: id %d does not exist" %(maxid+100) 

        # getResourceType 
        bad6 = testStore.getResourceType (0)
        if (bad6 != ""):
            print "FAIL: getResourceType: invalid id of 0 should cause failure"
            returnFlag = False
        else:
            print "PASS: getResourceType: invalid id of 0 caused failure"

        # getResourceType -- bad id None 
        bad7 = testStore.getResourceType (None)
        if (bad7 != ""):
            print "FAIL: getResourceType: invalid id of None should cause failure"
            returnFlag = False
        else:
            print "PASS: getResourceType: invalid id of None caused failure"

        # getParentResource -- bad id 0
        try:   
            bad8 = testStore.getParentResource (0)
            if (bad8 != None):
                print "FAIL: getParentResource: invalid childId of 0 should cause failure"
                returnFlag = False
            else:
                print "PASS: getParentResource: invalid childId of 0 caused failure"
        except:
            print "EXCEPTION CAUGHT: getParentResource: invalid childId of O raised an exception" 
        
        # getParentResource -- bad id None 
        try:
            bad9 = testStore.getParentResource (None)
            if (bad9 != None):
                print "FAIL: getParentResource: invalid childId of None should cause failure"
                returnFlag = False
            else:
                print "PASS: getParentResource: invalid childId of None caused failure"
        except:
            print "EXCEPTION CAUGHT: getParentResource: invalid childId of None raised an exception"

    testStore.abortTransaction()
    testStore.closeDB()
    return returnFlag

    

def test4(db):
    """ Tests findFocusByName and findFocusByID, createFocus, findorCreateFocus

    """
    # NOTE: Currently does not test createFocus or findOrCreateFocus

    no1 = " "
    no2 = "/8/main.o/main"
    
    #testConnection = testStore.connectToDB(testStore.NO_WRITE, dbname, dbpwd, dbfullname) # old Oracle
    #testConnection = testStore.connectToDB(testStore.NO_WRITE, dbhost, dbname, dbuser, dbpwd) # old Postgres
    testConnection = testStore.connectToDB(testStore.NO_COMMIT)
    # for now, can't continue with testing if no DB connection
    if testConnection == False:
        print "FAIL: test4: findResource:  unable to connect."
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
                print reslist
                testStore.abortTransaction()
                testStore.closeDB()
                return False
            else:
                print "PASS: createFocus: returned %d with resource list:" % (focusId)
                print reslist
        except:
            print "EXCEPTION CAUGHT: createFocus: with resource list:"
            print reslist
            testStore.abortTransaction()
            testStore.closeDB()
            return False

        # Then find the focus created by name and by id
        fid = testStore.findFocusByID(reslist)
        if fid == 0:
            print "FAIL: findFocusByID: could not find focus with resource ids:"
            print reslist
        else:
            print "PASS: findFocusByID: found focus %d using resource list" % (fid)
 
        fid2 = testStore.findFocusByName("funcB,execA,metricC")
        if fid2 == 0:
            print "FAIL: findFocusByName: could not find focus with name: funcB,execA,metricC"
        else:
            print "PASS: findFocusByName: found focus %d using focus name" % (fid2) 
        if fid != fid2:
            print "FAIL: IDs returned by findFocusByName and findFocusByID are different"
        else:
            print "PASS: IDs returned by findFocusByName and findFocusByID are the same" 

        # Test findOrCreateFocus
        fid3 = testStore.findOrCreateFocus(reslist)
        if fid3 == fid:
            print "PASS: findOrCreateFocus: found existing focus"
        elif fid3 == 0:
            print "FAIL: findOrCreateFocus: returned 0 with resource list of existing focus"
        else:
            print "FAIL: findOrCreateFocus: returned incorrect focus id for existing focus"
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
        else:
            print "FAIL: findOrCreateFocus: did not create new focus with resource list"
        

        answer3 = testStore.findFocusByName(no1)
        if answer3 == 0:
            print "PASS: findFocusByName can't find no1"
        else:
            print "FAIL: findFocusByName returns " + str(answer3) + "for no1"
        answer4 = testStore.findFocusByName(no2)
        if answer4 == 0:
            print "PASS: findFocusByName can't find no2"
        else:
            print "FAIL: findFocusByName returns " + str(answer4) + "for no2"

        # better safe than...    
        testStore.abortTransaction()
        testStore.closeDB()        

def test5(db):
    """ Tests enterResourceConstraints, lookupConstraints, lookupConstraint
        Returns True if all tests pass; False if some fail
        9-1-05 -- enterResourceConstraints deprecated
                  lookupConstraints deprecated
                  lookupConstraint deprecated
    """
    # 7-13-05: TODO: add testing for addResourceConstraint; 
    # enterResourceConstraints does not currently check that the resource ids exist
    #   prior to entering them as resource_constraints 

    # 9-4-05: TODO: re-write entire test.  Use addResourceConstraint instead of 
    #               enterResourceConstraints; use ?? instead of lookupConstraint/s
    # for now comment out test 
    #returnFlag = True
    ##testConnection = testStore.connectToDB(testStore.NO_WRITE, dbname, dbpwd, dbfullname) #old Oracle
    ##testConnection = testStore.connectToDB(testStore.NO_COMMIT, dbhost, dbname, dbuser, dbpwd)#old PG
    #testConnection = testStore.connectToDB(testStore.NO_COMMIT) 
    ## for now, can't continue with testing if no DB connection
    #if testConnection == False:
    #    print "FAIL: test5:  unable to connect."
    #    return False
    #else:
    #    print "PASS: test5: able to connect."
    #    #add resources to db, then build the constraints 
    #    p1 = testStore.createResource (None, None, "ParentA", "ParentA-type")
    #    p2 = testStore.createResource (None, None, "ParentB", "ParentB-type")
    #    if (p1 == None or p2 == None):
    #        print "ERROR: test5: unable to create resource(s) for test"
    #        returnFlag = False
    #        testStore.abortTransaction()
    #        testStore.closeDB()
    #        return returnFlag
    #    c1 = testStore.createResource (None, p1, "ChildA", "ChildA-type")
    #    c2 = testStore.createResource (None, p1, "ChildB", "ChildB-type") 
    #    c3 = testStore.createResource (None, p1, "ChildC", "ChildC-type")
    #    c4 = testStore.createResource (None, p2, "ChildD", "ChildD-type")
    #    c5 = testStore.createResource (None, p2, "ChildE", "ChildE-type")
    #    c6 = testStore.createResource (None, p2, "ChildF", "ChildF-type")
    #    if (c1 == None or c2 == None or c3 == None or c4 == None \
    #        or c5 == None or c6 == None):
    #        print "Error: test5: unable to create resource(s) for test" 
    #        returnFlag = False
    #        testStore.abortTransaction()
    #        testStore.closeDB()
    #        return returnFlag

        ##enter id with to_constraint list of ids that are not children  of id
        #print "\n5.1: Test enterResourceConstraints, lookupConstraint, lookupConstraints "
        #print "     Create constraints such that the from-to relationship is not a parent-child relationship."

        #try:
        #    testStore.enterResourceConstraints (p1, [p2, c4, c5])
        #except:
        #    print "FAIL: enterResourceConstraints: valid resource_item ids should pass test"
        #else:
        #    print "PASS: enterResourceConstraints: valid resource_item ids entered as constraints"
        #    #look up the contstraints just built with lookupConstraint()
        #    if not testStore.lookupConstraint(p1,p2):
        #        print "FAIL: lookupConstraint (%d, %d)" % (p1, p2)
        #        returnFlag = False
        #    else:
        #        print "PASS: lookupConstraint (%d, %d)" % (p1, p2)
        #    if not testStore.lookupConstraint(p1,c4):
        #        print "FAIL: lookupConstraint (%d, %d)" % (p1, c4)
        #        returnFlag = False
        #    else:
        #        print "PASS: lookupConstraint (%d, %d)" % (p1, c4)
        #    if not testStore.lookupConstraint(p1,c5):
        #        print "FAIL: lookupConstraint (%d, %d)" % (p1, c5)
        #        returnFlag = False
        #    else:
        #        print "PASS: lookupConstraint (%d, %d)" % (p1, c5)
        #    #look up all constraints using lookupConstraints()
        #    if not testStore.lookupConstraints(p1,[p2,c4,c5]):
        #        print "FAIL: lookupConstraints (%d, [%d, %d, %d])" % (p1,p2,c4,c5)
        #        returnFlag = False
        #    else:
        #        print "PASS: lookupConstraints (%d, [%d, %d, %d])" % (p1,p2,c4,c5)


        #print "\n5.2: Test enterResourceConstraints, lookupConstraint, lookupConstraints "
        #print "     Create constraints such that the from-to relationship is a parent-child relationship."
        #print "     A parent-child relationship should not be entered explicitly into the resource_constraint"
        #print "     table as a from-to relationship"

        ##enter id with to_constraint list of ids where some are children of from_id
        #try:
        #    testStore.enterResourceConstraints (p1, [c1, c2, c3])
        #except:
        #    print "PASS: enterResourceConstraints: parent-child relationships are not allowed as from-to"
        #    print "      relationships in resource_constraint"
        #else:
        #    # Technically a failure of the description of resource_constraints table, 
        #    # which states that the table is for relationships between resources that are not
        #    # parent/child relationships.
        #    #look up all constraints using lookupConstraints()
        #    if testStore.lookupConstraints(p1,[c1,c2,c3]):
        #        print "FAIL: lookupConstraints (%d, [%d, %d, %d])" % (p1,c1,c2,c3)
        #        print "      %d is parent of %d, %d, and %d" % (p1,c1,c2,c3)
        #        returnFlag = False 
        #    else:
        #        print "PASS: lookupConstraints (%d, [%d, %d, %d])" % (p1,c1,c2,c3)
        #        print "      The constraints were not added because %d is parent of" % (p1)
        #        print "      %d, %d, and %d" % (c1, c2, c3)   

        ##enter id with to_constraint list of ids where some ids do not already exist in resource_item
        #print "\n5.3: Test enterResourceConstraints"
        #print "     Create constraints where some of the ids (from_resource id or to_resource list)"
        #print "     do not already exist in resource_item."
        #print "     This should not be allowed because both elements of the resource_constraint table"
        #print "     are suppose to refer to existing resource items" 
        
        #sql = "select MAX(id) from resource_item"
        ##testStore.cursor.execute(sql)
        #testStore.dbapi.execute(testStore.cursor, sql)
        ##maxid, = testStore.cursor.fetchone()
        #maxid, = testStore.dbapi.fetchone(testStore.cursor) 
        #print "Max resource_item id is %d" % maxid
        #if maxid != None and maxid > 0:
        #    notAnId1 = maxid+100
        #    notAnId2 = maxid+200
        #    notAnId3 = maxid+300
        #    notAnId4 = maxid+400
        #else:
        #    print "ERROR: test5: sql query did not execute properly"
        #    testStore.abortTransaction()
        #    testStore.closeDB()
        #    return returnFlag

        ## make sure ids just created do not exist:
        
        ## test all ids do not exist
        #try:
        #    testStore.enterResourceConstraints (notAnId1, [notAnId2, notAnId3, notAnId4])
        #except:
        #    print "PASS: enterResourceConstraints (%d, [%d, %d, %d])" % (notAnId1,notAnId2,notAnId3,notAnId4)
        #    print "      the resources do not exist in resource_item." 
        #    # Passing means the resource constraint has not been entered and also that these resource ids
        #    # should not be found in resource_item
        #else:
        #    print "FAIL: enterResourceConstraints (%d, [%d, %d, %d])" % (notAnId1,notAnId2,notAnId3,notAnId4)
        #    print "      %d, %d, %d, and %d do not exist in resource_item." % (notAnId1,notAnId2,notAnId3,notAnId4) 
        #    returnFlag = False

        ## test from_resource id does not exist, but to_resource ids do exist
        #try:
        #    testStore.enterResourceConstraints (notAnId1, [c4, c5, c6])
        #except:
        #    print "PASS: enterResourceConstraints (%d, [%d, %d, %d])" % (notAnId1,c4,c5,c6)
        #    print "      the from_resource does not exist in resource_item."
        #else:
        #    print "FAIL: enterResourceConstraints (%d, [%d, %d, %d])" % (notAnId1,c4,c5,c6)
        #    print "      %d does not exist in resource_item." % (notAnId1)
        #    returnFlag = False

        ## test from_resource id exists, but to_resource ids do not exist
        #try:
        #    testStore.enterResourceConstraints (p2, [notAnId1,notAnId2,notAnId3])
        #except:
        #    print "PASS: enterResourceConstraints (%d, [%d, %d, %d])" % (p2,notAnId1,notAnId2,notAnId3)
        #    print "      the to_resources do not exist in resource_item."
        #else:
        #    print "FAIL: enterResourceConstraints (%d, [%d, %d, %d])" % (p2,notAnId1,notAnId2,notAnId3)
        #    print "      %d, %d, and %d do not exist in resource_item." % (notAnId1,notAnId2,notAnId3)
        #    returnFlag = False

    #testStore.abortTransaction()
    #testStore.closeDB()
    #return returnFlag

def test6(db):
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
    #testConnection = testStore.connectToDB(testStore.NO_WRITE, dbname, dbpwd, dbfullname) #old Oracle
    #testConnection = testStore.connectToDB(testStore.NO_COMMIT, dbhost, dbname, dbuser, dbpwd) #old PG
    testConnection = testStore.connectToDB(testStore.NO_COMMIT)

    # for now, can't continue with testing if no DB connection
    if testConnection == False:
        print "FAIL: test6:  unable to connect."
        return False
    print "PASS: test6: able to connect."

    #add resources to db, then enter attribute-value pairs in resource_attribute 
    p1 = testStore.createResource (None, None, "ParentA", "ParentA-type")
    p2 = testStore.createResource (None, None, "ParentB", "ParentB-type")
    if (p1 == None or p2 == None):
        print "ERROR: test6: unable to create resource(s) for test"
        returnFlag = False
        testStore.abortTransaction()
        testStore.closeDB()
        return returnFlag
    c1 = testStore.createResource (None, p1, "ChildA", "ChildA-type")
    c2 = testStore.createResource (None, p1, "ChildB", "ChildB-type")
    c3 = testStore.createResource (None, p1, "ChildC", "ChildC-type")
    if (c1 == None or c2 == None or c3 == None): 
        print "Error: test6: unable to create resource(s) for test"
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
    print "6.1: Enter resource_attribute entries for valid resources using addResourceAttribute"

    rv = 0
    try:
        rv = testStore.addResourceAttribute("ParentA", a5name, a5val, type)
    except:
        if not rv:
            print "FAIL-EXCEPTION RAISED: addResourceAttribute: (ParentA, %s, %s, %s): ParentA is valid resource," %(a5name, a5val, type)
            print "    but attribute not added"
        else:
            print "PASS-EXCEPTION RAISED: addResourceAttribute: (ParentA, %s, %s, %s): ParentA is valid resource;" %(a5name, a5val, type)
            print "    attribute added"
    else:
        if not rv:
            print "FAIL: addResourceAttribute: (ParentA, %s, %s, %s): ParentA is valid resource," %(a5name, a5val, type)
            print "    but attribute not added"
        else:
            print "PASS: addResourceAttribute: (ParentA, %s, %s, %s): ParentA is valid resource;" %(a5name, a5val, type)
            print "    attribute added"
    rv = 0
    try:
        rv = testStore.addResourceAttribute("ParentA", a6name, a6val, type)
    except:
        if not rv:
            print "FAIL-EXCEPTION RAISED: addResourceAttribute: (ParentA, %s, %s, %s): ParentA is valid resource," %(a6name, a6val, type) 
            print "    but attribute not added"
        else:
            print "PASS-EXCEPTION RAISED: addResource Attribute: (ParentA, %s, %s, %s): ParentA is valid resource;" %(a6name, a6val, type)
            print "    attribute added"
    else:
        if not rv:
            print "FAIL: addResourceAttribute: (ParentA, %s, %s, %s): ParentA is valid resource," %(a6name, a6val, type)
            print "    but attribute not added"
        else:
            print "PASS: addResourceAttribute: (ParentA, %s, %s, %s): ParentA is valid resource;" %(a6name, a6val, type)
            print "    attribute added"

    rv = 0
    try:
        rv = testStore.addResourceAttribute("ParentB", a7name, a7val, type)
    except:
        if not rv:
            print "FAIL-EXCEPTION RAISED: addResourceAttribute: (ParentB , %s, %s, %s): ParentB is valid resource," %(a7name, a7val, type)  
            print "    but attribute not added"
        else:
            print "PASS-EXCEPTION RASISE: addResource Attribute: (ParentB, %s, %s, %s): ParentB is valid resource;" %(a7name, a7val, type)
            print "    attribute added"
    else:
        if not rv:
            print "FAIL: addResourceAttribute: (ParentB, %s, %s, %s): ParentB is valid resource," %(a7name, a7val, type)
            print "    but attribute not added"
        else:
            print "PASS: addResourceAttribute: (ParentB, %s, %s, %s): ParentB is valid resource;" %(a7name, a7val, type)
            print "    attribute added"


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
        else:
            print "FAIL-EXCEPTION RAISED: addResourceAttribute: resource does not exist, but attribue was added"
    else:
        if not rv:
            print "PASS: addResourceAttribute: resource does not exist; attribute not added"
        else:
            print "FAIL: addResourceAttribute: resource does not exist, but attribue was added"
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


def test6b(testStore):
    """ Tests enterResourceAVs
        Returns true if all tests pass; false if some fail
        9-1-05: enterResourceAVs is deprecated; test no longer necessary
    """
    # 7-13-05: This is a new test to specially test enterResourceAVs
    #   the problem is with the pygresql implementation of executemany 
    #   which does not handle bind type variables properly.
    # 9-4-05: comment out test
    #returnFlag = True
    ##testConnection = testStore.connectToDB(testStore.NO_WRITE, dbname, dbpwd, dbfullname) # old Oracle 
    ##testConnection = testStore.connectToDB(testStore.NO_COMMIT, dbhost, dbname, dbuser, dbpwd) # old PG
    #testConnection = testStore.connectToDB(testStore.NO_COMMIT)
    ## for now, can't continue with testing if no DB connection
    #if testConnection == False:
    #    print "FAIL: test6b:  unable to connect."
    #    return False
    #print "PASS: test6b: able to connect."

    ##add resources to db, then enter attribute-value pairs in resource_attribute
    #p1 = testStore.createResource (None, None, "ParentA", "ParentA-type")
    #p2 = testStore.createResource (None, None, "ParentB", "ParentB-type")
    #if (p1 == None or p2 == None):
    #    print "ERROR: test6b: unable to create resource(s) for test"
    #    returnFlag = False
    #    testStore.abortTransaction()
    #    testStore.closeDB()
    #    return returnFlag
    #c1 = testStore.createResource (None, p1, "ChildA", "ChildA-type")
    #c2 = testStore.createResource (None, p1, "ChildB", "ChildB-type")
    #c3 = testStore.createResource (None, p1, "ChildC", "ChildC-type")
    #if (c1 == None or c2 == None or c3 == None):
    #    print "Error: test6b: unable to create resource(s) for test"
    #    returnFlag = False
    #    testStore.abortTransaction()
    #    testStore.closeDB()
    #    return returnFlag

    ## create some dictionaries
    #d1 = {"name": "name1", "value": "value1"}
    #d2 = {"name": "name2", "value": "value2"}
    #d3 = {"name": "name3", "value": "value3"}
    #d4 = {"name": "name4", "value": "value4"}
    #noValue = {"name": "nameWithNoValue"}
    #noName= {"value": "valueWithNoName"}
    #numbers = {"name": 1, "value": 2}


    #print "     Enter (attribute,value) pairs for valid resources."
    #try:
    #    testStore.enterResourceAVs(p1, [d1])          # a list of 1
    #except:
    #    print "FAIL-EXCEPTION RAISED: enterResourceAVs: valid (name,value) pair for a valid resource_id"
    #    returnFlag = False
    #else:
    #    print "PASS: enterResourceAVs: valid (name,value) pair for a valid resource_id"
    #try:
    #    testStore.enterResourceAVs(p2, [d1,d2,d3,d4]) # a list of several
    #except:
    #    print "FAIL: enterResourceAVs: a list of valid (name,value) pairs for a valid resource_id"
    #    returnFlag = False
    #else:
    #    print "PASS: enterResourceAVs: a list of valid (name,value) pairs for a valid resource_id"

    ##test: lookup attributes created in above test with lookupAttribute()
    #if not testStore.lookupAttribute (p1, d1["name"], d1["value"] ):
    #    print "FAIL: lookupAttribute: valid (%s, %s) entered for resource %d" % (d1["name"],d1["value"], p1)
    #    print "      not found"
    #    returnFlag = False
    #else:
    #    print "PASS: lookupAttribute: found (%s, %s) entered for resource %d" % (d1["name"],d1["value"], p1)

    #if not testStore.lookupAttribute (p2, d1["name"], d1["value"]):
    #    print "FAIL: lookupAttribute: valid (%s, %s) entered for resource %d" % (d1["name"],d1["value"], p2)
    #    print "      not found"
    #    returnFlag = False
    #else:
    #    print "PASS: lookupAttribute: found (%s, %s) entered for resource %d" % (d1["name"],d1["value"], p2)

    #if not testStore.lookupAttribute (p2, d4["name"], d4["value"] ):
    #    print "FAIL: lookupAttribute: valid (%s, %s) entered for resource %d" % (d4["name"],d4["value"], p2)
    #    print "      not found"
    #    returnFlag = False
    #else:
    #    print "PASS: lookupAttribute: found (%s, %s) entered for resource %d" % (d4["name"],d4["value"], p2)

    ##test: lookup attributes created above with lookupAttributes()
    #if not testStore.lookupAttributes (p1, [(d1["name"],d1["value"])]):
    #    print "FAIL: lookupAttributes: valid (%s, %s) entered for resource %d" % (d1["name"],d1["value"], p1)
    #    print "      not found"
    #    returnFlag = False
    #else:
    #    print "PASS: lookupAttributes: found (%s, %s) entered for resource %d" % (d1["name"],d1["value"], p1)
    #if not testStore.lookupAttributes (p2, [(d1["name"],d1["value"]),(d2["name"],d2["value"]),
    #                                        (d3["name"],d3["value"]),(d4["name"],d4["value"])]):
    #    print "FAIL: lookupAttributes: valid (name, value) list entered for resource %d not found" % (p2)
    #    returnFlag = False
    #else:
    #    print "PASS: lookupAttributes: found list of (name,value) pairs entered for resource %d" % (p2)

    #testStore.abortTransaction()
    #testStore.closeDB()
    #return returnFlag


def test7(db):
    """ Tests getHardwareId, getBuildName, getExecutionName
        9-1-05 -- getHardwareId deprecated
                  getBuildName deprecated
                  getExecutionName deprecated
    """
    print "test7 is just a placeholder right now."

def test8(testStore):
    """ Tests getChildResources, getAncestors, addAncestors, addDescendants
        9-1-05 -- getChildResources deprecated 
    """
    #9-4-05 -- comment out getChildResources parts
#Oracle Database data   
#    good1 = 2  # Frost. has children. has anscestor. has too many descendants
#    good2 = 12174 # a compiler resource. no children. no ancestor. no desc
#    good3 =  13263 # a thread resource. has ancestors. no desc
#    good4 = 13126 # an execution resource. has descendants in several levels
#    good5 = 13262 # a process resource. has one level of desc
#Postgres Database data
#    good1 = 1163 -- MCR. has 3 children. has 1 ancestor. has 3459 descendants
#    good2 = 4836 -- inputDeck resource. no children. no ancestor. no desc.
#    good3 = A thread resource without descendants and with ancestors does not exist yet.
#    good4 = 4624 -- an execution resource. has descendants in several levels
#    good5 = 4790 -- a process resource. has one level of desc.
    bad1 = None
    bad2 = 0

    #testConnection = testStore.connectToDB(testStore.NO_WRITE, dbname, dbpwd, dbfullname) #old Oracle
    #testConnection = testStore.connectToDB(testStore.NO_COMMIT, dbhost, dbname, dbuser, dbpwd) #old PG
    testConnection = testStore.connectToDB(testStore.NO_COMMIT)
    # for now, can't continue with testing if no DB connection
    if testConnection == False:
        print "FAIL: test8: ancestors/descendants:  unable to connect."
        return False
    else:
        good1 = int(testStore.findResourceByShortNameAndType("grid/machine",\
                   "Frost"))
        if good1 == None:
            print "findResourceByShortNameAndType: No match found for Frost, grid/machine"
        elif good1 == -1:
            print "findResourceByShortNameAndType: Found more than 1 for Frost, grid/machine"
        else:
            print "findResourceByShortNameAndType: Found 1 match for Frost, grid/machine"
        
        #This good2 is specific to data in oracle database
        # smtihmtest commented out this good2 because its oracle
        #good2 = int(testStore.findResourceByShortNameAndType("inputDeck", \
        #           "iq.h-33"))
        #This good2 exists in Postgresql database

        good2 = int(testStore.findResourceByShortNameAndType("inputDeck", \
                   "iq.h-22"))
        
        if good2 == None:
            print "findResourceByShortNameAndType: No match found for iq.h-22, inputDeck"
        elif good2 == -1:
            print "findResourceByShortNameAndType: Found more than 1 for iq.h-22, inputDeck"
        else:
            print "findResourceByShortNameAndType: Found 1 match for iq.h-22, inputDeck"

        #This is Oracle data.  Does not exists yet in PG
        good3 = int(testStore.findResourceByName("/irs-8-545/Process-38/Thread-0"))
        if good3:
            print "findResourceByName: Found resource with name /irs-8-545/Process-38/Thread-0"
        else:
            print "findResourceByName: Did not find resource with name /irs-8-545/Process-38/Thread-0"
        #print "POSTGRESQL: N/A"
        #This is the oracle data 
        good4 = int(testStore.findResourceByName("/irs-8-545"))
        #This is for the postgresql db
        #good4 = int(testStore.findResourceByName("/irs-2-503")) 
        if good4:
            print "findResourceByName: Found resource with name /irs-2-503"
        else:
            print "findResourceByName: Did not find resource with name /irs-2-503"

        #This is for the Oracle db 
        good5 = int(testStore.findResourceByName("/irs-8-545/Process-38"))
        #This is for the postgresql db
        #good5 = int(testStore.findResourceByName("/irs-2-503/Process-3"))
        if good5:
            print "findResourceByName: Found resource with name /irs-2-503/Process-3"
        else:
            print "findResourceByName: Did not find resource with name /irs-2-503/Process-3"

        #answer1 = testStore.getChildResources(good1)
        #if answer1 == []:
        #    print "FAIL: getChildResources can't find children of %d" % good1
        #else:
        #    print "PASS: ans/desc find a child " + str(answer1) + " for " +\
        #          str(good1)

        #answer2 = testStore.getChildResources(good2)
        #if answer2 != []:
        #    print "FAIL: getChildResources found children of %d" % good3
        #else:
        #    print "PASS: ans/desc did not find a child "+str(answer2)+" for " +\
        #          str(good2)

        #answer3 = testStore.getChildResources(bad1)
        #if answer3 != []:
        #    print "FAIL: getChildResources found children of %d" % bad1
        #else:
        #    print "PASS: ans/desc did not find a child "+str(answer3)+" for " +\
        #          str(bad1)

        #answer4 = testStore.getChildResources(bad2)
        #if answer4 != []:
        #    print "FAIL: getChildResources found children of %d" % bad2
        #else:
        #    print "PASS: ans/desc did not find a child "+str(answer4)+" for " +\
        #          str(bad2)

        answer5 = testStore.getAncestors(good1)

        if answer5 == []:
            print "FAIL: getAncestors can't find ans of %d" % good1
        else:
            print "PASS: ans/desc finds ancestors " + str(answer5) + " for " +\
                  str(good1)

        #Oracle only 
        #answer5a = testStore.getAncestors(good3)
        #if answer5a == []:
        #    print "FAIL: getAncestors can't find ans of %d" % good3
        #else:
        #    print "PASS: ans/desc finds ancestors " + str(answer5a) + " for " +\
        #          str(good3)
        #print "N/A for Posrgresql at this time -- need more data"

        answer6 = testStore.getAncestors(good2)
        if answer6 != []:
            print "FAIL: getAncestors found ans of %d" % good2
        else:
            print "PASS: ans/desc did not find ancestors " + str(answer6) +\
                  " for " + str(good2) #the oracle test has this as bad1, which is wrong

        answer7 = testStore.getAncestors(bad1)
        if answer7 != []:
            print "FAIL: getAncestors found ans of %d" % bad1
        else:
            print "PASS: ans/desc did not find ancestors " + str(answer7) +\
                  " for " + str(bad1)

        answer8 = testStore.getAncestors(bad2)
        if answer8 != []:
            print "FAIL: getAncestors found ans of %d" % bad2
        else:
            print "PASS: ans/desc did not find ancestors " + str(answer8) +\
                  " for " + str(bad2)

        try: 
           testStore.addAncestors(good1)
        except:
            print "FAIL: addAncestors failed for ans list of %s" % good1
        else:
            print "PASS: addAncestors passed for ans list of %s" % good1

        try:
           testStore.addAncestors(good2) # no anc but shouldn't except   
        except:
            print "FAIL: addAncestors failed for ans list of %s" % good2
        else:
            print "PASS: addAncestors passed for ans list of %s" % good2

        try:
           testStore.addAncestors(bad1) # no anc but shouldn't except   
        except:
            print "FAIL: addAncestors failed for ans list of %s" % bad1
        else:
            print "PASS: addAncestors passed for ans list of %s" % bad1

        try:
           testStore.addAncestors(bad2) # no anc but shouldn't except   
        except:
            print "FAIL: addAncestors failed for ans list of %s" % bad2
            raise
        else:
            print "PASS: addAncestors passed for ans list of %s" % bad2

        try:
           testStore.addDescendants(good4)
        except:
           print "FAIL: addDescendants failed for des list of %s" % good4
        else:
           print "PASS: addDescendants passed for des list of %s" % good4

        try:
           testStore.addDescendants(good5)
        except:
           print "FAIL: addDescendants failed for des list of %s" % good5
        else:
           print "PASS: addDescendants passed for des list of %s" % good5

        try:
           testStore.addDescendants(bad1)
        except:
           print "FAIL: addDescendants failed for des list of %s" % bad1
        else:
           print "PASS: addDescendants passed for des list of %s" % bad1

        try:
           testStore.addDescendants(bad2)
        except:
           print "FAIL: addDescendants failed for des list of %s" % bad2
        else:
           print "PASS: addDescendants passed for des list of %s" % bad2

        testStore.abortTransaction() 
        testStore.closeDB()

def test9(testStore):
    """ Tests addResource, getNewResourceName
    """
    #testConnection = testStore.connectToDB(testStore.NO_WRITE, dbname, dbpwd, dbfullname)
    #testConnection = testStore.connectToDB(testStore.NO_COMMIT, dbhost, dbname, dbuser, dbpwd)
    testConnection = testStore.connectToDB(testStore.NO_COMMIT)
    # for now, can't continue with testing if no DB connection
    if testConnection == False:
        print "FAIL: test9: addResource/getNewResourceName:  unable to connect."
        return False

    result = testStore.addResource("/testName", "execution")
    if result == 0:
        print "FAIL: addResource: did not add resource with name /testName and type /execution"
    else:
        print "PASS: addResource: returned id  %d for adding name /testName and type /execution"  % result

    result = testStore.addResource("/testName", "execution")
    if result != 0:
        print "FAIL: addResource: returned %d for adding resource name and type that exist"  % result
    else:
        print "PASS: addResource: returned 0 for trying to add resource name and type that exist"

    result = testStore.addResource("/testName-12", "execution")
    if result == 0:
        print "FAIL: addResource: did not add resource with name /testName-12 and type /execution"
    else:
        print "PASS: addResource: returned id  %d for adding name /testName-12 and type /execution"  % result

    result = testStore.addResource("/testName-12", "execution")
    if result != 0:
        print "FAIL: addResource: returned %d for adding resource name and type that exist"  % result
    else:
        print "PASS: addResource: returned 0 for trying to add resource name and type that exist"



    result = testStore.getNewResourceName("/testName")
    if result == "/testName":
        print "FAIL: getNewResourceName returned the givenName -- check debug level"
    else:
        print "PASS: getNewResourceName returned new name: %s for adding /testName" % result 

    result2 = testStore.getNewResourceName("/testName")
    if result2 == "/testName":
        print "FAIL: getNewResourceName returned the givenName -- check debug level"
    elif result2 == result:
        print "FAIL: getNewResourceName returned name: %s, which is already assigned" % result2 
    else:
        print "PASS: getNewResourceName returned new name: %s for adding /testName , which is different from %s" %(result2, result)

    result3 = testStore.getNewResourceName("/aNameThatDoesNotExist")
    if result3 == "/aNameThatDoesNotExist":
        print "FAIL: getNewResourceName returned the givenName -- check debug level"
    else:
        print "PASS: getNewResourceName returned %s for adding /aNameThatDoesNotExist" % result3 

    testStore.abortTransaction() 
    testStore.closeDB()

def test10(testStore):
    """ Tests createPerformanceResult

    """
    testConnection = testStore.connectToDB(testStore.NO_COMMIT)
    # for now, can't continue with testing if no DB connection
    if testConnection == False:
        print "FAIL: test10: createPerformanceResult:  unable to connect."
        return False


    testStore.abortTransaction()

testStore = PTdataStore()

#TEST 1 -- connection test
#print "test1.2 - connect, no optional parameters"
#test1_2(testStore)

#print "test1.3 - connect, with optional parameters"
#test1_3(testStore)


#TEST 2 -- createResource, findResourceByName, findResourceByShortNameAndType
#print "test2 -- createResource, findResourceByName, findResourceByShortNameAndType"
#test2(testStore)

#print "test3 -- findResourceByName, getResourceName, getResourceType, getParentResource"
#test3(testStore)

#print "test4 -- createFocus, findOrCreateFocus, findFocusByName, findFocusById"
#test4(testStore)

# This test function is commented out
#print "test5 -- enterResourceConstraints, lookupConstraint, lookupConstraints"
#test5(testStore)

#print "test6 -- addResourceAttribute, lookupAttribute, lookupAttributes"
#test6(testStore)

# This test function is commented out
#print "test6b"
#test6b(testStore)

print "test8"
test8(testStore)

print "test9"
test9(testStore)


