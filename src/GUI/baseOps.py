import __builtin__

def sum(data=[],args={}):
#   print "in sum data:%s, args:%s" %(data,args)
   #print "in sum data, answer is:%s" % __builtin__.sum(data)
   return __builtin__.sum(data)
      

def mean(data=[],args={}):
   #print "in mean data:%s, args:%s" %(data,args)
   if args.has_key("type"):
      type = args["type"]
   else:
      type = "arithmetic"
   if type == "arithmetic":
      #print "arithmetic mean requested"
      s = sum(data)
      a = float(s)/float(len(data))
      return a
   else:
      print "unexpected type given for mean: %s.\n This function accepts: \"arithmetic\", \"harmonic\", and \"geometric\"\n" % type
   return -1


def min(data=[],args={}):
  return __builtin__.min(data)

def max(data=[],args={}):
  return __builtin__.max(data)

def count(data=[],args={}):
  return __builtin__.len(data)
