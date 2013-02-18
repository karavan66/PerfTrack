#!/usr/bin/env python

# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information. 

import sys
from PTexception import PTexception
from Application import Application
from Execution import Execution
from Resource import Resource
from PerfResult import PerfResult
from AttrVal import AttrVal


def resourceBasicTests():
    try:
       # try giving Resource name=None
       app = Resource (None)
    except PTexception, a:
       print "PASS:" + a.value
    except:
       print "FAIL: non-PTexception when try giving Resource name=None"
    else:
       print "FAIL: try giving Resource name=None"

    try:
       # try giving Resource name=""
       app = Resource("","mytype")
    except PTexception, a:
       print "PASS:" + a.value
    except:
       print "FAIL: non-PTexception when try giving Resource name=''"
    else:
       print "FAIL: try giving Resource name=''"

    try:
       # try giving Resource name with illegal char '::'
       app = Resource("MFLOP::sec","thetype")
    except PTexception, a:
       print "PASS:" + a.value
    except:
       print "FAIL: non-PTexception when try giving Resource name=MFLOP::sec"
    else:
       print "FAIL: try giving Resource name=MFLOP::sec"

    try:
       # try giving Resource name with illegal char ','
       app = Resource ("MFLOP,sec","atype")
    except PTexception, a:
       print "PASS:" + a.value
    except:
       print "FAIL: non-PTexception when try giving Resource name=MFLOP,sec"
    else:
       print "FAIL: try giving Resource name=MFLOP,sec"

    try:
       # try giving Resource name with illegal char '('
       app = Resource("MFLOP(sec","yourtype")
    except PTexception, a:
       print "PASS:" + a.value
    except:
       print "FAIL: non-PTexception when try giving Resource name=MFLOP(sec"
    else:
       print "FAIL: try giving Resource name=MFLOP(sec"

    try:
       # try giving Resource name with illegal char ')'
       app = Resource("MFLOP)sec","ftype")
    except PTexception, a:
       print "PASS:" + a.value
    except:
       print "FAIL: non-PTexception when try giving Resource name=MFLOP)sec"
    else:
       print "FAIL: try giving Resource name=MFLOP)sec"

    try:
       # try giving Resource name with illegal char '####'
       app = Resource("MFLOP####sec","type")
    except PTexception, a:
       print "PASS:" + a.value
    except:
       print "FAIL: non-PTexception when try giving Appl name=MFLOP####sec"
    else:
       print "FAIL: try giving Resource name=MFLOP####sec"

    try:
       # try giving Resource bad attr name
       b = ""
       c = "super"
       app = Resource ("frank", "type", [(b,c)])
    except PTexception, a:
       print "PASS:" + a.value
    except:
       print "FAIL: non-PTexception when try giving Resource attr name=''"
    else:
       print "FAIL: try giving Resource attr name=''"

    try:
       # try giving Resource bad attr value 
       b = "superduper"
       c = ""
       app = Resource ("frank", "type", [(b,c)])
    except PTexception, a:
       print "PASS:" + a.value
    except:
       print "FAIL: non-PTexception when try giving Resource attr value=''"
    else:
       print "FAIL: try giving Resource attr value=''"
      
    try:
       # try giving Resource non-list attr value 
       b = "superduper"
       c = "extra"
       app = Resource("frank", "type", (b,c))
    except PTexception, a:
       print "PASS:" + a.value
    except:
       print "FAIL: non-PTexception raised when try giving Resource non-list attrvalue"
    else:
       print "FAIL: try giving Resource non-list attrvalue"

    try:
       # try giving Resource non-pair attr value 
       b = "superduper"
       app = Resource("frank", "type", [b])
    except PTexception, a:
       print "PASS:" + a.value
    except:
       print "FAIL: non-PTexception raised when try giving Resource non-pair attrvalue"
    else:
       print "FAIL: try giving Resource non-pair attrvalue"

    try:
       # try giving Resource good list attr value 
       b = "superduper"
       c = "extra"
       app = Resource("frank", "type", [(b,c)])
    except PTexception, a:
       print "FAIL:" + a.value
    except:
       print "FAIL: non-PTexception when try giving Resource good list attrvalue"
    else:
       print "PASS: try giving Resource good list attrvalue"

    try:
       # try giving Resource bad resource types
       b = "superduper"
       c = "extra"
       d = ""
       app = Resource("frank", "type", [(b,c)],[d])
    except PTexception, a:
       print "PASS:" + a.value
    except:
       print "FAIL: non-PTexception when try giving Resource bad resource type"
       raise
    else:
       print "FAIL: try giving Resource bad resource type"

    try:
       # try giving Resource non-list resource type
       b = "superduper"
       c = "extra"
       d = "eddie"
       app = Resource("frank", "type", [(b,c)],d)
    except PTexception, a:
       print "PASS:" + a.value
    except:
       print "FAIL: non-PTexception when try giving Resource non-list resource type"
    else:
       print "FAIL: try giving Resource non-list resource type"

    try:
       # try giving Resource good resource type
       b = "superduper"
       c = "extra"
       r = Resource("eddie","atype")
       d = [r]
       app = Resource("frank", "type", [(b,c)],d)
    except PTexception, a:
       print "FAIL:" + a.value
    except:
       print "FAIL: non-PTexception when try giving Resource good resource type"
    else:
       print "PASS: try giving Resource good resource type"

def resourceSearchTests():
    try:
       # try out isChild with a non-child resource
       p = Resource("eddie","atype")
       c = Resource("franks/schild","atype/btype")
       theVerdict = p.isChild(c)
    except PTexception, a:
       print "FAIL:" + a.value
    except:
       print "FAIL: non-PTexception when try isChild non-child resource"
    else:
       if theVerdict == True:
          print "FAIL: isChild fail with non-child resource"
       else:
          print "PASS: isChild pass with non-child resource"

    try:
       # try out isChild
       p = Resource("eddie","atype")
       c = Resource("eddie","atype")
       theVerdict = p.isChild(c)
    except PTexception, a:
       print "FAIL:" + a.value
    except:
       print "FAIL: non-PTexception when try isChild same name resource"
    else:
       if theVerdict == True:
          print "FAIL: isChild fail same name resource"
       else:
          print "PASS: isChild pass same name resource"

    try:
       # try out isChild
       p = Resource("eddie","atype")
       c = Resource("eddie/schild","atype/btype")
       theVerdict = p.isChild(c)
    except PTexception, a:
       print "FAIL:" + a.value
    except:
       print "FAIL: non-PTexception when try isChild actual child"
    else:
       if theVerdict == True:
          print "PASS: isChild pass actual child"
       else: 
          print "FAIL: isChild fail actual child"

    try:
       # try finding a static library
       build = Resource("mybuild","build")
       lib = Resource(build.name+"/libmpi.a","build/module")
       build.addResource(lib)
       env = Resource("myenv", "environment")
       execution = Execution("myexec")
       execution.addResources([build,env])
       resList = execution.findResourceByShortType("module")
       libname = ""
       for r in resList:
           if r.name.find("libmpi") >= 0:
              libname = r.name 
              break
    except PTexception, a:
       print "FAIL: PTexception raised when trying to find good static lib with findResourceByShortType: " + a.value
    except:
       print "FAIL: non-PTexception raised when trying to find good static lib with findResourceByShortType"
       raise
    else:
       if libname == "":
           print "FAIL: found empty library name  when trying to find good static lib with findResourceByShortType"
       elif not libname.endswith("/libmpi.a"):
           print "FAIL: found wrong library trying to find good static lib with findResourceByShortType"
       else:
           print "PASS: found libmpi.a with findResourceByShortType"

    try:
       # try finding a dynamic library
       build = Resource("mybuild","build")
       env = Resource("myenv", "environment")
       lib = Resource(env.name+"/libmpi.so","environment/module")
       env.addResource(lib)
       execution = Execution("myexec" )
       execution.addResources([build,env])
       resList = execution.findResourceByShortType("module")
       libname = ""
       for r in resList:
           if r.name.find("libmpi") >= 0:
              libname = r.name
              break
    except PTexception, a:
       print "FAIL: PTexception raised when trying to find good dynamic lib with findResourceByShortType: " + a.value
    except:
       print "FAIL: non-PTexception raised when trying to find good dynamic lib with findResourceByShortType"
       raise
    else:
       if libname == "":
           print "FAIL: found empty library name  when trying to find good dynamic lib with findResourceByShortType"
       elif not libname.endswith("/libmpi.so"):
           print "FAIL: found wrong library trying to find good dynamic lib with findResourceByShortType"
       else:
           print "PASS: found libmpi.so with findResourceByShortType"

    try:
       # try finding a resource with findResourceByType 
       build = Resource("mybuild","build")
       env = Resource("myenv", "environment")
       lib = Resource(env.name+"/libmpi.so","environment/module")
       env.addResource(lib)
       execution = Execution("myexec")
       execution.addResources([build,env])
       resList = execution.findResourceByType("environment/module")
       libname = ""
       for r in resList:
           if r.name.find("libmpi") >= 0:
              libname = r.name
              break
    except PTexception, a:
       print "FAIL: PTexception raised when trying to find good dynamic lib with findResourceByType: " + a.value
    except:
       print "FAIL: non-PTexception raised when trying to find good dynamic lib with findResourceByType"
       raise
    else:
       if libname == "":
           print "FAIL: found empty library name  when trying to find good dynamic lib with findResourceByType"
       elif not libname.endswith("/libmpi.so"):
           print "FAIL: found wrong library trying to find good dynamic lib with findResourceByType"
       else:
           print "PASS: found libmpi.so with findResourceByType"

    try:
       # try finding a resource with findResource
       build = Resource("mybuild","build")
       env = Resource("myenv", "environment")
       lib = Resource(env.name+"/libmpi.so","environment/module")
       env.addResource(lib)
       execution = Execution("myexec")
       execution.addResources([build,env])
       res = execution.findResource("/myenv/libmpi.so","environment/module")
       if res:
          libname = res.name
       else:
          libname = ""
    except PTexception, a:
       print "FAIL: PTexception raised when trying to find good dynamic lib with findResource: " + a.value
    except:
       print "FAIL: non-PTexception raised when trying to find good dynamic lib with findResource"
       raise
    else:
       if libname == "":
           print "FAIL: found empty library name  when trying to find good dynamic lib with findResource"
       elif not libname.endswith("/libmpi.so"):
           print "FAIL: found wrong library trying to find good dynamic lib with findResource"
       else:
           print "PASS: found libmpi.so with findResource"

    try:
       # try finding a non-existent resource with findResource
       build = Resource("mybuild","build")
       env = Resource("myenv", "environment")
       lib = Resource(env.name+"/libmpi.so","environment/module")
       env.addResource(lib)
       execution = Execution("myexec")
       execution.addResources([build,env])
       res = execution.findResource("/myenv/libmpi.frank","environment/module")
       if res:
          libname = res.name
       else:
          libname = ""
    except PTexception, a:
       print "FAIL: PTexception raised when trying to find non-existent lib with findResource: " + a.value
    except:
       print "FAIL: non-PTexception raised when trying to find non-existent lib with findResource"
       raise
    else:
       if libname == "":
           print "PASS: found '' library name when trying to find non-existent lib with findResource"
       else:
           print "FAIL: found non-existent lib with findResource"

    try:
       # try finding a non-existent resource with findResourceByType
       build = Resource("mybuild","build")
       env = Resource("myenv", "environment")
       lib = Resource(env.name+"/libmpi.so","environment/module")
       env.addResource(lib)
       execution = Execution("myexec")
       execution.addResources([build,env])
       res = execution.findResourceByType("environment/moduleS")
       if res:
          libname = res.name
       else:
          libname = ""
    except PTexception, a:
       print "FAIL: PTexception raised when trying to find non-existent lib with findResourceByType: " + a.value
    except:
       print "FAIL: non-PTexception raised when trying to find non-existent lib with findResourceByType"
       raise
    else:
       if libname == "":
           print "PASS: found '' library name when trying to find non-existent lib with findResourceByType"
       else:
           print "FAIL: found non-existent lib with findResourceByType"

    try:
       # try finding a non-existent resource with findResourceByType
       build = Resource("mybuild","build")
       env = Resource("myenv", "environment")
       lib = Resource(env.name+"/libmpi.so","environment/module")
       env.addResource(lib)
       execution = Execution("myexec")
       execution.addResources([build,env])
       res = execution.findResourceByShortType("moduleS")
       if res:
          libname = res.name
       else:
          libname = ""
    except PTexception, a:
       print "FAIL: PTexception raised when trying to find non-existent lib with findResourceByShortType: " + a.value
    except:
       print "FAIL: non-PTexception raised when trying to find non-existent lib with findResourceByShortType"
       raise
    else:
       if libname == "":
           print "PASS: found '' library name when trying to find non-existent lib with findResourceByShortType"
       else:
           print "FAIL: found non-existent lib with findResourceByShortType"


def execTests():

    try:
       # try giving Application  non-list execution
       b = "superduper"
       c = "extra"
       d = "eddie"
       e = Execution("sally")
       app = Application("frank", [(b,c)],[d],e)
    except PTexception, a:
       print "PASS:" + a.value
    except:
       print "FAIL: non-PTexception when try giving Application non-list execution"
    else:
       print "FAIL: try giving Application non-list execution"

    try:
       # try giving Application  good execution list 
       b = "superduper"
       c = "extra"
       d = ["eddie"]
       e = Execution("sally")
       app = Application("frank", [(b,c)],d,[e])
    except PTexception, a:
       print "FAIL:" + a.value
    except:
       print "FAIL: non-PTexception when try giving Application good execution list"
    else:
       print "PASS: try giving Application good execution list"

    try:
       exe = Execution()
    except PTexception, a:
       print "PASS:" + a.value
    except:
       print "FAIL: non-PTexception when try giving Execution no name" 
    else:
       print "FAIL: try giving Execution no name"

    try:
       a = ""
       exe = Execution(a)
    except PTexception, a:
       print "PASS:" + a.value
    except:
       print "FAIL: non-PTexception when try giving Execution name ''" 
    else:
       print "FAIL: try giving Execution name ''"


    try: 
       # try giving Execution bad attr value 
       a = "susan"
       c = "superduper"
       d = ""
       exe = Execution(a,[(c,d)])
    except PTexception, a:
       print "PASS:" + a.value
    except:
       print "FAIL: non-PTexception when try giving Execution attr value=''"
    else:
       print "FAIL: try giving Execution attr value=''"
      
    try:
       # try giving Execution non-list attr value 
       a = "susan"
       c = "superduper"
       d = "silliness"
       exe = Execution(a,(c,d))
    except PTexception, a:
       print "PASS:" + a.value
    except:
       print "FAIL: non-PTexception raised when try giving Execution non-list attrvalue"
    else:
       print "FAIL: try giving Execution non-list attrvalue"

    try:
       # try giving Execution non-pair attr value 
       a = "susan"
       c = "superduper"
       d = "silliness"
       exe = Execution(a,[c])
    except PTexception, a:
       print "PASS:" + a.value
    except:
       print "FAIL: non-PTexception raised when try giving Execution non-pair attrvalue"
    else:
       print "FAIL: try giving Execution non-pair attrvalue"

    try:
       # try giving Execution good list attr value 
       a = "susan"
       c = "superduper"
       d = "silliness"
       exe = Execution(a,[(c,d)])
    except PTexception, a:
       print "FAIL:" + a.value
    except:
       print "FAIL: non-PTexception when try giving Execution good list attrvalue"
    else:
       print "PASS: try giving Execution good list attrvalue"

    try:
       # try giving Execution  None resource list
       a = "susan"
       c = "superduper"
       d = "silliness"
       f = None
       exe = Execution(a,[(c,d)],[f])
    except PTexception, a:
       print "PASS:" + a.value
    except:
       print "FAIL: non-PTexception raised when try giving Execution None resource list"
    else:
       print "FAIL: try giving Execution None list"

    try:
       # try giving Execution  non-list resource list 
       a = "susan"
       c = "superduper"
       d = "silliness"
       f = Resource("a","b")
       exe = Execution(a,[(c,d)],f)
    except PTexception, a:
       print "PASS:" + a.value
    except:
       print "FAIL: non-PTexception raised when try giving Execution non-list resource list"
    else:
       print "FAIL: try giving Execution non-list resource list"

    try:
       # try giving Execution  good resource list 
       a = "susan"
       c = "superduper"
       d = "silliness"
       f = Resource("a","b")
       exe = Execution(a,[(c,d)],[f])
    except PTexception, a:
       print "FAIL:" + a.value
    except:
       print "FAIL: non-PTexception raised when try giving Execution good resource list"
       raise
    else:
       print "PASS: try giving Execution good resource list"

def focusTests():
    try:
       # try  getting a focus template
       build = Resource("mybuild","build")
       env = Resource("myenv", "environment")
       lib = Resource(env.name+"/libmpi.so","environment/module")
       env.addResource(lib)
       lib = Resource(env.name+"/libelf.so","environment/module")
       env.addResource(lib)
       compiler = Resource("theCompiler","compiler")
       execution = Execution("myexec")
       process0 = Resource(execution.name+"/Process-0","execution/process")
       process0.addResources([compiler,build,env])
       metric = Resource("MFLOPS","metric")
       pt = Resource("Paradyn","performanceTool")
       execution.addResources([build,env,process0,metric,pt])
       fl = execution.createFocusTemplate()
       #for f in fl:
       #    print f.getName()
    except:
       print "FAIL: non-PTexception raised when getting focusTemplate"
       raise
    else:
       if len(fl) != 4:
          print "FAIL: wrong number of resources. %d" % len(fl)
       else:
          print "PASS: got focus template successfully"

    try:
       # try getting a focus template with two top-level resources withthe 
       # same type
       build = Resource("mybuild","build")
       env = Resource("myenv", "environment")
       lib = Resource(env.name+"/libmpi.so","environment/module")
       env.addResource(lib)
       lib = Resource(env.name+"/libelf.so","environment/module")
       env.addResource(lib)
       compiler = Resource("theCompiler","compiler")
       execution = Execution("myexec")
       process0 = Resource(execution.name+"/Process-0","execution/process")
       process0.addResources([compiler,build,env])
       compiler = Resource("theOtherCompiler","compiler")
       process1 = Resource(execution.name+"/Process-1","execution/process")
       process1.addResources([compiler,build,env])
       execution.addResources([build,env,process0,process1])
       fl = execution.createFocusTemplate()
       #for f in fl:
       #    print f.getName()
    except:
       print "FAIL: non-PTexception raised when getting focusTemplate same types"
       raise
    else:
       if len(fl) != 5:
          print "FAIL: wrong number of resources same types. %d" % len(fl)
       else:
          print "PASS: got focus template successfully same types"


    try:
       # try adding a specific focus resources that is a child of a resource
       # in the template
       build = Resource("mybuild","build")
       env = Resource("myenv", "environment")
       lib = Resource(env.name+"/libmpi.so","environment/module")
       env.addResource(lib)
       lib = Resource(env.name+"/libelf.so","environment/module")
       env.addResource(lib)
       compiler = Resource("theCompiler","compiler")
       execution = Execution("myexec")
       process0 = Resource(execution.name+"/Process-0","execution/process")
       process0.addResources([compiler,build,env])
       execution.addResources([build,env,process0])
       fl = execution.createFocusTemplate()
       newfl = execution.addSpecificFocusResource(fl,process0)
       #for f in newfl:
       #    print f.getName()
       #for f in fl:
       #    print f.getName()
    except:
       print "FAIL: non-PTexception raised when adding specific focus child"
       raise
    else:
       if len(newfl) != 4:
          print "FAIL: wrong number of resources when adding specific focus child. %d" % len(newfl)
       else:
          print "PASS: got focus template successfully when adding specific focus child"

    try:
       # try adding a list of specific focus resources that is a child of 
       # a resource in the template
       build = Resource("mybuild","build")
       env = Resource("myenv", "environment")
       lib = Resource(env.name+"/libmpi.so","environment/module")
       env.addResource(lib)
       lib = Resource(env.name+"/libelf.so","environment/module")
       env.addResource(lib)
       compiler = Resource("theCompiler","compiler")
       execution = Execution("myexec")
       process0 = Resource(execution.name+"/Process-0","execution/process")
       process0.addResources([compiler,build,env])
       process1 = Resource(execution.name+"/Process-1","execution/process")
       process1.addResources([compiler,build,env])
       execution.addResources([build,env,process0,process1])
       fl = execution.createFocusTemplate()
       newfl = execution.addSpecificFocusResources(fl,[process0,process1])
       #for f in newfl:
           #print f.getName()
       #for f in fl:
           #print f.getName()
    except:
       print "FAIL: non-PTexception raised when adding specific focus child list"
       raise
    else:
       if len(newfl) != 5:
          print "FAIL: wrong number of resources when adding specific focus child list. %d" % len(newfl)
       else:
          print "PASS: got focus template successfully when adding specific focus child list"


def attrValTests():

    try:
        # test AttrVal class. nothing bad should happen
        av = AttrVal()
        av.addPair("frank", "alice")
        av.addPair("susan", "james")
        b = [("a",""),("c",None)] 
        av.addPairs(b)
        av.addPairs([])
        newlist = []
        for a in av:
           newlist.append(a) 
        if len(newlist) != 4:
           raise PTexception("wrong number in pair list")
        newlist = []
        for a in av:
           newlist.append(a) 
        if len(newlist) != 4:
           raise PTexception("wrong number in pair list")
        i = 0
        for a,v in av:
           i += 1
           if a == "susan":
              break
        for a,v in av:
           i += 1
        if i != 4:
           raise PTexception("break in iteration didn't work")
        a = av.getNext()
        newlist = []
        while a: 
           newlist.append(a)
           a,v = av.getNext()
        if len(newlist) != 4:
           raise PTexception("getNext not working")
            
    except PTexception, a:
        print "FAIL: PTexception raised for good AttrVal test: " + a.value
    except:
        print "FAIL: non-PTexception raised AttrVal good test"
        raise
    else:
        print "PASS: good AttrVal test"


    try:
        # test missing value for name 
        av = AttrVal()
        av.addPair("","frank") 
    except PTexception, a:
        print "PASS: PTexception raised for missing 'name' value: " + a.value
    except:
        print "FAIL: non-PTexception raised AttrVal missing 'name'"
        raise
    else:
        print "FAIL: no exception raised AttrVal 'missing name'"
    

    try:
        # test non-list given to addPairs
        av = AttrVal()
        av.addPairs("frank")
    except PTexception, a:
        print "PASS: PTexception raised for non-list to addPairs: " + a.value
    except:
        print "FAIL: non-PTexception raised AttrVal non-list to addPairs"
        raise
    else:
        print "FAIL: no exception raised AttrVal non-list to addPairs"


    try:
        # test non-pair list given to addPairs
        av = AttrVal()
        a = ["frank","allice","steve"]
        av.addPairs(a)
    except PTexception, a:
        print "PASS: PTexception raised for non-pair list to addPairs: " + a.value
    except:
        print "FAIL: non-PTexception raised AttrVal non-pair list to addPairs"
        raise
    else:
        print "FAIL: no exception raised AttrVal non-pair list to addPairs"


def main():
 
   tests = [resourceBasicTests,resourceSearchTests,execTests, attrValTests,\
            focusTests]
   for test in tests:
       test()


if __name__ == "__main__":
   sys.exit(main())
