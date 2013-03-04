# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information. 

from PTexception import PTexception
from Resource import Resource
from PTcommon import cws

class Application(Resource):
   """This is a class to hold information about application objects"""
   def __init__(self, appName="", AVs=None, executions=None):
      Resource.__init__(self,appName,"application")
      if AVs == None:
         self.attributes = []
      else:
         self.attributes = []
         self.addAttributes(AVs)
      if executions == None:
         self.executions = []
      else:
         self.executions = []
         self.addExecutions(executions)
   
   def dump(self):
      """ Dump routine for debugging """
      print "name: " + self.name
      print "attributes: " + str(self.attributes)
      print "resourceTypes: " + str(self.resourceTypes)
      print "executions: " 
      self.dumpExecutions()

   def dumpExecutions(self):
      """ Dump routine for debugging """
      for exe in self.executions:
          exe.dump(1, True)

   def PTdF(self, delim=" "):
      """Returns a string that contains the information about the 
         application in PTdF format"""
      toWrite = "Application" + delim + cws(self.name) + "\n" 
      for (n,v) in self.attributes:
          toWrite += "ResourceAttribute" + delim + cws(self.name) \
                  + delim + cws(n) + delim + cws(v) + delim + "string" + "\n"
      return toWrite

   def setName(self, appName):
      """Sets application name attribute"""
      if appName == "" or appName == None:
         raise PTexception("Applications must have a name. Given name:%s ." \
                           % appName)
      Resource.setName(self,appName)

   def addExecution(self, newExecution):
      """Adds an Execution to the application"""
      if newExecution == None:
         raise PTexception("Attempting to add a None-valued execution to "\
                           "application:%s." % self.name )
      try:  #list.index() throws exception if not found
         self.executions.index(newExecution)
      except ValueError:
         self.executions.append(newExecution)

   def addExecutions(self, NEs):
      """Adds a list of Executions to the application"""
      if type(NEs).__name__!='list':
         raise PTexception("Non-list type given to Application.addExecutions"\
                           " for application:%s" % self.name)
      for ne in NEs:
          self.addExecution(ne)
 
   def getExecutions(self):
      return self.executions


