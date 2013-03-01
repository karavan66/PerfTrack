#!/usr/bin/env python

from subprocess import call
import os,sys

def ptdf(repo):
    return repo + "/src/dataStore/ptdf_entry.py"

def env_db():
    repo = os.path.dirname(os.path.realpath(__file__)) + "/.."
    os.environ['PYTHONPATH'] = ("%s/src/dataStore/:%s/src/data_collection" % (repo, repo))
    os.environ['PTDB'] = 'PG_PYGRESQL'
    return repo

def init_db(repo):

    if not os.environ.get('DBPASS'):
        print "Must set env var DBPASS=dbname,hostname,username,dbpassword"
        print "In DBPASS, username should be your username!"
        sys.exit(1)

    (dbname, hostname, username, password) = os.environ['DBPASS'].split(",")
    
    print "Recreating Database"
    os.system("psql -d %s < %s/db_admin/postgres/pdropall.sql" % (dbname, repo))
    os.system("psql -d %s < %s/db_admin/postgres/pcreate.sql" % (dbname, repo))
    print "PTDF Entry of Default Framework"
    os.system("%s %s/share/PTdefaultFocusFramework.ptdf" % (ptdf(repo), repo))
    os.system("%s %s/share/dataCenterResourceHierarchyExtensions.ptdf" % (ptdf(repo), repo))

def run_tests():
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

    passes = 0
    fails = 0
    t_count = 0
    for t in tests:
        t_count += 1
        print "Running test %s/%s" % (t_count, len(tests))
        if os.system(t) == 0:
            passes += 1
        else:
            fails += 1

    print "Loading Known Good IRS-Reference File"
    if os.system("%s %s/tests/PTdFgenTestData/irs-good-reference.ptdf" % (ptdf(repo), repo)) != 0:
        print "Failed to load irs-good-reference.ptdf"
        fails += 1

    print("Total Passed: %s Total Failed %s" % (passes, fails))
    return fails
    
sys.exit(run_tests() > 0)
