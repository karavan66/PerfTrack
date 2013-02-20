# ptPyDBAPI.py
# Contains class definition for ptPyDBAPI

import logging;
import pickle
import readline
import sys, os, string, re
from getpass import getpass

class PTpyDBAPI:
   """ methods for interfacing with python DB API for specific interfaces
       supported by PerfTrack
   """
   def __init__(self):
      self.pyDBmap = {"PG_PYGRESQL":"psycopg2",
                      "ORA_CXORACLE":"cx_Oracle",
                      "MYSQL":"MySQLdb"}

      self.dbenv = self.__getDBenv()
      self.dbMod = self.importDBapi()
      
      # Constants*
      self.paramstyle = self.dbMod.paramstyle
      
      # user defined exceptions
      self.dbapiError = "PTpyDBAPI error"
         
   
   # Private Methods
   def __getDBenv (self):
      if (os.environ.get("PTDB")):
         db = os.environ.get("PTDB")
         if (db in self.pyDBmap):
            self.dbEnv = db
         else:
            raise Exception("PTDB value \"%s\" is not one of the possible database types\n%s" % 
                            (os.environ.get("PTDB"), self.pyDBmap.keys()))
      else:
         raise Exception("PTDB Environment Variable not set")

      return self.dbEnv
   
   # Method: __getConnectionParameters
   # Input:  None
   # Output: Dictionary of parameters for connection
   #
   def __getConnParams (self):
      if self.dbenv == "PG_PYGRESQL":
         if os.environ.get ("DBPASS"):
            data = os.environ.get ("DBPASS")
            splitted = data.split(",")
            dbname = splitted[0]
            dbhost = splitted[1]
            dbuser = splitted[2]
            dbpwd = splitted[3]
            dbdsn = None
         else:
            dbname = raw_input("Please enter the name of the database: ")
            dbhost = raw_input("Please enter the hostname for the database: ")
            dbuser = raw_input("Please enter your database user name: ")
            dbpwd = getpass("Please enter your database password: ")
            dbdsn = None

         paramDict = {"DSN":None,
                      "USER":dbuser,
                      "PASSWORD":dbpwd,
                      "HOST":dbhost,
                      "DATABASE":dbname }
         
         return paramDict
      elif self.dbenv == "ORA_CXORACLE":
         dbdsn = raw_input("Please enter the TNS entry for the database: ")
         dbuser = raw_input("Please enter your database user name: ")
         dbpwd = getpass("Please enter your database password: ")
         dbmode = None
         dbhandle = None
         dbpool = None
         dbthread = None
         dbphase = None
         paramDict = {"DSN":dbdsn,
                      "USER":dbuser,
                      "PASSWORD":dbpwd,
                      "MODE":dbmode,
                      "HANDLE":dbhandle,
                      "POOL":dbpool,
                      "THREAD":dbthread,
                      "TWOPHASE":dbphase }
         return paramDict
 
      elif self.dbenv == "MYSQL":
         dbname = raw_input("Please enter the name of the database: ")
         dbhost = raw_input("Please enter the hostname for the database: ")
         dbuser = raw_input("Please enter your database user name: ")
         dbpwd = getpass("Please enter your database password: ")
         dbdsn = None
         paramDict = {"DSN":None,
                      "USER":dbuser,
                      "PASSWORD":dbpwd,
                      "HOST":dbhost,
                      "DATABASE":dbname }
         
         return paramDict
   
      else:
         raise Exception("Unknown Database Type")

   # Method: __opToParamFormat
   # Description: Converts sql operation with parameter variables
   #              into correct format expected by the Python db interface
   #              module.
   # Input: string - sql statement with the parameter variables marked with ':'
   #                 before each var.  This is like the named format.
   #        list   - list of variable names. Must match the vars provided in
   #                 sql parameter.
   # Output: string that is in correct format and can be used as the
   #         the sql operation argument for Python db interface methods
   #         like execute and executemany.  If there is an error, or the format
   #         is not supported, None is returned
   # Example:
   #   SQL statement: "insert into teachers (name, grade, classsize)
   #                   values (:tname, :tgrade, :tsize)"
   #   The method will return a string according to the format supported
   #   by the Python DB interface module:
   #   Format   String
   #   qmark    "insert into teachers (name, grade, classsize)
   #             values (?, ?, ?)"
   #   numeric  "insert into teachers (name, grade, classsize)
   #             values (:1, :2, :3)"
   #   named    "insert into teachers (name, grade, classsize)
   #             values (:tname, :tgrade, :tsize)"
   #   format   "insert into teachers (name, grade, classsize)
   #             values (%s, %s, %s)"
   #   pyformat "insert into teachers (name, grade, classsize)
   #             values (%(tname)s, %(tgrade)s, %(tsize)s)"
   #
   #   NOTE: only does named, pyformat, and format right now
   def __opToParamFormat (self, sqlOpToConvert, paramList):
     if self.paramstyle == "named":
          return sqlOpToConvert
     elif self.paramstyle == "pyformat":
        slist = []
        slist.append(sqlOpToConvert)
        for x in paramList:
           tmp = slist[0]
           count = tmp.count(":"+x)
           if count < 1:
              return None
           else:
              newstr = tmp.replace(":"+x, "%("+x+")s")
              slist[0] = newstr
        convertedOp = slist[0]
        return convertedOp
     elif self.paramstyle == "format":
        formatRe = re.compile(r"[^,]+")
        val_index = sqlOpToConvert.index("values")
        convertedOp = sqlOpToConvert[:val_index] + "values (" + formatRe.sub(" %s", sqlOpToConvert[val_index:]) + ")"
        return convertedOp
     else:
        return None
   
   # Public Methods
            
   # Method: __orderParams
   # Description:  Orders the parameters for an SQL query into the same order
   #               as found in SQL query text
   # Input: string - sql statement with the parameter variables marked with ':'
   #                 before each var.  This is like the named format.
   #        dictionary - A dictionary of values for the parameter variables
   #                     in the SQL statement.  The keys must match the
   #                     variable names in the SQL statement.
   # Output: A list of strings ordered to match the ordering of parameter
   #         variables found in the SQL statement.
   # Example:
   # SQL statement: "insert into resource_item
   #                (id, focus_framework_id, type, parent_id, name, ff)
   #                values (:rid, :fid, :ftype, :par_id, :fname, :ffw)"
   # dictionary: {"rid":1, 
   #              "fid":3, 
   #              "ftype":"some_type", 
   #              "par_id":10, 
   #              "fname":"full_name", 
   #              "ffw":"focus_frame"}
   # Would return the list:
   # [1, 3, "some_type", 10, "full_name", "focus_frame"]
   def orderParams(self, sqlStatement, paramDict):
      
      # Get the list of parameters
      reParam = re.compile(r":[a-zA-Z_\-]+")
      paramList = reParam.findall(sqlStatement)
      
      # check that the there are the same number of sql parameters as dict keys
      if len(paramList) != len(paramDict):
         return None

      # strip the ':' out of each string in paramList
      for i in xrange(len(paramList)):
         paramList[i] = paramList[i][1:]
      
      list = []
      for i in paramList:
         try:
            value = paramDict[i]
         except KeyError:
            return None
            
         list.append(value)
         
      return list

   def importDBapi(self):
      name = self.pyDBmap[self.dbenv]
      self.moduleName = __import__(name)
      return self.moduleName
   
   # -- Connection Object and Methods
   # Method: connect
   # Input:  connect accepts the following optional arguments
   #         pt_db - name of database to connect to 
   #         pt_dsn - data source name to use
   #         pt_host - hostname of the database
   #         pt_pwd - user's password
   #         pt_user - username
   #         If any of the optional parameters (except dsn) are None then
   #         the user will be prompted for connection parameters.
   # Input:  dictionary of db connection parameters see readme
   #         for specific key info
   # Output: On success connection to db is established and
   #         Connection object is returned to caller. On failure
   #         Exception raised, caller should catch this.
   #
   # 20090228 smithm: extended connect method to take optional arguments
   #				  for connecting to a database.  These coincide with
   #				  with DBAPI 2.0
   def connect (self, pt_db=None, pt_dsn=None, pt_host=None, pt_pwd=None,
				pt_user=None):
      if pt_db == None or pt_host == None or pt_pwd == None or pt_user == None:
         paramDict = self.__getConnParams()
         # The PyGreSQL connect method will accept a single argument as a
         # connection string of format 'host:database:user:password:opt:tty'.
         # This is supplied as the DSN parameter. Or it will accept keyword
         # parameters, all of which are optional.  The PerfTrack interface
         # supports the keyword method.
         if self.dbenv == "PG_PYGRESQL":
            self.connection = self.dbMod.connect(dsn=paramDict["DSN"],
                                                 host=paramDict["HOST"],
                                                 database=paramDict["DATABASE"],
                                                 user=paramDict["USER"],
                                                 password=paramDict["PASSWORD"])      	
         # The cx_Oracle connect method will accept a single argument as a
         # connection string of the format accepted by SQLPLUS.  Generally, this
         # is user/password@dsn'.  The dsn is the TNS entry and looks like a host
         # name.  The cx_Oracle connect method will also accept optional
         # arguments as keyword parameters.  The Perftrack interface supports
         # the keyword method.
         elif self.dbenv == "ORA_CXORACLE":
            self.connection = self.dbMod.connect(user=paramDict["USER"],
                                                 password=paramDict["PASSWORD"],
                                                 dsn=paramDict["DSN"])
            
         # MySQLdb accepts the following name parameters; host, db, user, and passwd.
         elif self.dbenv == "MYSQL":
            self.connection = self.dbMod.connect(host=paramDict["HOST"],
                                                 db=paramDict["DATABASE"],
                                                 user=paramDict["USER"],
                                                 passwd=paramDict["PASSWORD"])
         else:
            # all of the optional parameters (except dsn) have been entered
            # so use them
            self.connection = self.dbMod.connect(database = pt_db, host = pt_host,
                                                 password = pt_pwd, user = pt_user,
                                                 dsn = pt_dsn)
      
      return self.connection
      
   # Method: closeCnx
   # Description: close database connection
   # Input:  Connection object
   # Output: nothing returned, connection to database is closed
   def closeCnx (self, cnx):
      cnx.close()
   
   # Method: commit
   # Description: commit pending transaction to database
   # Input:  Connection object
   # Output: nothing returned
   def commit (self, cnx):
      cnx.commit()
   
   # Method: rollback
   # Description: rollback to start of pennding transaction
   # Input:  Connection object
   # Output: nothing returned
   def rollback (self, cnx):
      cnx.rollback()
   
   # Method: getCursor
   # Description:  get a new cursor object using connection
   # Input:  Connection object
   # Output: Cursor object returned
   def getCursor(self, cnxObject):
      self.cursor = cnxObject.cursor()
      return self.cursor
   
   # -- Cursor Object and Methods --
   
   # Method: closeCrs
   # Description: close cursor object
   # Input:  Cursor object
   # Output: Cursor is closed and no longer accessible
   def closeCrs(self, crs):
      crs.close()
   
   # Method: execute
   # Description:
   # Input: Cursor object,
   #        string -- sql operation
   #        dictionary -- optional. Keys are names supplied in the
   #                      operation with correct parameter marker
   #                      format. Values are the values that the
   #                      Python db interface module will bind to
   #                      the variables in the operation.
   #        NOTE: If the dictionary is supplied, it is expected that the
   #              operation is passed in using 'named' format for the
   #              variables . This method will convert 'named' format into the
   #              correct format.
   # Output: not defined by DB API 2.0
   # not completely finished. only does simple ops right now
   def execute (self, crs, operation, parameters = None):
#      f = open("pickle.log", "a")
      #f = None
#      sql = operation
#      if (parameters != None):
#         sql = self.__opToParamFormat(operation, parameters.keys())
         
# f.write("%s" % pickle.dumps((sql, parameters)))

      if parameters == None:
         crs.execute (operation)
      else:
         plist = parameters.keys()
         sql = self.__opToParamFormat(operation, plist)
         if sql != None:
            if self.dbenv == "MYSQL":
               crs.execute (sql, self.orderParams(operation, parameters))
            else:
               crs.execute (sql, parameters)
         else:
            raise self.dbapiError
      f = open("sql.log", "a")
      f.write("%s :: %s :: %s\n" % (operation.strip(), parameters, crs.rowcount > 0))
   
   # Method: executemany
   # Descrtiption: Prepare a database operation and then execute it
   #         against all parameter mappings found in
   #         sequenceOfParameters
   # Input:  Cursor Object
   #         string - sql operation, where variables that require
   #             mapping must be provided in 'named' format.
   #         list of dictionaries - The key names for all the
   #             dictionaries in the list must be the same.  These
   #             names are used to map the values provided in the
   #             dictionary to the variables provided in the sql
   #             operation.
   #
   # Output: Return values are not defined by DB API 2.0
   def executemany (self, crs, operation, seqOfParameters):
      try:
         plist = seqOfParameters[0].keys()
      except:
         raise self.dbapiError
      sql = self.__opToParamFormat(operation, plist)
      if sql != None:
         crs.executemany(sql, seqOfParameters)
      else:
         raise self.dbapiError
   
   # Method: fetchone
   # Descrtiption: fetch next row of a query and return a single sequence
   # Input: Cursor object
   # Output: Single sequence if there is still data available; None if no
   #         data left; an Error exception is raised by the specific DB API
   #         implementation if the previous call to executeXXX() did not
   #         produce a result set
   def fetchone (self, crs):
      #print "ptPyDBAPI: fetchone"
      sequence = crs.fetchone()
      return sequence

   # Method: fetchmany
   # Description: Fetch the next set of rows of a query result, returning
   #         a sequence of sequences (list of tuples). An empty sequence
   #         is returned when no more rows are available
   # Input:  Cursor Object
   #         size - Optional, used to indicate number of rows to fetch
   #                per call.  If size is not given, the cursor's
   #                arraysize attribute will be used.
   # Output: List of rows; An exception is raised if previous executeXXX()
   #         did not produce a result set. The call may return fewer rows
   #         than what is specified by size when there are fewer rows
   #         available.
   def fetchmany (self, crs, size=None):
      if size == None:
         size = crs.arraysize
      seqList = crs.fetchmany(size)
      return seqList
   
   # Method: fetchall
   # Description: Fetch all (remaining) rows of a query result, returning
   #         them as a sequence of sequences (list of tuples)
   # Input:  Cursor object
   # Output: A list on success; if previous call to executeXXX() did not
   #         produce a result set, an exception is raised by the Python
   #         interface module
   def fetchall (self, crs):
      seqList = crs.fetchall()
      return seqList
   
   
   # Method: getTables
   # Description: Returns a list of all the tables in the database
   # Input:  Cursor object
   # Output: A list on success; if previous call to executeXXX() did not
   #         produce a result set, an exception is raised by the Python
   #         interface module
   def getTables(self, crs):
      if self.dbenv == "PG_PYGRESQL":
         sql = "SELECT tablename FROM pg_tables where tablename not like 'pg_%%'"
      elif self.dbenv == "ORA_CXORACLE":
         sql = "select table_name from tabs"
      elif self.dbenv == "MYSQL":
         sql = "show tables"
      else:
         raise Exception("Unknown Database Type")

      crs.execute(sql)
      tables = crs.fetchall()
      return [t.upper() for t, in tables]
