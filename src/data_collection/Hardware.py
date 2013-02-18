#!/usr/bin/env python

# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information. 

from optparse import OptionParser
from Resource import Resource
from ResourceIndex import ResourceIndex
from PTexception import PTexception
import PTcommon
import sys

def main():
   try:
      options = checkInputs()
      grids = getHardwareInfo(options.dataFile)

      ptdfname = options.ptdfFile
      f = open(ptdfname,'w')
      for grid in grids:
         f.write(grid.PTdF(""," "))
      f.close()
   except PTexception, a:
      print a.value 
      return

def getHardwareInfo(resIdx, filename ): 
  
  process(resIdx, filename)
  

 
def getMachineAVs( resIdx, attrs ):
    """ Takes attrs, which is a list of name, value pairs, and inserts them
    """

    MachName = ""
    NodeNumProcs = 0
    partitions = []  # list of (name, partition size) tuples
    NodeNamePattern = ""

    gridAVs = []
    machineAVs = []
    partitionAVs = []
    nodeAVs = []
    processorAVs = []
   
    lineno = 0 

    for nv in attrs:
        lineno += 1
        try:
           name,value = nv
        except:
           raise PTexception("No value given for attribute:%s. Offending line"\
                             ":%d" %(nv,lineno))
        value = value.strip()
        name = name.strip()
   
        # grid info
        if name.startswith("Grid"):
           if value != "":
              # name is recorded as the name of the resource, don't need
              # to keep it as an attribute
              if name != "GridName":
                gridAVs.append((name, value)) 
        # machine info
        elif name == "MachName":
           MachName = value
        elif name.startswith("Mach"):
           if value != "":
              if name == "MachArchName":
                 machineAVs.append(("Architecture",value,"string")) 
              elif name == "MachConfigEnd":
                 machineAVs.append(("ConfigEnd",value,"string")) 
              elif name == "MachConfigStart":
                 machineAVs.append(("ConfigStart",value,"string")) 
              elif name == "MachHomoNodes":
                 machineAVs.append(("Homogenous",value,"string")) 
              # ATTR CHANGE TODO
              # this attribute will be moved to node
              elif name == "MachNodeInterConAdapter":
                 machineAVs.append(("Interconnect Adapter",value,"string")) 
              elif name == "MachNodeInterConGB/sec":
                 machineAVs.append(("Interconnect GB/sec",value,"string")) 
              elif name == "MachNodeInterConnect":
                 machineAVs.append(("Interconnect",value,"string")) 
              elif name == "MachNumNodes" or name == "MachNumOfNodes":
                 machineAVs.append(("NumOfNodes",value,"string")) 
              elif name == "MachParIOSizeTB":
                 machineAVs.append(("ParallelIOSize TB",value,"string")) 
              elif name == "MachTotalDiskSpaceGB":
                 machineAVs.append(("TotalDiskSpace GB",value,"string")) 
              elif name == "MachType":
                 machineAVs.append(("Type",value,"string")) 
              elif name == "MachVendor":
                 machineAVs.append(("Vendor",value,"string")) 
              elif name == "MachTOPS":
                 machineAVs.append(("TOPS",value,"string")) 
              elif name == "MachTflops":
                 machineAVs.append(("Tflops",value,"string")) 
              else:
                 machineAVs.append((name,value,"string")) 
        # partition info
        elif name == "PartitionNames":
           names = value.split()
           for name in names:
              partitions.append((name,-1))
        elif name == "PartitionSizes":
           i = 0
           psizes = value.split()
           if len(psizes) < len(partitions):
              raise PTexception("Missing partition size. Offending line: %d."\
                                % lineno)
           while i < len(partitions): # set the number of nodes in part
               partitions[i] = (partitions[i][0], psizes[i])
               i += 1
        # node info
        elif name == "NodeNames":
           NodeNamePattern = value
        elif name == "NodeNumProcs":
           NodeNumProcs = value
           if value != "":
              nodeAVs.append(("NumOfProcs",value,"string"))
        elif name.startswith("Node"):
           if value != "":
              if name == "NodeL1DataAssoc":
                 nodeAVs.append(("L1 Data Associativity",value,"string"))
              elif name == "NodeL1DataKB":
                 nodeAVs.append(("L1 Data Size KB",value,"string"))
              elif name == "NodeL1InstrAssoc":
                 nodeAVs.append(("L1 Instruction Associativity",value,"string"))
              elif name == "NodeL1InstrKB":
                 nodeAVs.append(("L1 Instruction Size KB",value,"string"))
              elif name == "NodeL1LineSizeBytes":
                 nodeAVs.append(("L1 Line Size Bytes",value,"string"))
              elif name == "NodeL2MB":
                 nodeAVs.append(("L2 MB",value,"string"))
              elif name == "NodeL3MB":
                 nodeAVs.append(("L3 MB",value,"string"))
              elif name == "NodeLocalDiskMb/sec":
                 nodeAVs.append(("Local Disk MB/sec",value,"string"))
              elif name == "NodeLocalDiskSizeGB":
                 nodeAVs.append(("Local Disk Size GB",value,"string"))
              elif name == "NodeMainMemGB":
                 nodeAVs.append(("Main Memory GB",value,"string"))
              elif name == "NodeMainMemGB/sec":
                 nodeAVs.append(("Main Memory GB/sec",value,"string"))
              elif name == "NodeMainMemType":
                 nodeAVs.append(("Main Memory Type",value,"string"))
              elif name == "name":
                 pass
              else:
                 nodeAVs.append((name,value,"string"))
        # processor info
        elif name.startswith("Proc"):
           if value != "":
              if name == "ProcBits":
                 processorAVs.append(("WordSize",value,"string"))
              elif name == "ProcMHz":
                 processorAVs.append(("MHz",value,"string"))
              elif name == "ProcType":
                 processorAVs.append(("Type",value,"string"))
              else: 
                 processorAVs.append((name,value,"string"))

    if MachName == "" or MachName == None:
       raise PTexception("There was no name given for the machine. Need value "\
                         "for the attribute 'MachName'.")    
    if NodeNamePattern == "" or NodeNamePattern == None:
       raise PTexception("There were no node names given. Need a value for" \
                         " the attribute 'NodeNames'.")
    if len(partitions) == 0:
       raise PTexception("There were no partition names given. Need a value" \
                         " for the attribute 'PartitionNames'")
    if NodeNumProcs == 0:
       raise PTexception("No value was specified for attribute NodeNumProcs.")
    grid = Resource("SingleMachine"+MachName, "grid", gridAVs) 
    resIdx.addResource(grid)
    machine = Resource(grid.name+Resource.resDelim+MachName, "grid"+Resource.resDelim+"machine", machineAVs)
    resIdx.addResource(machine)

    nodeNumDigits = parseNodeNamePattern(NodeNamePattern)

    # need to make sure that partition sizes are correct in case
    # a parition is listed twice because nodes in parition are not
    # contiguous name-wise
    partitions = checkPartitions(partitions) 

    nodeTotal = 0
    for p in partitions:
        nodeIndex = 0
        partitionChunkSize = int(p[1])
        partitionRealSize = int(p[2])
        print "processing partition %s of %d nodes" % (p[0], partitionChunkSize)
        part = Resource(machine.name+Resource.resDelim+p[0], "grid"+Resource.resDelim+"machine"+Resource.resDelim+"partition",  partitionAVs+[("NumOfNodes",str(partitionRealSize), "string")])
        resIdx.addResource(part)
        while nodeIndex < partitionChunkSize:
            # if the node's name has three digits for the number part 
            # e.g. node000
            if nodeNumDigits == 3:
               if nodeTotal < 10:
                  nodeCountStr = "00" + str(nodeTotal)
               elif nodeTotal < 100:
                  nodeCountStr = "0" + str(nodeTotal)
            # if the node's name has two digits for the number part 
            # e.g. mynode00
            elif nodeNumDigits == 2:
               if nodeIndex < 10:
                  nodeCountStr = "0" + str(nodeTotal)
            # if the node's name has one digit for the number part 
            # e.g. mynode0
            else:
               nodeCountStr = str(nodeTotal)
            nodeName = "%s%s" % (MachName.lower(), nodeCountStr)
            node = Resource(part.name+Resource.resDelim+nodeName,\
                     "grid"+Resource.resDelim+"machine"+Resource.resDelim+"partition"+Resource.resDelim+"node", nodeAVs)
            resIdx.addResource(node)
            procIndex = 0
            while procIndex < int(NodeNumProcs):
               procName = str(procIndex) 
               proc = Resource(node.name+Resource.resDelim+procName, \
                       "grid"+Resource.resDelim+"machine"+Resource.resDelim+"partition"+Resource.resDelim+"node"+Resource.resDelim+"processor",processorAVs)
               resIdx.addResource(proc)
               procIndex += 1
            nodeIndex += 1
            nodeTotal += 1

    return grid


def checkPartitions(partitions):
    # takes  a list of partition names and sizes
    # The sizes are the number of contiguous nodes that belong 
    # to that partition. We want to count up the total number of nodes
    # that belong to the partition.
    # example:
    # node0-node21 interactive
    # node22-node644 batch
    # node645-node657 vtune
    # node658-node1007 batch
    # node1008-node1023 debug
    # 
    # here we have the batch partition listed twice, with vtune nodes between
    # the two batch 'chunks'
    # the 'size' for each batch partition would be the number of nodes in each
    # chunk. We also need to know the total number of nodes that belong to the
    # batch partition. This function returns a list of tuples:
    # (partitionName, chunkSize, realSize)
    # where chunkSize is the number of nodes in the 'chunk' and realSize is 
    # the number of nodes that belong to the entire partition

    temp = {}
    for name,size in partitions:
        if name in temp:
           temp[name] += int(size)
        else:
           temp[name] = int(size)
    newPartitions = []
    for name,chunkSize in partitions:
        realSize = temp[name]
        newPartitions.append((name, chunkSize, realSize))
    return newPartitions     
        
        
def parseNodeNamePattern(pt):
    # parses strings like {node0, node1, ...., node1024}
    # or {node000, node001, ...., node999}
    # to see how many digits the node number should have in it
    # it starts at the end of the first node (e.g. node0 or node000) and
    # counts the number of digits (e.g. 1 or 3)
    pt = pt.rstrip("}").lstrip("{")
    nodes = pt.split(",")
    node0 = nodes[0]
    go = True
    i = 0
    while go:
       i = i + 1
       d = node0[len(node0)-i:]
       if not d.isdigit():
          go = False
    return i-1



def process(resIdx, filename):

    

    # open the data file
    try:
       f = open(filename, 'r')
    except:
       raise PTexception("Hardware.process: unable to open machine data file"\
                         ":%s." % filename)

    # make a list

    line = f.readline()
    while line != '':
       if line.startswith("BEGIN"):
           attrs = []
           line = f.readline()
           # while not end of machine or EOF
           while line != '' and not line.startswith("END"): 
              # get this value
              data = line.split('####', 1)  # strip comment
              attr_val = data[0].split(None, 1)    # split data on whitespace
              # hack to keep this version consistent with re version
              # removes lines beginning with comments
              if len(attr_val) == 0:
                 line = f.readline()
                 continue
              # adds empty string to attributes with blank entries
              if len(attr_val) == 1:
                 attr_val.append('')
              attrs.append(attr_val)
              line = f.readline()
           getMachineAVs(resIdx, attrs )  # get machine data
       line = f.readline()

    f.close()

def checkInputs():
    """Parses command line arguments and returns their values"""

    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-i","--in_file", dest="dataFile", 
                      help="the input machine data file name")
    parser.add_option("-o","--out_file", dest="ptdfFile", 
                      help="the name for the PTdF file")

    (options, args) = parser.parse_args()

    if not options.dataFile:
       parser.print_help()
       raise PTexception("-i or --in_file argument required")
    if not options.ptdfFile:
       parser.print_help()
       raise PTexception("-o or --out_file argument required")
  
    return options


if __name__ == "__main__":
        sys.exit(main())

