#!/usr/bin/env python

# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information. 

# 9-20-05: Do not use this test code. Use PTdataStore_PTpyDBAPItester.py.

import sys
from PTds import PTdataStore
from getpass import getpass


# connect/close
def test1 (testStore, dbn, dbp, dbf):
    """Tests connect and close

    return values:  0 = all connects fail
                    1 = debug works, db fails
                    2 = debug fails, db works
                    3 = all connects work
    """
    testConnection = testStore.connectToDB(testStore.NO_WRITE, dbn, dbp, dbf)
    if testConnection:
        print "connectToDB passed using DB"
        testStore.closeDB()
    else:
        print "FAIL:  connectToDB failed using DB"
    testConnection = testStore.connectToDB(testStore.NO_WRITE, "", "", "")
    if testConnection:
        print "connectToDB passed using debug"
        testStore.closeDB()
    else:
        print "FAIL:  connectToDB failed using debug"

def test2(db):
    """Tests findOrCreateResource/createResource/findResource/findResourcebyShortNameAndType

    returns True if all tests pass, False if some fail  
    """
    testConnection = testStore.connectToDB(testStore.NO_WRITE, dbname, dbpwd, dbfullname)
    # for now, can't continue with testing if no DB connection
    if testConnection == False:
        print "FAIL: findResource:  unable to connect."
        return False
    else:
        improbableResource = testStore.findResource(0, "execution", "test1999")
        if improbableResource != None:
            print "improbableResource set to " + improbableResource
            print "FAIL:  improbableResource:  resource name test1999 in use"
            return False
        else:
            print "improbableResource not found"
            
        improbableResource2 = testStore.findResource(0, "execution", "test2000")
        if improbableResource2 != None:
            print "improbableResource2 set to " + improbableResource2
            print "FAIL:  improbableResource2: resource name test2000 in use"
            return False
        else:
            print "improbableResource2 not found"
        newResID = 0
        newResID = testStore.createResource(14, 0, "testerA", "execution")
        print "createResource returns: "
        print newResID
        newResID = testStore.findOrCreateResource(0, "execution", "testerB", "execution")
        print "findOrCreateResource returns: "
        print newResID

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
    """
    parent_res_id = -1
    childname = ""
    childtype = ""
    childparentid = None
    parentname = ""
    parenttype = ""
    parentparentid = None
    returnFlag = True
    testConnection = testStore.connectToDB(testStore.NO_COMMIT, dbname, dbpwd, dbfullname)
    
    #ask if this is the right kind of connection
    if testConnection == False:
        print "FAIL: getResource: unable to connect."
        return False
    else:
        # add some data to db using PTdataStore methods (this will not be committed to db)
        # createResource only adds resource if focus_frame_id is None
        print "\n3.1: add a resource that does not have a parent id."
        print "     Test createResource() with getResourceName, getResourceType,"
        print "     getParentResource, and getResourceId"

        noParentId = 0
        noParentId = testStore.createResource(None, None, "test3A", "execution")
        print "id of resource without a parent_id: " + str(noParentId)  
        if (noParentId == None): 
            print "FAIL: createResource returned invalid resource_item id"
            returnFlag = False
        else:
            print "PASS: resource id returned from createResource: %d" % (noParentId)
            #find resource just added
            #use getResourceName, getResourceType, and getResourceId
            resourcename = testStore.getResourceName(noParentId)
            print "name of this resource: %s" % (resourcename)
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
                        parent_res_id = testStore.getResourceId (restype, resourcename, parId)
                        if (parent_res_id != noParentId):
                            print "FAIL: getResourceId did not return expected id of resource"
                            print "      expected: %d" % (noParentId)
                            print "      returned: " + str(parent_res_id)
                            returnFlag = False
                        else:
                            print "PASS: getResourceId returned correct id of resource"
 
        #Add a resource who is a child of a known parent
        print "\n3.2: add a resource who is a child of known parent."
        print "     Test createResource() with getResourceName, getResourceType,"
        print "     getParentResource, and getResourceId"
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
            #use getResourceName, getResourcType, and getResourceId
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
                        print "FAIL: getResourceParent: parent_id of child1Id is not expected"
                        returnFlag = False
                    else:
                        print "PASS: getResourceParent: parent_id of child1Id is expected"
                        childparentid = cparId
                        res_id = testStore.getResourceId (ctype, cname, cparId)
                        if (res_id != child1Id):
                            print "FAIL: getResourceId did not return expected id of child resource"
                            print "      expected: %d returned: %d" % (child1Id, res_id)
                            returnFlag = False
                        else:
                            print "PASS: getResourceId returned correct id of child resource"


        # Test getResourceId, getResourceName, getResourceType, getParentResource with bad parameters.  Use
        # resource ids of parent and child created above in some of tests
        print "\n3.3: Test getResourceId, getResourceName, getResourceType, "
        print "     getParentResource with bad parameters." 
        # getResourceId -- bad type
        bad1 = testStore.getResourceId ("badtype", childname, childparentid) 
        if (bad1 != 0):
            print "FAIL: getResourceId: invalid type should cause failure"
            returnFlag = False
        else:
            print "PASS: getResourceId: invalid type caused failure"
        # getResourceId -- bad name 
        bad2 = testStore.getResourceId (childtype, "badname", childparentid)
        if (bad2 != 0):
            print "FAIL: getResourceId: invalid name should cause failure"
            returnFlag = False
        else:
            print "PASS: getResourceId: invalid name caused failure"
        # getResourceId -- bad parentid 
        bad3 = testStore.getResourceId (childtype, childname, 0)
        if (bad3 != 0):
            print "FAIL: getResourceId: invalid parent_id should cause failure"
            returnFlag = False
        else:
            print "PASS: getResourceId: invalid parent_id caused failure"

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
            print "FAIL: getResourceName: invalid id of None should cause failure"
            returnFlag = False
        else:
            print "PASS: getResourceName: invalid id of None caused failure"

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
    yes1 = "/sppm,/build-2,/mpiicc-8.0 Version 8.0-4,/mpiifort-8.0 Version 8.0-5,/env-9,/sppm-1-1/Process-0,/SingleMachineMCR/MCR,/inputdeck-10,/iq.h-11,/Linux #1 SMP Mon Sep 27 13:51:13 PDT 2004 2.4.21-p4smp-71.3chaos-8,/Linux #1 SMP Wed Sep 1 16:37:16 PDT 2004 2.4.21-p4smp-71chaos-3,/fpp-6,/m4-7,/whole execution/10"
    yes2 = "/smg2000,/build-1187/mod0x0000000100074537/fun0x0000000100074537/0x0000000100074537,/env-1188,/smg2000-1209/Process-20,/SingleMachineUV/UV,/whole execution"
    no1 = " "
    no2 = "/8/main.o/main"
    
    testConnection = testStore.connectToDB(testStore.NO_WRITE, dbname, dbpwd, dbfullname)
    # for now, can't continue with testing if no DB connection
    if testConnection == False:
        print "FAIL: findResource:  unable to connect."
        return False
    else:
        answer1 = testStore.findFocusByName(yes1)
        if answer1 == 0:
            print "FAIL: findFocusByName can't find: %s" % yes1
        else:
            print "PASS: findFocusByName returns " + str(answer1) + " for yes1"
        answer2 = testStore.findFocusByName(yes2)
        if answer2 == 0:
            print "FAIL: findFocusByName can't find: %s" % yes2
        else:
            print "PASS: findFocusByName returns " + str(answer2) + " for yes2"
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
        # tests for findFocusByID
        ans = testStore.findFocusByID([1163, 4641, 4643, 4658, 4659, 4660, 4661, 4662, 4663, 4664, 4665, 4666, 4668, 4678])


        if ans == 0:
            print "FAIL: findFocusByID can't find [1163, 4641, 4643, 4658, 4659, 4660, 4661, 4662, 4663, 4664, 4665, 4666, 4668, 4678]"
        else:
            print "PASS: findFocusByID returns " + str(ans) + " for [1163, 4641, 4643, 4658, 4659, 4660, 4661, 4662, 4663, 4664, 4665, 4666, 4668, 4678]"
        # better safe than...    
        testStore.abortTransaction()
        

def test5(db):
    """ Tests enterResourceConstraints, lookupConstraints, lookupConstraint
        Returns True if all tests pass; False if some fail
    """
    returnFlag = True
    testConnection = testStore.connectToDB(testStore.NO_WRITE, dbname, dbpwd, dbfullname)
    # for now, can't continue with testing if no DB connection
    if testConnection == False:
        print "FAIL: test5:  unable to connect."
        return False
    else:
        print "PASS: test5: able to connect."
        #add resources to db, then build the constraints 
        p1 = testStore.createResource (None, None, "ParentA", "ParentA-type")
        p2 = testStore.createResource (None, None, "ParentB", "ParentB-type")
        if (p1 == None or p2 == None):
            print "ERROR: test5: unable to create resource(s) for test"
            returnFlag = False
            testStore.abortTransaction()
            testStore.closeDB()
            return returnFlag
        c1 = testStore.createResource (None, p1, "ChildA", "ChildA-type")
        c2 = testStore.createResource (None, p1, "ChildB", "ChildB-type") 
        c3 = testStore.createResource (None, p1, "ChildC", "ChildC-type")
        c4 = testStore.createResource (None, p2, "ChildD", "ChildD-type")
        c5 = testStore.createResource (None, p2, "ChildE", "ChildE-type")
        c6 = testStore.createResource (None, p2, "ChildF", "ChildF-type")
        if (c1 == None or c2 == None or c3 == None or c4 == None \
            or c5 == None or c6 == None):
            print "Error: test5: unable to create resource(s) for test" 
            returnFlag = False
            testStore.abortTransaction()
            testStore.closeDB()
            return returnFlag

        #enter id with to_constraint list of ids that are not children  of id
        print "\n5.1: Test enterResourceConstraints, lookupConstraint, lookupConstraints "
        print "     Create constraints such that the from-to relationship is not a parent-child relationship."

        try:
            testStore.enterResourceConstraints (p1, [p2, c4, c5])
        except:
            print "FAIL: enterResourceConstraints: valid resource_item ids should pass test"
        else:
            print "PASS: enterResourceConstraints: valid resource_item ids entered as constraints"
            #look up the contstraints just built with lookupConstraint()
            if not testStore.lookupConstraint(p1,p2):
                print "FAIL: lookupConstraint (%d, %d)" % (p1, p2)
                returnFlag = False
            else:
                print "PASS: lookupConstraint (%d, %d)" % (p1, p2)
            if not testStore.lookupConstraint(p1,c4):
                print "FAIL: lookupConstraint (%d, %d)" % (p1, c4)
                returnFlag = False
            else:
                print "PASS: lookupConstraint (%d, %d)" % (p1, c4)
            if not testStore.lookupConstraint(p1,c5):
                print "FAIL: lookupConstraint (%d, %d)" % (p1, c5)
                returnFlag = False
            else:
                print "PASS: lookupConstraint (%d, %d)" % (p1, c5)
            #look up all constraints using lookupConstraints()
            if not testStore.lookupConstraints(p1,[p2,c4,c5]):
                print "FAIL: lookupConstraints (%d, [%d, %d, %d])" % (p1,p2,c4,c5)
                returnFlag = False
            else:
                print "PASS: lookupConstraints (%d, [%d, %d, %d])" % (p1,p2,c4,c5)

        #enter id with to_constraint list of ids where some are children of id
        print "\n5.2: Test enterResourceConstraints, lookupConstraint, lookupConstraints "
        print "     Create constraints such that the from-to relationship is a parent-child relationship."
        print "     A parent-child relationship should not be entered explicitly into the resource_constraint"
        print "     table as a from-to relationship"

        try:
            testStore.enterResourceConstraints (p1, [c1, c2, c3])
        except:
            print "PASS: enterResourceConstraints: parent-child relationships are not allowed as from-to"
            print "      relationships in resource_constraint"
        else:
            # Technically a failure of the description of resource_constraints table, 
            # which states that the table is for relationships between resources that are not
            # parent/child relationships.
            #look up all constraints using lookupConstraints()
            if testStore.lookupConstraints(p1,[c1,c2,c3]):
                print "FAIL: lookupConstraints (%d, [%d, %d, %d])" % (p1,c1,c2,c3)
                print "      %d is parent of %d, %d, and %d" % (p1,c1,c2,c3)
                returnFlag = False 
            else:
                print "PASS: lookupConstraints (%d, [%d, %d, %d])" % (p1,c1,c2,c3)
                print "      The constraints were not added because %d is parent of" % (p1)
                print "      %d, %d, and %d" % (c1, c2, c3)   

        #enter id with to_constraint list of ids where some ids do not already exist in resource_item
        print "\n5.3: Test enterResourceConstraints"
        print "     Create constraints where some of the ids (from_resource id or in the to_resource list)"
        print "     This should not be allowed because both elements of resource_constraint refer to" 
        print "     existing resource items" 
        
        sql = "select MAX(id) from resource_item"
        testStore.cursor.execute(sql)  
        maxid, = testStore.cursor.fetchone()
        #print "Max resource_item id is %d" % maxid
        if maxid != None and maxid > 0:
            notAnId1 = maxid+100
            notAnId2 = maxid+200
            notAnId3 = maxid+300
            notAnId4 = maxid+400
        else:
            print "ERROR: test5: sql query did not execute properly"
            testStore.abortTransaction()
            testStore.closeDB()
            return returnFlag

        # test all ids do not exist 
        try:
            testStore.enterResourceConstraints (notAnId1, [notAnId2, notAnId3, notAnId4])
        except:
            print "PASS: enterResourceConstraints (%d, [%d, %d, %d])" % (notAnId1,notAnId2,notAnId3,notAnId4)
            print "      the resources do not exist in resource_item." 
        else:
            print "FAIL: enterResourceConstraints (%d, [%d, %d, %d])" % (notAnId1,notAnId2,notAnId3,notAnId4)
            print "      %d, %d, %d, and %d do not exist in resource_item." % (notAnId1,notAnId2,notAnId3,notAnId4) 
            returnFlag = False

        # test from_resource id does not exist, but to_resource ids do exist
        try:
            testStore.enterResourceConstraints (notAnId1, [c4, c5, c6])
        except:
            print "PASS: enterResourceConstraints (%d, [%d, %d, %d])" % (notAnId1,c4,c5,c6)
            print "      the from_resource does not exist in resource_item."
        else:
            print "FAIL: enterResourceConstraints (%d, [%d, %d, %d])" % (notAnId1,c4,c5,c6)
            print "      %d does not exist in resource_item." % (notAnId1)
            returnFlag = False

        # test from_resource id exists, but to_resource ids do not exist
        try:
            testStore.enterResourceConstraints (p2, [notAnId1,notAnId2,notAnId3])
        except:
            print "PASS: enterResourceConstraints (%d, [%d, %d, %d])" % (p2,notAnId1,notAnId2,notAnId3)
            print "      the to_resources do not exist in resource_item."
        else:
            print "FAIL: enterResourceConstraints (%d, [%d, %d, %d])" % (p2,notAnId1,notAnId2,notAnId3)
            print "      %d, %d, and %d do not exist in resource_item." % (notAnId1,notAnId2,notAnId3)
            returnFlag = False

    testStore.abortTransaction()
    testStore.closeDB()
    return returnFlag

def test6(db):
    """ Tests enterResourceAVs, lookupAttributes, lookupAttribute
        Returns true if all tests pass; false if some fail
    """
    returnFlag = True
    testConnection = testStore.connectToDB(testStore.NO_WRITE, dbname, dbpwd, dbfullname)
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
    #test: enter some valid resource_attibute (name,value) pairs for the resources created above 
    print "\n6.1: Test enterResourceAVs, lookupAttribute, lookupAttributes "
    print "     Enter (attribute,value) pairs for valid resources."

    try:
        testStore.enterResourceAVs(p1, [d1])          # a list of 1
    except:
        print "FAIL: enterResourceAVs: valid (name,value) pair for a valid resource_id"
        returnFlag = False
    else:
        print "PASS: enterResourceAVs: valid (name,value) pair for a valid resource_id"
    try:
        testStore.enterResourceAVs(p2, [d1,d2,d3,d4]) # a list of several
    except:
        print "FAIL: enterResourceAVs: a list of valid (name,value) pairs for a valid resource_id"
        returnFlag = False
    else:
        print "PASS: enterResourceAVs: a list of valid (name,value) pairs for a valid resource_id"

    #test: lookup attributes created in above test with lookupAttribute()
    if not testStore.lookupAttribute (p1, d1["name"], d1["value"] ):
        print "FAIL: lookupAttribute: valid (%s, %s) entered for resource %d" % (d1["name"],d1["value"], p1)
        print "      not found"
        returnFlag = False
    else:
        print "PASS: lookupAttribute: found (%s, %s) entered for resource %d" % (d1["name"],d1["value"], p1)

    if not testStore.lookupAttribute (p2, d1["name"], d1["value"]):
        print "FAIL: lookupAttribute: valid (%s, %s) entered for resource %d" % (d1["name"],d1["value"], p2)
        print "      not found"
        returnFlag = False
    else:
        print "PASS: lookupAttribute: found (%s, %s) entered for resource %d" % (d1["name"],d1["value"], p2)

    if not testStore.lookupAttribute (p2, d4["name"], d4["value"] ):
        print "FAIL: lookupAttribute: valid (%s, %s) entered for resource %d" % (d4["name"],d4["value"], p2)
        print "      not found"
        returnFlag = False
    else:
        print "PASS: lookupAttribute: found (%s, %s) entered for resource %d" % (d4["name"],d4["value"], p2)

    #test: lookup attributes created above with lookupAttributes()
    if not testStore.lookupAttributes (p1, [(d1["name"],d1["value"])]):
        print "FAIL: lookupAttributes: valid (%s, %s) entered for resource %d" % (d1["name"],d1["value"], p1)
        print "      not found"
        returnFlag = False
    else:
        print "PASS: lookupAttributes: found (%s, %s) entered for resource %d" % (d1["name"],d1["value"], p1)
    if not testStore.lookupAttributes (p2, [(d1["name"],d1["value"]),(d2["name"],d2["value"]), 
                                            (d3["name"],d3["value"]),(d4["name"],d4["value"])]):
        print "FAIL: lookupAttributes: valid (name, value) list entered for resource %d not found" % (p2)
        returnFlag = False
    else:
        print "PASS: lookupAttributes: found list of (name,value) pairs entered for resource %d" % (p2)

    #test: enter some invalid resource_attibute (name,value) pairs for invalid resources
    print "\n6.2: Test enterResourceAVs, lookupAttribute, lookupAttributes "
    print "     Enter valid and invalid (attribute,value) pairs for invalid resources."
    sql = "select MAX(id) from resource_item"
    testStore.cursor.execute(sql)
    maxid, = testStore.cursor.fetchone()
    sql = "select MAX(resource_id) from resource_attribute"
    testStore.cursor.execute(sql)
    maxresid, = testStore.cursor.fetchone()
    print "Max resource_item id is %d" % (maxid)
    print "Max resource_attribute resource_id is %d" % (maxresid) 
    #invalid resource ids
    try:
        testStore.enterResourceAVs(maxid+100, [d1])          # a list of 1
    except:
        print "PASS: enterResourceAVs: not allowed to enter a (name,value) pair for a resource_id that does not exist"
    else:
        print "FAIL: enterResourceAVs: allowed to enter a (name,value) pair for a resource_id that does not exist"
        retrurnFlag = False 
    try:
        testStore.enterResourceAVs(maxid+200, [d1,d2,d3])          # a list of 1
    except:
        print "PASS: enterResourceAVs: not allowed to enter a list of (name,value) pairs"
        print "      for a resource_id that does not exist"
    else:
        print "FAIL: enterResourceAVs: allowed to enter a list of (name,value) pairs "
        print "      for a resource_id that does not exist"
        retrurnFlag = False
    #invalid attribute,value pairs
    try:
        testStore.enterResourceAVs(c1, [noValue])
    except:
        sql = "select count(*) from resource_attribute where resource_id = " + str(c1)
        testStore.cursor.execute(sql)
        count, = testStore.cursor.fetchone()
        if count == 0:
            print "PASS: enterResourceAVs: not allowed to enter a (name,value) pair that does not have a value"
        else:
            print "FAIL: enterResourceAVs: (name,value) pair without a value should not cause there"
            print "      to be any entries in resource_attribute for id %d" % (c1) 
    else:
        print "FAIL: enterResourceAVs: allowed to enter a (name,value) pair that does not have a value"
        retrurnFlag = False
    try:
        testStore.enterResourceAVs(c1, [noName])
    except:
        sql = "select count(*) from resource_attribute where resource_id = " + str(c1)
        testStore.cursor.execute(sql)
        count, = testStore.cursor.fetchone()
        if count == 0:
            print "PASS: enterResourceAVs: not allowed to enter a (name,value) pair that does not have a name"
        else:
            print "FAIL: enterResourceAVs: (name,value) pair without a name should not cause there" 
            print "      to be any entries in resource_attribute for id %d" % (c1)
    else:
        print "FAIL: enterResourceAVs: allowed to enter a (name,value) pair that does not have a name"
        retrurnFlag = False

    # test: lookupAttribute with invalid resource_id
    if testStore.lookupAttribute (maxid+300, d4["name"], d4["value"] ):
        print "FAIL: lookupAttribute: invalid resource_id of %d should cause lookupAttribute to fail" % (maxid+300)
        sql = "select count(*) from resource_attribute where resource_id = " + str(maxid+300)
        print "    Execute following query: " + sql
        testStore.cursor.execute(sql)
        cnt, = testStore.cursor.fetchone()
        if cnt != 0:
           print "??HUH?? the query works says count = " + str(cnt) + "! How can this be?"
        else:
           print "the query says count = " + str(cnt) 
        returnFlag = False
    else:
        print "PASS: lookupAttribute: invalid resource_id caused lookupAttribute to fail"

    #test: lookupAttribute with valid resource_item id that is not a resource_attribute resource_id
    rangelist = range(1,maxid+1)
    doesNotExist = 0
    for x in rangelist:
        sql = "select count(*) from resource_attribute where resource_id = " + str(x)
        testStore.cursor.execute(sql)
        cnt, = testStore.cursor.fetchone()
        if cnt == 0:
            doesNotExist = x
            break    
    if testStore.lookupAttribute (doesNotExist, d4["name"], d4["value"] ):
        print "FAIL: lookupAttribute: resource_id %d does not exist in resource_attribute." % (doesNotExist)
        print "      This should cause lookupAttribute to fail"
        returnFlag = False
    else:
        print "PASS: lookupAttribute: valid resource_item id %d which is an invalid" % (doesNotExist)
        print "      resource_attribute resource_id caused lookupAttribute to fail"

    #test: lookup attribute with invalid name or value
    if testStore.lookupAttribute (p1, "Not a Name", "Not a Value"):
        print "FAIL: (name,value) of (Not a Name, Not a Value) is not a valid"
        print "      name,value pair and should cause lookupAttribute to fail"
        returnFlag = False
    else:
        print "PASS: (name,value) of (Not a Name, Not a Value) caused lookupAttribute to fail"
    if testStore.lookupAttribute (p1, "Not a Name", d1["value"]):
        print "FAIL: (name,value) of (Not a Name, " + str(d1["value"]) + ") has invalid name"
        print "      and should cause lookupAttribute to fail"
        returnFlag = False
    else:
        print "PASS: (name,value) of (Not a Name, " + str(d1["value"]) + ") caused lookupAttribute to fail"
    if testStore.lookupAttribute (p1, d1["name"], "Not a Value"):
        print "FAIL: (name,value) of (" + str(d1["name"]) + ", Not a Value) has invalid value"
        print "      and should cause lookupAttribute to fail"
        returnFlag = False
    else:
        print "PASS: (name,value) of (" + str(d1["name"]) + ", Not a Value) caused lookupAttribute to fail"

    #test: lookup attributes with invalid resource_id
    if testStore.lookupAttributes (maxid+400, [(d1["name"],d1["value"])]):
        print "FAIL: lookupAttributes: resource_id %d does not exist in resource_attribute" % (maxid+400)
        print "      and should cause lookup attributes to fail"
        returnFlag = False
    else:
        print "PASS: lookupAttributes: resource_id %d does not exist in resource_attribute" % (maxid+400)
        print "      and did not cause lookupAttributes to fail"
    if testStore.lookupAttributes (doesNotExist, [(d1["name"],d1["value"])]):   
        print "FAIL: lookupAttributes: resource_id %d does not exist in resource_attribute." % (doesNotExist)
        print "      This should cause lookupAttributes to fail"

    else:
        print "PASS: lookupAttributes: valid resource_item id %d which is an invalid" % (doesNotExist)
        print "      resource_attribute resource_id caused lookupAttributes to fail"
 

    #test: lookupAttributes with invalid (name,value) list

    testStore.abortTransaction()
    testStore.closeDB()
    return returnFlag


def test7(db):
    """ Tests getHardwareId, getBuildName, getExecutionName

    """
    print "test7 is just a placeholder right now."
def test8(testStore):
    """ Tests getChildResources, getAncestors , getDescendants, addAncestors
        addDescendants
 
    """
#    good1 = 2  # Frost. has children. has anscestor. has too many descendants
#    good2 = 12174 # a compiler resource. no children. no ancestor. no desc
#    good3 =  13263 # a thread resource. has ancestors. no desc
#    good4 = 13126 # an execution resource. has descendants in several levels
#    good5 = 13262 # a process resource. has one level of desc
    bad1 = None
    bad2 = 0

    testConnection = testStore.connectToDB(testStore.NO_WRITE, dbname, dbpwd, dbfullname)
    # for now, can't continue with testing if no DB connection
    if testConnection == False:
        print "FAIL: ancestors/descendants:  unable to connect."
        return False
    else:
        good1 = int(testStore.findResourceByShortNameAndType("grid/machine",\
                   "Frost"))
        good2 = int(testStore.findResourceByShortNameAndType("inputDeck", \
                   "iq.h-33"))
        good3 = int(testStore.findResourceByName("/irs-8-545/Process-38/Thread-0"))
        good4 = int(testStore.findResourceByName("/irs-8-545"))
        good5 = int(testStore.findResourceByName("/irs-8-545/Process-38"))

        answer1 = testStore.getChildResources(good1)
        if answer1 == []:
            print "FAIL: getChildResources can't find children of %d" % good1
        else:
            print "PASS: ans/desc find a child " + str(answer1) + " for " +\
                  str(good1)

        answer2 = testStore.getChildResources(good2)
        if answer2 != []:
            print "FAIL: getChildResources found children of %d" % good3
        else:
            print "PASS: ans/desc did not find a child "+str(answer2)+" for " +\
                  str(good2)

        answer3 = testStore.getChildResources(bad1)
        if answer3 != []:
            print "FAIL: getChildResources found children of %d" % bad1
        else:
            print "PASS: ans/desc did not find a child "+str(answer3)+" for " +\
                  str(bad1)

        answer4 = testStore.getChildResources(bad2)
        if answer4 != []:
            print "FAIL: getChildResources found children of %d" % bad2
        else:
            print "PASS: ans/desc did not find a child "+str(answer4)+" for " +\
                  str(bad2)

        answer5 = testStore.getAncestors(good1)
        if answer5 == []:
            print "FAIL: getAncestors can't find ans of %d" % good1
        else:
            print "PASS: ans/desc finds ancestors " + str(answer5) + " for " +\
                  str(good1)


        answer5a = testStore.getAncestors(good3)
        if answer5a == []:
            print "FAIL: getAncestors can't find ans of %d" % good3
        else:
            print "PASS: ans/desc finds ancestors " + str(answer5a) + " for " +\
                  str(good3)

        answer6 = testStore.getAncestors(good2)
        if answer6 != []:
            print "FAIL: getAncestors found ans of %d" % good2
        else:
            print "PASS: ans/desc did not find ancestors " + str(answer6) +\
                  " for " + str(bad1)

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

def test9(testStore):
    testConnection = testStore.connectToDB(testStore.NO_WRITE, dbname, dbpwd, dbfullname)
    # for now, can't continue with testing if no DB connection
    if testConnection == False:
        print "FAIL: ancestors/descendants:  unable to connect."
        return False

    result = testStore.addResource("/icc", "execution")
    print "result: %d for adding /icc execution"  % result
    result = testStore.addResource("/icc", "execution")
    print "result: %d for adding /icc execution"  % result
    result = testStore.addResource("/icc-12", "execution")
    print "result: %d for adding /icc execution"  % result
    result = testStore.addResource("/icc-12", "execution")
    print "result: %d for adding /icc execution"  % result

    result = testStore.getNewResourceName("/icc")
    print "result: %s for adding /icc" % result 
    result = testStore.getNewResourceName("/icc")
    print "result: %s for adding /icc" % result 
    result = testStore.getNewResourceName("/frank")
    print "result: %s for adding /frank" % result 

    testStore.abortTransaction() 



dbname = raw_input("Please enter your database username: ")
dbfullname = raw_input("Please enter the tnsname for the database: ")
dbpwd = getpass("Please enter your database password: ")


testStore = PTdataStore()

print "test1 real"
test1(testStore, dbname, dbpwd, dbfullname)
print "test1 fakename"
test1(testStore, "lalala", dbpwd, dbfullname)
print "test1 fakepwd"
test1(testStore, dbname, "lalala", dbfullname)
print "test1 fakefullname"
test1(testStore, dbname, dbpwd, "lalala")
print "test2"
test2(testStore)
print "test3"
test3(testStore)
print "test4"
test4(testStore)
print "test8"
test8(testStore)
print "test9"
test9(testStore)


