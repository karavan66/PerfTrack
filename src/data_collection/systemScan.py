#!/usr/bin/env python

# +++++++++++++++++++++++++++++++
# +++++++++++++++++++++++++++++++
# SystemScan
# Host System Method (Manager Component)
#
# amaubaa   3/7/2006 Initial Release
# amaubaa   3/14/2006   Added File Name option
#           Added PTDF object

import sys, types, datetime
from optparse import OptionParser
import iMDL, ptdf, gm_hs_tools, gmLogger

import PTcommon 

# FUNCTIONS
# +++++++++++++++++++++++++++++++
# +++++++++++++++++++++++++++++++

# Function: Get Module
# Preconditions: None
# Postconditions: Module has been loaded.
#
# Loads module at runtime.
# Used to load user specified attribute module.
def _get_mod(modulePath):
   try:
   # Check if module is already loaded
      aMod = sys.modules[modulePath]
      if not isinstance(aMod, types.ModuleType):
         raise KeyError
   except KeyError:
   # Load the module if it exists. Error and exit if it does not
      try:
         aMod = __import__(modulePath, globals(), locals(), [''])
         sys.modules[modulePath] = aMod
      except ImportError:
         print ""
         print " +++++++ MODULE ERROR +++++++"
         print " The module specified '" + modulePath + \
               "' is not available or is not in the path"
         print ""
         sys.exit()
   return aMod

# MAIN
# +++++++++++++++++++++++++++++++
# +++++++++++++++++++++++++++++++
def main (argv=None):

   __version__ = '1.0.1'

   ## parse the command line
   usage = "%prog  systemScan [-h] [-d] [-m module name] [-f config file] [-p]" 
   #version = "%prog 1.0.1"
   parser = OptionParser(usage=usage, version="%prog " + __version__)
   parser.add_option ("-d", "--debug", dest="debugMode", \
                      help="Enable debug mode", default=1)
   parser.add_option ("-m", "--module", dest="module", \
                      help="Name of Python module containing attribute " +\
                      "classes to load. The default file is pt_proc.", \
                      default="pt_proc")
   parser.add_option ("-f", "--configfile", dest="configFile", \
                      help="Name of configuration file containing machine " +\
                      "configuration data.  The default file for PTdf is ./iMDL.cfg."\
                      " The default for PERI xml is ./PERIiMDL.cfg. Look in "\
                      "the perftrack/share directory for example files.", \
                      default="iMDL.cfg")
   parser.add_option ("-o", "--outfile", dest="outputFile", \
                      help="Name of output file. Default name is " +\
                      "systemScan.ptdf (or systemScan.xml if PERI output is "\
                      " selected).", default="systemScan.ptdf")
   parser.add_option ("-p", "--peri", dest="PERIxml", action="store_true",\
                      help="Change output format to PERI xml. Default is PTdf."\
                      ,default=False)
 

   (options, args) = parser.parse_args()
   _debug = options.debugMode
   attrModule = options.module
   configFileName = options.configFile
   if options.PERIxml:
      outputFormat = "PERIxml"
      outputFileName = options.outputFile.replace(".ptdf",".xml")
      if options.configFile == "iMDL.cfg":
         configFileName = "PERIiMDL.cfg"
      from PERIxml import PERIxml
   else:
      outputFormat = "PTdf"
      outputFileName = options.outputFile


   ## unknown string
   unknownStr = "Unknown"
   dqStr      = '"'
   sqStr      = "'"

   # Create Logging object
   logObj = gmLogger.gmlog()
   logObj.gmLogWrite(2,"Host System Method Version: " + __version__)


   # Load the user specified attribute module
   logObj.gmLogWrite(0,"Loading Atribute Module Name: " + attrModule)
   moduleObj = _get_mod(attrModule)
   logObj.gmLogWrite(0,"Loaded Atribute Module Name: " + attrModule + \
                     " " + moduleObj.__version__)

   # Create the MDL objects
   m_mdl = iMDL.imdl(configFileName, outputFormat)
   if outputFormat == "PTdf":
      ptdf_mdl = ptdf.PerfTrackDataFormat()
   elif outputFormat == "PERIxml":
      peri = PERIxml() 

   # Get all the class definitions in the user specified module
   # We only want the class definitions that are a child
   # of superclass baseAttrib. Create a dictionary of class instances
   # indexed by resource type
   # that we know are attribute gathering functions.
   attribFuncsByType = {}
   for key in moduleObj.__dict__:
      # Dont look at special attributes or attributes that are not class objects
      if key[0:2] != "__" and type(moduleObj.__dict__[key]) == types.ClassType:
         # Dont get the super class
         if key != "baseAttrib":
            # Only get class objects that are children of the super class
            if issubclass(moduleObj.__dict__[key], \
                          moduleObj.gm_hs_tools.baseAttrib):
               logObj.gmLogWrite(0,"Found Attribute Object: " + key)
               if moduleObj.__dict__[key]().attribFuncReq():
                  continue  # the function does not work on this system, so ignore
               # get the resource type the function gathers data for
               restype = \
                  m_mdl.getResourceTypeFor(key,"") #TODO 2nd arg is supposed
               restype = PTcommon.cws(restype)
                  #to be attribute Name, but it's not used in the function,
                  # so it doesn't matter
               # if you don't get type from MDL, ask the object
               if restype == unknownStr:
                  restype = moduleObj.__dict__[key]().attribDefaultResourceType()
                  restype = restype.strip("'")
                  logObj.gmLogWrite(0,"Resource Type determined by object " + \
                           restype)
               else:
                  logObj.gmLogWrite(0,"Resource Type determined by iMDL " + restype)
               restype = PTcommon.cws(restype)

               #TODO get restype from the MDL
               if restype.upper() in attribFuncsByType.keys(): 
                  attribFuncsByType[restype.upper()].append((key, \
                            moduleObj.__dict__[key]()))
               else:
                  attribFuncsByType[restype.upper()] = [(key,moduleObj.__dict__[key]())]

   #print attribFuncsByType

   resources = m_mdl.getResources()
   if resources == unknownStr:
      print "No resource names were found for this system. Perhaps you forgot to specify a configuration file with the -f option?"
      sys.exit()

   for resName,resType in resources:
      logObj.gmLogWrite(0,"Working on resource " + resName)
      attribFuncs = []
      try:
         attribFuncs = attribFuncsByType[resType.upper()]
      except:
         logObj.gmLogWrite(0,"There are no attribute functions for " + resName)
         pass
      resourceTypeHierarchy = \
         m_mdl.getResourceTypeHierarchyFor(resType.strip("'"))
      if resourceTypeHierarchy != unknownStr:
         ## Populate the hierarchy with real resource names.
         ## At this point, the only resource name we know is
         ## the resource name of the leaf node.
         ## We must ask the iMDL for all the parent names.
         ## The MDL also has the ability to override what we think
         ## the leaf node name is now.

         ##  create the parent names one at a time
         ## from the type hierarchy
         resourceNameHierarchy = ""
         for key1 in resourceTypeHierarchy.split("/"):
            if len(key1) > 0:
               tmpResourceName = \
                  m_mdl.getResourceNameFor(str(key1)).strip("'")
               resourceNameHierarchy = resourceNameHierarchy + "/" + \
                  tmpResourceName
         resourceNameHierarchy = resourceNameHierarchy + "/" + resName.strip("'")
         resourceNameHierarchy = PTcommon.cws(resourceNameHierarchy)
         logObj.gmLogWrite(0, "Resource Name Hierarchy has been " + \
            "constructed: " + resourceNameHierarchy)
         #print "Resource Name Hierarchy has been constructed: " + \
            #resourceNameHierarchy

      logObj.gmLogWrite(0,"iMDL determined Resource Type: " + resType + \
                        " Hierarchy is " + resourceTypeHierarchy)

      resourceTypeHierarchy = resourceTypeHierarchy + "/" + resType.strip("'")
      #print "Resource Type Hierarchy has been constructed: " + \
            #resourceTypeHierarchy 
      
      if outputFormat == "PTdf":
         ptdf_mdl[resourceNameHierarchy.split('/')[1:]] = resourceTypeHierarchy.split("/")[1:]
      elif outputFormat == "PERIxml":
         peri.createPERIelement(resourceNameHierarchy, resourceTypeHierarchy)

      for fname,instance in attribFuncs:
         attributeName = m_mdl.getAttribNameFor(fname)
         #print attributeName
         if attributeName == unknownStr:
            attributeName = instance.attribDefaultName()
            logObj.gmLogWrite(0,"Attribute Name determined by object. " +\
                              attributeName)
         else:
            logObj.gmLogWrite(0,"Attribute Name determined by iMDL. " + \
                           attributeName)
         attributeName = PTcommon.cws(attributeName)
         # check if there's a resource name override in the config file
         # for this attribute function
         tmpResourceName = m_mdl.getOverrideResourceNameHierarchyFor(key)
         if tmpResourceName == unknownStr:
            tmpResourceName = resourceNameHierarchy
         else:
            tmpResourceName = PTcommon.cws(tmpResourceName)
         #print "final resourcename is %s" % tmpResourceName

         # Get the attribute value this object returns. Finally!!
         ## This is the call to run the data collection method
         attributeValue = instance.attribFunc(resName)
         if not isinstance(attributeValue, list):
            attributeValue = PTcommon.cws(str(attributeValue))
         else:
            """
               future work: support multi-item return (i.e. list, tuples,)
            """
         #print "attributeValue is %s" % (attributeValue)

         if outputFormat == "PTdf":
             # Convert to something the ptdf object can use.
             #print "resourceTypeHierarchy: %s" % resourceTypeHierarchy
            
             tmpType = resourceTypeHierarchy.strip("'") 
             tmpTypeList = tmpType.split("/")
             tmpTypeList.remove('')
             #print "Type List: " + str(tmpTypeList)
    
             #print "resourceNameHierarchy: %s" % resourceNameHierarchy
             tmpName = resourceNameHierarchy.strip("'")
             tmpNameList = tmpName.split("/")
    
             try:  #list.index() throws exception if not found
                ind = tmpNameList.index('')
                del tmpNameList[ind]
             except ValueError:
                ""
             if tmpNameList[0] == dqStr:
                #print "!!! found a multi word rnh !!!"
                tmpNameList[1] = dqStr + tmpNameList[1]
                #print tmpNameList[0] + " --- " + tmpNameList[1]
                del tmpNameList[0]

             #print "Name List: " + str(tmpNameList)

             ## create the PTDF
             ## Create the Resource Type and Name
             ptdf_mdl[tmpNameList] = tmpTypeList
             #print "ptdf_mdl" + str(tmpNameList) + " = " + str(tmpTypeList)
             ## Add the attribute name and value
             ptdf_mdl[tmpNameList][attributeName.strip("'")] = \
                repr(attributeValue).strip("'")
             #print "ptdf_mdl" + str(tmpNameList) + "[" + \
         elif outputFormat == "PERIxml":
             peri.addAttribute(resourceNameHierarchy, resourceTypeHierarchy, attributeName.strip("'").strip('"'), attributeValue.strip("'").strip('"'))





   # Write the PTDF file
   if outputFormat == "PTdf":
      oFile = open(outputFileName, "w")
      oFile.writelines(ptdf_mdl)
      oFile.close()
   elif outputFormat == "PERIxml":
      peri.writeData(outputFileName)

   logObj.gmLogWrite(3,"Host System Method")


if __name__ == "__main__":
   sys.exit (main())
