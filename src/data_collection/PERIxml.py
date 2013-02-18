#!/usr/bin/env python


import xml.dom.minidom
import datetime

# This class is used for generating PERI xml

class PERIxml:
    identifier = 0
    def __init__(self):
        self.build = None
        self.run = None
        self.genPERIheader()
        # what function is used to create each type
        self.periCreateMap = {}
        self.periCreateMap["peri:resourceSet"] = "createResourceSet"
        self.periCreateMap["peri:resource"] = "createResource"
        self.periCreateMap["peri:nodeList"] = "createNodeList"
        self.periCreateMap["peri:node"] = "createNode"
        self.periCreateMap["peri:memory"] = "createMemory"
        self.periCreateMap["peri:cpu"] = "createCpu"
        # what function is used to add an attribute to each type
        self.periAttrMap = {}
        self.periAttrMap["peri:memory"] = "setMemoryAttribute"
        self.periAttrMap["peri:nodeList"] = "setNodeListAttribute"
        self.periAttrMap["peri:node"] = "setNodeAttribute"
        self.periAttrMap["peri:cpu"] = "setCpuAttribute"
        # when we look up elements, what type is their "name"
        self.tagMap = {}
        self.tagMap['peri:cpu'] = ("attribute","index")
        self.tagMap['peri:memory'] = (None,"")
        self.tagMap['peri:runrules'] = (None,"")
        self.tagMap['peri:resourceSet'] = (None,"")
        self.tagMap['peri:resource'] = (None,"")
        self.tagMap['peri:nodeList'] = (None,"")
        self.tagMap['peri:node'] = ("element","peri:nodeName")


    def getRoot(self):
        return self.doc

    def PERI_nvp(self, name, value, parent):
        nv = self.doc.createElement("peri:nvp")
        n = self.doc.createAttribute("name")
        n.value = name
        v = self.doc.createTextNode(value)
        nv.appendChild(v)
        nv.setAttributeNode(n)
        if parent:
           parent.appendChild(nv)
    
    def PERI_person(self, parent=None, userName=None, realName=None, email=None, phone=None, group=None):
        person = self.doc.createElement("peri:person")
        if userName:
           user = self.doc.createElement("user")
           name = self.doc.createTextNode(userName)
           user.appendChild(name)
           person.appendChild(user)
        if realName:
           user = self.doc.createElement("realName")
           name = self.doc.createTextNode(realName)
           user.appendChild(name)
           person.appendChild(user)
        if email:
           user = self.doc.createElement("email")
           name = self.doc.createTextNode(email)
           user.appendChild(name)
           person.appendChild(user)
        if phone:
           user = self.doc.createElement("phone")
           name = self.doc.createTextNode(phone)
           user.appendChild(name)
           person.appendChild(user)
        if group:
           user = self.doc.createElement("group")
           name = self.doc.createTextNode(group)
           user.appendChild(name)
           person.appendChild(user)
        if parent:
           parent.appendChild(person)
        return person
    
    def PERI_operatingSystem(self, osName, osVersion, osRelease, parent):
        os = self.doc.createElement("peri:operatingSystem")
        n = self.doc.createElement("name")
        name = self.doc.createTextNode(osName)
        n.appendChild(name)
        os.appendChild(n)
        if osVersion:
           v = self.doc.createElement("version")
           vers = self.doc.createTextNode(osVersion)
           v.appendChild(vers)
           os.appendChild(v)
        if osRelease:
           details = self.doc.createElement("peri:details")
           self.PERI_nvp("release type", osRelease, details)
           os.appendChild(details)
        if parent:
           parent.appendChild(os)
        return os
    
    def PERI_time(self, time=None, parent=None):
        timeElem = self.doc.createElement("peri:time")
        t = self.doc.createAttribute("value")
        if time:
           t.value = time
        else: 
           t.value = (str(datetime.datetime.isoformat(datetime.datetime.now())),'.')[0]
        timeElem.setAttributeNode(t)
        if parent:
           parent.appendChild(timeElem)
        return timeElem

    def PERI_file(self, value, which, parent):
       fc = self.doc.createElement("peri:file")
       if parent:
          parent.appendChild(fc)
       if which == "abspath":
          f = self.doc.createAttribute("abspath")
          f.value = value
          fc.setAttributeNode(f)
       elif which == "path-filename":
          f = self.doc.createAttribute("path")
          f.value = value
          fc.setAttributeNode(f)
          f = self.doc.createAttribute("filename")
          parts = value.split('/') # extract the filename portion of the path
          f.value = parts[len(parts)-1]
          fc.setAttributeNode(f)
       return fc

    
    def genPERIheader(self):
        # get the XML document ready and initialized
        self.doc = xml.dom.minidom.Document()
        self.rootElem = self.doc.createElement("peri:runrules")
        self.doc.appendChild(self.rootElem)
        # set namespace
        ns = self.doc.createAttribute("xmlns:peri")
        ns.value = "http://peri-scidac.org/"
        self.rootElem.setAttributeNode(ns)
        # create id
        id = self.doc.createAttribute("id")
        id.value = str(self.identifier)
        self.identifier += 1
        self.rootElem.setAttributeNode(id)
        # add time element to root
        self.PERI_time(None, self.rootElem)
    
    def createRun(self, name=None, parent=None):
        # create a peri:run element, if a parent element is sent in, we will use
        # that, otherwise, the run element becomes a child of root
        self.run = self.doc.createElement("peri:run")
        if parent:
           parent.appendChild(self.run)
        else:
           self.rootElem.appendChild(self.run)
        return self.run

    def getRun(self):
        return self.run

    def createBuild(self, name=None, parent=None):
        # create peri:transformationSet and peri:transformation elements, 
        # we are modeling the build as a transformation of type compile/link
        # if a parent element is sent in, we will use
        # that, otherwise, the run element becomes a child of root
        transE = self.doc.createElement("peri:transformationSet")
        self.build = self.doc.createElement("peri:transformation")
        transE.appendChild(self.build)
        # transformation type
        type = self.doc.createElement("type")
        ty = self.doc.createTextNode("compile/link")
        type.appendChild(ty)
        self.build.appendChild(type)
        if parent:
           parent.appendChild(transE)
        else:
           self.rootElem.appendChild(transE)
        return self.build

    def getBuild(self):
        return self.build

    def createCompiler(self, name, parent=None):
        # create a compiler, we are modeling compilers as a peri:resource
        # if a parent is sent in, we will use that,
        # otherwise, the compiler is a child of the build
        compiler = self.doc.createElement("peri:resource")
        type = self.doc.createElement("type")
        t = self.doc.createTextNode("compiler")
        type.appendChild(t)
        compiler.appendChild(type)
        nme = self.doc.createElement("name")
        n = self.doc.createTextNode(name)
        nme.appendChild(n)
        compiler.appendChild(nme)
        if parent:
           parent.appendChild(compiler)
        else:
           self.build.appendChild(compiler)
        return compiler

    #def setCompilerName(self, compiler, CompilerName):
        #nme = self.doc.createElement("name")
        #n = self.doc.createTextNode(CompilerName)
        #nme.appendChild(n)
        #compiler.appendChild(nme)

    def setCompilerAttribute(self, compiler, nme, val):
        E = self.doc.createElement(nme)
        e = self.doc.createTextNode(val)
        E.appendChild(e)
        compiler.appendChild(E)

    def createLibrarySet(self, name=None, parent=None):
        #model library set as resource
        res = self.doc.createElement("peri:resource")
        libs = self.doc.createElement("peri:libraries")
        res.appendChild(libs)
        if parent:
           parent.appendChild(res)
        return libs
         
    def createLibrary(self, name, parent):
        lib = self.doc.createElement("peri:library")
        self.PERI_file(name, "path-filename", lib)
        if parent:
           parent.appendChild(lib)
        return lib

    def setLibraryAttribute(self, lib, name, val):
        type = self.doc.createElement(name)
        t = self.doc.createTextNode(val)
        type.appendChild(t)
        lib.appendChild(type)

    
    def createTime(self,value, parent):
        time = self.PERI_time(value,parent)
        return time

    def createApplication(self, AppName, parent):
        # create a peri:program element, enclosed in a peri:resource
        res = self.doc.createElement("peri:resource")
        prog = self.doc.createElement("peri:program")
        self.PERI_nvp("name", AppName, prog)
        res.appendChild(prog)
        parent.appendChild(res)
        return prog

    def setApplicationAttribute(self, app, name, val):
        self.PERI_nvp(name, val, app)

    def createPerson(self, userName, parent):
       # modeling a person as a resource
       res = self.doc.createElement("peri:resource")
       person = self.PERI_person( res, userName)
       if parent:
          parent.appendChild(res)
       return person

    def createEnvironment(self, name=None, parent=None):
       env = self.doc.createElement("peri:environment")
       parent.appendChild(env)
       return env

    def setEnvironmentAttribute(self,env, nme, val):
       self.PERI_nvp(nme, val, env)

    def createExecutable(self, exeName, parent):
       # modeling the executable as an output file of the build transformation
       oSet = self.doc.createElement("peri:outputs")
       file = self.PERI_file(exeName, "abspath", oSet)
       if parent:
          parent.appendChild(oSet)
       return file

    def createMachineNode(self, nodeName, parent):
        # the machine is also a resource element
        res = self.doc.createElement("peri:resource")
        node = self.createNode(nodeName, res)
        if parent:
           parent.appendChild(res)
        return node

    def createOperatingSystem(self, OSName, parent): 
        # the build doesn't have an OS in it, so we model it as a 
        # resource element. However, the run does have an OS, 
        # so we don't need a resource element
        if parent == self.build:
           res = self.doc.createElement("peri:resource")
           newParent = res
           parent.appendChild(newParent)
        else:
           newParent = parent
        os = self.doc.createElement("peri:operatingSystem")
        n = self.doc.createElement("name")
        name = self.doc.createTextNode(OSName)
        n.appendChild(name)
        os.appendChild(n)
        if newParent:
           newParent.appendChild(os)
        return os

    def setOperatingSystemAttribute(self, os, name, value):
        if name == "version":
           v = self.doc.createElement(name)
           vers = self.doc.createTextNode(value)
           v.appendChild(vers)
           os.appendChild(v)
        elif name == "release type":
           details = self.doc.createElement("peri:details")
           self.PERI_nvp(name, value, details)
           os.appendChild(details)


    def createProgram(self, name, parent):
        prog = self.doc.createElement("peri:program")
        n = self.doc.createElement("name")
        v = self.doc.createTextNode(name)
        n.appendChild(v)
        prog.appendChild(n)
        if parent:
           parent.appendChild(prog)
        return prog

    def setProgramAttribute(self, prog, name, value):
        if name == "version":
           v = self.doc.createElement(name)
           ver = self.doc.createAttribute("number")
           ver.value = value
           v.setAttributeNode(ver)
           prog.appendChild(v)

    def createScheduler(self, name, parent):
        sched = self.doc.createElement("peri:scheduler")
        set = self.doc.createElement("peri:settings")
        self.PERI_nvp("name", name, set)
        sched.appendChild(set)
        if parent:
           parent.appendChild(sched)
        return sched

    def setSchedulerAttribute(self, sched, name, value):
        if name == "version" and value != "":
           [set] = sched.getElementsByTagName("peri:settings")
           self.PERI_nvp("version", value, set)
 
    def createQueue(self,name=None, parent=None):
        queue = self.doc.createElement("peri:queueContents")
        if parent: 
           parent.appendChild(queue)
        return queue

    def createSchedulerJob(self, name=None, parent=None):
        job = self.doc.createElement("peri:schedulerJob")
        if parent:
           parent.appendChild(job)
        return job
 
    def setSchedulerJobAttribute(self, job, name, value):
        if name == "jobid":
           jobid = self.doc.createElement("jobid")
           id = self.doc.createAttribute("id")
           id.value = value
           jobid.setAttributeNode(id)
           job.appendChild(jobid)
        elif name == "programName":
           pgname = self.doc.createElement("programName")
           pgn = self.doc.createTextNode(value)
           pgname.appendChild(pgn)
           job.appendChild(pgname)
        elif name == "hoursRunning":
           hours = self.doc.createElement("hoursRunning")
           if value.find(":") >= 0:
             s = ""
             if value.count(":") == 2:
                h,m,s = value.split(":")
             elif value.count(":") == 1:
                h,m = value.split(":")
             ht = int(h) + float(m)/60.0
             if s != "":
                ht += float(s)/60.0/60.0
           elif value.strip() == "N/A":
             ht = 0.0
           else:
             ht = value
           hs = self.doc.createTextNode(str(ht))
           hours.appendChild(hs)
           job.appendChild(hours)
        elif name == "status":
           stats = self.doc.createElement("status")
           sts = self.doc.createTextNode(value)
           stats.appendChild(sts)
           job.appendChild(stats)

    def createBatchFile(self, batchName, parent):
        # batch file is also modeled as a peri:resource
        res = self.doc.createElement("peri:resource")
        bf = self.doc.createElement("batchFile")
        name = self.doc.createElement("name")
        n = self.doc.createTextNode(batchName)
        name.appendChild(n)
        bf.appendChild(name)
        res.appendChild(bf)
        if parent: 
           parent.appendChild(res)
        return bf

    def setBatchFileAttribute(self, batch, name, value):
        reses = self.doc.createElement(name)
        rs = self.doc.createTextNode(value)
        reses.appendChild(rs)
        batch.appendChild(reses)

    def createFileSystemSet(self, name=None,parent=None):
        res = self.doc.createElement("peri:resource")
        if parent: 
           parent.appendChild(res)
        return res

    def createFileSystem(self, name, parent):
        fs = self.doc.createElement("fileSystem")
        fsn = self.doc.createElement("name")
        n = self.doc.createTextNode(name)
        fsn.appendChild(n)
        fs.appendChild(fsn)
        if parent:
           parent.appendChild(fs)
        return fs

    def setFileSystemAttribute(self, fs, name, value):
        if name == "version" and value != "":
           fsn = self.doc.createElement(name)
           n = self.doc.createTextNode(value)
           fsn.appendChild(n)
           fs.appendChild(fsn)

    def createDevice(self, name, parent):
        dev = self.doc.createElement("device")
        devn = self.doc.createElement("name")
        n = self.doc.createTextNode(name)
        devn.appendChild(n)
        dev.appendChild(devn)
        if parent: 
           parent.appendChild(dev)
        return dev

    def addDeviceAttribute(self, dev, name, val):
        devn = self.doc.createElement(name)
        n = self.doc.createTextNode(val)
        devn.appendChild(n)
        dev.appendChild(devn)

    def createInputs(self, name=None, parent=None):
        iset = self.doc.createElement("peri:inputs")
        if parent:
           parent.appendChild(iset)
        return iset
   
    def createFile(self, fullname, parent):
        file = self.PERI_file(fullname, "abspath", parent)
        return file

    def createResourceSet(self, name=None, parent=None):
        resSet = self.doc.createElement("peri:resourceSet")
        if parent:
           parent.appendChild(resSet)
        return resSet

    def createResource(self, name=None, parent=None):
        res = self.doc.createElement("peri:resource")
        if parent:
           parent.appendChild(res)
        return res

    def createNodeList(self, name=None, parent=None):
        res = self.doc.createElement("peri:nodeList")
        if parent:
           parent.appendChild(res)
        return res

    def setNodeListAttribute(self, nl, name, val):
        if name == "concurrency":
           conc = self.doc.createAttribute(name)
           conc.value = val
           nl.setAttributeNode(conc)

    def createNode(self, nodeName=None, parent=None):
        node = self.doc.createElement("peri:node")
        name = self.doc.createElement("peri:nodeName")
        n = self.doc.createTextNode(nodeName)
        name.appendChild(n)
        node.appendChild(name)
        if parent:
           parent.appendChild(node)
        return node

    def setNodeAttribute(self, node, name, val):
        self.PERI_nvp(name, val, node)
 
    def createMemory(self, name=None, parent=None):
        mem = self.doc.createElement("peri:memory")
        if parent:
           parent.appendChild(mem)
        return mem

    def setMemoryAttribute(self, mem, name, val):
        if name == "mainKB":
           mainE = self.doc.createElement(name)
           main = self.doc.createTextNode(val)
           mainE.appendChild(main)
           mem.appendChild(mainE)
        elif name.find("cacheKB") >= 0:
           # a hack... name could be "L1 cacheKB" or "L2 cacheKB"
           level = ""
           if name.upper().startswith("L"): # tell us the level?
              level,name = name.split(" ")
           E = self.doc.createElement(name)
           if level:
              lev = self.doc.createAttribute("level")
              lev.value = level
              E.setAttributeNode(lev)
           e = self.doc.createTextNode(val)
           E.appendChild(e)
           mem.appendChild(E)

    def createCpu(self, name=None, parent=None):
        res = self.doc.createElement("peri:cpu")
        index = self.doc.createAttribute("index")
        index.value = name 
        res.setAttributeNode(index)
        if parent:
           parent.appendChild(res)
        return res

    def setCpuAttribute(self, cpu, name, val):
        if name == "MHz":
           mhzE = self.doc.createElement(name)
           mhz = self.doc.createTextNode(val)
           mhzE.appendChild(mhz)
           cpu.appendChild(mhzE)
 
    def findElement(self, tagName, parent, ident):
       #print "searching for: %s %s %s" % (tagName,parent,ident)
       children = self.rootElem.getElementsByTagName(tagName)
       for child in children: 
          if child.parentNode == parent:
             if ident == None or ident == "Unknown":
                return child # assume only one, so there's no identifier
             ret =  self.tagMap[tagName]
             if ret == None:
                #print "%s: not in self.tagMap" % tagName
                continue
             type,name = ret
             if type == None:
                return child
             elif type == "attribute":
                id = child.getAttribute(name)
                if id == ident:
                   return child
             elif type == "element":
                chldlist = child.childNodes
                #print chldlist
                for u in chldlist: 
                    #print "NodeName: %s" % u.nodeName
                    if u.nodeName == name:
                       if u.childNodes[0].nodeValue == ident:
                          return child

       return None


    def createPERIelement(self, nameHier, typeHier):
        parent = self.rootElem
        nameHier = nameHier.lstrip("/")
        typeHier = typeHier.lstrip("/")
        for name, type in zip(nameHier.split("/"), typeHier.split("/")):
            el = self.findElement(type, parent, name)
            if not el:
               cFunc = self.periCreateMap[type]
               cf = getattr(self,cFunc)
               el = cf(name, parent)
            parent = el
            

    def addAttribute(self, nameHier, typeHier, attrName, attrValue):
        parent = self.rootElem
        nameHier = nameHier.lstrip("/")
        typeHier = typeHier.lstrip("/")
        el = None
        elType = ""
        for name, type in zip(nameHier.split("/"), typeHier.split("/")):
            el = self.findElement(type, parent, name)
            if not el:
               print "ERROR: could not find parent of: %s " % name
               return
            parent = el
            elType = type
        aFunc = self.periAttrMap[elType]
        af = getattr(self,aFunc)
        af(el, attrName, attrValue)

    def writeData(self, fileName):
       oF = open(fileName,'w')
       oF.write(self.doc.toprettyxml(encoding='utf-8'))
       oF.close()




