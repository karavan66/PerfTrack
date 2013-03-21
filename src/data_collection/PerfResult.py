# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information. 

from PTexception import PTexception
from PTcommon import cws

class PerfResult:
   """Holds information for one PerfTrack performance result"""
   def __init__(self, focus=None, perfTool=None, metric=None, value="",\
               units="noValue", startTime="noValue", endTime="noValue"):
      self.setFocus(focus)
      self.setPerformanceTool(perfTool)
      self.setMetric(metric)
      self.setValue(value)
      self.setUnits(units)
      self.setStartTime(startTime)
      self.setEndTime(endTime)
 
   def dump(self, indent=0, recurse=False):
      """dump routine for debugging"""
      i = indent
      ind_str = ""
      while i > 0:
         ind_str += "  "
         i -= 1

      for f,t in self.focus:
         print ind_str + "focus: " + f.name
      print ind_str + "perfTool: " + self.performanceTool.name
      print ind_str + "metric: " + self.metric.name
      print ind_str + "value: " + self.value
      print ind_str + "units: " + self.units
      print ind_str + "start time: " + self.startTime
      print ind_str + "end time: " + self.endTime


   def PTdF(self, exeName, delim="\t", type=None):
      """Returns a string with the information of the performance result
         in PTdF format"""
      if type == None:
         toWrite = "PerfResult" + delim + cws(exeName) + delim
      elif type == "nonExec":
         toWrite = "Result" + delim + cws(exeName) + delim
      focusname = ""
      first = True
      for flist,type in self.focus:
         if first:
            first = False
         else:
            focusname += "::"  # this is the delimiter between foci

         for f in flist:
            focusname += f.name + "," # this is the delim b/w focus names
         focusname = focusname.rstrip(',') # get rid of last comma
         if len(self.focus) != 1: # if there's just one focus, it's primary
            focusname += "(" + type + ")"
      toWrite += cws(focusname) + delim + cws(self.performanceTool.name) + delim
      toWrite += cws(self.metric.name) + delim + cws(self.value) + delim \
              + cws(self.units) + delim
      toWrite += cws(self.startTime) + delim + cws(self.endTime) + "\n"
      return toWrite

   def setFocus(self, focus): 
      # expecting either a list of (focus,type) pairs, where focus is a list
      #  of resource ids
      # OR
      # a list of resource ids
      self.focus = []
      try:
         for f,t in focus:
            self.addFocus(f,t) 
      except:
         self.addFocus(focus)
         

   def addFocus(self, focus, type = "primary"):
      """Adds a focus to the performance result."""
      if focus == None or focus == []:
         raise PTexception("A perfResult must have a focus. Given focus:" \
                           "%s." % focus)
      self.focus.append((focus,type))

   def getFocus(self):
      return self.focus

   def setPerformanceTool(self, perfTool):
      """Sets the performance tool attribute of the performance result."""
      if perfTool == None:
         raise PTexception("A perfResult must have a perfTool. Given perfTool:"\
                           "%s." % perfTool)
      self.performanceTool = perfTool

   def getPerformanceTool(self):
      return self.performanceTool

   def setMetric(self, metric):
      """Sets the metric attribute of the performance result."""
      if metric == None:
         raise PTexception("A perfResult must have a metric. Given metric:"\
                           "%s." % metric)
      self.metric = metric
  
   def getMetric(self):
      return self.metric

   def setValue(self, value):
      """Sets the value attribute of the performance result."""
      if value == None or value == "":
         raise PTexception("A perfResult must have a value. Given value:"\
                           "%s." % value)
      self.value = value
 
   def getValue(self):
      return self.value

   def setUnits(self, units):
      """Sets the units attribute of the performance result."""
      if units == None or units == "":
         units = "noValue"
      self.units = units

   def getUnits(self):
      return self.units

   def setStartTime(self, start):
      """Sets the startTime attribute of the performance result."""
      if start == None or start == "":
         start = "noValue"
      self.startTime = start

   def getStartTime(self):
      return self.startTime

   def setEndTime(self, end):
      """Sets the endTime attribute of the performance result."""
      if end == None or end == "":
         end = "noValue"
      self.endTime = end

   def getEndTime(self):
      return self.endTime
