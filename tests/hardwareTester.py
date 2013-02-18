#!/usr/bin/env python

# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information. 

import Hardware,os
from PTexception import PTexception

dataDir = "badMachineFiles"
files = os.listdir(dataDir)
for f in files:
   print "processing:" + f
   try: 
      Hardware.getHardwareInfo(dataDir + "/" + f)
   except PTexception, a:
      print a.value
