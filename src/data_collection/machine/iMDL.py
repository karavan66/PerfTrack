#! /usr/bin/env python

import gmLogger
import re

# ++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++
# Intermediate Machine Data Library
#
# amaubaa   3/14/2006   Initial Release
## filename: iMDL.py

# Create Logging object
logObj = gmLogger.gmlog()

# Function: Get Line that starts with a word
# Preconditions: None
# Postconditions: file pointer is at the found line
#                 or end of file if no matching line exists.
#
# Returns the line that matches
def getLineThatStartsWith(fileHandle,startWord):
        fileHandle.seek(0)
        for line in fileHandle:
                if line.startswith(startWord):
                        return line
        #return ''
        return None

def getLinesThatStartWith(fileHandle,startWord):
        fileHandle.seek(0)
        lines = []
        for line in fileHandle:
                if line.startswith(startWord):
                        lines.append(line)
        return lines 

class imdl:
   def __init__(self, configDB, format):
      """
       The imdl constructor.  A db specifying machine resourceName and
       resourceTypeName hierarchies is passed in.  This method currently
       supports the reading of a text file, configured according to the
       Intermediate Machine Description Language
      """
      self.configDB = configDB
      self.format = format #PTdf or PERI
      word = r"'([^']+)'|([\S]+)"
      self.re_word = re.compile(word)

   def getConfiguration(self):
      return self.configDB

   def getAttribNameFor(self,hostSysMethod):
      """
         Ask PerfTrack database for the Attribute Name the object collects
            Not implemented yet
            prototype ptdb_int_get_Attribute_name_for(hostSysMethod)
            If PerfTrack database does not know then look in local database
         Local database is really just a config file
            Open the Config file where the object to attrib name map exists
      """
      try:
         f = open(self.configDB, 'r')
         # TO DO Verfiy the config file is in correct format
      except IOError:
         logObj.gmLogWrite(2,repr(self) + " Local config file not found: " +\
                           self.configDB)
         return 'Unknown'

      # If the length is 0, the attribute name is not in the 
      # Config file. return an unknown name
      line = getLineThatStartsWith(f, "'" + hostSysMethod + "'")
      f.close()
      attrName = ""
      if not line:
         attrName = "Unknown"
      else:
         currInput = [(qw or sw) for qw, sw in re.findall(self.re_word,line)]
         #print "REized: " 
         #print currInput
         attrName = currInput[1]

      return attrName

   def getResources(self):
      """ Return all the resources that we should collect data for.
         Returns a list of tuples (name, type)
      """
      try:
            f = open (self.configDB, 'r')
            # TO DO Verfiy the config file is in correct format
      except IOError:
         logObj.gmLogWrite(2,repr(self) + " Local config file not found: " + \
                           self.configDB)
         return 'Unknown'

      lines = f.readlines()
      resources = []
      for line in lines:
          if line.startswith('ResourceType'): # resource definition
             pts = line.strip("ResourceType").strip() # ResourceType 'type':'name'
             try:
                if self.format == "PTdf":
                   type,name= pts.split(':')
                elif self.format == "PERIxml":
                   type,name= pts.split(' ')
                else:
                   type,name= pts.split(':')
                type = type.rstrip("'").lstrip("'") # remove quotes
                name = name.rstrip("'").lstrip("'") # remove quotes
                resources.append((name,type))
             except:
                logObj.gmLogWrite(2,repr(self) + " Bad resource definition: "+ \
                           line)

      return resources


   def getResourceTypeFor(self,U_ID,attributeName):
      """
         Ask PerfTrack database Resource Type this attribute lives under
            Not implemented yet
            prototype ptdb_int_get_ResourceType_for(attributeName)
            If PerfTrack database does not know then look in local database
         Local database is really just a config file
         Open the Config file where the object to attrib name map exists
      """
      # TODO, think about whether it makes sense to search for type by 
      # attribute name. For example, libraries and compilers can have 
      # attributes called "version". How do you know which type to return?
      # Note: it doesn't matter now, because the attributeName is not used
      # in this function, but the comment above makes it seem as if the 
      # original intent was to use it.
      try:
            f = open (self.configDB, 'r')
            # TO DO Verfiy the config file is in correct format
      except IOError:
         logObj.gmLogWrite(2,repr(self) + " Local config file not found: " + \
                           self.configDB)
         return 'Unknown'

      # If the attribute name is found on the same line as the U_ID, then 
      # the resource type is the last item in the hierachy tree.

      line = getLineThatStartsWith(f, "'" + U_ID + "'")
      f.close()
      resourceType = ""
      if not line:
         resourceType =  'Unknown'
      else:
         currInput = [(qw or sw) for qw, sw in re.findall(self.re_word,line)]
         #print "REized: "
         #print currInput
         if len(currInput) > 2:
            resourceType = currInput[2]
         else:
            resourceType = 'Unknown'
      #print "getResourceTypeFor(): " + attributeName + \
      #      " has resource type: " + resourceType
      return resourceType


   def getResourceNameFor(self, ResourceType):
      """
         Ask PerfTrack database for the Resource Name
            Not implemented yet
            prototype ptdb_int_get_ResourceNmae_for(?????????)
         If PerfTrack database does not know then look in local database
            Local database is really just a config file
         Open the Config file where the object to attrib name map exists.
            This is the top section of the config file where
            resource types are mapped to resource names, using the following
            syntax:  ResourceType 'type':'name'
      """
      try:
         f=open(self.configDB, 'r')
         # TO DO Verfiy the config file is in correct format
      except IOError:
         logObj.gmLogWrite(2,repr(self) + " Local config file not found: iMDL.cfg")
         return 'Unknown'
      if self.format == "PERIxml":
         spltter = " "
      else:
         spltter = ":"
      lines = getLinesThatStartWith(f, "ResourceType")
      rName = "Unknown"
      for rt in lines:
         str1 = rt.strip("ResourceType").strip()
         tmpStr = str1.split(spltter)[0].strip("'")
         if tmpStr == ResourceType:
           rName = str1.split(spltter)[1].strip("'")
           break
      if rName.strip() == "":
         rName = "Unknown"
      #print "rName:%s" % rName
      return rName

   def getOverrideResourceNameHierarchyFor(self,U_ID):

      # This method applies to the config file only
      # If there is an entry in the config file for
      # for this uniquie ID. THen override the 
      # resource name hierarchy with whats in the file.
   
      try:
         #f=open('iMDL.cfg', 'r')
         f = open (self.configDB, 'r')
         # TO DO Verfiy the config file is in correct format
      except IOError:
         logObj.gmLogWrite(2,repr(self) + " Local config file not found: " + \
                           self.configDB)
         return 'Unknown'
      line = getLineThatStartsWith(f, "'"+U_ID+"'")
      if not line:
         return "Unknown"
      f.close()
      nameHierarchy = ""
      currInput = [(qw or sw) for qw, sw in re.findall(self.re_word,line)]
      #print "getOverrideResourceNameHierarchyFor() REsized:"
      #print currInput 
      if len(currInput) != 4:
            nameHierarchy = 'Unknown'
      else:
         nameHierarchy = currInput[3]
      return nameHierarchy


   def getResourceTypeHierarchyFor(self,resourceType):
      """   
       Ask PerfTrack database for the hierarchy
             Not implemented yet
             prototype ptdb_int_get_hierarchy_for(resourceName)
       If PerfTrack database does not know then look in local database
             Local database is really just a config file
       Open the Config file where the object to attrib name map exists
      """
      try:
         f=open(self.configDB, 'r')
         # TO DO Verfiy the config file is in correct format
      except IOError:
         logObj.gmLogWrite(2,repr(self) + " Local config file not found: " + \
                           self.configDB)
         return 'Unknown'

      resourceTypeHierarchy = ""
      lines = getLinesThatStartWith(f, "Hierarchy")
      for line in lines:
          currInput = [(qw or sw) for qw, sw in re.findall(self.re_word,line)]
          #print "getResourceTypeHierarchyFor() REsized:"
          #print currInput
          resourceTypeHierarchy = ""
          if not line:
             resourceTypeHierarchy = 'Unknown'
          else: 
             rts = currInput[1].split("/")
             for rt in rts: 
                if rt == resourceType:
                   return resourceTypeHierarchy 
                resourceTypeHierarchy = resourceTypeHierarchy + "/" + rt 
      return ""
