#!/usr/bin/env python

import os,sys


class plugin:
   def __init__(self, name="", file=None, argList=[], retType=None):
      #print "im a plugin initializing: %s" % name
      self.name = name
      self.file = file
      self.func = None
      self.argList = argList
      self.retType = retType
      self.__initCheck()

   def getName(self):
      #print "my name is: %s" % self.name
      return self.name
 
   def getFile(self):
      return self.file

   def getFunc(self):
      return self.func

   def getArgList(self):
      return self.argList

   def getRetType(self):
      return self.retType
 
   def callFunc(self):
      self.func()

   def __initCheck(self):
      self.__checkFile()
      self.__findFunc()

   def __checkFile(self):
      path = sys.path
      found = False
      for p in path:
          if os.path.lexists(p+"/"+self.file):
             found = True
             break
      if not found:
         print "cannot find file: %s for operator:%s" % (self.file, self.name)
         raise

   def __findFunc(self):
      try:
         importName = self.file.rstrip(".py")
         module = __import__(importName)
      except:
         print "error importing %s for operator: %s" % (self.file, self.name)
         return
      try:
         self.func = getattr(module, self.name) 
      except:
         print "cannot find callable function for operator:%s" % (self.name) 
         raise
      

class operator:

    def __init__(self, rcfile=".ptoperators"):
        self.rcfile = rcfile
        self.plugins = None 
        self.lineno = 0
        self.plugins = self.__parseRcFile(self.rcfile)

    def getPlugins(self, haveData=True):
        return self.plugins

    def operator(self, plugin, data,args ):
        #print " calling %s" % plugin.name
        #print "plugin: %s, data: %s, args: %s" % (plugin,data,args)
        ret = plugin.func(data,args)
        #print "operator returning ret: %s" % ret
        return ret

    def getName(self, plugin):
        return plugin.getName()

    def getArgList(self, plugin):
        return plugin.getArgList()

    def getRetType(self, plugin):
        return plugin.getRetType()


    def __parseRcFile(self, file):
        path = sys.path
        for p in path:
           try:
              fl = p + "/" + file  
              #print "trying: %s" % fl
              f = open(fl,'r')
              break
           except:
              f = None
        if f == None:
           print "operator::__parseRcFile could not locate %s" % file
           return [] 
        plugins = []
        plugin = True
        while plugin:
          plugin = self.__parseOnePlugin(f)
          if plugin:
             plugins.append(plugin)
        #print plugins
        return plugins

    def __parseOnePlugin(self, f):
        line = self.__readline(f)
        #print "got line: %s" % line
        if line == None:
           return None
        if not line.strip().startswith("operator"):
           print "syntax error: expected 'operator' keyword at line:%d, got:\"%s\"" \
                 % (self.lineno,line)
           return None
        try:
           (operKeyWd, opName, brace)= line.split()
        except:
           print "syntax error: expected \"'operator' <opName> {\" got:\"%s\" at line:%d" % (line, self.lineno)
           return None
        fileName = None
        argList = []
        retTypeName = None
        while line != None:
           line = self.__readline(f)
           if line == None:
              print "syntax error: unexpected end of operator %s at line: %d " % (opName, self.lineno)
              return None
           if line.startswith("file"):
              try:
                 (fileKeyWd, fileName) = line.split()
              except:
                 print "syntax error: expected \"'file' <fileName>\" got:\"%s\" at line: %d" (line, self.lineno)
                 return None
           elif line.startswith("arg"):
              try:
                 (argKeyWd, argName, argType) = line.split()
                 argList.append((argName,argType))
              except:
                 print "syntax error: expected \"'arg' <argName> <argType>\" got:\"%s\" at line: %d" (line, self.lineno)
                 return None
           elif line.startswith("retType"):
              try:
                 (retKeyWd, retTypeName) = line.split()
              except:
                 print "syntax error: expected \"'retType' <retTypeName>\" got:\"%s\" at line :%d" (line, self.lineno) 
                 return None
           elif line.startswith("}"):
              break  # end of operator
        if not fileName:
           print "fileName required for operator: %s" % opName
           return None
        try:
           op = plugin(opName,fileName,argList, retTypeName)
        except:
           return None
        return op
        
 
    def __readline(self, f):
        # skip blanks and comment lines
        line = f.readline()
        if line == '':
           return None
        #print "line:%s" % line
        self.lineno += 1
        while line != '' and (line.strip() == "" or line.startswith ("#")):
             line = f.readline()   
             #print "line:%s" % line
             self.lineno += 1
        return line.strip()

    

