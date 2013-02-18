#!/usr/bin/env python

import sys, glob, shutil

# usage: progName ptDataDirectory
dataDir = sys.argv[1]

osFiles = glob.glob("%s/out.uname" % dataDir)
f = open(osFiles[0],'r')
lines = f.readlines()
if len(lines) == 0 or len(lines) < 5:
   print "FAIL: no OS information"
   sys.exit(1)
osName = lines[0].strip()
osReleaseType= lines[2].strip()
osVersion = lines[4].strip()
f.close()


envFiles = glob.glob("%s/out.env" % dataDir)
f = open(envFiles[0],'r')
lines = f.readlines()
if len(lines) == 0:
   print "FAIL: no env information"
   sys.exit(1)
envVars = ""
i = 0
for line in lines:
   # the last line is usually some run information and is not an environment
   # variable
   if i == (len(lines)-1) and line.startswith("Application") and line.find("resources:") >= 0:
      break
   if i == 0:
      envVars += line.strip()
   else:
      envVars += "@@@" + line.strip()
   i += 1

f.close()


runfiles = glob.glob("%s/*_run_*" % dataDir)
if len(runfiles) > 1:
   print "FAIL: more than one run file!"
   sys.exit(1)
runfile = runfiles[0]
f = open(runfile,'r')
lines = f.readlines()
newlines = []

for line in lines:
   if line.startswith("RunOSName="):
      newline = "RunOSName=%s\n" % osName
   elif line.startswith("RunOSReleaseVersion="):
      newline = "RunOSReleaseVersion=%s\n" % osVersion
   elif line.startswith("RunOSReleaseType="):
      newline = "RunOSReleaseType=%s\n" % osReleaseType
   elif line.startswith("RunEnv="):
      newline = envVars + "\n"
   else:
      newline = line
   newlines.append(newline)

f.close()

shutil.move(runfile,"%s.orig" % runfile)
f = open(runfile,'w')
f.writelines(newlines)
f.close()
