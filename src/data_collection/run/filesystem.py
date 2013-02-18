import os,sys,stat,time
from PTcommon import my_exec2


class device:
   def __init__(self,nme="",devName="", mountPoint="", size="",used="",avail="",usedPercent=""):
      self.name = nme
      self.deviceName = devName
      self.mountPoint = mountPoint
      self.size = size
      self.used = used
      self.avail = avail
      self.usedPercent = usedPercent

   def printData(self):
      toPrint = "DeviceBegin\n"
      toPrint += "Name = %s\n" % self.name
      if self.deviceName != "":
         toPrint += "deviceName = %s\n" % self.deviceName
      if self.mountPoint != "":
         toPrint += "mountPoint = %s\n" % self.mountPoint
      if self.size != "":
         toPrint += "Size = %s\n" % self.size
      if self.used != "":
         toPrint += "Used = %s\n" % self.used
      if self.avail != "":
         toPrint += "Avail = %s\n" % self.avail
      if self.usedPercent != "":
         toPrint += "Used%% = %s\n" % self.usedPercent
      toPrint += "DeviceEnd\n"
      return toPrint

   def PERIformat(self, peri, parent):
      dev = peri.createDevice(self.name, parent)
      if self.mountPoint != "":
         peri.addDeviceAttribute(dev, "mountPoint",self.mountPoint)
      if self.size != "":
         peri.addDeviceAttribute(dev, "Size",self.size)
      if self.used != "":
         peri.addDeviceAttribute(dev, "Used",self.used)
      if self.avail != "":
         peri.addDeviceAttribute(dev, "Avail",self.avail)
      if self.usedPercent != "":
         peri.addDeviceAttribute(dev, "UsedPercent",self.usedPercent)
    
      
   def getInfo(self,OS):
       if not self.mountPoint:
          self.getMountPoint(OS)
       if self.mountPoint and (not self.size or not self.used or not self.avail or not self.usedPercent):
          self.getSizeAvailUsage(OS)

   def getMountPoint(self,OS):
      (out,err,ret) = my_exec2("which","df")
      command = out
      if ret != 0:
         print "WARNING: could not locate df command to get device mount point for %s" % self.name
         return
      if OS == "Linux":
         args = "-Ph %s" % self.deviceName
      elif OS == "AIX":
         args = "-Pg %s" % self.deviceName
      (out,err,ret) = my_exec2(command,args)
      if ret != 0:
         print "WARNING: could not get device mount point with command: %s %s \n" % (command, args)
         return
      # Filesystem            Size  Used Avail Use% Mounted on
      self.mountPoint = out.split("\n")[1].split()[5]

   def getSizeAvailUsage(self, OS):
      (out,err,ret) = my_exec2("which","df")
      if ret != 0:
         print "WARNING: can't locate df to get device size and usage information for %s" % self.name 
         return
      command = out 
      if OS == "Linux":
         args = "-Ph %s" % self.deviceName
      elif OS == "AIX":
         args = "-Pg %s" % self.deviceName
      (out,err,ret) = my_exec2(command,args)
      if ret != 0:
         print "WARNING: could not get device size and usage with command: %s %s \n" % (command, args)
         return
      self.size = out.split("\n")[1].split()[1]
      self.used = out.split("\n")[1].split()[2]
      self.avail = out.split("\n")[1].split()[3]
      # for AIX, we add on a G, because we requested data in units of GB
      if OS == "AIX":
         self.size += "G"
         self.used += "G"
         self.avail += "G"
      self.usedPercent = out.split("\n")[1].split()[4]

class filesystem:
   def __init__(self,nme=""):
      self.name = nme
      self.version  = ""
      self.versionCommand = ""
      self.devices = []

   def addDevice(self,longname,mountPoint,size, used,avail,usedPercent):
      pts = longname.split('/') 
      name = pts[len(pts)-1]
      d = device(name,longname,mountPoint,size,used,avail,usedPercent)
      self.devices.append(d)

 
   def getVersion(self):
      # MMFS is what GPFS is called in AIX system files
      if self.name.upper() == "GPFS" or self.name.upper() == "MMFS":
         self.getGPFSversion()
      elif self.name.upper() == "LUSTRE":
         self.getLustreVersion()

   def getDeviceInfo(self,OS):
      print "getting filesystem device information...."
      for d in self.devices:
          d.getInfo(OS)

 
   def printData(self):
      toPrint = "FileSystemBegin\n"
      toPrint += "Name = %s\n" % self.name
      if self.version != "":
         toPrint += "Version = %s\n" % self.version
      for d in self.devices:
         toPrint += d.printData()
      toPrint += "FileSystemEnd\n"
      return toPrint

   def PERIformat(self, peri, parent):
      fs = peri.createFileSystem(self.name, parent)
      peri.setFileSystemAttribute(fs, "version", self.version)
      for d in self.devices:
          d.PERIformat(peri, fs)
      
      

   def getGPFSversion(self):
      if self.versionCommand != "":
         if self.devices != []:
            d = self.devices[0]
            c = self.versionCommand.replace("$device",d.name)
            command = c.split()[0]
            args = ""
            for a in c.split()[1:]:
                args += "%s " % a
            (out,err,ret) = my_exec2(command,args)
            if ret != 0:
               print "WARNING: could not get file system version with command: %s %s \n" % (command, args) 
               return
            if command.find("mmlsfs") >= 0:
               self.version = out.split("\n")[2].split()[1]
              
      else:
         if os.path.isfile("/usr/lpp/mmfs/bin/mmlsfs"):
            command = "/usr/lpp/mmfs/bin/mmlsfs"
         else:
            (out,err,ret) = my_exec2("which","mmlsfs")
            command = out
            if ret != 0:
               print "WARNING: could not locate mmlsfs command to get file system version information."
               return
         if self.devices != []:
            d = self.devices[0]
            args = "%s -V" % d.name
            (out,err,ret) = my_exec2(command,args)
            if ret != 0:
               print "WARNING: could not get file system version with command: %s %s \n" % (command, args) 
               return
            self.version = out.split("\n")[2].split()[1]

   def getLustreVersion(self):
      if not self.versionCommand :  # no command supplied
          test = os.path.isfile("/proc/fs/lustre/version")
          if test:
             command = "cat /proc/fs/lustre/version"
             (out,err,ret) = my_exec2(command,"")
             if ret != 0:
                print "WARNING: could not get file system version with command: %s \n" % command
                return
             self.version = out.strip()
      else:  # they supplied a command they want us to use
          parts = self.versionCommand.split(None,1) # split into cmmand and args
          command = parts[0]
          if len(parts) > 1:
            args = parts[1]
          else:
            args = []
          (out,err,ret) = my_exec2(command,args)
          if ret != 0:
             print "WARNING: could not get file system version with command: %s %s" % (command,args)
             return
          self.version = out 
              
         
       

class fsInfo:
   def __init__(self):
      self.filesystems = []
      self.OS = ""

   def getInfo(self):
      self.getfsInfo()
      
      for fs in self.filesystems:
         fs.getVersion()
         fs.getDeviceInfo(self.getOS())
      return True

   def printData(self):
      toPrint = ""
      for fs in self.filesystems:
          toPrint += fs.printData()

      return toPrint

   def PERIformat(self, peri, run):
      if len(self.filesystems) > 0:
         fsSet = peri.createFileSystemSet(None, run)
      for fs in self.filesystems:
          fs.PERIformat(peri, fsSet)

   def getOS(self):
      if self.OS == "":
         self.OS = os.uname()[0]
      return self.OS

   def getfsInfo(self):
      if self.getOS() == "Linux":
         (out,err,ret) = my_exec2("which","df")
         command = out
         if ret != 0:
            print "WARNING: could not locate df command to get file system info" 
            print "attempting to retrieve file system info from $HOME/.ptconfig..."
            self.getFsInfoFromFile()    
            return
         args = "-PTh"
         (out,err,ret) = my_exec2(command,args)
         if ret != 0:
            print "WARNING: could not get filesystem info with command: %s %s" % (command,args)
            return
         lines = out.splitlines()[1:] # skip first line
         fses = {}
         for l in lines:
             #print l
             name = l.split()[1]
             if name in fses:
                fs = fses[name]
             else:
                fs = filesystem()
                fs.name = name
                fses[name] = fs
             parts = l.split()
             device = parts[0]
             size = parts[2]
             used = parts[3]
             avail = parts[4]
             usedPercent = parts[5]
             mountPoint = parts[6]
             #print "adding device: %s %s %s" % (device, mountPoint,size)
             fs.addDevice(device,mountPoint,size,used,avail,usedPercent)

         self.filesystems =  fses.values()

      elif self.getOS() == "AIX":
         if not os.path.isfile("/etc/filesystems"):
            print "WARNING: could not get filesystem info from /etc/filesystems"
            return
         command = "cat"
         args = "/etc/filesystems"
         (out,err,ret) = my_exec2(command,args)
         if ret != 0:
            print "WARNING: could not get filesystem info with command: %s %s" % (command,args)
            return
         fses = {}
         lines = out.splitlines()
         i = 0
         while i < len(lines)-1:
             l = lines[i].strip()
             #print "line:%s, %s" % (i,l)
             # skip if comments,blanks
             if l.startswith("*") or l == "":
                i += 1
                continue         
             if l.endswith(":"): # that's a new device to parse
                mountPoint = l.rstrip(":").strip() 
                i += 1
                while i < len(lines)-1:
                    l = lines[i].strip()
                    #print "line:%s, %s" % (i,l)
                    # see if we're done with this one yet or not 
                    if l.endswith(":") or l == "":
                       break 
                    if l.startswith("dev"):
                       deviceName = l.split("=")[1].strip()
                    elif l.startswith("vfs"):
                       fsname = l.split("=")[1].strip()
                       if fsname in fses:
                          fs = fses[fsname]
                       else:
                          fs = filesystem()
                          fs.name = fsname
                          fses[fsname] = fs
                    i += 1
                fs.addDevice(deviceName,mountPoint,"","","","")
         self.filesystems =  fses.values()

   def getfsInfoFromFile(self):
      try:
         homedir = os.getenv("HOME")
         f = open(homedir + "/.ptconfig",'r')
      except:
         print "WARNING: could not open $HOME/.ptconfig to get known file system information."
         return 
      lines = f.readlines()
      i = 0
      while (i < (len(lines)-1)):
          if lines[i].startswith("filesystem"):
             fs = filesystem()
             fs.name = lines[i].split()[1]
             i += 1
             if lines[i].startswith("versionCommand"):
                for w in lines[i].split()[2:]:
                   fs.versionCommand += "%s " % w
                i += 1

             while (i < len(lines) and lines[i].startswith("device")):
                   fs.addDevice(lines[i].split()[2])
                   i += 1
             self.filesystems.append(fs)
          else:
             i += 1

      #for f in self.filesystems:
         #print f.printData()



