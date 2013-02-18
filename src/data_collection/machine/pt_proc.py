#!/usr/bin/env python

## filename: pt_proc.py
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



# (Linux) Number of Processors
# ========================================================
class attribFunc_linux_numOfProc(gm_hs_tools.baseAttrib):

	def attribFuncReq(self):
		if os.path.isfile("/proc/cpuinfo"):
			return 0
		else:
			return 1

	def attribFunc(self, resName=""):
		try:
			f=open('/proc/cpuinfo', 'r')

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

# (AIX) Number of Processors
# ========================================================
class attribFunc_AIX_numOfProc(gm_hs_tools.baseAttrib):

	def attribFuncReq(self):
		attribReq = sys.platform
                if attribReq.startswith("aix"):
                        return 0
                else:
                        return 1

	def attribFunc(self,resName =""):
		attribValue = gm_hs_tools.execCmdGetOutput('lsdev -c processor | grep -c proc').strip()
		return attribValue

	def attribDefaultName(self):
		return "'numOfProc'"

	def attribDefaultResourceType(self):
		return "'Node'"

	def attribDefaultResourceName(self):
		return "'Unknown'"

# ========================================================

#  (Linux)CPU Vendor ID
# ========================================================
class attribFunc_linux_CPUVendorID(gm_hs_tools.baseAttrib):

	def attribFuncReq(self):
		if os.path.isfile("/proc/cpuinfo"):
			return 0
		else:
			return 1

	def attribFunc(self, resName=""):
		try:
			f=open('/proc/cpuinfo', 'r')

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
		return "'0'"

# ========================================================

#  (Linux) CPU Model
# ========================================================
class attribFunc_linux_CPUModel(gm_hs_tools.baseAttrib):

	def attribFuncReq(self):
		if os.path.isfile("/proc/cpuinfo"):
			return 0
		else:
			return 1

	def attribFunc(self, resName = ""):
		try:
			f=open('/proc/cpuinfo', 'r')

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

#  (Aix) CPU Model
# ========================================================
class attribFunc_AIX_CPUModel(gm_hs_tools.baseAttrib):

	def attribFuncReq(self):
		attribReq = sys.platform
                if attribReq.startswith("aix"):
                        return 0
                else:
                        return 1

	def attribFunc(self, resName=""):
                # if they don't provide a resource name, we'll just grab the
                # data for proc0
                if resName == "":
                   resName = "proc0"
		cmdValue = gm_hs_tools.execCmdGetOutput('lsattr -E -l %s | grep "Processor type"' % resName).strip()
		attribValue = cmdValue.split()[1]
		return attribValue

	def attribDefaultName(self):
                return "'CPUModel'"

	def attribDefaultResourceType(self):
		return "'Processor'"

	def attribDefaultResourceName(self):
		return "'0'"

# ========================================================

#  (Linux) CPU Mhz
# ========================================================
class attribFunc_linux_CPUMhz(gm_hs_tools.baseAttrib):

	def attribFuncReq(self):
		if os.path.isfile("/proc/cpuinfo"):
			return 0
		else:
			return 1

	def attribFunc(self, resName=""):
		try:

			f=open('/proc/cpuinfo', 'r')
          
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

#  (Aix) CPU Mhz
# ========================================================
class attribFunc_AIX_CPUMhz(gm_hs_tools.baseAttrib):

	def attribFuncReq(self):
		attribReq = sys.platform
                if attribReq.startswith("aix"):
                        return 0
                else:
                        return 1

	def attribFunc(self,resName=""):
                # if they don't give a name for the processor, default
                # to proc0
                if resName == "":
                   resName = "proc0"
		cmdValue = gm_hs_tools.execCmdGetOutput('lsattr -E -l %s | grep "Processor Speed"' % resName).strip()
		attribValue = cmdValue.split()[1]
                # value is given in Hz, we want MHz
                av = float(attribValue)
                mz = av/(1000*1000)
                attribValue = "%.2f" % mz
		return attribValue

	def attribDefaultName(self):
                return "'CPUMhz'"

	def attribDefaultResourceType(self):
		return "'Processor'"

	def attribDefaultResourceName(self):
		return "'0'"

# ========================================================

#  (Linux) CPU Cache Size
# ========================================================
class attribFunc_linux_CPUCacheSize(gm_hs_tools.baseAttrib):

   def attribFuncReq(self):
      if os.path.isfile("/proc/cpuinfo"):
         return 0
      else:
         return 1

   def attribFunc(self, resName=""):
      try:
         f=open('/proc/cpuinfo', 'r')
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

#  (Linux)Memory Amount Mem
# ========================================================
class attribFunc_linux_amountMem(gm_hs_tools.baseAttrib):

   def attribFuncReq(self):
      if os.path.isfile("/proc/meminfo"):
         return 0
      else:
         return 1

   def attribFunc(self,resName=""):
      bikb = 1024
      try:
         f=open('/proc/meminfo', 'r')
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

#  (Linux)Memory Amount Mem in KB
# ========================================================
class attribFunc_linux_amountMemKB(gm_hs_tools.baseAttrib):

   def attribFuncReq(self):
      if os.path.isfile("/proc/meminfo"):
         return 0
      else:
         return 1

   def attribFunc(self,resName=""):
      bikb = 1024
      try:
         f=open('/proc/meminfo', 'r')
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

#  (Aix)Memory Amount Mem
# ========================================================
class attribFunc_AIX_amountMem(gm_hs_tools.baseAttrib):

        def attribFuncReq(self):
		attribReq = sys.platform
                if attribReq.startswith("aix"):
                        return 0
                else:
                        return 1

        def attribFunc(self,resName=""):
		attribValue = gm_hs_tools.execCmdGetOutput("lsattr -El mem0 | awk '/^size/ {print $2} '").strip()
                # lsattr gives value in MB, we want GB
                av = float(attribValue)
                gb = av/(1024)
                attribValue = "%.2f" % gb
		return attribValue

	def attribDefaultName(self):
                return "'AmountMem'"

	def attribDefaultResourceType(self):
		return "'Node'"

# ========================================================

#  (Linux)Memory Amount Swap
# ========================================================
class attribFunc_linux_amountSwap(gm_hs_tools.baseAttrib):

        def attribFuncReq(self):
		if os.path.isfile("/proc/meminfo"):
			return 0
		else:
			return 1

        def attribFunc(self,resName=""):
                try:
                        f=open('/proc/meminfo', 'r')

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

#  (Infiniband)Network Interface ID
# ========================================================
class attribFunc_infiniband_networkInterfaceID(gm_hs_tools.baseAttrib):

        def attribFuncReq(self):
                if os.path.isfile("/usr/bin/vstat"):
                        return 0
                else:
                   (out,err,ret) = my_exec2("vstat","")
                   if ret == 0:
                        return 0
                   else:
                        return 1

        def attribFunc(self,resName=""):
                try:
                        (out,err, ret) = my_exec2("vstat","")

                        attribValue = None
                        lines = out.split("\n")
                        for line in lines:
                           if line.strip().startswith("hca_id"):
                              avList = line.split("=")
                              attribValue = avList[1]
                        return attribValue
                except IOError:
                        pass

        def attribDefaultName(self):
                return "'Network Interface ID'"

        def attribDefaultResourceType(self):
                return "'Node'"

# ========================================================

#  (Infiniband)Network Interface Firmware Version
# ========================================================
class attribFunc_infiniband_networkInterfaceFWver(gm_hs_tools.baseAttrib):

        def attribFuncReq(self):
                   (out,err,ret) = my_exec2("vstat","")
                   if ret == 0:
                        return 0
                   else:
                        return 1

        def attribFunc(self,resName=""):
                try:
                        (out,err, ret) = my_exec2("vstat","")

                        attribValue = None
                        lines = out.split("\n")
                        for line in lines:
                           if line.strip().startswith("fw_ver"):
                              avList = line.split("=")
                              attribValue = avList[1]
                        return attribValue
                except IOError:
                        pass

        def attribDefaultName(self):
                return "'Network Interface Firmware Version'"

        def attribDefaultResourceType(self):
                return "'Node'"


# ========================================================

#  (Unix) Machine Host Name
# ========================================================
class attribFunc_Unix_hostName(gm_hs_tools.baseAttrib):

        def attribFuncReq(self):
                attribReq = os.name
                if attribReq == 'posix':
                        return 0
                else:
                        return 1

        def attribFunc(self,resName=""):
                attribValue = os.uname()[1]
                return attribValue

	def attribDefaultName(self):
                return "'MachineName'"

	def attribDefaultResourceType(self):
		return "'Machine'"

# ========================================================

# (Linux) Number of SCSI Devices
# ========================================================
class attribFunc_linux_numOfScsiDevices(gm_hs_tools.baseAttrib):

        def attribFuncReq(self):
		if os.path.isfile("/proc/scsi/scsi"):
			return 0
		else:
			return 1

        def attribFunc(self,resName=""):
                try:
                        f=open('/proc/scsi/scsi', 'r')

                        attribValue  = 0
                        for line in f:
                                if line.startswith("Host:"):
                                        attribValue = attribValue + 1

                        f.close()
                        return attribValue
                except IOError:
                        pass

	def attribDefaultName(self):
		return "'NumberOfSCSIDevices'"

	def attribDefaultResourceType(self):
		return "'Machine'"

# ========================================================

# ========================================================
# (Linux) Size (In Blocks) of /dev/sda
# ========================================================
"""
class attribFunc_linux_sizeOfSDA(gm_hs_tools.baseAttrib):

# Note: Should probably use SG3 Utils for this
#       Something too think about
        def attribFuncReq(self):
                try:
                        f=open('/proc/partitions', 'r')
			for line in f:
				if line.strip().endswith('sda'):
                        		f.close()
                        		return 0
			return 1
                except IOError:
                        return 1

        def attribFunc(self,resName=""):
                try:
                        f=open('/proc/partitions', 'r')

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
"""

# ========================================================
# (Linux) Get Architech
# ========================================================
class attribFunc_linux_getArch(gm_hs_tools.baseAttrib):

        def attribFuncReq(self):
		attribReq = sys.platform
		if attribReq.startswith("linux"):
			return 0
		else:
			return 1

        def attribFunc(self,resName = ""):
			attribValue = gm_hs_tools.execCmdGetOutput('arch').strip()
                        return attribValue

	def attribDefaultName(self):
		return "'Arch'"

	def attribDefaultResourceType(self):
		return "'Machine'"

# ========================================================











