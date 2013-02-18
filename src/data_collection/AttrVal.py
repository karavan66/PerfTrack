# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information. 

from PTexception import PTexception

class AttrVal:
   """A class to store attribute value pairs for parsing build and run data files."""
   def __init__(self):
       self.index = 0
       self.length = 0
       self.pairs = []


   def addPair(self, name, value=None,type="string"):
       """Add an attribute value pair. Only 'name' needs to have a value. If 'value' is not
          given, its value will be changed to ''.
       """
       if name == "" or name == None:
          raise PTexception("AttrVal.addPair: invalid value for 'name':%s" \
                            % name)
       #if value == "" or value == None:
       #   raise PTexception("AttrVal.addPair: invalid value for 'value':%s" \
       #                     % value)
       # allowing blank values because these show up in build and run data files
       if value == None:
          value = ""
       name = name.strip()
       value = value.strip()
       self.pairs.append((name,value,type))
       self.length += 1
    
   def addPairs(self, avlist):
       """Adds a list of pairs to the AttrVal pair list.
       """
       if type(avlist) != list:
          raise PTexception("AttrVal.addPairs: non-list 'avlist' argument")
       for av in avlist:
          try:
             a,v,t = av
          except:
             try:
                a,v = av
                t = "string"
             except:
                raise PTexception("AttrVal.addPairs: 'avlist' argument is not a list of pairs")
          self.addPair(a,v,t)

   def __iter__(self):
       """ To support iterating over the list of pairs
       """
       return self


   def next(self):
       """ To support iterating over the list of pairs
       """
       if self.index >= self.length:
          self.index = 0
          raise StopIteration
       ret = self.pairs[self.index]
       self.index += 1
       return ret
   
   def getNext(self):
       """Returns the next pair in the pairs list. Increments index.
       """
       if self.index >= self.length:
          self.index = 0
          return None,None,None
       ret = self.pairs[self.index]
       self.index += 1
       return ret

   def getLength(self):
       return self.length

   def getFirst(self):
       """Returns the first pair in the pairs list.
       """
       return self.pairs[0]

   def getLast(self):
       """Returns the last pair in the pairs list.
       """
       return self.pairs[self.length-1]

   def getCurrent(self):
       """Returns the current pair in the pairs list (what getNext returned last time).
       """
       if self.index-1 < self.length:
          return self.pairs[self.index-1]
       else:
          return None, None

