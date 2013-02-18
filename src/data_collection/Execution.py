# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information. 

from Resource import Resource
from PTexception import PTexception
from PerfResult import PerfResult
from PTcommon import cws

class Execution(Resource):
   """Holds information about one PerfTrack execution"""
   def __init__(self, resName="", AttrVals=None):
       Resource.__init__(self, resName, "execution", AttrVals)
       self.performanceResults = []
       self.application = None


   def dump(self, indent=0, recurse=False):
       """Dump routine for debugging."""
       i = indent
       ind_str = ""
       while i > 0:
          ind_str += "  "
          i -= 1

       Resource.dump(self, indent, recurse)
       print ind_str + self.name + "'s performanceResults: " \
             + str(len(self.performanceResults)) 
       for p in self.performanceResults:
          p.dump(indent+1, recurse)

   def PTdF(self, appName, delim="\t"):   
       """Returns a string that contains the information about the
          Execution in PTdF format"""
       #print "Execution.PTdF: called"
       # write this execution
       resConstraints = ""
       toWrite = "Execution" + delim + cws(self.name) + delim \
                 + cws(appName) + "\n"
       # write any attributes of this execution
       attrstr,ignore, resConst = Resource.PTdF(self,self.name, delim)
       toWrite += attrstr
       resConstraints += resConst
       # write the perf results
       perfReses = []
       for p in self.performanceResults:
          perfReses.append(p.PTdF(self.name,delim))
       perfRs = ''.join(perfReses)
       return toWrite, perfRs, resConstraints

   def setApplication(self, app):
       self.application = app

   def addPerfResult(self, perfRes):
       """Adds a performance result to the execution"""
       if perfRes == None:
          raise PTexception("Attempting to add a None-valued perfResult to "\
                            "execution:%s." % self.name )
       self.performanceResults.append(perfRes)


   def addPerfResults(self, perfReses):
      """Adds a list of performance results to the execution"""
      if type(perfReses) != list:
         raise PTexception("Non-list type given to Execution.addPerfResults"\
                           " for execution:%s" % self.name)
      for perfRes in perfReses:
          self.addPerfResult(perfRes)

