class PTdS_t7:

	def __init__(self, outFile):
		self.out = outFile

	def test7(self, testStore):
	    """ Tests addResource, getNewResourceName
	    """
	    #testConnection = testStore.connectToDB(testStore.NO_DEBUG, dbname, dbpwd, dbfullname)
	    #testConnection = testStore.connectToDB(testStore.NO_COMMIT, dbhost, dbname, dbuser, dbpwd)
	    testConnection = testStore.connectToDB(testStore.NO_COMMIT)
	    # for now, can't continue with testing if no DB connection
	    if testConnection == False:
	        print "FAIL: test9: addResource/getNewResourceName:  unable to connect."
		self.out.write("Test 7.0 - FAIL - addResource/getNewResourceName unable to connect.\n")
	        return False
	
	    result = testStore.addResource("/testName", "execution")
	    if result == 0:
	        print "FAIL: addResource: did not add resource with name /testName and type /execution"
		self.out.write("Test 7.1 - FAIL - addResource did not add resource with name /testName and type /execution.")
	    else:
	        print "PASS: addResource: returned id  %d for adding name /testName and type /execution"  % result
		self.out.write("Test 7.1 - PASS - returned id result for adding name /testName and type /execution.\n")
	
	    result = testStore.addResource("/testName", "execution")
	    if result != 0:
	        print "FAIL: addResource: returned %d for adding resource name and type that exist"  % result
		self.out.write("Test 7.2 - FAIL - addResource: returned %d for adding resource name and type that exist.\n")
	    else:
	        print "PASS: addResource: returned 0 for trying to add resource name and type that exist"
		self.out.write('Test 7.2 - Pass - addResource returned 0 for trying to add resource name and type that exist.\n')
	
	    result = testStore.addResource("/testName-12", "execution")
	    if result == 0:
	        print "FAIL: addResource: did not add resource with name /testName-12 and type /execution"
		self.out.write('Test 7.3 - FAIL - addResource did not add resource with /testName-12 and type /execution.\n')
	    else:
	        print "PASS: addResource: returned id  %d for adding name /testName-12 and type /execution"  % result
		self.out.write('Test 7.3 - PASS - addResource returned id %d for adding name /testName-12 and type /execution.\n')
	
	    result = testStore.addResource("/testName-12", "execution")
	    if result != 0:
	        print "FAIL: addResource: returned %d for adding resource name and type that exist"  % result
		self.out.write('Test 7.4 - FAIL - addResource returned %d for adding resource name and type that exist.\n')
	    else:
	        print "PASS: addResource: returned 0 for trying to add resource name and type that exist"
		self.out.write('Test 7.4 - PASS - addResource returned 0 for trying to add resource name and type that exist.\n')
	


	    result = testStore.getNewResourceName("/testName")
	    if result == "/testName":
	        print "FAIL: getNewResourceName returned the givenName -- check debug level"
		self.out.write('Test 7.5 - FAIL - getNewResourceName returned the giveName -- check debug level.\n')
	    else:
	        print "PASS: getNewResourceName returned new name: %s for adding /testName" % result 
		self.out.write('Test 7.5 - PASS - getNewResourceName returned new game: %s for adding /testName.\n')

	    result2 = testStore.getNewResourceName("/testName")
	    if result2 == "/testName":
	        print "FAIL: getNewResourceName returned the givenName -- check debug level"
		self.out.write('Test 7.6 - FAIL - getNewResourceName returned the givenName -- check debug level.\n')
	    elif result2 == result:
	        print "FAIL: getNewResourceName returned name: %s, which is already assigned" % result2 
		self.out.write('Test 7.6 - FAIL - getNewResourceName returned name: %s, which is already assigned.\n')
	    else:
	        print "PASS: getNewResourceName returned new name: %s for adding /testName , which is different from %s" %(result2, result)
		self.out.write('Test 7.6 - PASS - getNewResourceName returned new name: %s fora dding /testName, which is different from %s.\n')
	
	    result3 = testStore.getNewResourceName("/aNameThatDoesNotExist")
	    if result3 == "/aNameThatDoesNotExist":
	        print "FAIL: getNewResourceName returned the givenName -- check debug level"
		self.out.write('Test 7.7 - FAIL - getNewResourceName returned the givenName -- check debug level.\n')
	    else:
	        print "PASS: getNewResourceName returned %s for adding /aNameThatDoesNotExist" % result3 
		self.out.write('Test 7.7 - PASS - getNewResourceName returned %s for adding /aNameThatDoesNotExist.\n')
	
	    testStore.abortTransaction() 
	    testStore.closeDB()

