#!/usr/bin/env python
from glob import glob
from optparse import OptionParser, SUPPRESS_HELP
import sys,os
import re

def main(argv=sys.argv):
    procmhz = None
    proctype = None
    numprocs = None

    usage = "usage: %prog [options]\nexecute '%prog --help' to see options"
    version = "%prog 1.0"
    parser = OptionParser(usage=usage,version=version)
    parser.add_option("-n","--name", dest="machine_name", action="store", help="machine name of system")
    parser.add_option("-s","--system_details", dest="sys_file",  action="store",
                      help="the location of the system details file")
    parser.add_option("-m", "--machine_file", dest="machine_file", 
                      help="output name of the machine data file", default="-")

    (options, args) = parser.parse_args(argv[1:])
    
    machine_name = options.machine_name
    if (options.machine_name == None):
        print "Specify machine name with -n"
        sys.exit(1)

    if (options.sys_file == None):
        print "Specify the input system details file with -s"
        sys.exit(1)

    if (not os.path.exists(options.sys_file)):
        print "\"%s\" input system details file does not exist" % options.sys_file
        sys.exit(1)

  
    f_system = open(options.sys_file, "r")
    details = dict()
    for line in f_system.readlines():
        #print line
        try:
            (left, right) = line.split("|")
        except:
            print "%s :: invalid statement"
            sys.exit(1)

        left = left.strip()
        right = right.strip()
        left = re.sub("\s+", " ", left)
        right = re.sub("\s+", " ", right)

        if (left == "Start Time" or left == "End Time"):
            pass
        elif (left == "Processor"):
            proctype = right
            proc_match = re.search("([0-9]+)(?:\.([0-9]+))? *([GM])Hz", right)
            if (proc_match):
                speed_part = proc_match.group(2)
                if (speed_part == None):
                    speed_part = 0
                if (len(speed_part) < 3):
                    speed_part += "0" * (3 - len(speed_part))
                elif (len(speed_part) == 3):
                    pass
                elif (len(speed_part) > 3):
                    speed_part = speed_part[0:2]
                speed_part = int(speed_part)
                speed = int(proc_match.group(1)) * 1000 + int(speed_part)
                mult = 1
                if (proc_match.group(3) == "M"):
                    mult = 1
                else:
                    mult = 10**3
                speed *= mult
                procmhz = speed
            else:
                raise Exception("Can't find CPU Speed in SystemData \"%s\" Expecting XX.XX [GM]Hz" % right)
            
        elif(left == "Processor Cores"):
            numprocs = int(right)
        else:
            index = 1
            left = left.replace(" ", "_")
            left_key = left
            while left_key in details:
                left_key = "%s_%03d" % (left, index)
                index += 1
                
            details[left_key] = right

    error = 0
    if (machine_name == None):
        print "MachineName unspecified"
        error += 1
    if (numprocs == None):
        print "Number of Processors Unspecified"
        error += 1
    if (proctype == None):
        print "Processor Type unspecified"
        error += 1
    if (procmhz == None):
        print "Processor MHz unable to determined"
        error += 1

    if (error > 0):
        sys.exit(1)

    if (options.machine_file == '-'):
        outf = sys.stdout
    else:
        try:
            outf = open(options.machine_file, "w")
        except:
            print "An error occurred while opening %s for write" % options.machine_file
            sys.exit(1)

    outf.write("BEGIN %s\n" % machine_name)
    outf.write("MachName %s\n" % machine_name)

    for (k, v) in iter(sorted(details.iteritems())):
        outf.write("Node%s %s\n" % (k, v))

    outf.write("PartitionNames partition\n")
    outf.write("PartitionSizes 1\n")
    outf.write("NodeNames {%s}\n" % machine_name)
    outf.write("NodeNumProcs %s\n" % numprocs)
    outf.write("ProcType %s\n" % proctype)
    outf.write("ProcMHz %s\n" % procmhz)
    outf.write("END %s\n" % machine_name)

main()
