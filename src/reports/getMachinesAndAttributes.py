#!/usr/bin/env python

# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information. 

# a python script to get machine names and associated attributes

import os, sys
from PTds import PTdataStore
from getpass import getpass


def getMachinesAndAttributes(filename):
   outfile = open (filename, "w")
   outfile.write ("Report of machine names and associated attributes\n\n")
   debugLevel = ptds.NO_DEBUG 
   status = ptds.connectToDB(debugLevel)
   if status == False:
      print "Unable to connect to database"
      return False
   print "Connection made"

   #get list of resource ids 
   sql = "select id from resource_item where type like '%machine%' order by id"
   #ptds.cursor.execute(sql)
   ptds.dbapi.execute(ptds.cursor,sql) 
   #resourceList = ptds.cursor.fetchall()
   resourceList = ptds.dbapi.fetchall(ptds.cursor)
   for rid, in resourceList:
      sql = "select name from resource_item where id = '" + str(rid) + "'"
      #ptds.cursor.execute(sql)
      ptds.dbapi.execute(ptds.cursor, sql)
      #rname, = ptds.cursor.fetchone()
      rname, = ptds.dbapi.fetchone(ptds.cursor)
      sql = "select type from resource_item where id = '" + str(rid) + "'"
      #ptds.cursor.execute(sql)
      ptds.dbapi.execute(ptds.cursor,sql)
      #type, = ptds.cursor.fetchone()
      type, = ptds.dbapi.fetchone(ptds.cursor)
      outfile.write ("ID:    " + str(rid) + "\n")
      outfile.write ("NAME:  " + rname + "\n")
      outfile.write ("TYPE:  " + type + "\n")

      sql = "select name,value from resource_attribute where resource_id = '" \
            + str(rid) + "'"
      #ptds.cursor.execute(sql)
      ptds.dbapi.execute(ptds.cursor, sql)
      #nameValueList = ptds.cursor.fetchall()
      nameValueList = ptds.dbapi.fetchall(ptds.cursor)
      outfile.write ("RESOURCE ATTRIBUTES:\n")
      for (name, value) in nameValueList:
         outfile.write ("       name:  " + name + "\n")
         outfile.write ("       value: " + value + "\n\n")
   outfile.close()
   ptds.closeDB()
   return True

ptds = PTdataStore()
filename = raw_input("Enter a name to call the report: ")
if filename == "":
   print "The report must have a valid name"
   sys.exit() 
getMachinesAndAttributes(filename)

