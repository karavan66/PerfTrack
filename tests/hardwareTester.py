#!/usr/bin/env python

# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information. 

import Hardware,os,sys
from PassFail import PassFail 
from PTexception import PTexception

dataDir = "badMachineFiles"
files = os.listdir(dataDir)
files.sort()
pf = PassFail()
for f in files:
   print "processing:" + f
   try: 
      Hardware.main(["", "--in_file", dataDir + "/" + f, "--out_file", "/dev/null"])
      pf.failed("Bad Machine Data for %s did not fail" % f)
   except PTexception, a:
      pf.passed("Intentional FAIL: %s" % a.value)

pf.test_info()

sys.exit(pf.failed_count > 0)
