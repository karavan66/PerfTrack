#!/usr/bin/env python

from optparse import OptionParser, SUPPRESS_HELP
from ParseOprof import ParseOprof, print_countable, find_binary
from glob import glob
import re, sys
from ResourceIndex import ResourceIndex
from Application import Application
from Execution import Execution
from Resource import Resource
from PerfResult import PerfResult
from PTexception import PTexception
import Hardware
import Build
import Run

def prepare(resIdx, tool_res):
    counts = ["LLC_COUNT", "LLC_MISSES", "CPU_CLK_UNHALTED"]
    for c in counts:
        r = Resource(c, "metric")
        resIdx.addResource(r)
        #r.addAttribute("performanceTool", tool_res.name, "resource")


def add_perfresults(resIdx, e, countable, context, tool):
    for c_k, c_v in countable.count.iteritems():
        metric = resIdx.findResourceByName(str(c_k))
        value = str(c_v)
        units = "noValue"
        startTime = "noValue"
        endTime = "noValue"
        pr = PerfResult(context, tool, metric, value, units, startTime, endTime)
        e.addPerfResult(pr)

def countable_binary_execution(resIdx, e, orig_context, tool_res, countable):
    m = re.match("^.*/([^/]+)$", countable.getName())

    context = resIdx.addSpecificContextResources(orig_context, [tool_res])
    add_perfresults(resIdx, e, countable, context, tool_res)
    for c in countable.subs:
        r = tool_res.extend(c.name, c.type)
        resIdx.addResource(r)
        context = resIdx.addSpecificContextResources(orig_context, [tool_res, r])
        add_perfresults(resIdx, e, c, context, tool_res)


def main(argv=sys.argv):
    usage = "usage: %prog [options]\nexecute '%prog --help' to see options"
    version = "%prog 1.0"
    parser = OptionParser(usage=usage,version=version)
    parser.add_option("-n","--name", dest="machine_name", action="store", help="machine name of system")
    parser.add_option("-o", "--output_ptdf", dest="ptdf", 
                      help="output name of the ptdf", default="-")

    (options, args) = parser.parse_args(argv[1:])
    if (options.machine_name == None):
        print "Need machine name specified by -n"
        sys.exit(1)

    machine = options.machine_name
    repo = "/home/crzysdrs/PerfTrack/"

    process_list = [
        ("%s/benchmarks/blocked_multiplication/blocked_Reports/XML/blocked_*.xml", 
         'blocked'),
        ("%s/benchmarks/2d_image_processing/2d_img_processing_Reports/XML/2d_img_processing_*.xml", 
         '2d_img_processing'),
        ("%s/benchmarks/unblocked_multiplication/un_blocked_Reports/XML/un_blocked_*.xml", 
         'un_blocked'),
        ("%s/benchmarks/int_multiplication/int_multiplication_Reports/XML/matrixMult_int_*.xml",
         'matrixMult_int'),
        ("%s/benchmarks/int_multiplication/int_multiplication_Reports/XML/multOMP_int_*.xml",
         'multOMP_int'),
        ("%s/benchmarks/float_multiplication/float_multiplication_Reports/XML/matrixMult_float_*.xml",
         'matrixMult_float'),
        ("%s/benchmarks/float_multiplication/float_multiplication_Reports/XML/multOMP_float_*.xml",
         'multOMP_float'),
        ("%s/benchmarks/float_multiplication/float_multiplication_Reports/XML/multOMP_random*.xml", 
         'multOMP_random'),
        ("%s/benchmarks/float_multiplication/float_multiplication_Reports/XML/matrixMult_random*.xml", 
         'matrixMult_random')
        ]

    full_env = ['%s/benchmarks/Benchmark2-XML-reports/*.xml']
    resIdx = ResourceIndex()
    resIdx.addResource(Resource(machine, Resource.resDelim.join(["grid", "machine"])))
    app = Application("oprofile")
    global_e = Execution("oprofile-exec", [])
    resIdx.addResource(global_e)
    resIdx.addResource(app)
    for p in process_list:
        files = glob(p[0] % repo)
        tool_res = resIdx.findOrCreateResource(Resource.resDelim.join([p[1]]),
                                               Resource.resDelim.join(["performanceTool"]))
        resIdx.addResource(tool_res)
        for f in files:
            exec_re = re.match("^.*/([^/]+).xml$", f)
            tool_args = tool_res.extend(exec_re.group(1), "args")
            resIdx.addResource(tool_args)
            context = resIdx.addSpecificContextResources([],[global_e, tool_args])
            prepare(resIdx, tool_args)
            oprof = ParseOprof()
            countables = oprof.processOPROF(f)
            countable_binary_execution(resIdx, global_e, context, tool_args, find_binary(countables, p[1]))

    if (options.ptdf == "-"):
        f = sys.stdout
    else:
        f = open(options.ptdf, "w")

    writeLst = resIdx.PTdF()
    for w in writeLst:
        f.write(w)
    f.close()

main()
