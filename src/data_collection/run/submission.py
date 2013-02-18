import os,sys,stat,datetime

from PTcommon import my_exec2

class machine:
   def __init__(self,nme=""):
      self.name = nme
      self.partitions = []

class Submission:
   def __init__(self):
      self.launcher = ""
      self.launcherVersion = ""
      self.batchFile = ""
      self.fileDateTime = ""
      self.batchShell = ""
      self.batchDirectives = []
      self.hostFile = ""
      self.runMachine = ""
      self.runPartition = ""
      self.queueContents = []
      self.batchShellCmds = []
      self.batchEnvCmds = []
      self.batchRunCmds = []
      self.batchJobName = ""
      self.numberOfNodes = -1
      self.numberOfThreads = -1
      self.numberOfProcesses = -1
      self.processesPerNode = -1 
      self.threadsPerProcesses = 1
      self.cpusPerProcess = -1
      self.cpusPerNode = 1
      self.knownMachines = []
      self.pbsResources = ""
      self.lcrmResources = ""
      self.OS = ""
      
      

   def getInfo(self, launcher, batchFile):
      self.getKnownMachineInfo()
      if launcher == "lcrm":
         self.launcher = "lcrm"
         ret = self.parseLCRM(batchFile)
         self.getLCRMqueueContents()
      elif launcher == "pbs":
         self.launcher = "pbs"
         self.getPBSversion()
         ret = self.parsePBS(batchFile)
         self.getPBSqueueContents()
      elif launcher == "mpirun":
         self.launcher = "mpirun"
         self.getMPIRUNversion()
         ret = self.parseMPIRUN(batchFile)
      return ret 


   def getKnownMachineInfo(self):
      try:
         homedir = os.getenv("HOME")
         f = open(homedir + "/.ptconfig",'r')
      except:
         print "WARNING: could not open $HOME/.ptconfig to get known machine information."
         raise
         return
      lines = f.readlines()
      i = 0
      while (i < (len(lines)-1)):
          if lines[i].startswith("machine"):
             mname = lines[i].split()[1]
             i += 1
             mach = machine(mname)
             self.knownMachines.append(mach)
             while (i < (len(lines)-1) and lines[i].startswith("partition")):
                   mach.partitions.append(lines[i].split()[2])
                   i += 1
          else:
             i += 1
                
      #for m in self.knownMachines:
         #toPrint = "%s: " % m.name
         #for p in m.partitions:
             #toPrint += "%s " % p
         #print toPrint
                   

   def printData(self):
      toPrint = "SubmissionBegin\n"
      if self.launcher != "":
         toPrint += "launcher = %s\n" % self.launcher
      if self.launcherVersion != "":
         toPrint += "launcherVersion = %s\n" % self.launcherVersion
      if self.batchFile != "":
         toPrint += "batchFile = %s\n" % self.batchFile
      if self.fileDateTime != "":
         toPrint += "batchFileDateTime = %s\n" % self.fileDateTime
      if self.runPartition != "":
         toPrint += "machinePartition = %s\n" % self.runPartition
      count = 1
      for q in self.queueContents:
         toPrint += "batchQueueEntry_%d = %s\n" % (count,q.strip())
         count += 1
      if self.batchShell != "":
         toPrint += "batchShell = %s\n" % self.batchShell
      if self.batchJobName != "":
         toPrint += "jobName=%s\n" % self.batchJobName
      if self.launcher == "lcrm":
         dirAttrName = "#PSUB"
      elif self.launcher == "pbs":
         dirAttrName = "#PBS"
      if self.launcher == "pbs" and self.pbsResources != "":
         toPrint += "pbsResources=%s\n" % self.pbsResources
      if self.launcher == "lcrm" and self.lcrmResources != "":
         toPrint += "lcrmResources=%s\n" % self.lcrmResources
      # count is to differentiate attrs with same name
      # name is transformed to name_number
      count = 1
      for bd in self.batchDirectives:
         toPrint += "%s_%d=%s\n" % (dirAttrName,count ,bd)
         count += 1
      if self.hostFile != "":
         toPrint += "hostFile = %s\n" % self.hostFile
      count = 1
      for sc in self.batchShellCmds:
         toPrint += "batchCmd_%d=%s\n" %  (count,sc)
         count += 1
      count = 1
      for ec in self.batchEnvCmds:
         toPrint += "envVar_%d=%s\n" %  (count,ec)
         count += 1
      count = 1
      for rc in self.batchRunCmds:
         toPrint += "runCmd_%d=%s\n" %  (count,rc)
         count += 1
      toPrint += "SubmissionEnd\n"
      return toPrint

   def PERIformat(self, peri, parent):
      if self.launcher != "":
         sched = peri.createScheduler(self.launcher,parent)
         peri.setSchedulerAttribute(sched, "version", self.launcherVersion)
         # batch queue entries
         queue = peri.createQueue(None,sched)
         for qe in self.queueContents:
            jobId = ""
            progName = ""
            userName = ""
            hoursRun = ""
            status = ""
            jobQueue = ""
            host = ""
            if self.launcher == "pbs":
               jobId,progName,userName,hoursRun,status,jobQueue= qe.split()
            elif self.launcher == "lcrm":
               jobId,progName,userName,hoursRun,status,host= qe.split()
            else:
               #TODO fix me
               print "unsupported launcher: get queue contents"
               break
            job = peri.createSchedulerJob(None, queue)
            peri.setSchedulerJobAttribute(job, "jobid", jobId)
            peri.setSchedulerJobAttribute(job, "programName", progName)
            peri.setSchedulerJobAttribute(job, "hoursRunning", hoursRun)
            peri.setSchedulerJobAttribute(job, "status", status)
 
         batchAVs = [] 
         batchAVs.append(("timeStamp",self.fileDateTime))
         if self.batchJobName != "":
             batchAVs.append(("jobName",self.batchJobName))
         if  self.launcher == "pbs":
            dirAttrName = "pbsDirective"
            batchAVs.append(("pbsResources",self.pbsResources))
         elif self.launcher == "lcrm":
            dirAttrName = "lcrmDirective"
            batchAVs.append(("lcrmResources",self.lcrmResources))
         for bd in self.batchDirectives:
            batchAVs.append((dirAttrName,bd))
         for sc in self.batchShellCmds:
            batchAVs.append(("batchCmd",sc))
         for ec in self.batchEnvCmds:
            batchAVs.append(("envVar",ec))
         for rc in self.batchRunCmds:
            batchAVs.append(("runCmd",rc))

         if self.batchFile != "":
             batch = peri.createBatchFile(self.batchFile, parent)
             for name,value in batchAVs:
                peri.setBatchFileAttribute(batch, name, value)




   def parseMPIRUN(self, batchFile):
      # for mpirun, the arguments to the command are in the batchfile
      if batchFile == "":
         print "batch file required for mpirun. The contents of the file should be the arguments to the mpirun command"
         return False
      try:
          f = open(batchFile,'r')
      except:
          print "couldn't open the batch file containing mpirun arguments: %s" % batchFile
          return False
          
      lines = f.readlines() # really expect only one line... 
      self.launcherArgs = ""
      for line in lines:
          self.launcherArgs += " %s" % line.strip()

      self.batchRunCmds.append("mpirun %s" % self.launcherArgs)
      index =  self.launcherArgs.find("-n ")
      if index >= 0:
         index += 3 # skip over "-n " 
         count = ""
         while self.launcherArgs[index] != " " and index < len(self.launcherArgs)-1:
            count += self.launcherArgs[index]
            index += 1
         self.numberOfProcesses = count
      else:
         index =  self.launcherArgs.find("-np ")
         if index >= 0:
            index += 4 # skip over "-n " 
            count = ""
            while self.launcherArgs[index] != " " and index < len(self.launcherArgs)-1:
               count += self.launcherArgs[index]
               index += 1
            self.numberOfProcesses = count

      return True
           

   def parseLCRM(self, batchFile):
      # parse LCRM batch file for run configuration information
      #check for batch file
      if batchFile == "":
         print "batch file required for LCRM launcher"
         return False
      
      # get time stamp of file
      ret = self.getTimeStamp(batchFile)
      if ret == "":
         print "could not stat batch file: %s " % batchFile
         return False
      else:
         self.fileDateTime = ret
      self.batchFile = batchFile

      psubs = []
      userCmds = []
      runCmds = []

      f = open(batchFile,'r')
      lines = f.readlines()
      self.fileContents = lines
      for line in lines:
          # skip blanks
          if line.strip() == "":
             continue
          #print line.strip() 
          if line.find("#PSUB") >= 0:
             psubs.append(line.strip())
          elif line.find("srun") >= 0 or line.find("poe") >= 0:
             runCmds.append(line.strip())
          elif line.find("#!") == 0:
             l = line.split("/")
             batchShell = l[len(l) - 1].strip()
             if batchShell.find("csh") < 0:
                self.batchShell == "csh"
                #TODO fix this
                print ' currently only csh is supported '
          else:
             userCmds.append(line.strip())

      self.parse_LCRM_directives(psubs)
      self.parse_user_commands(userCmds)
      self.parse_run_commands(runCmds)
      return True


   def parsePBS(self, batchFile):
      # parse PBS batch file for run configuration information
      #check for batch file
      if batchFile == "":
         print "batch file required for LCRM launcher"
         return False

      # get time stamp of file
      ret = self.getTimeStamp(batchFile)
      if ret == "":
         print "could not stat batch file: %s " % batchFile
         return False
      else:
         self.fileDateTime = ret
      self.batchFile = batchFile

      psubs = []
      userCmds = []
      runCmds = []

      f = open(batchFile,'r')
      lines = f.readlines()
      self.fileContents = lines
      for line in lines:
          # skip blanks
          if line.strip() == "":
             continue
          #print line.strip() 
          if line.find("#PBS") >= 0:
             psubs.append(line.strip())
          elif line.find("mpiexec") >= 0 or line.find("mpirun") >= 0:
             runCmds.append(line.strip())
          elif line.find("#!") == 0:
             l = line.split("/")
             batchShell = l[len(l) - 1].strip()
             if batchShell.find("bash") < 0:
                self.batchShell == "bash"
          else:
             userCmds.append(line.strip())

      self.parse_PBS_directives(psubs)
      self.parse_user_commands(userCmds)
      self.parse_run_commands(runCmds)

      return True
     
   def parse_LCRM_directives(self,psubs):
       """ This function parses a list of #PSUB directives looking for 
           information about the execution, such as the run machine,
           the partition to be used, the name of the job, the number of
           nodes, and tasks per node.
           Current requirement: tasks per node needs to be specified 
           with the -g x@tpny option to PSUB. Otherwise it is assumed
           to be one.
       """
       for psub in psubs:
          self.batchDirectives.append(psub)
          ps = psub.split()
          #print ps
          if len(ps) > 1:
              if ps[1] == "-c":  # found constraints line
                 for p in ps[2].split(','):
                     if not self.runMachine:
                        p = p.rstrip("\"").lstrip("\"")
                        for m in self.knownMachines:
                           if p.lower().find(m.name.lower()) >= 0:
                              self.runMachine = m.name
                              break
                        p = p.rstrip("\"").lstrip("\"")
                        for part in m.partitions:
                           if p.lower().find(part.lower()) >= 0:
                              self.runPartition = part
                              break
              elif ps[1] == '-r': # found job name
                 self.batchJobName = ps[2]
              elif ps[1] == '-ln':
                 self.lcrmResources = ps[2].strip()
                 # format: -ln X(x:(spec),y:(spec),z:(spec))
                 # variations: -ln X
                 # 		-ln X-Y
                 #          	-ln X-Y(x,y:(spec))
                 parts = ps[2].split("(",1) # split between node count
	                                   # and feature requests
                 nodeCount = parts[0] # how many nodes
                 features = ""        # what features do they need to have
                 if len(parts) == 2:
                    features = parts[1]
                 if nodeCount.find("-") == -1: # request a specific # of nodes 
                    self.numberOfNodes = nodeCount
                 else: # can't figure the rest out if we don't know this
                    continue
                 if features != "":
                    # get rid of enclosing parens
                    features = features.rstrip(")").lstrip("(")
                    # if it's a list of features, we don't try to parse that
                    # this bit of code tells us if there is more than one
                    # feature request list
                    foundLeftParen = False
                    foundRightParen = False
                    foundComma = False
                    multiRequest = False
                    for char in features:
                        if char == "(":
                           foundLeftParen = True
                        elif char == ",":
                           foundComma = True
                        elif char == ")":
                           foundRightParen = True
                        if foundComma and not foundLeftParen:
                           multiRequest = True
                           break
                        if foundRightParen:
                           foundLeftParen = False
                           foundRightParen = False
                           foundComma = False
                    if multiRequest:
                       continue
                    # find cpn feature if it exists 
                    index = features.find("cpn")
                    if index != -1:
                       i = 1
                       cpn = ""
                       # search backward to get the cpn count
                       # Remember cpn is counter intuitive. It really
                       # specifies how many cpus each process in your
                       # job will need, according to LC web pages
                       while features[index-i].isdigit():
                           cpn = "%s%s" % (features[index-i],cpn)
                           i = i+1
                       self.cpusPerNode = self.parse_cpuinfo()
                       self.processesPerNode = int(self.cpusPerNode)/int(cpn)
                       self.cpusPerProcess = cpn
              elif ps[1] == '-cpn':
                 cpu_count = self.parse_cpuinfo()
                 self.cpusPerNode = cpu_count
                 self.processesPerNode = cpu_count/(int(ps[2]))
                 self.cpusPerProcess = ps[2]
              elif ps[1] == '-g':
                  if ps[2].find("@tpn") >= 0:
                     # ps[2] is like 2@tpn2
                     p = ps[2].split('@tpn')
                     if p[0] != '':
                        self.numberOfNodes = p[0]
                     self.processesPerNode = p[1]
                  else:
                     # ps[2] is the total number of tasks
                     self.numberOfProcesses = ps[2]
                     cpu_count = self.parse_cpuinfo()
                     self.cpusPerNode = cpu_count
                     self.processesPerNode  = int(self.numberOfProcesses)/int(self.numberOfNodes)

   def parse_PBS_directives(self, psubs):
       """ This function parses a list of #PBS directives looking for 
           information about the execution, such as the run machine,
           the partition to be used, the name of the job, the number of
           nodes, and tasks per node.
       """
       for psub in psubs:
          self.batchDirectives.append(psub)
          ps = psub.split()
          #print ps
          if len(ps) > 1:
             if ps[1] == '-N': # found jobname
                self.batchJobName = ps[2]
             elif ps[1] == '-q':  # which queue
                self.runPartition = ps[2]
             elif ps[1] == '-S':    # which shell
                self.batchShell = ps[2]
             elif ps[1] == '-l':   # resource requests
                cpu_count = self.parse_cpuinfo()
                self.cpusPerNode = cpu_count

                class nodespec:
                   def __init__(self, nodes=1,ncpus=1,ppn=1):
                     self.nodes = nodes
                     self.ncpus = ncpus
                     self.ppn = ppn
                # syntax: -l resname[=value][,resname[=value], ...]
                # if resname == "nodes" then
                # value : nodespec[+nodespec ...][#suffix]
                # nodespec:   property[:property ...]
                request = ps[2]
                self.pbsResources = request
                resources = request.split(',')
                nodes = []
                for r in resources:
                  #print "resource: %s" % r
                  if r.startswith("nodes"):
                     value = r.split("=",1)[1].split("#")[0]
                     #print "value: %s" % value
                     nodespecs = value.split("+")
                     #print "nodespecs: %s" % nodespecs
                     for nd in nodespecs:
                        node = nodespec()
                        nodes.append(node)
                        properties = nd.split(":")
                        for p in properties:
                     # if they specify the number of nodes, it has to be the first property
                           if p.isdigit():
                               node.nodes = p
                           if p.startswith("ppn"): # processes per node
                              pts = p.split("=")
                              if len(pts) != 1: # it's not a default value
                                 node.ppn =  pts[1]
                           # cpus per process, man page says use cpp, manual says ncpus,
                           # so we'll look for both
                           elif p.startswith("cpp") or p.startswith("ncpus"):
                              pts = p.split("=")
                              if len(pts) != 1: # it's not a default value
                                 node.ncpus=  pts[1]
                totalNodes = 0
                totalCpus = 0
                totalProcesses = 0
                for n in nodes:
                   #print "nodes: %s, ncpus: %s, ppn: %s" % (n.nodes, n.ncpus, n.ppn)
                   totalNodes += int(n.nodes)
                   totalProcesses += int(n.nodes) * int(n.ppn)
                # if there's only one nodespec in the resource list, then we know
                # the following, otherwise, we don't 
                self.numberOfNodes = totalNodes
                self.numberOfProcesses = totalProcesses
                if len(nodes)  == 1:
                   self.processesPerNode = int(nodes[0].ppn)
                   self.cpusPerProcess = int(nodes[0].ncpus )
                else:
                   self.processesPerNode = -1
                   self.cpusPerProcess = -1

                #print "totalNodes: %d, totalProcesses: %d, processesPerNode: %d, cpusPerProcess: %d" % (self.numberOfNodes, self.numberOfProcesses, self.processesPerNode, self.cpusPerProcess)

   def getPBSversion(self):
      args = "-Bf | awk '/pbs_version/ {print $3}'"
      (out, err, retval) = my_exec2("qstat", args)
      #print "pbs version said: " + out
      self.launcherVersion = out
       

   def getPBSqueueContents(self):
      (out, err, retval) = my_exec2("qstat","" )
      if retval == 0:
         lines = out.split("\n")
         for line in lines[2:]: # chop off header lines
             self.queueContents.append(line)

   def getLCRMqueueContents(self):
      if self.runMachine != "":
         args = "-m %s -o jid,name,user,runtime,status,exehost " % self.runMachine
         (out,err, ret) = my_exec2("pstat",args)
         print err
         if ret == 0:
            lines = out.split("\n")
            for line in lines[1:]: # chop off header line
               self.queueContents.append(line)


   def getMPIRUNversion(self):
         # this works with openMPI, mpich2 doesn't seem to have a version flag
         # so we don't get a version for it.
         (out,err,ret) = my_exec2("mpirun","--version")
         if ret == 0:
            # open mpi outputs version info to stderr
            if out == "":
               lines = err.split("\n")
            else:
               lines = out.split("\n")
            self.launcherVersion = ""
            for line in lines:
               if self.launcherVersion != "":
                   self.launcherVersion += " ;%s" % line
               else:
                   self.launcherVersion += "%s" % line
 
   def parse_user_commands(self, userCmds):
        """ parses the shell commands in the batch script. Attempts to separate out the commands that alter the environment"""
        envCmds = []
        for uc in userCmds:
            if uc.startswith("setenv"):
               envCmds.append(uc)
            else:
               if uc[0][0] != "#":  # skip comment lines
                  self.batchShellCmds.append(uc)
        self.parse_env_commands(envCmds)

   def parse_env_commands(self, userEnv):
        """ parses environment altering commands. Attempts to find number of OpenMP threads and the name of the hostfile"""
        for ue in userEnv:
           if ue.find("OMP_NUM_THREADS") >= 0:
              self.numberOfThreads = uc[2] 
           elif ue.find("MP_SAVEHOSTFILE") >= 0:
              self.hostFile = uc[2]
           self.batchEnvCmds.append(ue)


   def parse_run_commands(self, runCmds):
        for rc in runCmds:
           self.batchRunCmds.append(rc.strip())
 

   def getTimeStamp(self,file):
       """ gets the modification time of the file"""
       try:
          mode = os.stat(file)
       except :
          raise
          return ""
       time = datetime.datetime.fromtimestamp( \
                           mode[stat.ST_MTIME]).isoformat()
       return  time


   def parse_cpuinfo(self):
       if self.OS == "":
          self.OS = os.uname()[0]
       if self.OS.upper() == "LINUX":
          f = open('/proc/cpuinfo', 'r')
          lines = f.readlines()
          count = 0
          for line in lines:
             if line.startswith("processor"):
                count += 1
          return count
       elif self.OS.upper == "AIX":
          (out,err,ret) = my_exec2("lsdev -c processor | grep -c proc")
          if ret != 0:
             return -1
          return out.strip()


   def getRunMachine(self):
       return self.runMachine

   def getNumberOfProcesses(self):
       if self.numberOfProcesses != -1:
          return self.numberOfProcesses
       elif self.numberOfNodes != -1 and self.processesPerNode != -1:
          return int(self.numberOfNodes) * int(self.processesPerNode)
       else:
          return -1

   def getProcessesPerNode(self):
       return self.processesPerNode

   def getNumberOfThreads(self):
       return self.numberOfThreads

   def getNumberOfNodes(self):
       return self.numberOfNodes

   def getCpusPerNode(self):
       return self.cpusPerNode

   def getLauncherArgs(self):
       return self.launcherArgs
