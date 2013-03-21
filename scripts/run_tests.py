#!/usr/bin/env python

import subprocess
import shutil
import os,sys,re
from env import *
from glob import glob

def repo_files(repo, files):
    return [(f % repo) for f in files]

def cleanup_file(f, func):
    with open(f, "r") as mod_file:
        lines = mod_file.readlines()
    with open(f, "w") as mod_file:
        for line in lines:
            mod_file.write(func(line))

def load_db(repo, files, split=False, reinit=False):
    if (reinit):
        env_db(repo)
        init_db(repo)

    if split:
        for f in files:
            sys_cmd = "%s %s" % (ptdf(repo), f)
            print sys_cmd
            if os.system(sys_cmd) != 0:
                print "Error loading files"
                return False
    else:
        final_files = " ".join(files)
        sys_cmd = "%s %s" % (ptdf(repo), final_files)
        print "DBPASS=%s PYTHONPATH=%s %s" % (os.environ.get("DBPASS"), 
                                              os.environ.get("PYTHONPATH"),
                                              sys_cmd)
        print sys_cmd
        if os.system(sys_cmd) != 0:
            print "Error loading files"
            return False

    return True

def run_test_set(tests, passes, fails):
    t_count = 0
    for t in tests:
        t_count += 1
        print "**************************** Running test %s/%s ****************************" \
            % (t_count, len(tests))
        print "%s" % t
        if os.system(t) == 0:
            passes += 1
            print "**************************** Test Passed %s/%s ****************************" \
                % (t_count, len(tests))
        else:
            fails += 1
            print "**************************** Test Failed %s/%s ****************************" \
                % (t_count, len(tests))
    return (passes, fails)

def run_tests(ld_data = None, hd_data = None):    
    if (os.environ.get('DBPASS') == None):
        print "Set the DBPASS environment variable"
        sys.exit(1)
    saved_dbpass = os.environ.get("DBPASS")

    update_dbpass(dbname='TEST_DB')

    passes = 0
    fails = 0
    repo = os.path.dirname(os.path.realpath(__file__)) + "/.."

    if ld_data != None and os.path.isdir(ld_data):
        test_files = [
            "%s" % ld_data,
            "%s/01_machinePTDF" % ld_data,
            "%s/02_esdcPTDF" % ld_data,
            "%s/03_systemPTDF" % ld_data,
            "%s/04_appPTDF_t01" % ld_data,
            "%s/04_appPTDF_t02" % ld_data,
            "%s/04_appPTDF_t03" % ld_data]
        if load_db(repo, test_files, reinit=True):
            passes += 1
        else:
            fails += 0
 
    if hd_data != None and os.path.isdir(hd_data):
        repo = env_db()
        def clean_run(line):
            line = re.sub(r"^RunMachine=nwiceb", "RunMachine=NWICE", line)
            line = re.sub(r"^jobName=.*$", "jobName=%s" % exec_name, line)
            line = re.sub(r"^RunDataBegin$", "RunDataBegin\nThreadsPerProcess=2\nNumberOfProcesses=2", line)
            return line

        def clean_build(line):
            line = re.sub(r"CompilerName=.*$", "CompilerName=arbitrary_compiler", line)
            return line

        def clean_sys(line):
            line = re.sub(r"^Resource NWICE grid\|machine", 
                          "Resource NWICE grid|machine\nResource NWICE|batch grid|machine|partition", line)
            return line

        exec_name = "nwchem-siosi6_224p-8ppn_NWICE-A1_HDfull_t01"
        
        if  not os.path.exists("%s/tmp" % repo):
            os.makedirs("%s/tmp" % repo)
        
        runs_dir = "%s/t1/output/perfTrackData_2011-04-25T15:49:00/" % hd_data
        cg_dir = "%s/t1/output/sysmpi-parsed/" % hd_data
        bld_file = "%s/tmp/%s.bld" % (repo, exec_name)
        run_file = "%s/tmp/%s.run" % (repo, exec_name)
        shutil.copyfile("%s/perftrack_build_nwchem-5.1_2009-03-06T00:21:37.nwiceb.txt" % runs_dir,
                        bld_file)
        shutil.copyfile("%s/perftrack_run_nwchem_2011-04-25T15:49:00.nwiceb.txt" % runs_dir,
                        run_file)
        
        cleanup_file(bld_file, clean_build)
        cleanup_file(run_file, clean_run)

        shutil.copyfile("%s/%s.sysmpi.rpt" % (cg_dir, exec_name),
                        "%s/tmp/%s.sysmpi.rpt" % (repo, exec_name))
        shutil.copyfile("%s/%s.sysmpi.0.cg" % (cg_dir, exec_name),
                        "%s/tmp/%s.sysmpi.0.cg" % (repo, exec_name))
        f = open ("%s/tmp/PTrunIndex.txt" % repo, "w")
        f.write("%s app-name MPI-OPENMP 2 2 2011-04-25T15:49:00 2011-04-25T15:49:00\n" % exec_name)
        f.close()
        load_db(repo, ["%s/tests/nwice.ptdf" % repo], reinit=True)
        tests =  ["%s/src/data_collection/PTdFgen.py --data_dir %s/tmp -e -s --split --perfTools=\"SYSMPI\" "
                  "-M NWICE -v" % (repo, repo)]
        (passes, fails) = run_test_set(tests, passes, fails)
        load_db(repo, ["%s/tests/nwice.ptdf" % repo], reinit=True)

        cleanup_file("%s/tmp/sys.ptdf" % repo, clean_sys)
        ptdfs = ["%s/tmp/sys.ptdf" % repo]
        globbed = glob("%s/tmp/%s*.ptdf" % (repo, exec_name))
        globbed.sort()
        ptdfs.extend(globbed)

        load_db(repo, ptdfs)

    basic_tests = True
    if basic_tests:
        repo = env_db()
        os.chdir(repo + "/tests")
        load_db(repo, ["%s/etc/PTdefaultMachines.ptdf" % repo], None, reinit=True)
        tests =  ["./PTdFgenTester.py --data_dir %s/tests/PTdFgenTestData" % repo]
        (passes, fails) = run_test_set(tests, passes, fails)
        
        load_db(repo, repo_files(repo, ["%s/tests/PTdFgenTestData/sppm-2.ptdf",
                                                   "%s/tests/PTdFgenTestData/irs-2.ptdf", 
                                                   "%s/tests/PTdFgenTestData/irs-6.ptdf",
                                                   "%s/tests/PTdFgenTestData/irs-15.ptdf"]))
    
        tests = ["./combPRtest.py",
                 "./PTdataStore_PTpyDBAPItester.py",
                 "./ptdfClassesTester.py",
                 "./hardwareTester.py",
                 "./PTdS_testsCall.py",
                 "./test_orderParams.py"]
        
        (passes, fails) = run_test_set(tests, passes, fails)
     
    oprofile_tests = True
    if oprofile_tests:
        repo = env_db()
        os.chdir(repo + "/")    
        tests = ["./src/data_collection/sys2machine.py -n localhost "
                 "-s %s/tests/system_details/SystemDetails.csv -m machine.temp" % repo,
                 "./src/data_collection/PTdFgen.py " \
                     "-m --machine_file machine.temp --machine_out %s/machine.ptdf" % repo,
                 "./src/data_collection/run_oprofile.py -n localhost -o %s/oprofile.ptdf" % repo]

        (passes, fails) = run_test_set(tests, passes, fails)

        load_db(repo, repo_files(repo, ["%s/machine.ptdf", "%s/oprofile.ptdf"]), reinit=True)
    
    print("Total Passed: %s Total Failed %s" % (passes, fails))
    return fails
    

#If you have downloaded some big data_sets:
#Enable it with something like this: hd_data = "/home/$USER/pt_data/HD_A1_224p_8ppn_28n_RAWDATA/"
#or ld_data ld_data=LD_A1_56p_2ppn_28n_IO-BASIC_even_forHema/
#and pass it to run_tests
failed = run_tests(
    #hd_data = "/home/%s/pt_data/HD_A1_224p_8ppn_28n_RAWDATA/" % os.environ.get("USER"),
    #ld_data = "/home/%s/pt_data/LD_A1_56p_2ppn_28n_IO-BASIC_even_forHema/" % os.environ.get("USER")
    ) > 0

if (not failed):
    print "*************** All Tests Passed *****************"
else:
    print "*************** One or more tests failed ******************"

sys.exit(failed)

