#!/usr/bin/env python

# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information.

# a python script to get resource attribute names and values for executions
# of applications.

import os, sys
from PTds import PTdataStore
from getpass import getpass

# outputs to file

def getExecutionAttributes(filename): 
   debugLevel = ptds.NO_DEBUG 
   status = ptds.connectToDB(debugLevel)
   if status == False:
      print "Unable to connect to database"
      return False
   print "Connection made"

   outfile = open (filename, "w")
   outfile.write ("Report of resource attribute names and values for executions of applications\n\n")
   #TODO: 9-20-05: generate applist automatically
   applist = ["/sppm", "/irs"]  
   for app in applist:
      outfile.write ("APPLICATION:  " + app.upper() + "\n")
      sql = "select id from resource_item where type='application' and name='" \
            + app + "'"
      #ptds.cursor.execute(sql)
      ptds.dbapi.execute (ptds.cursor, sql)
      #appId, = ptds.cursor.fetchone()    #get one id from those retrieved in above query  
      appId, = ptds.dbapi.fetchone(ptds.cursor)    #get one id from those retrieved in above query
      # get eid elements from application_has_execution where aid = appId 
      sql = "select eid from application_has_execution where aid='" + \
             str(appId) + "'"
      #ptds.cursor.execute(sql)
      ptds.dbapi.execute(ptds.cursor, sql)      
      #execList = ptds.cursor.fetchall()
      execList = ptds.dbapi.fetchall(ptds.cursor)
      
      for execution, in execList:
         sql = "select name from resource_item where id='" + str(execution) + \
              "'"
         #ptds.cursor.execute(sql)
         ptds.dbapi.execute(ptds.cursor,sql)
         #name, = ptds.cursor.fetchone()
         name, = ptds.dbapi.fetchone(ptds.cursor)
         outfile.write ("\n   EXECUTION NAME:  " + str(name,) + "\n")
        
         sql = "select name, value from resource_attribute where resource_id='"\
                + str(execution) + "'"
         #ptds.cursor.execute(sql)
         ptds.dbapi.execute(ptds.cursor, sql)
         #nameValueList = ptds.cursor.fetchall()
         nameValueList = ptds.dbapi.fetchall(ptds.cursor)
         outfile.write ("      RESOURCE ATTRIBUTES:" + "\n")
         for (name, value) in nameValueList:
            outfile.write ("         name:  " + name + "\n")
            outfile.write ("         value: " + value + "\n\n")

   ptds.closeDB()
   return True


ptds = PTdataStore()
filename = raw_input("Enter a name to call the report: ")
if filename == "":
   print "The report must have a valid name"
   sys.exit()
getExecutionAttributes(filename)

