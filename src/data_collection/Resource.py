# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information. 

from PTexception import PTexception
from PTcommon import cws

class Resource:
   """Holds information about a PerfTrack resource"""
   resDelim = "|"
   def __init__(self, resName="", type="", AttrVals=None):
      #print "new Resource: name:%s type:%s" % (resName, type)
      self.setName(resName) 
      self.setType(type)
      self.performanceResults = []
      if AttrVals == None:
         self.attributes = []
      else:
         self.attributes = []
         self.addAttributes(AttrVals)

   def dump(self, indent=0, recurse=False):
      """dump routine for debugging"""
      i = indent
      ind_str = ""
      while i > 0:
         ind_str += "  "
         i -= 1
        
      print(ind_str + "Name: " + self.name)
      print(ind_str + "type: " + self.type)
      print(ind_str + "attributes: " + str(self.attributes))

   def PTdF(self, exeName=None, delim="\t"):
      """Returns a string that contains the information about the resource
         in PTdF format"""
      toWrite = ""
      resConstraints = ""
      if self.type != "execution" : 
         toWrite = "Resource" + delim + cws(self.name) + delim \
                   + cws(self.type) + delim
         if exeName != None:
            toWrite += cws(exeName) + "\n"
      for (n,v,t) in self.attributes:
         # for now resource attributes of type "resource" are written out as
         # resource constraints. Later they will be written out as attrs
         # of type "resource"
         if t  == "string":
            toWrite += "ResourceAttribute" + delim + cws(self.name) + delim \
                 + cws(n) + delim + cws(v) + delim + cws(t) + "\n"
         else:
            resConstraints += "ResourceConstraint" + delim + cws(self.name) + \
                 delim  + cws(v)  + "\n"
      # write perf results for non-execution resources
      perfRs = ""
      if self.type != "execution":
         perfReses = []
         #print "Resource.PTdF: There are %d non-exec perf results." % len(self.performanceResults)
         for p in self.performanceResults:
            #print "Resource.PTdF: perfResults for non-exec resource: %s" % p
            perfReses.append(p.PTdF(self.name,delim,"nonExec"))
         perfRs = ''.join(perfReses)

      return toWrite, perfRs, resConstraints

   def isChild(self, res):
     """Determines whether res is a child of this resource based on its name."""
     if res.name == self.name:
        return False
     if res.name.startswith(self.name+Resource.resDelim) and res.type.startswith(self.type):
        return True
     return False 


   def setName(self, resName):
      """Sets the resource name attribute"""
      if resName == "" or resName == None:
         raise PTexception("Resources must have a name. Given name:%s ." \
                           % resName)
      # check for illegal characters
      if resName.find('::') >= 0 or resName.find(',') >= 0 or \
         resName.find('(') >= 0 or resName.find(')') >= 0 or \
         resName.find('####') >= 0: 
         raise PTexception("Resource names cannot contain the following characters: ',' '(' ')' '::' '####'.  Given name:%s ."  % resName)
    
      self.name = resName 

   def getName(self):
      return self.name

   def setType(self, type):
      """Sets the resource type attribute"""
      if type == "" or type == None:
         raise PTexception("Resources must have a type. Given type:%s ." \
                           % type)
      self.type = type
   
   def getType(self):
      return self.type

   def addAttribute(self, attrName, value, type="string"):
      """Adds an attribute value pair to the list of attributes of the resource.      """
      if attrName == "" or attrName == None:
         raise PTexception("Resource attribute names must have a value. " \
                           "Given attribute name:%s for resource:%s." \
                            % (attrName,self.name))
      if value == "" or value == None:
         raise PTexception("Resource attribute values must have a value. " \
                           "Given attribute value :%s for resource:%s."\
                            % (value,self.name))
      # single quotes upset databases, replace them with `
      if value.find("'") >= 0:
         value = value.replace("'","''")
      for a,v,t in self.attributes:
          #if attrName already exists, replace it
          if a == attrName:
             self.attributes.remove((a,v,t))
             self.attributes.append((attrName,value,type))
             return
      # otherwise, just add it to the list
      self.attributes.append((attrName,value,type))

   def addAttributes(self, AVs):
      """Adds a list of attribute value pairs to the list of attributes of 
         the resource."""
      if type(AVs) != list:
         raise PTexception("Non-list type given to Resource.addAttributes" \
                           " for resource:%s" % self.name)
      for av in AVs:
         try:
            (a,v,t) = av
         except:
            raise PTexception("Non-triple type in list given to Resource." \
                              "addAttributes for resource:%s" % self.name)
         self.addAttribute(a,v,t)
 
   def getAttributes(self):
      return self.attributes


   def getAttributeByName(self,attr_name):
      # looks for attributes with name attr_name. Returns the 3-tuple if
      # a match is found. Otherwise, returns a 3-tuple of Nones.
      for n,v,t in self.attributes:
          if n == attr_name:
             return (n,v,t) 
      return (None, None, None)

   def addPerfResult(self, perfRes):
       #print "Resource.addPerfResult: called on resource %s" % self.name
       """Adds a performance result to a resource"""
       if perfRes == None:
          raise PTexception("Resource.addPerfResult: Attempting to add a " \
                            "None-valued perfResult to "\
                            "resource:%s." % self.name )
       self.performanceResults.append(perfRes)


   def addPerfResults(self, perfReses):
      """Adds a list of performance results to a resource"""
      if type(perfReses) != list:
         raise PTexception("Resource.addPerfResults: Non-list type given " \
                           "for adding results to resource:%s" % self.name)
      for perfRes in perfReses:
          self.addPerfResult(perfRes)

   def extend(self, name, type):
      return Resource(self.name + self.resDelim + name, self.type + self.resDelim + type)
