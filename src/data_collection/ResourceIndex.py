# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information. 

from Resource import Resource
from PTexception import PTexception
from PTcommon import cws

class ResourceIndex:
   """Container class for PerfTrack Resources"""
   def __init__(self):
       self.resesByName = {}
       self.resesByType = {}

   def addResource(self, res):
      # add a resource to the resource index
      if res.name in self.resesByName:
         # duplicate, return
         return
      # a dictionary of resources indexed by name
      self.resesByName[res.name] = res
      # we keep a dictionary indexed by resource type, too
      # the value for each self.resesByType[type]
      # is a dictionary indexed by the resource's names. I did it this way
      # to prevent duplicates and for speed
      # example:
      # resesByType['environment/module'] = 
      # {'env/libelf.so.1': <resource instance>, 
      # 'env/libmpi.so.1.0': <resource instance>}
      self.resesByType.setdefault(res.type,{})[res.name] = res

   def addResources(self, NRs):
      """Adds a list of resources to the execution
      """
      if type(NRs) != list:
         raise PTexception("Non-list type given to Resource.addResources" \
                           " for resource:%s" % self.name)
      # execute self.addResource on each element of NRs
      map(self.addResource, NRs)

   def updateResourceName(self, res, newName):
      # if we update the resource's name, then we need to update
      # the resource dictionaries
      # destroy old name entry
      del self.resesByName[res.name]
      # make a new name entry
      self.resesByName[newName] = res
      # destroy old type entry
      rd = self.resesByType[res.type]
      del rd[res.name]
      # make a new type entry
      self.resesByType.setdefault(res.type,{})[newName] = res
      # officially change the name
      res.setName(newName)
        

   def getResourcesSortedByName(self):
      # returns a list of resources sorted by name
      # the names are the keys of this dictionary
      names = self.resesByName.keys()
      # sort them
      names.sort()
      # this applies the 'get' method of the dictionary for each name in names,
      # essentially returning a list of resources sorted in name order
      return map(self.resesByName.get,names)
 
   def getResourcesSortedByType(self):
      # returns a list of dictionaries (indexed by name) sorted by type
      # the types are the keys of this dictionary
      types = self.resesByType.keys()
      # sort them
      types.sort()
      # this applies the 'get' method of the dictionary for each type in types,
      # essentially returning a list of dictionaries of resources in type order 
      return map(self.resesByType.get,types)

   def getAllResourceTypes(self):
      # returns a list of all the types of resources in this container
      types = self.resesByType.keys()
      types.sort()
      return types

   def getResourceDescendants(self,res):
      # returns the descendants of the resource res in a list
      # first get all the types
      types = self.resesByType.keys()
      reses = []
      for t in types:
         # if this type is prefixed by the type of res, 
         if t.startswith(res.type):
            for r in self.resesByType[t].values():
               # and the  name of this resource is prefixed by res's name
               # then, it's a descendant
               if r.name.startswith(res.name+Resource.resDelim):
                   reses.append(r)
      # this creates a list of tuples of (name,resource instance) in place
      reses[:] = [(r.name,r) for r in reses]
      # sort the reses by name
      reses.sort()
      # return a list of the resource instances
      return [val for (key,val) in reses]

   def findResourceByName(self,name):
      # looks to see if a resource by that name exists. If so, it is returned
      # otherwise, returns None
      if self.resesByName.has_key(name):
         return self.resesByName[name]
      return None

   def findOrCreateResource(self,name,type):
      # looks to see if a resource by that name exists. If so, it is returned
      # otherwise, creates one and returns it. The new resource is added to
      # the class data structures	
      res = self.findResourceByName(name)
      if res:
         return res
      else:
         res = Resource(name,type)
         self.addResource(res)
      return res

   def findResourcesByType(self, ftype):
      # returns a list of resources of type ftype, sorted by name
      d = self.resesByType.get(ftype,{})
      names = d.keys() 
      names.sort()
      return map(d.get, names)

   def findResourcesByShortType(self, stype):
      """Attempts to find resources with short type 'type.'
         If it doesn't find a match, [] is returned."""
      # searches through all types to see which ones end with stype
      # It continues to search even after it finds a match, because
      # there may be more than one match. e.g. /build/module/function
      # and /environment/module/function
      types = self.resesByType.keys()     
      reses = []
      for t in types:
         # found one
         if t.endswith(Resource.resDelim+stype):
            reses += self.resesByType[t].values()
      return reses
 

   def createContextTemplate(self):
      # returns a list of resources for the top-level context for performance
      # results. The context is a list of the most general types of resources 
      # in each type hierarchy.
      drs = self.getResourcesSortedByType()
      context = []
      first = True
      # the current "parent" type
      generalType = ""
      for dr in drs:
          # get the resources
          rs = dr.values()
          # sort by name of resources
          reses = [(r.name,r) for r in rs]
          reses.sort()
          reses[:] = [val for (key,val) in reses]
          for r in reses:
              t = r.type
              if t == "metric" or t == "performanceTool" :
                 pass
              elif first:
                 first = False
                 generalType = t
                 context.append(r)
              elif t == generalType:
                 context.append(r)
              # have we reached a new type?
              elif not t.startswith(generalType):
                 generalType = t
                 context.append(r)
      return context 
    

   def addSpecificContextResource(self,orig,addition):
      """Adds a single specific resource to the context. If the added resource is more specific than a resource that already exists in the context(i.e. is its child), the existing resource is replaced with the new resource. Otherwise, the resource is simply added to the list of context resources. Returns the new list of context resources."""
      found = False
      new = []
      for r in orig:
         # if addition matches a resource already in the list, then
         # the resource is added to the new list
         if not found and r.name == addition.name:
            found = True
            new.append(addition)
         # if addition is a child, replace parent with child in new list
         elif not found and r.isChild(addition):
            #print "%s is child of %s" % (addition.name,r.name)
            found = True
            new.append(addition)
            #break
         # else copy over original resource
         else:
            new.append(r)
      # else, simply add the resource to the list of context resources.
      if not found:
         new.append(addition)
      # sort the list by type
      new.sort(self.__cmpTypeThenName) 
      return new  

   def __cmpTypeThenName(self,x,y):
      """Comparator function for sorting resources by type and then by name. If resources have same type, they will be ordered by name."""
      if x.type == y.type:
         return x.name < y.name
      else:
         return x.type < y.type

   def addSpecificContextResources(self,orig,additions):
       """Adds a list of specific resources to the context template. If any of the added resources is a child of an existing resource (in orig), the resource in the original list is replaced with the addition. Otherwise, the resource is simply added to the list of context resources. Returns the new list of context resources.""" 
       for r in additions:
           orig = self.addSpecificContextResource(orig,r)
       return orig 


   def PTdF(self, delim=" "):
       # returns a list of strings to write to the ptdf file.
       # the strings should be written in the order that they are returned.
   
       # order of writing here is important
       # first resource types
       # then application
       # then execution
       # then resources and their attributes of type string, resources listed 
       # in lexicographical order
       # then any resource attributes that are of type resource
       # then performance results
      
       # gather all resources and string attributes to write in a list 
       # this is done for performance. At the end the lists are 'joined'.
       resAndAttrs = []
       # perf results list
       perfReses = []
       # special list for resource attributes of type resource to make sure
       # they get printed last. Right now they are printed as resource
       # constraints
       resConstr = []
       
       # gather types
       types = self.getAllResourceTypes()
       for t in types:
           pt_str = "ResourceType" + delim + cws(t) + "\n" 
           resAndAttrs.append(pt_str)
      
       # see if there's application and execution data 
       try:
          # expect one application resource
          [app] = self.findResourcesByType("application") 
          pt_str = app.PTdF()
          resAndAttrs.append(pt_str)
          # expect one execution resource
          [exe] = self.findResourcesByType("execution") 
          pt_str,perfRes_str,attr_str = exe.PTdF(app.name, delim)
          resAndAttrs.append(pt_str)
          perfReses.append(perfRes_str)
          resConstr.append(attr_str)
       except:
          # there is no application and/or execution for this data. 
          # this can happen if we are processing machine data
          app = None
          exe = None

       reses = self.getResourcesSortedByName()
       for r in reses:
          if r == exe or r == app:
             pass
          elif exe: # is there an execution resource for this data? 
             pt_str, perfRes_str, attr_str = r.PTdF(exe.name, delim)
             resAndAttrs.append(pt_str)
             perfReses.append(perfRes_str)
             resConstr.append(attr_str)
          else:
             pt_str, perfRes_str, attr_str = r.PTdF("", delim)
             resAndAttrs.append(pt_str)
             perfReses.append(perfRes_str)
             resConstr.append(attr_str)
           
       resAndAttrs = ''.join(resAndAttrs)
       resConstr = ''.join(resConstr)
       perfReses = ''.join(perfReses)
       return [resAndAttrs,resConstr,perfReses]
        
       
