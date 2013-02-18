#!/usr/bin/env python

## filename: pt_xt4_proc.py
## purpose:  attribute functions specific to Cray XT4 
## note: because the XT4 machines we are using run Compute
## Node Linux on the compute nodes, we are not looking in the usual
## locations for information. We assume that an ash script (or other
## method) has written files in the current working directory that
## contain the contents of /proc/cpuinfo and /proc/meminfo, etc.
## EXPECTED:
## /proc/cpuinfo in ./cpuinfo
## /proc/meminfo in ./meminfo
## /proc/partitions in ./partitions
## output of hostname in ./hostname
## output of arch in ./arch
## NOTE:  If you want to use these functions, specify the module
##        option when running systemScan.py and include this file.

import gm_hs_tools
import os, sys
import gmLogger
from PTcommon import my_exec2

__version__ = '1.0.1'
logObj = gmLogger.gmlog()

# Base Super Class
#class baseAttrib:
#        def attribFuncReq(self):
#                # This function must be implemented by the child class
#                # if not everything should break.
#                none #Requirements function implemented by child class
#
#        def attribFunc(self):
#                # This function must be implemented by the child class
#                # if not everything should break.
#                none #Attribute function implemented by child class
#
#        def attribDefaultName(self):
#                # So, we are assuming that an attribute class
#                # will know the atribute name that it
#                # is retrieving the attribute for. This can be
#                # over-ridden by the loacl database (Config file)
#                # or a call to the PTDB.
#                # If the child class does not implement we return
#                # an 'unknown' value.
#                return "noDefault_Unknown"
#
#        def attribDefaultResourceType(self):
#                # So, we are assuming that an attribute class
#                # will know the resource type that it
#                # is retrieving the attribute for. This can be
#                # over-ridden by the loacl database (Config file)
#                # or a call to the PTDB.
#                # If the child class does not implement we return
#                # an 'unknown' value.
#                return "noDefault_Unknown"
#
#        def attribDefaultResourceName(self):
#                # So, we are assuming that an attribute class
#                # will know the resource type that it
#                # is retrieving the attribute for. This can be
#                # over-ridden by the loacl database (Config file)
#                # or a call to the PTDB.
#                # If the child class does not implement we return
#                # an 'unknown' value.
#                return "noDefault_Unknown"

# ========================================================
# (Compute Node Linux) Number of Processors
# ========================================================
class attribFunc_cnl_numOfProc(gm_hs_tools.baseAttrib):

	def attribFuncReq(self):
		if os.path.isfile("./cpuinfo"):
			return 0
		else:
			return 1

	def attribFunc(self, resName=""):
		try:
			f=open('./cpuinfo', 'r')

			# Number of Processors
			# Count the number of occurences of processor
			attribValue  = 0
			for line in f:
				if line.startswith("processor"):
					attribValue = attribValue + 1
			
                        f.close()
			return attribValue
                except IOError:
                        pass

	def attribDefaultName(self):
		return "'numOfProc'"

	def attribDefaultResourceType(self):
		return "'Node'"

	def attribDefaultResourceName(self):
		return "'Unknown'"


# ========================================================
# (Compute Node Linux) Number of Cores
# ========================================================
class attribFunc_cnl_numOfCores(gm_hs_tools.baseAttrib):

        def attribFuncReq(self):
                if os.path.isfile("./cpuinfo"):
                        return 0
                else:
                        return 1

        def attribFunc(self, resName=""):
                try:
                        f=open('./cpuinfo', 'r')

                        # Total Number of Cores for the node
                        # Count the number of occurences of processor
                        attribValue  = 0
                        for line in f:
                                if line.startswith("processor"):
                                        attribValue = attribValue + 1

                        f.close()
                        return attribValue
                except IOError:
                        pass

        def attribDefaultName(self):
                return "'numOfCores'"

        def attribDefaultResourceType(self):
                return "'Node'"

        def attribDefaultResourceName(self):
                return "'Unknown'"

# ======================================================== 
# (Compute Node Linux) Number of Sockets 
# ========================================================
class attribFunc_cnl_numOfSockets(gm_hs_tools.baseAttrib):

        def attribFuncReq(self):
           if os.path.isfile("./cpuinfo"):
              return 0
           else:
              return 1

        def attribFunc(self, resName=""):
           try:
              f=open('./cpuinfo', 'r')
              procs = []
              aProc = [] 
              attribValue  = 0
              lines = f.readlines() 
              f.close()
              for line in lines:
                 if line.startswith("processor"):
                    if len(aProc) > 0:
                       procs.append(aProc)
                       aProc = []
                    aProc.append(line) 
                 else:
                    aProc.append(line)
              if len(aProc) > 0:
                 procs.append(aProc)
              sockets = set()
              for proc in procs:
                 for field in proc:
                    if field.startswith("physical"):
                       words = field.split()
                       sockets.add(words[3])
              numProcs = len(procs)
              attribValue = len(sockets)
              #print "Sockets=%d" % attribValue
              return attribValue
           except IOError:
              pass

        def attribDefaultName(self):
           return "'numOfSockets'"

        def attribDefaultResourceType(self):
           return "'Node'"

        def attribDefaultResourceName(self):
           return "'Unknown'"


# ========================================================
# (Compute Node Linux) Cores Per Socket
# ========================================================
class attribFunc_cnl_coresPerSocket(gm_hs_tools.baseAttrib):
        def attribFuncReq(self):
           if os.path.isfile("./cpuinfo"):
              return 0
           else:
              return 1

        def attribFunc(self, resName=""):
           try:
              f=open('./cpuinfo', 'r')
              lines = f.readlines()
              f.close()
              attribValue = "" 
              for line in lines:
                 if line.startswith("cpu cores"):
                    words = line.split()
                    attribValue = words[3] 
                 else:
                    continue
              #print "CoresPerSocket=%d" % int(attribValue)
              return attribValue
           except IOError:
              pass

        def attribDefaultName(self):
           return "'coresPerSocket'"

        def attribDefaultResourceType(self):
           return "'Node'"

        def attribDefaultResourceName(self):
           return "'Unknown'"



# ========================================================
#  (Compute Node Linux)CPU Vendor ID
# ========================================================
class attribFunc_cnl_CPUVendorID(gm_hs_tools.baseAttrib):

	def attribFuncReq(self):
		if os.path.isfile("./cpuinfo"):
			return 0
		else:
			return 1

	def attribFunc(self, resName=""):
		try:
			f=open('./cpuinfo', 'r')
                        #print "attribFunc() VENDOR_ID: resName=%s" % resName
			# Number of Processors
			# Count the number of occurences of processor
			attribValue = None
                        found = True
                        # if they don't send in a name, we'll just take the 1st one
                        if resName != "":
                           found = False
			for line in f:
                             if line.startswith("processor"): 
                                procName = line.split(":")[1].strip()
                                if procName == resName:
                                   found = True 
                                   #print "setting found to TRUE"
                             elif line.startswith("vendor_id"):
                                if found:
                                   attribValue = line.split(":")[len(line.split(":")) - 1].strip()
                                   found = False
                                   break
			
                        f.close()
			return attribValue
                except IOError:
                        pass

	def attribDefaultName(self):
                return "'vendorID'"

	def attribDefaultResourceType(self):
		return "'Processor'"

	def attribDefaultResourceName(self):
		#return "'0'"
                return "'Unknown'"
                #return "'cpu0'"

# ========================================================
#  (Compute Node Linux) CPU Model
# ========================================================
class attribFunc_cnl_CPUModel(gm_hs_tools.baseAttrib):

	def attribFuncReq(self):
		if os.path.isfile("./cpuinfo"):
			return 0
		else:
			return 1

	def attribFunc(self, resName = ""):
		try:
			f=open('./cpuinfo', 'r')

			# Number of Processors
			# Count the number of occurences of processor
			attribValue = None
                        found = True
                        if resName != "": # if they don't send in a name
                                          # we'll just grab the first one we see
                           found = False
			for line in f:
                            if line.startswith("processor"):
                                procName = line.split(":")[1].strip()
                                if procName == resName:
                                   found = True 
                            elif line.startswith("model name"):
                                   if found:
                                      attribValue = line.split(":")[len(line.split(":")) - 1].strip()
                                      found = False
                                      break
			
                        f.close()
			return attribValue
                except IOError:
                        pass

	def attribDefaultName(self):
                return "'CPUModel'"

	def attribDefaultResourceType(self):
		return "'Processor'"

	def attribDefaultResourceName(self):
		return "'0'"


# ========================================================

#  (Compute Node Linux) CPU Mhz
# ========================================================
class attribFunc_cnl_CPUMhz(gm_hs_tools.baseAttrib):

	def attribFuncReq(self):
		if os.path.isfile("./cpuinfo"):
			return 0
		else:
			return 1

	def attribFunc(self, resName=""):
		try:

			f=open('./cpuinfo', 'r')
          
			attribValue = None
                        found = True
                        # if they don't send in a name, we'll just take the 1st one
                        if resName != "":
                           found = False
			for line in f:
                             if line.startswith("processor"):
                                procName = line.split(":")[1].strip()
                                if procName == resName:
                                   found = True
                             elif line.startswith("cpu MHz"):
                                  if found: 
                                     attribValue = line.split(":")[len(line.split(":")) - 1].strip()
                                     found = False
                                     break
			
                        f.close()
			return attribValue
                except IOError:
                        pass

	def attribDefaultName(self):
                return "'CPUMhz'"

	def attribDefaultResourceType(self):
		return "'Processor'"

	def attribDefaultResourceName(self):
		return "'0'"


# ========================================================

#  (Compute Node Linux) CPU Cache Size
# ========================================================
class attribFunc_cnl_CPUCacheSize(gm_hs_tools.baseAttrib):

   def attribFuncReq(self):
      if os.path.isfile("./cpuinfo"):
         return 0
      else:
         return 1

   def attribFunc(self, resName=""):
      try:
         f=open('./cpuinfo', 'r')
         attribValue = None
         found = True
         if resName != "":
            found = False
         for line in f:
            if line.startswith("processor"):
                procName = line.split(":")[1].strip()
                if procName == resName:
                   found = True
            elif line.startswith("cache size"):
               if found:
                  attribValList = line.split()
                  attribValue = attribValList[3]
                  #print "cache size %s" % (attribValue)
                  #attribValue = line.split(":")[len(line.split(":")) - 1].strip()
                    
                  f.close()
                  return attribValue
      except IOError:
         pass

   def attribDefaultName(self):
                return "'CPUCacheSize'"

   def attribDefaultResourceType(self):
		return "'Processor'"

   def attribDefaultResourceName(self):
		return "'0'"

# ========================================================

#  (Compute Node Linux)Memory Amount Mem
# ========================================================
class attribFunc_cnl_amountMem(gm_hs_tools.baseAttrib):

   def attribFuncReq(self):
      if os.path.isfile("./meminfo"):
         return 0
      else:
         return 1

   def attribFunc(self,resName=""):
      bikb = 1024
      try:
         f=open('./meminfo', 'r')
         attribValue = None
         for line in f:
            if line.startswith("MemTotal"):
               attribValList = line.split()
               #print attribValList
               ## convert from KB to GB
               av = float(attribValList[1])
               convFlt = av/(bikb*bikb)
               attribValue = "%.2f" % convFlt
               f.close()
               return attribValue
      except IOError:
         pass

   def attribDefaultName(self):
      return "'AmountMem'"

   def attribDefaultResourceType(self):
      return "'Node'"

# ========================================================

#  (Compute Node Linux)Memory Amount Mem in KB
# ========================================================
class attribFunc_cnl_amountMemKB(gm_hs_tools.baseAttrib):

   def attribFuncReq(self):
      if os.path.isfile("./meminfo"):
         return 0
      else:
         return 1

   def attribFunc(self,resName=""):
      bikb = 1024
      try:
         f=open('./meminfo', 'r')
         attribValue = None
         for line in f:
            if line.startswith("MemTotal"):
               attribValList = line.split()
               #print attribValList
               av = float(attribValList[1])
               convFlt = av
               attribValue = "%.2f" % convFlt
               f.close()
               return attribValue
      except IOError:
         pass

   def attribDefaultName(self):
      return "'AmountMemKB'"

   def attribDefaultResourceType(self):
      return "'Node'"

# ========================================================

#  (Compute Node Linux)Memory Amount Swap
# ========================================================
class attribFunc_cnl_amountSwap(gm_hs_tools.baseAttrib):

        def attribFuncReq(self):
		if os.path.isfile("./meminfo"):
			return 0
		else:
			return 1

        def attribFunc(self,resName=""):
                try:
                        f=open('./meminfo', 'r')

                        attribValue = None
                        for line in f:
                           if line.startswith("SwapTotal"):
                              avList = line.split()
                              attribValue = avList[1]
                              #print "Swap Total: %s" % attribValue
                              #attribValue = line.split(":")[len(line.split(":")) - 1].strip()
                        f.close()
                        return attribValue
                except IOError:
                        pass

	def attribDefaultName(self):
                return "'AmountSwap'"

	def attribDefaultResourceType(self):
		return "'Node'"


# ========================================================

#  (XT4) Machine Host Name
# ========================================================
class attribFunc_cnl_hostName(gm_hs_tools.baseAttrib):

        def attribFuncReq(self):
		if os.path.isfile("./hostname"):
                        return 0
                else:
                        return 1

        def attribFunc(self,resName=""):
                f=open('./hostname', 'r')
                attribValue = f.readline().strip()
                f.close()
                return attribValue

	def attribDefaultName(self):
                return "'MachineName'"

	def attribDefaultResourceType(self):
		return "'Machine'"



# ========================================================
# (Compute Node Linux) Size (In Blocks) of /dev/sda
# ========================================================
class attribFunc_cnl_sizeOfSDA(gm_hs_tools.baseAttrib):

# Note: Should probably use SG3 Utils for this
#       Something too think about
        def attribFuncReq(self):
                try:
                        f=open('./partitions', 'r')
			for line in f:
				if line.strip().endswith('sda'):
                        		f.close()
                        		return 0
			return 1
                except IOError:
                        return 1

        def attribFunc(self,resName=""):
                try:
                        f=open('./partitions', 'r')

                        attribValue = 0

			for line in f:
				if line.strip().endswith('sda'):
					attribValue = line.strip().split()[2]
					f.close()
					return attribValue
                        f.close()
                        return attribValue
                except IOError:
                        pass

	def attribDefaultName(self):
		return "'sizeOfSDA'"

	def attribDefaultResourceType(self):
		return "'Machine'"


# ========================================================
# (Compute Node Linux) Get Architech
# ========================================================
class attribFunc_cnl_getArch(gm_hs_tools.baseAttrib):

        def attribFuncReq(self):
		if os.path.isfile("./arch"):
			return 0
		else:
			return 1

        def attribFunc(self,resName = ""):
                        f = open("./arch","r")
                        attribValue = f.readline().strip()
                        f.close()
                        return attribValue

	def attribDefaultName(self):
		return "'Arch'"

	def attribDefaultResourceType(self):
		return "'Machine'"

# ========================================================











