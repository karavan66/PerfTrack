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
from PassFail import PassFail
from ResourceIndex import ResourceIndex

def resourceBasicTests(pf):
    try:
       # try giving Resource name=None
       app = Resource (None)
    except PTexception, a:
        pf.passed(a.value)
    except:
       pf.failed("non-PTexception when try giving Resource name=None")
    else:
       pf.failed("try giving Resource name=None")

    try:
       # try giving Resource name=""
       app = Resource("","mytype")
    except PTexception, a:
        pf.passed(a.value)
    except:
       pf.failed("non-PTexception when try giving Resource name=''")
    else:
       pf.failed("try giving Resource name=''")

    try:
       # try giving Resource name with illegal char '::'
       app = Resource("MFLOP::sec","thetype")
    except PTexception, a:
        pf.passed(a.value)
    except:
       pf.failed("non-PTexception when try giving Resource name=MFLOP::sec")
    else:
       pf.failed("try giving Resource name=MFLOP::sec")

    try:
       # try giving Resource name with illegal char ','
       app = Resource ("MFLOP,sec","atype")
    except PTexception, a:
        pf.passed(a.value)
    except:
       pf.failed("non-PTexception when try giving Resource name=MFLOP,sec")
    else:
       pf.failed("try giving Resource name=MFLOP,sec")

    try:
       # try giving Resource name with illegal char '('
       app = Resource("MFLOP(sec","yourtype")
    except PTexception, a:
        pf.passed(a.value)
    except:
       pf.failed("non-PTexception when try giving Resource name=MFLOP(sec")
    else:
       pf.failed("try giving Resource name=MFLOP(sec")

    try:
       # try giving Resource name with illegal char ')'
       app = Resource("MFLOP)sec","ftype")
    except PTexception, a:
        pf.passed(a.value)
    except:
       pf.failed("non-PTexception when try giving Resource name=MFLOP)sec")
    else:
       pf.failed("try giving Resource name=MFLOP)sec")

    try:
       # try giving Resource name with illegal char '####'
       app = Resource("MFLOP####sec","type")
    except PTexception, a:
        pf.passed(a.value)
    except:
       pf.failed("non-PTexception when try giving Appl name=MFLOP####sec")
    else:
       pf.failed("try giving Resource name=MFLOP####sec")

    try:
       # try giving Resource bad attr name
       b = ""
       c = "super"
       app = Resource ("frank", "type", [(b,c)])
    except PTexception, a:
        pf.passed(a.value)
    except:
        pf.failed("non-PTexception when try giving Resource attr name=''")
    else:
        pf.failed("try giving Resource attr name=''")

    try:
       # try giving Resource bad attr value 
       b = "superduper"
       c = ""
       app = Resource ("frank", "type", [(b,c)])
    except PTexception, a:
        pf.passed(a.value)
    except:
       pf.failed("non-PTexception when try giving Resource attr value=''")
    else:
       pf.failed("try giving Resource attr value=''")
      

    try:
       # try giving Resource non-list attr value 
       b = "superduper"
       c = "extra"
       app = Resource("frank", "type", (b,c))
    except PTexception, a:
        pf.passed(a.value)
    except:
       pf.failed("non-PTexception raised when try giving Resource non-list attrvalue")
    else:
       pf.failed("try giving Resource non-list attrvalue")

 
    try:
       # try giving Resource non-pair attr value 
       b = "superduper"
       app = Resource("frank", "type", [b])
    except PTexception, a:
        pf.passed(a.value)
    except:
       pf.failed("non-PTexception raised when try giving Resource non-pair attrvalue")
    else:
       pf.failed("try giving Resource non-pair attrvalue")

    try:
       # try giving Resource bad resource types
       b = "superduper"
       c = "extra"
       d = ""
       app = Resource("frank", "type", [(b,c),d])
    except PTexception, a:
        pf.passed(a.value)
    except:
       pf.failed("non-PTexception when try giving Resource bad resource type")
       raise
    else:
       pf.failed("try giving Resource bad resource type")

def resourceSearchTests(pf):
    try:
       # try out isChild with a non-child resource
       p = Resource("eddie","atype")
       c = Resource("franks|schild","atype|btype")
       theVerdict = p.isChild(c)
    except PTexception, a:
        pf.failed(a.value)
    except:
       pf.failed("non-PTexception when try isChild non-child resource")
    else:
       if theVerdict == True:
          pf.failed("isChild fail with non-child resource")
       else:
          pf.passed("isChild pass with non-child resource")

    try:
       # try out isChild
       p = Resource("eddie","atype")
       c = Resource("eddie","atype")
       theVerdict = p.isChild(c)
    except PTexception, a:
        pf.failed(a.value)
    except:
       pf.failed("non-PTexception when try isChild same name resource")
    else:
       if theVerdict == True:
          pf.failed("isChild fail same name resource")
       else:
          pf.passed("isChild pass same name resource")

    try:
       # try out isChild
       p = Resource("eddie","atype")
       c = Resource("eddie|schild","atype|btype")
       theVerdict = p.isChild(c)
    except PTexception, a:
        pf.failed(a.value)
    except:
       pf.failed("non-PTexception when try isChild actual child")
    else:
       if theVerdict == True:
          pf.passed("isChild pass actual child")
       else: 
          pf.failed("isChild fail actual child")

    try:
       # try finding a static library
       ri = ResourceIndex()
       build = Resource("mybuild","build")
       lib = Resource(build.name+"|libmpi.a","build|module")
       ri.addResource(lib)
       env = Resource("myenv", "environment")
       execution = Execution("myexec")
       ri.addResources([build,env])
       resList = ri.findResourcesByShortType("module")
       libname = ""
       for r in resList:
           if r.name.find("libmpi") >= 0:
              libname = r.name 
              break
    except PTexception, a:
       pf.failed("PTexception raised when trying to find good static lib with findResourceByShortType: " + a.value)
    except:
       pf.failed("non-PTexception raised when trying to find good static lib with findResourceByShortType")
       raise
    else:
       if libname == "":
           pf.failed("found empty library name  when trying to find good static lib with findResourceByShortType")
       elif not libname.endswith("|libmpi.a"):
           pf.failed("found wrong library trying to find good static lib with findResourceByShortType")
       else:
           pf.passed("found libmpi.a with findResourceByShortType")

    try:
        # try finding a dynamic library
        ri = ResourceIndex()
        build = Resource("mybuild","build")
        env = Resource("myenv", "environment")
        lib = Resource(env.name+"|libmpi.so","environment|module")
        ri.addResource(lib)
        execution = Execution("myexec" )
        ri.addResources([build,env])
        resList = ri.findResourcesByShortType("module")
        libname = ""
        for r in resList:
            if r.name.find("libmpi") >= 0:
                libname = r.name
                break
    except PTexception, a:
       pf.failed("PTexception raised when trying to find good dynamic lib with findResourceByShortType: " + a.value)
    except:
       pf.failed("non-PTexception raised when trying to find good dynamic lib with findResourceByShortType")
       raise
    else:
       if libname == "":
           pf.failed("found empty library name  when trying to find good dynamic lib with findResourceByShortType")
       elif not libname.endswith("|libmpi.so"):
           pf.failed("found wrong library trying to find good dynamic lib with findResourceByShortType")
       else:
           pf.passed("found libmpi.so with findResourceByShortType")

    try:
       # try finding a resource with findResourceByType 
        ri = ResourceIndex()
        build = Resource("mybuild","build")
        env = Resource("myenv", "environment")
        lib = Resource(env.name+"|libmpi.so","environment|module")
        ri.addResource(lib)
        execution = Execution("myexec")
        ri.addResources([build,env])
        resList = ri.findResourcesByType("environment|module")
        libname = ""
        for r in resList:
            if r.name.find("libmpi") >= 0:
                libname = r.name
                break
    except PTexception, a:
       pf.failed("PTexception raised when trying to find good dynamic lib with findResourceByType: " + a.value)
    except:
       pf.failed("non-PTexception raised when trying to find good dynamic lib with findResourceByType")
       raise
    else:
       if libname == "":
           pf.failed("found empty library name  when trying to find good dynamic lib with findResourceByType")
       elif not libname.endswith("|libmpi.so"):
           pf.failed("found wrong library trying to find good dynamic lib with findResourceByType")
       else:
           pf.passed("found libmpi.so with findResourceByType")

    try:
       # try finding a resource with findResource
        ri = ResourceIndex()
        build = Resource("mybuild","build")
        env = Resource("myenv", "environment")
        lib = Resource(env.name+"|libmpi.so","environment|module")
        ri.addResource(lib)
        execution = Execution("myexec")
        ri.addResources([build,env])
        res = ri.findResourceByName("myenv|libmpi.so")
        if res:
            libname = res.name
        else:
            libname = ""
    except PTexception, a:
       pf.failed("PTexception raised when trying to find good dynamic lib with findResource: " + a.value)
    except:
       pf.failed("non-PTexception raised when trying to find good dynamic lib with findResource")
       raise
    else:
       if libname == "":
           pf.failed("found empty library name  when trying to find good dynamic lib with findResource")
       elif not libname.endswith("|libmpi.so"):
           pf.failed("found wrong library trying to find good dynamic lib with findResource")
       else:
           pf.passed("found libmpi.so with findResource")

    try:
        ri =ResourceIndex()
        # try finding a non-existent resource with findResource
        build = Resource("mybuild","build")
        env = Resource("myenv", "environment")
        lib = Resource(env.name+"|libmpi.so","environment|module")
        ri.addResource(lib)
        execution = Execution("myexec")
        ri.addResources([build,env])
        res = ri.findResourceByName("myenv|libmpi.frank")
        if res:
            libname = res.name
        else:
            libname = ""
    except PTexception, a:
       pf.failed("PTexception raised when trying to find non-existent lib with findResource: " + a.value)
    except:
       pf.failed("non-PTexception raised when trying to find non-existent lib with findResource")
       raise
    else:
       if libname == "":
           pf.passed("found '' library name when trying to find non-existent lib with findResource")
       else:
           pf.failed("found non-existent lib with findResource")

    try:
       # try finding a non-existent resource with findResourceByType
        ri = ResourceIndex()
        build = Resource("mybuild","build")
        env = Resource("myenv", "environment")
        lib = Resource(env.name+"|libmpi.so","environment|module")
        ri.addResource(lib)
        execution = Execution("myexec")
        ri.addResources([build,env])
        res = ri.findResourcesByType("environment|moduleS")
        if res:
            libname = res.name
        else:
            libname = ""
    except PTexception, a:
       pf.failed("PTexception raised when trying to find non-existent lib with findResourceByType: " + a.value)
    except:
       pf.failed("non-PTexception raised when trying to find non-existent lib with findResourceByType")
       raise
    else:
       if libname == "":
           pf.passed("found '' library name when trying to find non-existent lib with findResourceByType")
       else:
           pf.failed("found non-existent lib with findResourceByType")

    try:
       # try finding a non-existent resource with findResourceByType
        ri = ResourceIndex()
        build = Resource("mybuild","build")
        env = Resource("myenv", "environment")
        lib = Resource(env.name+"|libmpi.so","environment|module")
        ri.addResource(lib)
        execution = Execution("myexec")
        ri.addResources([build,env])
        res = ri.findResourcesByShortType("moduleS")
        if res:
            libname = res.name
        else:
            libname = ""
    except PTexception, a:
       pf.failed("PTexception raised when trying to find non-existent lib with findResourceByShortType: " + a.value)
    except:
       pf.failed("non-PTexception raised when trying to find non-existent lib with findResourceByShortType")
       raise
    else:
       if libname == "":
           pf.passed("found '' library name when trying to find non-existent lib with findResourceByShortType")
       else:
           pf.failed("found non-existent lib with findResourceByShortType")


def execTests(pf):

    try:
       # try giving Application  non-list execution
        b = "superduper"
        c = "extra"
        d = "eddie"
        av = AttrVal()
        av.addPair(b, c)
        av.addPair(d, "")
        e = Execution("sally")
        app = Application("frank", av ,e)
    except PTexception, a:
        pf.passed(a.value)
    except:
       pf.failed("non-PTexception when try giving Application non-list execution")
    else:
       pf.failed("try giving Application non-list execution")

    try:
       # try giving Application  good execution list 
       b = "superduper"
       c = "extra"
       d = "eddie"
       e = Execution("sally")
       app = Application("frank", None,[e])
    except PTexception, a:
        pf.failed(a.value)
    except:
        pf.failed("non-PTexception when try giving Application good execution list")
    else:
        pf.passed("try giving Application good execution list")

    try:
       exe = Execution()
    except PTexception, a:
        pf.passed(a.value)
    except:
        pf.failed("non-PTexception when try giving Execution no name" )
    else:
       pf.failed("try giving Execution no name")

    try:
       a = ""
       exe = Execution(a)
    except PTexception, a:
        pf.passed(a.value)
    except:
       pf.failed("non-PTexception when try giving Execution name ''" )
    else:
       pf.failed("try giving Execution name ''")


    try: 
       # try giving Execution bad attr value 
       a = "susan"
       c = "superduper"
       d = ""
       exe = Execution(a,[c,d])
    except PTexception, a:
        pf.passed(a.value)
    except:
       pf.failed("non-PTexception when try giving Execution attr value=''")
    else:
       pf.failed("try giving Execution attr value=''")
      
    try:
       # try giving Execution non-list attr value 
       a = "susan"
       c = "superduper"
       d = "silliness"
       exe = Execution(a,(c,d))
    except PTexception, a:
        pf.passed(a.value)
    except:
       pf.failed("non-PTexception raised when try giving Execution non-list attrvalue")
    else:
       pf.failed("try giving Execution non-list attrvalue")

    try:
       # try giving Execution non-pair attr value 
       a = "susan"
       c = "superduper"
       d = "silliness"
       exe = Execution(a,[c])
    except PTexception, a:
        pf.passed(a.value)
    except:
       pf.failed("non-PTexception raised when try giving Execution non-pair attrvalue")
    else:
       pf.failed("try giving Execution non-pair attrvalue")

    try:
       # try giving Execution good list attr value 
       a = "susan"
       c = "superduper"
       d = "silliness"
       exe = Execution(a,[(c,d)])
    except PTexception, a:
        pf.failed(a.value)
    except:
       pf.failed("non-PTexception when try giving Execution good list attrvalue")
    else:
       pf.passed("try giving Execution good list attrvalue")

    try:
       # try giving Execution  None resource list
       a = "susan"
       c = "superduper"
       d = "silliness"
       f = None
       exe = Execution(a,[(c,d)],[f])
    except PTexception, a:
        pf.passed(a.value)
    except:
       pf.failed("non-PTexception raised when try giving Execution None resource list")
    else:
       pf.failed("try giving Execution None list")

    try:
       # try giving Execution  non-list resource list 
       a = "susan"
       c = "superduper"
       d = "silliness"
       f = Resource("a","b")
       exe = Execution(a,[(c,d)],f)
    except PTexception, a:
        pf.passed(a.value)
    except:
       pf.failed("non-PTexception raised when try giving Execution non-list resource list")
    else:
       pf.failed("try giving Execution non-list resource list")

    try:
       # try giving Execution  good resource list 
       a = "susan"
       c = "superduper"
       d = "silliness"
       f = Resource("a","b")
       exe = Execution(a,[(c,d), f])
    except PTexception, a:
        pf.failed(a.value)
    except:
       pf.failed("non-PTexception raised when try giving Execution good resource list")
       raise
    else:
       pf.passed("try giving Execution good resource list")

def focusTests(pf):
    try:
       # try  getting a focus template
        ri = ResourceIndex()
        build = Resource("mybuild","build")
        env = Resource("myenv", "environment")
        lib = Resource(env.name+"|libmpi.so","environment|module")
        ri.addResource(lib)
        lib = Resource(env.name+"|libelf.so","environment|module")
        ri.addResource(lib)
        compiler = Resource("theCompiler","compiler")
        execution = Execution("myexec")
        process0 = Resource(execution.name+"|Process-0","execution|process")
        ri.addResources([compiler,build,env])
        metric = Resource("MFLOPS","metric")
        pt = Resource("Paradyn","performanceTool")
        ri.addResources([build,env,process0,metric,pt])
        fl = ri.createContextTemplate()
    except:
       pf.failed("non-PTexception raised when getting focusTemplate")
       raise
    else:
       if len(fl) != 4:
          pf.failed("wrong number of resources. %d" % len(fl))
       else:
          pf.passed("got focus template successfully")

    try:
       # try getting a focus template with two top-level resources withthe 
       # same type
        ri =ResourceIndex()
        build = Resource("mybuild","build")
        env = Resource("myenv", "environment")
        lib = Resource(env.name+"|libmpi.so","environment|module")
        ri.addResource(lib)
        lib = Resource(env.name+"|libelf.so","environment|module")
        ri.addResource(lib)
        compiler = Resource("theCompiler","compiler")
        execution = Execution("myexec")
        process0 = Resource(execution.name+"|Process-0","execution|process")
        ri.addResources([compiler,build,env])
        compiler = Resource("theOtherCompiler","compiler")
        process1 = Resource(execution.name+"|Process-1","execution|process")
        ri.addResources([compiler,build,env])
        ri.addResources([build,env,process0,process1])
        fl = ri.createContextTemplate()
    except:
       pf.failed("non-PTexception raised when getting focusTemplate same types")
       raise
    else:
       if len(fl) != 5:
          pf.failed("wrong number of resources same types. %d" % len(fl))
       else:
          pf.passed("got focus template successfully same types")


    try:
       # try adding a specific focus resources that is a child of a resource
       # in the template
        ri = ResourceIndex()
        build = Resource("mybuild","build")
        env = Resource("myenv", "environment")
        lib = Resource(env.name+"|libmpi.so","environment|module")
        ri.addResource(lib)
        lib = Resource(env.name+"|libelf.so","environment|module")
        ri.addResource(lib)
        compiler = Resource("theCompiler","compiler")
        execution = Execution("myexec")
        process0 = Resource(execution.name+"|Process-0","execution|process")
        ri.addResources([compiler,build,env])
        ri.addResources([build,env,process0])
        fl = ri.createContextTemplate()
        newfl = ri.addSpecificContextResource(fl,process0)
    except:
       pf.failed("non-PTexception raised when adding specific focus child")
       raise
    else:
       if len(newfl) != 4:
          pf.failed("wrong number of resources when adding specific focus child. %d" % len(newfl))
       else:
          pf.passed("got focus template successfully when adding specific focus child")

    try:
       # try adding a list of specific focus resources that is a child of 
       # a resource in the template
        ri = ResourceIndex()
        build = Resource("mybuild","build")
        env = Resource("myenv", "environment")
        lib = Resource(env.name+"|libmpi.so","environment|module")
        ri.addResource(lib)
        lib = Resource(env.name+"|libelf.so","environment|module")
        ri.addResource(lib)
        compiler = Resource("theCompiler","compiler")
        execution = Execution("myexec")
        process0 = Resource(execution.name+"|Process-0","execution|process")
        ri.addResources([compiler,build,env])
        process1 = Resource(execution.name+"|Process-1","execution|process")
        ri.addResources([compiler,build,env])
        ri.addResources([build,env,process0,process1])        
        fl = ri.createContextTemplate()
        newfl = ri.addSpecificContextResources(fl,[process0,process1])
    except:
       pf.failed("non-PTexception raised when adding specific focus child list")
       raise
    else:
       if len(newfl) != 5:
          pf.failed("wrong number of resources when adding specific focus child list. %d" % len(newfl))
       else:
          pf.passed("got focus template successfully when adding specific focus child list")


def attrValTests(pf):

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
        print av.pairs
        for (a,v,t) in av:
           i += 1
           if a == "susan":
              break
        for a,v,t in av:
           i += 1
        if i != 4:
           raise PTexception("break in iteration didn't work")
        a = av.getNext()
        newlist = []
        while a: 
           newlist.append(a)
           a,v,t = av.getNext()
        if len(newlist) != 4:
           raise PTexception("getNext not working")
            
    except PTexception, a:
        pf.failed("PTexception raised for good AttrVal test: " + a.value)
    except:
        pf.failed("non-PTexception raised AttrVal good test")
        raise
    else:
        pf.passed("good AttrVal test")


    try:
        # test missing value for name 
        av = AttrVal()
        av.addPair("","frank") 
    except PTexception, a:
        pf.passed("PTexception raised for missing 'name' value: " + a.value)
    except:
        pf.failed("non-PTexception raised AttrVal missing 'name'")
        raise
    else:
        pf.failed("no exception raised AttrVal 'missing name'")
    

    try:
        # test non-list given to addPairs
        av = AttrVal()
        av.addPairs("frank")
    except PTexception, a:
        pf.passed("PTexception raised for non-list to addPairs: " + a.value)
    except:
        pf.failed("non-PTexception raised AttrVal non-list to addPairs")
        raise
    else:
        pf.failed("no exception raised AttrVal non-list to addPairs")


    try:
        # test non-pair list given to addPairs
        av = AttrVal()
        a = ["frank","allice","steve"]
        av.addPairs(a)
    except PTexception, a:
        pf.passed("PTexception raised for non-pair list to addPairs: " + a.value)
    except:
        pf.failed("non-PTexception raised AttrVal non-pair list to addPairs")
        raise
    else:
        pf.failed("no exception raised AttrVal non-pair list to addPairs")


def main():
    pf = PassFail()
    tests = [resourceBasicTests,resourceSearchTests,execTests, attrValTests,\
                 focusTests]
    for test in tests:
        test(pf)
        
    pf.test_info()
    return pf.failed_count > 0

if __name__ == "__main__":
   sys.exit(main())
