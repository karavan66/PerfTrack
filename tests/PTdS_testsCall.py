#!/usr/bin/env python

# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information.

import sys
from PTdS_test1 import PTdS_t1
from PTdS_test2 import PTdS_t2
from PTdS_test3 import PTdS_t3
from PTdS_test4 import PTdS_t4
from PTdS_test5 import PTdS_t5
from PTdS_test6	import PTdS_t6
from PTdS_test7 import PTdS_t7
from PTdS_test8 import *
from PTds import PTdataStore
from mx.DateTime import *
#from getpass import getpass

out = open('results', 'a')
out.write('\n' + ARPA.str(now()) + '\n')

testStore = PTdataStore()

test1 = PTdS_t1(out)
test2 = PTdS_t2(out)
test3 = PTdS_t3(out)
test4 = PTdS_t4(out)
test5 = PTdS_t5(out)
test6 = PTdS_t6(out)
test7 = PTdS_t7(out)
test8 = PTdS_t8()

##TEST 1 -- connection test
print "test1.2 - connect, no optional parameters"
#test1.test1_2(testStore)

print "test1.3 - connect, with optional parameters"
#test1.test1_3(testStore)

##TEST 2 -- resource tests
print "test 2 - tests resource scripts"
test2.test2_1(testStore)
test2.test2_2(testStore)
test2.test2_3(testStore)
test2.test2_4(testStore)
test2.test2_5(testStore)
test2.test2_6(testStore)
test2.test2_7(testStore)

##TEST 3 --
print "test 3 -- "
test3.test3_1(testStore)

##TEST 4 --
print "test 4 -- "
test4.test4_1(testStore)

##TEST5 --
print "test 5 -- "
test5.test5_1(testStore)

##TEST 6 --
print "test 6 -- "
test6.test6(testStore)

##TEST 7 --
print "test 7 -- "
test7.test7(testStore)

##TEST * --
print "test 8 -- combPRtest"

ptds = PTdataStore()
connected = ptds.connectToDB(False)
if not connected:
	print "could not connect to DB"
	sys.exit(0)

tests = [test8.test1,test8.test2,test8.test3,test8.test4,test8.test5,test8.test6,test8.test7,test8.test8]

for tests in tests:
	tests(ptds)
