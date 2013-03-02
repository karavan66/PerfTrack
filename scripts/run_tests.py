#!/usr/bin/env python

import subprocess
import os,sys
from env import *

def load_db(repo, dbname, files, outfile):
    dbinfo = os.environ.get('DBPASS').split(",")
    dbinfo[0] = dbname
    os.environ['DBPASS'] = ",".join(dbinfo)
    os.system("createdb %s" % dbname)
    
    env_db(repo)
    init_db(repo)
    
    for f in files:
        print os.environ['DBPASS'], os.environ['PYTHONPATH']
        sys_cmd = "%s %s > /dev/null" % (ptdf(repo), (f % repo))
        print "Running: %s" % sys_cmd
        if os.system(sys_cmd) != 0:
            print "Failed to load %s" % (f % repo)

    os.system("pg_dump %s > %s" % (dbname, outfile))
    
    
def run_tests():
    if (os.environ.get('DBPASS') == None):
        print "Set the DBPASS environment variable"
        sys.exit(1)
    passes = 0
    fails = 0
    repo = env_db()
    if os.path.isdir(repo + '/../pt_old'):
        test_files = ["%s/tests/PTdFgenTestData/irs-good-reference.ptdf"]
        load_db(repo, 'temp1', test_files, "temp1_out")
        load_db(repo + '/../pt_old/', 'temp2', test_files, "temp2_out")
        p = subprocess.Popen("diff temp1_out temp2_out | wc -l", shell=True, stdout=subprocess.PIPE)
        diffs = int(p.stdout.read())
        os.system("rm temp1_out temp2_out")
        expected = 4
        print "# Differences %s (%s is expected)" % (diffs, expected)
        if (diffs != expected):
            fails += 1
        else:
            passes += 1

    repo = env_db()
    init_db(repo)
    os.chdir(repo + "/tests")

    print "Loading Default Machines"
    if os.system("%s %s/etc/PTdefaultMachines.ptdf" % (ptdf(repo), repo)) != 0:
        print "Failed to load PTDefaultMachines"
        return 1

    tests = ["./PTdFgenTester.py --data_dir %s/tests/PTdFgenTestData" % repo,
             "./combPRtest.py",
             "./PTdataStore_PTpyDBAPItester.py",
             "./ptdfClassesTester.py",
             "./hardwareTester.py",
             "./PTdS_testsCall.py",
             "./test_orderParams.py"]

    t_count = 0
    for t in tests:
        t_count += 1
        print "Running test %s/%s" % (t_count, len(tests))
        if os.system(t) == 0:
            passes += 1
        else:
            fails += 1


    print("Total Passed: %s Total Failed %s" % (passes, fails))
    return fails
    
sys.exit(run_tests() > 0)
