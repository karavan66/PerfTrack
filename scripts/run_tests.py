#!/usr/bin/env python

import subprocess
import os,sys
from env import *

def load_db(repo, dbname, files, outfile=None, split=False, reinit=False):
    dbinfo = os.environ.get('DBPASS').split(",")
    dbinfo[0] = dbname
    os.environ['DBPASS'] = ",".join(dbinfo)

    if (reinit):
        os.system("createdb %s" % dbname)
        env_db(repo)
        init_db(repo)
    
    if split:
        for f in files:
            sys_cmd = "%s %s" % (ptdf(repo), f % repo )
            if os.system(sys_cmd) != 0:
                print "Error loading files"
    else:
        final_files = " ".join([(f % repo) for f in files])
        sys_cmd = "python -m cProfile -s cumulative %s %s" % (ptdf(repo), final_files )
        if os.system(sys_cmd) != 0:
            print "Error loading files"

    if (outfile != None):
        os.system("pg_dump %s > %s" % (dbname, outfile))
    
def run_tests():
    if (os.environ.get('DBPASS') == None):
        print "Set the DBPASS environment variable"
        sys.exit(1)

    passes = 0
    fails = 0
    repo = env_db()
    init_db(repo)

    if False:
        os.system("/home/crzysdrs/test.sh")
        sys.exit(1)    


    if False and os.path.isdir(repo + '/../pt_data/'):
        test_files = [
            "%s/../pt_data/LD_A1_56p_2ppn_28n_IO-BASIC_even_forHema/",
            "%s/../pt_data/LD_A1_56p_2ppn_28n_IO-BASIC_even_forHema/01_machinePTDF",
            "%s/../pt_data/LD_A1_56p_2ppn_28n_IO-BASIC_even_forHema/02_esdcPTDF",
            "%s/../pt_data/LD_A1_56p_2ppn_28n_IO-BASIC_even_forHema/03_systemPTDF",
            "%s/../pt_data/LD_A1_56p_2ppn_28n_IO-BASIC_even_forHema/04_appPTDF_t01",
            "%s/../pt_data/LD_A1_56p_2ppn_28n_IO-BASIC_even_forHema/04_appPTDF_t02",
            "%s/../pt_data/LD_A1_56p_2ppn_28n_IO-BASIC_even_forHema/04_appPTDF_t03"]
        load_db(repo, 'ld', test_files)
        sys.exit(1)

    if False and os.path.isdir(repo + '/../pt_old'):
        test_files = ["%s/tests/PTdFgenTestData/irs-good-reference.ptdf"]
        load_db(repo, 'temp1', test_files, "temp1_out", reinit=True)
        load_db(repo + '/../pt_old/', 'temp2', test_files, "temp2_out", split=True, reinit=True)
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

    tests =  ["./PTdFgenTester.py --data_dir %s/tests/PTdFgenTestData" % repo,
              "./PTdS_test8.py"]
    load_db(repo, 'crzysdrs', ["%s/tests/PTdFgenTestData/sppm-2.ptdf",
                               "%s/tests/PTdFgenTestData/irs-2.ptdf", 
                               "%s/tests/PTdFgenTestData/irs-6.ptdf",
                               "%s/tests/PTdFgenTestData/irs-15.ptdf"])
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
