class PTdS_t7:

	def __init__(self, pf):
		self.pf = pf

	def test7(self, testStore):
	    """ Tests addResource, getNewResourceName
	    """
	    #testConnection = testStore.connectToDB(testStore.NO_DEBUG, dbname, dbpwd, dbfullname)
	    #testConnection = testStore.connectToDB(testStore.NO_COMMIT, dbhost, dbname, dbuser, dbpwd)
	    testConnection = testStore.connectToDB(testStore.NO_COMMIT)
	    # for now, can't continue with testing if no DB connection
	    if testConnection == False:
	        self.pf.failed("test9: addResource/getNewResourceName:  unable to connect.")
		self.pf.failed("Test 7.0 - FAIL - addResource/getNewResourceName unable to connect.\n")
	        return False
	
	    result = testStore.addResource("/testName", "execution")
	    if result == 0:
	        self.pf.failed("addResource: did not add resource with name /testName and type /execution")
		self.pf.failed("Test 7.1 - FAIL - addResource did not add resource with name /testName and type /execution.")
	    else:
	        self.pf.passed("addResource: returned id  %d for adding name /testName and type /execution"  % result)
		self.pf.passed("Test 7.1 - PASS - returned id result for adding name /testName and type /execution.\n")
	
	    result = testStore.addResource("/testName", "execution")
	    if result != 0:
	        self.pf.failed("addResource: returned %d for adding resource name and type that exist"  % result)
		self.pf.failed("Test 7.2 - FAIL - addResource: returned %d for adding resource name and type that exist.\n")
	    else:
	        self.pf.passed("addResource: returned 0 for trying to add resource name and type that exist")
		self.pf.passed('Test 7.2 - Pass - addResource returned 0 for trying to add resource name and type that exist.\n')
	
	    result = testStore.addResource("/testName-12", "execution")
	    if result == 0:
	        self.pf.failed("addResource: did not add resource with name /testName-12 and type /execution")
		self.pf.failed("Test 7.3 - addResource did not add resource with /testName-12 and type /execution.\n")
	    else:
	        self.pf.passed("addResource: returned id  %d for adding name /testName-12 and type /execution"  % result)
		self.pf.passed("Test 7.3 - addResource returned id %d for adding name /testName-12 and type /execution.\n")
	
	    result = testStore.addResource("/testName-12", "execution")
	    if result != 0:
	        self.pf.failed("addResource: returned %d for adding resource name and type that exist"  % result)
		self.pf.failed("Test 7.4 - addResource returned %d for adding resource name and type that exist.\n")
	    else:
	        self.pf.passed("addResource: returned 0 for trying to add resource name and type that exist")
		self.pf.passed("Test 7.4 - addResource returned 0 for trying to add resource name and type that exist.\n")
	


	    result = testStore.getNewResourceName("/testName")
	    if result == "/testName":
	        self.pf.failed("getNewResourceName returned the givenName -- check debug level")
		self.pf.failed("Test 7.5 - getNewResourceName returned the giveName -- check debug level.\n")
	    else:
	        self.pf.passed("getNewResourceName returned new name: %s for adding /testName" % result )
		self.pf.passed("Test 7.5 - getNewResourceName returned new game: %s for adding /testName.\n")

	    result2 = testStore.getNewResourceName("/testName")
	    if result2 == "/testName":
	        self.pf.failed("getNewResourceName returned the givenName -- check debug level")
		self.pf.failed("Test 7.6 - getNewResourceName returned the givenName -- check debug level.\n")
	    elif result2 == result:
	        self.pf.failed("getNewResourceName returned name: %s, which is already assigned" % result2 )
		self.pf.failed("Test 7.6 - getNewResourceName returned name: %s, which is already assigned.\n")
	    else:
	        self.pf.passed("getNewResourceName returned new name: %s for adding /testName , which is different from %s" %(result2, result))
		self.pf.passed("Test 7.6 - getNewResourceName returned new name: %s fora dding /testName, which is different from %s.\n")
	
	    result3 = testStore.getNewResourceName("/aNameThatDoesNotExist")
	    if result3 == "/aNameThatDoesNotExist":
	        self.pf.failed("getNewResourceName returned the givenName -- check debug level")
		self.pf.failed("Test 7.7 - getNewResourceName returned the givenName -- check debug level.\n")
	    else:
	        self.pf.passed("getNewResourceName returned %s for adding /aNameThatDoesNotExist" % result3 )
		self.pf.passed("Test 7.7 - getNewResourceName returned %s for adding /aNameThatDoesNotExist.\n")
	
	    testStore.abortTransaction() 
	    testStore.closeDB()

