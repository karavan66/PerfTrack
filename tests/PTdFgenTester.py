#!/usr/bin/env python

# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information. 

import sys,os
from glob import glob
from optparse import OptionParser
from getpass import getpass
from PTexception import PTexception
from PassFail import PassFail
import PTdFgen

class testData:
   def __init__(self, dataDir, username, password, dbname, hostname):
      self.tests = PassFail()
      self.args = {"--data_dir":dataDir,
                   "--dbname":dbname, 
                   "--password":password, 
                   "--username":username,
                   "--host":hostname,
                   "--testMode":''}

   def genArgs(self, more_args):
      #NOTE THAT MORE_ARGS OVERRIDES VALUES IN ARGS
      all_args = dict(list(self.args.items()) + list(more_args.items()))
      arg_list = [""]
      for key, value in all_args.iteritems():
         arg_list.append(key)
         arg_list.append(value)
      return arg_list


def announceTest(testName):
   print "** Running %s in %s **" % (testName, __file__)

def test1(td):
   # PTrunIndex.txt good, no problems, no oddities
   # PTrunIndex.txt.13 good run data file, but no libraries defined
   # PTrunIndex.txt.14 good run data file, but no input decks defined
   # PTrunIndex.txt.15 good run data file, but no input decks or libs defined
   # PTrunIndex.txt.19 good build data file, but no libs defined (sppm)
   # PTrunIndex.txt.20 good build data file, but no compilers defined
   # PTrunIndex.txt.21 good build data file, but no compilers or preprocs def'ed
   # PTrunIndex.txt.22 good build data file, but no comps,preprocs,or libs def'd
   testName = "test1"
   announceTest(testName)
   TIs = ["PTrunIndex.txt", "PTrunIndex.txt.13", "PTrunIndex.txt.14", 
          "PTrunIndex.txt.15", "PTrunIndex.txt.19", "PTrunIndex.txt.20",
          "PTrunIndex.txt.21", "PTrunIndex.txt.22", "PTrunIndex.txt.33"]

   for testIndex in TIs:
      try:
         PTdFgen.main(td.genArgs({
                  "--exec_data":"", 
                  "--testRunIndex":testIndex
                  }))
      except PTexception,a:
         td.tests.failed("%s : good input files given. PTexception raised: %s" % (testName,a.value))
      except:
         td.tests.failed("%s : good input files given. other exception raised" % testName)
         raise
      else:
         td.tests.passed("%s : good input files given." % testName)

def test2(td):
   # bad password 
   testName = "test2"
   announceTest(testName)
   try:
      PTdFgen.main(td.genArgs({
               "--exec_data":"", 
               "--testRunIndex":'PTrunIndex.txt', 
               '--password':'badPassword'
               }))
   except PTexception,a:
      td.tests.passed("%s : bad database password given. PTexception raised:%s" % (testName,a.value))
   except:
      td.tests.failed("%s : bad database password given. other exception raised." % testName)
      raise
   else:
      td.tests.failed("%s : bad database password given." % testName)
    
def test3(td):
   # bad username
   testName = "test3"
   announceTest(testName)
   try:
      PTdFgen.main(td.genArgs({
               "--exec_data":"", 
               "--testRunIndex":'PTrunIndex.txt', 
               '--username':'badUsername'
               }))
   except PTexception,a:
      td.tests.passed("%s : bad database username given. PTexception raised:%s" % (testName,a.value))
   except:
      td.tests.failed("%s : bad database username given. other exception raised." % testName)
      raise
   else:
      td.tests.failed("%s : bad database username given." % testName)

def test4(td):
   # bad PTrunIndex files. 
   # PTrunIndex.txt.1 is missing data on one line
   # PTrunIndex.txt.2 has additional data on one line
   # PTrunIndex.txt.3 points to non-existing data files
   testName = "test4"
   announceTest(testName)
   TIs = ["PTrunIndex.txt.1","PTrunIndex.txt.2","PTrunIndex.txt.3"]
   for testIndex in TIs:
      try:
         PTdFgen.main(td.genArgs({
                  "--exec_data":"", 
                  "--testRunIndex":testIndex
                  }))
      except PTexception,a:
         td.tests.passed("%s : bad PTrunIndex.txt given:%s. PTexception raised:%s"
                         % (testName,testIndex, a.value))
      except:
         td.tests.failed("%s : bad PTrunIndex.txt given:%s. other exception raised."
                         % (testName,testIndex))
         raise
      else:
         td.tests.failed("%s : bad PTrunIndex.txt given:%s." % (testName,testIndex))
   
def test5(td):
   # PTrunIndex.txt.5 build data file missing build machine information
   # PTrunIndex.txt.6 build data file missing build os name 
   # PTrunIndex.txt.18 build data file missing BuildDataEnd 
   # PTrunIndex.txt.26 build data file missing build os version 
   # PTrunIndex.txt.27 build data file missing build os release type
   # PTrunIndex.txt.28 build data file missing compiler name 
   testName = "test5"
   announceTest(testName)
   TIs = ["PTrunIndex.txt.5","PTrunIndex.txt.6","PTrunIndex.txt.18",\
          "PTrunIndex.txt.26", "PTrunIndex.txt.27", "PTrunIndex.txt.28"]
   for testIndex in TIs:
      try:
         PTdFgen.main(td.genArgs({
                  "--exec_data":"", 
                  "--testRunIndex":testIndex
                  }))
      except PTexception,a:
         td.tests.passed("%s : bad build data file. PTexception raised:%s" % (testName,a.value))
      except:
         td.tests.failed("%s : bad build data file. other exception raised. %s" % (testName, testIndex))
         raise
      else:
         td.tests.failed("%s : no notification bad build data file. %s" % (testName, testIndex))


def test6(td):
   # bad run data files. 
   # PTrunIndex.txt.7 is missing run machine name
   # PTrunIndex.txt.8 is missing run os name
   # PTrunIndex.txt.9 is mssing ThreadsPerProcess attribute
   # PTrunIndex.txt.10 is mssing NumberOfProcesses attribute
   # PTrunIndex.txt.11 is mssing LibraryName attribute in Lib definition
   # PTrunIndex.txt.12 is mssing InputDeckName attribute in inputdeck def
   # PTrunIndex.txt.16 is mssing RunDataEnd but has libs and idecks
   # PTrunIndex.txt.17 is mssing RunDataEnd has no libs or decks
   # PTrunIndex.txt.30 is missing run os version 
   # PTrunIndex.txt.31 is missing run os release type 
   # PTrunIndex.txt.32 is missing libmpi in the run data file for irs
   testName = "test6"
   announceTest(testName)
   TIs = ["PTrunIndex.txt.7","PTrunIndex.txt.8","PTrunIndex.txt.9",\
          "PTrunIndex.txt.10", "PTrunIndex.txt.11", "PTrunIndex.txt.12",\
          "PTrunIndex.txt.16", "PTrunIndex.txt.17", "PTrunIndex.txt.30",\
          "PTrunIndex.txt.31", "PTrunIndex.txt.32"]
   for testIndex in TIs:
      try:
         PTdFgen.main(td.genArgs({
                  "--exec_data":"", 
                  "--testRunIndex":testIndex
                  }))
      except PTexception,a:
         td.tests.passed("%s : bad run data file given:%s. PTexception raised:%s" 
                         % (testName,testIndex, a.value))
      except:
         td.tests.failed("%s : bad run data file given:%s. other exception raised."
                         % (testName,testIndex))
         raise
      else:
         td.tests.failed("%s : bad run data file given:%s." % (testName,testIndex))

def test7(td):  
   # bad sppm data files - detect incomplete run
   #PTrunIndex.txt.23 missing run termination line in output0
   testName = "test7"
   announceTest(testName)
   TIs = ["PTrunIndex.txt.23"]
   for testIndex in TIs:
      try:
         PTdFgen.main(td.genArgs({
                  "--exec_data":"", 
                  "--testRunIndex":testIndex
                  }))
      except PTexception,a:
         td.tests.passed("%s : bad sppm data file given:%s. PTexception raised:%s" 
                         % (testName,testIndex, a.value))
      except:
         td.tests.failed("%s : bad sppm data file given:%s. other exception raised." % (testName,testIndex))
         raise
      else:
         td.tests.failed("%s : bad sppm data file given:%s." % (testName,testIndex))

def test8(td):
   # bad irs data files - detect incomplete run
   #PTrunIndex.txt.24  incomplete hsp file
   #PTrunIndex.txt.25  incomplete tmr file
   testName = "test8"
   announceTest(testName)
   TIs = ["PTrunIndex.txt.24", "PTrunIndex.txt.25"]
   for testIndex in TIs:
      try:
         PTdFgen.main(td.genArgs({
                  "--exec_data":"", 
                  "--testRunIndex":testIndex
                  }))
      except PTexception,a:
         td.tests.passed("%s : bad irs data file given:%s. PTexception raised:%s"
                         % (testName,testIndex, a.value))
      except:
         td.tests.failed("%s : bad irs data file given:%s. other exception raised." % (testName,testIndex))
         raise
      else:
         td.tests.failed("%s : bad irs data file given:%s." % (testName,testIndex))

def main(argv=sys.argv):

   options = parseOptions(argv)
                      
   if options.dataDir:
      dataDir = options.dataDir
   else:
      dataDir = "PTdFgenTestData"

   if os.environ.get("DBPASS"):
      splitted = os.environ.get("DBPASS").split(",")
      username = splitted[2]
      password = splitted[3]
      tnsname = splitted[0]
      options.hostname = splitted[1]
   else:
      if options.username == None:
         username = raw_input("Please enter your database username: ")
      else:
         username = options.username
      if options.tnsname == None:
         tnsname = raw_input("Please enter the tnsname for the database: ")
      else:
         tnsname = options.tnsname
      password = getpass("Please enter your database password: ")

   td = testData(dataDir, username, password, tnsname, options.hostname)

   tests = [test1,test2,test3,test4,test5,test6,test7,test8]
   for test in tests:
       test(td)

   td.tests.test_info()

   return (td.tests.failed_count > 0)

def parseOptions(argv):
    """Parses command line arguments and returns their values"""
    
    usage = "usage: %prog [options]\nexecute '%prog --help' to see options"
    version = "%prog 1.0"
    parser = OptionParser(usage=usage,version=version)
    parser.add_option("-H", "--hostname", dest="hostname", default="localhost",
                      help="the hostname of the machine for the database")
    parser.add_option("-u","--username", dest="username",
                      help="the username for accessing the database")
    parser.add_option("-t","--tnsname", dest="tnsname", 
                      help="the full name of the database")
    parser.add_option("-d","--data_dir", dest="dataDir",
                      help="the name of the data directory")
    (options, args) = parser.parse_args(argv[1:])

    return options

if __name__ == "__main__":
   sys.exit(main())

