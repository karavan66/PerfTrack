# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information.

# PTds.py
# Contains the class definition for PTdataStore

#import sys, cx_Oracle, string, re 
#import sys, pgdb, string, re

import sys, string, re, array
from ptPyDBAPI import *             #class to support Python DB API 2.0
from Resource import Resource
from ResourceIndex import ResourceIndex

class PTdataStore:
    """ Access methods for storing, querying, and retrieving PerfTrack data from a database.
    RDBMs/packages supported:  Postgresql/PyGreSql(DB API 2.0); Oracle/cx_oracle.
    """
    # debug levels
    NO_DEBUG = 0 # no debug turned on
    NO_COMMIT = 1 # will not commit transactions, sequence numbers will change
    NO_WRITE = 5  # will only read from db, no sequence numbers will change
    NO_CONNECT = 10 # will not connect to the database

    def __init__(self):
        self.cursor = None          # object for using db 
        self.connection = None      # object for db connection
        self.debug = self.NO_DEBUG  
        self.dbapi = PTpyDBAPI()    # instantiate PTpyDBAPI class 
        self.contextCache = {}      # cache contexts for easy lookup
        self.tempTablesCreated = False     # keep a record of whether we have 
                                           # created the temporary tables for
                                           # retrieving performance results

        self.resDelim = "|"

    def connectToDB(self, debugFlag, ctb_db = None, ctb_dsn = None,
                    ctb_host = None, ctb_pwd = None, ctb_user = None):
        """ Connect to a database, using a Python interface module.
			Input:
				debugFlag - flag to use debug mode 
				The following optional arguments are accepted:
				ctb_db - name of database to connect to 
				ctb_dsn - data source name to use
				ctb_host - hostname of the database
				ctb_pwd - user's password
				ctb_user - username
			Output:
				True - returned on success and a connection and cursor
				       objects have been instantiated.
				False - failure; no objects are instantiated.
        """

        if debugFlag:     
            print "debug requested"
            self.debug = debugFlag
        if debugFlag < self.NO_CONNECT:
            try:
                self.connection = self.dbapi.connect(pt_db = ctb_db,
                                                     pt_dsn = ctb_dsn,
                                                     pt_host = ctb_host,
                                                     pt_pwd = ctb_pwd,
                                                     pt_user = ctb_user)
                self.cursor = self.dbapi.getCursor(self.connection)
            except:
                print "ERROR: Cannot connect to database."
                return False
            return True
        return False 

    def closeDB(self):
        if self.debug == self.NO_CONNECT:
            return
        else:
            #self.cursor.close()
            self.dbapi.closeCrs(self.cursor)
            #self.connection.close()
            self.dbapi.closeCnx(self.connection)

    def abortTransaction(self):
        if self.debug == self.NO_CONNECT:
            return
        else:
            #self.connection.rollback()
            self.dbapi.rollback(self.connection)

    def commitTransaction(self):
        if self.debug >= self.NO_COMMIT:
            return
        else:
            #self.connection.commit()
            self.dbapi.commit(self.connection) 

    # -- resource --

    # May be Deprecated 
    def getResourceId(self, type, Name, parent_id):
        """ Finds the id for resource of type "type" and name "Name"

        Note:  parent_id is no longer used, but remains in the interface for
        backwards compatibility.
        Returns ID if found, 0 if not.
        """
        query = "select resource_item.id from resource_item "
        query += "where upper(resource_item.name)=\'" + Name.upper() + "\' "
        query += " and resource_item.type=\'" + type + "\' "

        if self.debug:
            print query
        if self.debug >= self.NO_CONNECT:
            return
        try:
            #self.cursor.execute(query)
            self.dbapi.execute(self.cursor, query)
            #temp = self.cursor.fetchone()
            temp = self.dbapi.fetchone(self.cursor)
            if (temp != None):
                res_id = temp[0]
            else: 
                res_id = 0
        except:
            print "Could not execute query in getResourceId: " + query
            raise
        return res_id

    def createResource(self, focus_frame_id, parent_id, fullName, fullType):
        """ Creates a new entry in the resource_item table.

        Returns new resource id
        """
        if self.debug >= self.NO_WRITE:
            return 0
        if parent_id == 0:
            parent_id = None
        try:
            # get unique id
            if self.dbapi.dbenv == "ORA_CXORACLE":
                self.dbapi.execute(self.cursor, "select seq_resource_item.nextval from dual")

            if self.dbapi.dbenv == "PG_PYGRESQL":
                self.dbapi.execute (self.cursor, "select nextval('seq_resource_item')")
				
			# smithm 2008-7-10
			# Added clause for MySQL
            if self.dbapi.dbenv == "MYSQL":
                self.dbapi.execute (self.cursor, "UPDATE sequence SET prev_value = @ri_value := prev_value + 1 where name = 'seq_resource_item'")
                self.dbapi.execute (self.cursor, "SELECT @ri_value")
				
            #res_id, = self.cursor.fetchone()
            res_id, = self.dbapi.fetchone(self.cursor)
            res_id = self.__convertToInt(res_id)

            # get focus framework id
            if (focus_frame_id):
                ff = 1
            else:
                ff = 0
            if focus_frame_id == None:
                focus_frame_id = 0
            #06-30-05 - comment out next section. cx_Oracle format
            #self.cursor.execute("insert into resource_item \
            #        (id, focus_framework_id, type, parent_id, name, ff) \
            #        values (:id, :focus_framework_id, \
            #        :type, :parent_id, :name, :ff)", \
            #        id = res_id, focus_framework_id = focus_frame_id, \
            #        type = fullType, parent_id = parent_id, name = fullName, ff = ff)

            #06-30-05 - create dictionary resource_params and pass it to execute as
            #           second parameter
            #08-23-05 -comment out pygres format
            #resource_params = {"rid":res_id, "fid":focus_frame_id, "ftype":fullType, \
            #       "par_id":parent_id, "fname":fullName, "ffw":ff}
            #self.cursor.execute("insert into resource_item \
            #       (id, focus_framework_id, type, parent_id, name, ff) \
            #       values (%(rid)s, %(fid)s, %(ftype)s, %(par_id)s, %(fname)s, %(ffw)s)", \
            #       resource_params)

            #08-24-05 - create dictionary. create named format sql with variables that
            #    are the keys from the dictionary. Pass the sql and dictionary to the
            #    dbapi.execute method
            #           correct format:
            resource_params = {"rid":res_id, 
                               "fid":focus_frame_id, 
                               "ftype":fullType, 
                               "par_id":parent_id, 
                               "fname":fullName, 
                               "ffw":ff}

            sql = "insert into resource_item " +\
                  "(id, focus_framework_id, type, parent_id, name, ff) " +\
                  "values (:rid, :fid, :ftype, :par_id, :fname, :ffw)"
            self.dbapi.execute(self.cursor, sql, resource_params)
        except:
            raise
        # update table resource_has_descendant if needed
        #  we only need to do the update if an ancestor of the new resource is in the table
        ancestors = self.getAncestors(res_id)
        for aid in ancestors:
            sql = "select rid from resource_has_descendant where rid = '" + str(aid) + "'"
            try:
                #self.cursor.execute (sql)
                self.dbapi.execute(self.cursor, sql)
                #thisid = self.cursor.fetchone()
                thisid = self.dbapi.fetchone(self.cursor) 
            except:
                raise
            if thisid != None:
                try:
                    sql = "insert into resource_has_descendant (rid,did) values " +\
                          "(" + str(aid) + "," + str(res_id) + ")"
                    #self.cursor.execute(sql)
                    self.dbapi.execute(self.cursor, sql)
                except:
                    raise

        return res_id

    # May be Deprecated
    def findOrCreateResource(self, parent_id, type, name, focus_frame_name,
                         associateList = []):
        """ Returns id of newly created resource, or existing resource.

        Check for existing resource uses parent_id, type, name,
        focus_frame_name, and a list of associated resources (from
        resource_constraint table). If it finds it, the resource_id is
        returned. Otherwise, a new resource_item entry is made for the
        resource and new entries are made in the resource_constraint table,
        using associateList.
        """

        if self.debug >= self.NO_CONNECT:
           return 0
        # look for it
        if parent_id:
            parent_name = self.getResourceName(parent_id)
            full_name = parent_name + self.resDelim + name
        else:
            full_name = name
        id = self.getResourceId(type, full_name, parent_id)
        # if found, make sure it's the right one by checking constraints
        if id:
            if associateList:
                if self.lookupConstraints(id, associateList):
                    return id
            else:
                # if we don't care about the constraints, we can just return
                # the resource id
                return id
        if self.debug >= self.NO_WRITE:
           return id
        # if not found or constraints didn't match, make new one
        if focus_frame_name != None and focus_frame_name != "":
            focus_frame_id = self.getFocusFrameId(focus_frame_name)
        else:
            focus_frame_id= None
        id = self.createResource(focus_frame_id, parent_id, full_name, type)
        self.enterResourceConstraints(id, associateList)
        return id
 
    def findResourceByName (self, fullName):
        """Search for resource by full name
        Attributes are not checked/matched.
        Returns rid or 0 if not found.
        """
        #print "findResourceByName: " + fullName
        query = "select resource_item.id from resource_item where "
        query += "name = '"
        query += fullName
        query += "'"
        #print query
        if self.debug >= self.NO_CONNECT:
           return 0
        try:
            #self.cursor.execute(query)
            self.dbapi.execute(self.cursor, query)
            #temp = self.cursor.fetchall()
            temp = self.dbapi.fetchall(self.cursor)
        except:
            print "Could not execute query in findResourceByName: " + query
            raise
        else:
            if len(temp) == 0:
                # no matches found
                return 0
            else:
                retid, = temp[0]
                #print "findResourceByShortName: returning %d" % retid
                return retid

    # May be Deprecated 
    def findResource(self, parent_id, type, name, attributeList=[]):
        "Search for resource by full name"

        if self.debug >= self.NO_CONNECT:
            return None
        if parent_id:
            parent_name = self.getResourceName(parent_id)
            full_name = parent_name + self.resDelim + name
        else:
            full_name = name
        id = self.getResourceId(type, full_name, parent_id)
        if id:
            if self.debug:
                print "id: " + str(id) + "for " + full_name
            if attributeList:
                if self.lookupAttributes(id, attributeList):
                    return id
                else:
                    # attributes didn't match
                    return None
            else:  # else we don't care about the attributes
                return id
        else:  # not found
            return None

    def findResourceByShortNameAndType(self, type, shortname):
        """ Attempts to find a resource based on its short name and its
        type. This is useful in situations where information about
        parent resources is unknown.
        Returns: The resource id if the resource is located.
                 None if no resource matches.
                 -1 if more than one resource matches.
        """
        query = "select resource_item.id from resource_item where "
        query += "upper(resource_item.name) like \'%"
        query += str(shortname).upper()
        query += "\' and resource_item.type=\'"
        query += str(type) + "\' "
   
        if self.debug >= self.NO_CONNECT:
           return None
        try:
            #self.cursor.execute(query)
            self.dbapi.execute(self.cursor, query)
            #temp = self.cursor.fetchall()
            temp = self.dbapi.fetchall(self.cursor)
            if len(temp) == 0:
                # no matches found
                return None
            if len(temp) > 1:
                # multiple matches found
                return -1
            else:
                retid, = temp[0]
                return retid
        except:
            print "Could not execute query in findResourceByShortNameAndType: " + query
        raise

    def findResourceByShortNameAndShortType(self, shorttype, shortname):
        """ Attempts to find a resource based on its short name and its
        short type. This is useful in situations where information about
        parent resources is unknown.
        Returns: The resource id if the resource is located.
                 None if no resource matches.
                 -1 if more than one resource matches.
        """
        query = "select resource_item.id from resource_item where "
        query += "upper(resource_item.name) like \'%"
        query += str(shortname).upper()
        query += "\' and resource_item.type like \'%"
        query += str(shorttype) + "\' "

        if self.debug >= self.NO_CONNECT:
           return None
        try:
            self.dbapi.execute(self.cursor, query)
            temp = self.dbapi.fetchall(self.cursor)
            if len(temp) == 0:
                # no matches found
                return None
            if len(temp) > 1:
                # multiple matches found
                return -1
            else:
                retid, = temp[0]
                return retid
        except:
            print "Could not execute query in findResourceByShortNameAndShortType: " + query
        raise

    def getResourceName(self, id):
        """ Takes a resource id and returns the resource's name.
        If id is None, the empty string is returned.
        """
        if self.debug >= self.NO_CONNECT:
           return ""
        try:
            if id:
                sql = "select name from resource_item where id='" + str(id) + "'"
                #self.cursor.execute(sql)
                self.dbapi.execute(self.cursor, sql)
                #name, = self.cursor.fetchone()
                name, = self.dbapi.fetchone(self.cursor)
            else:
                #print "debug: returning empty string"
                name = ""
        except:
            print "debug: raising exception"
            raise
        return name

    def getResourceType(self, id):
        """ Takes a resource id and returns the resource's type.

        If id is None, the empty string is returned.
        """
        if self.debug >= self.NO_CONNECT:
            return ""
        type = ""
        try:
            if id:
                sql = "select type from resource_item where id='" + str(id) + "'"
                self.dbapi.execute(self.cursor, sql)
                type, = self.dbapi.fetchone(self.cursor)
        except:
            raise
        return type

    # -- constraints --
    # May be Deprecated
    def lookupConstraints(self, from_resource, toResourceList):
        """ For each resource in toResourceList, lookupConstraint is called
        to see if there is an entry in the resource_constraint table for
        from_resource and that resource. If all have entries, this
        function returns True. False is returned otherwise.
        """
        if self.debug >= self.NO_CONNECT:
           return False
        for res in toResourceList:
            if not self.lookupConstraint(from_resource, res):
                return False
        return True

    # May be Deprecated
    def lookupConstraint(self, from_resource, to_resource):
        """ Queries to see if a constraint exists in the resource_constraint
        table between from_resource and to_resource. Returns True if a
        constraint exists and False if not.
        """

        if self.debug >= self.NO_CONNECT:
           return False
        sql = "select count(*) from resource_constraint where from_resource='" + \
              str(from_resource) + "' and to_resource='" + str(to_resource) + "'"

        #self.cursor.execute(sql)
        self.dbapi.execute(self.cursor, sql)
        #number = self.cursor.fetchone()
        number = self.dbapi.fetchone(self.cursor)
        if number > 0 :
            return True
        else:
            return False

    # --Attributes--
    # May be Deprecated
    def lookupAttributes(self, resource, attrList):
       """ For each attribute in attrList, lookupAttribute is called
       to see if there is an entry in the resource_attribute table for
       resource and that attribute/value pair. If all have entries, this
       function returns True. False is returned otherwise.
       """
       if self.debug >= self.NO_CONNECT:
          return False
       for a in attrList:
           #if not self.lookupAttribute(resource, a['name'], a['value']):
           if not self.lookupAttribute(resource, a[0], a[1]):
               return False
       return True

    # May be Deprecated
    def lookupAttribute(self, resource, attr, value, type="string"):
       """ Queries to see if an attr/value pair exists in the resource_attribute_
        table for resource. Returns True if it exists and False if not.
        """
       if self.debug >= self.NO_CONNECT:
          return False
       sql = "select count(*) from resource_attribute where resource_id='" + \
          str(resource) + "' and name='" + str(attr) + "' and value='" + \
          str(value) + "' and attr_type='" + str(type) + "'"
       #self.cursor.execute(sql)
       self.dbapi.execute(self.cursor, sql)
       #number, = self.cursor.fetchone()
       number, = self.dbapi.fetchone(self.cursor)
       if number > 0:
           return True
       else:
           return False


    def createPerformanceResult(self,  metric_id,value,start_time,\
                           end_time, units,  foci, result_id, label=None, combined=0):
        """Creates an entry in the performance_result table

        """
        if self.debug >= self.NO_WRITE:
            return 0
        #print "perfTool: %s metric: %s, value: %s start: %s end: %s units %s, app: %s, exec: %s, focus: %s" %(perf_tool_id, metric_id, value, start_time, end_time, units, application_id, execution_id, focus_id)
        try:
            for f,t in foci:
                if t == "primary":
                    focus_id = f
                    break
            if self.dbapi.dbenv == "ORA_CXORACLE":
                self.dbapi.execute(self.cursor, "select seq_performance_result.nextval from dual")

            if self.dbapi.dbenv == "PG_PYGRESQL":
                self.dbapi.execute (self.cursor, "select nextval('seq_performance_result')")
            
            # smithm 2008-7-11
			# Added clause for MySQL
            if self.dbapi.dbenv == "MYSQL":
                self.dbapi.execute (self.cursor, "UPDATE sequence SET prev_value = @pr_value := prev_value + 1 where name = 'seq_performance_result'")
                self.dbapi.execute (self.cursor, "SELECT @pr_value")
            
            perfRes_id, = self.cursor.fetchone()
            perfRes_id = self.__convertToInt(perfRes_id)
            
            #oracle/cx_Oracle specific way
            #self.cursor.execute("insert into performance_result\
            #            (id, performance_tool_id, metric_id,\
            #            value, start_time, end_time, units, \
            #            application_id, execution_id, focus_id) values \
            #            (:id, :performance_tool_id, :metric_id, :value, \
            #            :start_time, :end_time, :units, :application_id, \
            #            :execution_id, :focus_id)", id = perfRes_id, \
            #            performance_tool_id = perf_tool_id, \
            #            metric_id = metric_id, value = float(value),\
            #            start_time = start_time, end_time = end_time, \
            #            units = units, application_id = application_id, \
            #            execution_id = execution_id, focus_id = focus_id)

            #postgres/pygresql specific way
            #perfResParams = {"rid":perfRes_id, "ptid":perf_tool_id, \
            #                 "mid":metric_id, "val":float(value), \
            #                 "stime":start_time, "etime":end_time, \
            #                 "units":units, "aid":application_id, \
            #                 "eid":execution_id, "fid":focus_id}
            #self.cursor.execute("insert into performance_result \
            #            (id, performance_tool_id, metric_id, \
            #            value, start_time, end_time, units, \
            #            application_id, execution_id, focus_id) values \
            #            (%(rid)s, %(ptid)s, %(mid)s, %(val)s, %(stime)s, \
            #             %(etime)s, %(units)s, %(aid)s, %(eid)s, %(fid)s)",\
            #            perfResParams)

            #09-01-05 - create dictionary. create named format sql with variables that
            #    are the keys from the dictionary. Pass the sql and dictionary to the
            #    dbapi.execute method
            #           correct format:

            perfResParams = {"rid":perfRes_id, 
                             "mid":metric_id, 
                             "val":float(value), 
                             "stime":start_time, 
                             "etime":end_time, 
                             "units":units, 
                             "fid":focus_id,
                             "rsid":result_id,
                             "lbl":label,
                             "comb":combined}
            sql = "insert into performance_result " +\
                  "(id, metric_id, " +\
                  "value, start_time, end_time, units, " +\
                  "focus_id, label, combined, complex_result_id) " +\
                  "values (:rid, :mid, :val, :stime, " +\
                  ":etime, :units, :fid, :lbl, :comb, :rsid)"


            self.dbapi.execute(self.cursor, sql, perfResParams)


            for fid,ftype in foci:
                #Oracle/cx_Oracle specific 
                #self.cursor.execute("insert into performance_result_has_focus\
                #          (performance_result_id, focus_id, focus_type) values \
                #          (:performance_result_id, :focus_id, :focus_type)", \
                #          performance_result_id = perfRes_id, \
                #          focus_id = fid, focus_type = ftype)

                #Postgres/pyGresql specific
                #perfFocusParams = {"prid":perfRes_id, "fcid":fid, "fctype":ftype}
                #self.cursor.execute("insert into performance_result_has_focus\
                #          (performance_result_id, focus_id, focus_type) values \
                #          (%(prid)s, %(fcid)s, %(fctype)s)", perfFocusParams)

                #09-01-05 -create dictionary. create named format sql with variables that
                #    are the keys from the dictionary. Pass the sql and dictionary to the
                #    dbapi.execute method
                perfFocusParams = {"prid":perfRes_id, 
                                   "fcid":fid, 
                                   "fctype":ftype}
                sql = "insert into performance_result_has_focus " +\
                      "(performance_result_id, focus_id, focus_type) " +\
                      "values(:prid, :fcid, :fctype)"
                self.dbapi.execute(self.cursor, sql, perfFocusParams)                
        except:
            raise

        return perfRes_id
    
    def createComplexResult(self, metric_id, foci, value_array, start_times, end_times, units):                        
        """Creates an entry in the complex_perf_result table
	and inserts a row in performace_result table 1 per complex_result_id"""                 
        
        if self.debug >= self.NO_WRITE:
            return 0
        try:
            for f,t in foci:
                if t == "primary":
                    focus_id = f
                    break
            
            if self.dbapi.dbenv == "ORA_CXORACLE":
                self.dbapi.execute(self.cursor, "select seq_complex_perfresult.nextval from dual")

            if self.dbapi.dbenv == "PG_PYGRESQL":
                self.dbapi.execute (self.cursor, "select nextval('seq_complex_perfresult')")            
            
            if self.dbapi.dbenv == "MYSQL":
                self.dbapi.execute (self.cursor, "UPDATE sequence SET prev_value = @pr_value := prev_value + 1 where name = 'seq_complex_perfresult'")
                self.dbapi.execute (self.cursor, "SELECT @pr_value")


            result_id, = self.cursor.fetchone()
            result_id = self.__convertToInt(result_id)
            

            valueInput = value_array.split(', ')
            valCount = len(valueInput)
            
            startInput = start_times.split(', ')
            sTimeCount = len(startInput)
            
            endInput = end_times.split(', ')
            eTimeCount = len(endInput)

#            print "stTimeCount: %s, val1: %s, val2: %s, val3: %s, val4: %s" %(sTimeCount, startInput[0], startInput[2], startInput[3], startInput[4])
            
            i = 0
            valSum = 0
            while (i < valCount):
                valSum = valSum + float(valueInput[i].strip('[]'))
#                print i
                i = i + 1                
            avgValue = valSum/valCount
            
            j = 0
            while (j < sTimeCount):
                startInput[j] = startInput[j].strip('[]')
#                print j
                j = j + 1
            startInput.sort()
            start_time = startInput[0].strip('\'')

            k = 0
            while (k < eTimeCount):
                endInput[k] = endInput[k].strip('[]')
#                print k
                k = k + 1
            endInput.sort()
            end_time = endInput[eTimeCount-1].strip('\'')

            """
#            print "result_id: %s metric: %s, focus: %s, value: %s, start: %s, end: %s" %(result_id, metric_id, foci, value_array, start_times, end_times)
            cplxperfResParams = {"rid":result_id,
                                 "mid":metric_id,
                                 "fid":focus_id}
                             
            sql = "insert into complex_perf_result " +\
                  "(result_id, metric_id, focus_id," +\
                  "result_value.value, result_value.start_time, " +\
                  "result_value.end_time) values " +\
                  "(:rid, :mid, :fid, ARRAY" + value_array + ", " +\
                  "ARRAY" + start_times + ", ARRAY" + end_times + ")"

#            print sql """
            print result_id
            cplxperfResParam = {"rid":result_id}
            
            sql = "insert into complex_perf_result " +\
                  "(result_id, result_value.value," +\
                  "result_value.start_time, result_value.end_time) values " +\
                  "(:rid, ARRAY" + value_array + ", " +\
                  "ARRAY" + start_times + ", ARRAY" + end_times + ")"

#            print sql
            self.dbapi.execute(self.cursor, sql, cplxperfResParam)

            result = self.createPerformanceResult( metric_id, avgValue, start_time, end_time, units, foci, result_id)    

        except:
            raise
        return result_id

#    def createResult(self,  metric_id,value,start_time,\
#                           end_time, units,  foci, label=None, combined=0):
#        # Creates an entry in the performance_result_gen table
#        # This is part of testing new Results idea

#        if self.debug >= self.NO_WRITE:
#            return 0
#        try:
#            for f,t in foci:
#                if t == "primary":
#                    focus_id = f
#                    break
#            if self.dbapi.dbenv == "ORA_CXORACLE":
#                self.dbapi.execute(self.cursor, "select  seq_performance_result_gen.nextval from dual")
#
#            if self.dbapi.dbenv == "PG_PYGRESQL":
#                self.dbapi.execute (self.cursor, "select nextval('seq_performance_result_gen')")

#            # smithm 2008-7-11
#                        # Added clause for MySQL
#            if self.dbapi.dbenv == "MYSQL":
#                self.dbapi.execute (self.cursor, "UPDATE sequence SET prev_value = @pr_value := prev_value + 1 where name = ' seq_performance_result_gen'")
#                self.dbapi.execute (self.cursor, "SELECT @pr_value")

#            result_id, = self.cursor.fetchone()
#            result_id = self.__convertToInt(result_id)

#            #09-01-05 - create dictionary. create named format sql with variables that
#            #    are the keys from the dictionary. Pass the sql and dictionary to the
#            #    dbapi.execute method
#            #           correct format:
#            resultParams = {"rid":result_id,
#                             "mid":metric_id,
#                             "val":float(value),
#                             "stime":start_time,
#                             "etime":end_time,
#                             "units":units,
#                             "fid":focus_id,
#                             "lbl":label,
#                             "comb":combined}
#            sql = "insert into performance_result_gen " +\
#                  "(id, metric_id, " +\
#                  "value, start_time, end_time, units, " +\
#                  "focus_id, label, combined) " +\
#                  "values (:rid, :mid, :val, :stime, " +\
#                  ":etime, :units, :fid, :lbl, :comb)"


#            self.dbapi.execute(self.cursor, sql, resultParams)


#            for fid,ftype in foci:
#                #09-01-05 -create dictionary. create named format sql with variables that
#                #    are the keys from the dictionary. Pass the sql and dictionary to the
#                #    dbapi.execute method
#                resultFocusParams = {"prid":result_id,
#                                   "fcid":fid,
#                                   "fctype":ftype}
#                sql = "insert into performance_result_gen_has_focus " +\
#                      "(performance_result_id, focus_id, focus_type) " +\
#                      "values(:prid, :fcid, :fctype)"
#                self.dbapi.execute(self.cursor, sql, resultFocusParams)
#        except:
#            raise

#        return result_id

    def createCombinedPerformanceResult(self, metric_id,value,start_time,\
                           end_time, units, context, pr_ids, label):
        """Creates an entry in the performance_result table
           Creates entries in the combined_perf_result_has_member table
           Returns 0 on failure
           Returns perf_result id on success
        """
        # expects 'context' to be in the format returned by 
        # PTds.parseAndCreateContext,
        # a list of (id, contextType) tuples
        
        # pr_ids is the list of performance results used to make this new one

        # first create an entry in the performance_result table
        prId = self.createPerformanceResult(metric_id,value,start_time,\
                           end_time, units,  context, label, 1)
        if prId == 0:
            return 0
        # then add the list of prids that were used to make this comb perfRes
        # to the combined_perf_result_has_member table
        params = []
        for pr in pr_ids:
           params = {'c_pr_id':prId,'pr_id':pr}

           sql = "insert into combined_perf_result_members " +\
                 "(c_pr_id, pr_id) values (:c_pr_id, :pr_id)"
           self.dbapi.execute(self.cursor, sql, params)

        return prId

    def findFocusByID (self, resource_id_list):
        """ lookup and return the focus ID that matches the list of resource IDs provided.

        Returns [number] 0 if focus not found in DB.
        """
        if self.debug >= self.NO_CONNECT:
           return 0
        if resource_id_list == None:
           return 0
        #print "findFocusByID: " + str(resource_id_list)

        # get all the resource names
        # and sort the resources by their type
        resource_info = []
        for resource in resource_id_list:
           if resource:
               name = self.getResourceName(resource)
               type = self.getResourceType(resource)
               resource_info.append((type, name, resource))
        resource_info.sort()  # sort by resource type

        # build the name of the focus, which is a comma separated list
        # of the resources that make up the focus (in order by type)
        focusname = ""
        first = True
        for res in resource_info:
           if not first:
               focusname += ","
           focusname += res[1]
           first = False
        #print focusname
        sql = "select id from focus where focusName = '" + focusname + "'"

        try:
          #self.cursor.execute(sql)
          self.dbapi.execute(self.cursor, sql)
          #result = self.cursor.fetchone()
          result = self.dbapi.fetchone (self.cursor)
        except:
           raise
        if result == None:
           return 0
        if self.debug:
           print "result is " + str(result)
        print "result is " + str(result)
        return result[0]


    def addResourceNameToFocus(self, focusId, resName):
        """This function adds an entry to the focus_has_resource_name table.
           It assumes that :
             1. It is given a valid resource name in resName. In other words,
                it does not look up in resource_item to see that resName exists.
             2. It is given a valid focus id in focusId. Does not check focus
                table to see if focusId exists. 
           It returns focusId on success and 0 on failure.
        """
        if resName == None or focusId == 0:
           return 0
        sql = "insert into focus_has_resource_name (focus_id,resource_name)"\
              " values (%d, '%s')" % (focusId, resName)
        #print sql
        if self.debug:
           print sql
        if self.debug >= self.NO_WRITE:
           return 0
        #self.cursor.execute(sql)
        self.dbapi.execute (self.cursor, sql)
        return focusId

    def findFocusByName (self, focusName):
        """ lookup and return the focus ID that matches the string name provided.

        returns [number] 0 if focus name not found in the DB.
        """

        if focusName == None:
            return 0
        sql = "select id from focus where focusName = '" + focusName + "'"
        """ lookup and return the focus ID that matches the string name provided.

        returns [number] 0 if focus name not found in the DB.
        """

        if focusName == None:
            return 0
        sql = "select id from focus where focusName = '" + focusName + "'"

        if self.debug >= self.NO_CONNECT:
           return 0
        try:
          #self.cursor.execute(sql)
          self.dbapi.execute(self.cursor, sql)
          #result = self.cursor.fetchone()
          result = self.dbapi.fetchone (self.cursor)
        except:
           raise
        if result == None:
           return 0
        if self.debug:
           print "result is " + str(result)
        return result[0]

    def findOrCreateFocus(self, resource_id_list):
       """This function attempts to find a focus that has entries in the
       focus_has_resource table matching the resource id's in resource_id_list.
       If one is found, that focus id is returned. Otherwise, a new focus
       is created with entries in focus_has_resource for each resource in
       resource_id_list
       """
       # look up focus by trying to find an entry that matches the resource list

       if self.debug >= self.NO_CONNECT:
           return 0
       focusID = self.findFocusByID(resource_id_list)
       if self.debug >= self.NO_WRITE:
           return focusID
       #if focusID == None: #focus not found
       if not focusID: #focus not found
           focusID = self.createFocus(resource_id_list)
       return focusID


    def createFocus(self, resource_id_list):
       """Creates an entry in the focus table.  Associates focus with resources
       in the resource_id_list
       """
       if self.debug >= self.NO_CONNECT:
          return 0
       try:
           # get all the resource names
           # and sort the resources by their type
           resource_info = []
           for resource in resource_id_list:
               if resource:
                   name = self.getResourceName(resource)
                   type = self.getResourceType(resource)
                   resource_info.append((type, name, resource))
           resource_info.sort()  # sort by resource type

           # build the name of the focus, which is a comma separated list
           # of the resources that make up the focus (in order by type)
           focusname = ""
           first = True
           for res in resource_info:
               if not first:
                   focusname += ","
               focusname += res[1]
               first = False

           if self.debug >= self.NO_WRITE:
               return 0
           # create focus
           if self.dbapi.dbenv == "ORA_CXORACLE":
               sql = "select seq_focus.nextval from dual"
               self.dbapi.execute (self.cursor, sql)
           if self.dbapi.dbenv == "PG_PYGRESQL":
               sql = "select nextval('seq_focus')"
               self.dbapi.execute (self.cursor, sql)
               
           # smithm 2008-7-11
           # Added clause for MySQL
           if self.dbapi.dbenv == "MYSQL":
               self.dbapi.execute (self.cursor, "UPDATE sequence SET prev_value = @f_value := prev_value + 1 where name = 'seq_focus'")
               self.dbapi.execute (self.cursor, "SELECT @f_value")

           #focus_id, = self.cursor.fetchone()
           focus_id, = self.dbapi.fetchone(self.cursor)
           focus_id = self.__convertToInt(focus_id) 

           #Oracle/cx_Oracle
           #self.cursor.execute("insert into focus (ID, focusname) values " + \
           #            "(:ID, :focusname)", \
           #             ID = focus_id, focusname = focusname)

           #PG/Pygresql
           #focusParams = {"fid":focus_id, "fname":focusname}
           #self.cursor.execute("insert into focus (id, focusname) values \
           #           (%(fid)s, %(fname)s)", focusParams)

           #09-01-05 - create dictionary. create named format sql with variables that
           #    are the keys from the dictionary. Pass the sql and dictionary to the
           #    dbapi.execute method
           focusParams = {"fid":focus_id, 
                          "fname":focusname}
           sql = "insert into focus " +\
                 "(id, focusname) " +\
                 "values (:fid, :fname)"
           self.dbapi.execute(self.cursor, sql, focusParams)


           for resource in resource_info:
               if self.debug:
                   print "resource is : " + str(resource) + " focus is : " + str(focus_id)
               if resource != 0: # for now there may be zero entries in the focus
                                  # list to deal with missing information
                   #Oracle/cx_Oracle
                   #self.cursor.execute("insert into focus_has_resource\
                   #            (focus_id, resource_id) values \
                   #            (:focus_id, :resource_id)", focus_id = focus_id,\
                   #            resource_id = resource[2])
                   #PG/Pygresql
                   #focResParams = {"fid":focus_id, "rid":resource[2]}
                   #self.cursor.execute("insert into focus_has_resource \
                   #           (focus_id, resource_id) values \
                   #           (%(fid)s, %(rid)s)", focResParams)
                   #09-01-05 - create dictionary. create named format sql with variables that
                   #    are the keys from the dictionary. Pass the sql and dictionary to the
                   #    dbapi.execute method
                   focResParams = {"fid":focus_id, 
                                   "rid":resource[2]}
                   sql = "insert into focus_has_resource " +\
                         "(focus_id, resource_id) " +\
                         "values (:fid, :rid)"
                   self.dbapi.execute (self.cursor, sql, focResParams)
                   self.addAncestors(resource[2])
                   self.addDescendants(resource[2])
       except:
           raise
       return focus_id

    def addAncestors(self, rid):
       """Adds the ancestors of rid to the resource_has_ancestor table.

       If resource already has an entry in getAncestors, does nothing.
       """
       if self.debug >= self.NO_WRITE:
           return
       if rid == None or rid == 0:
          return
       # first, check if resource already entered into table -- if so, we're done
       try:
           sql = "select rid from resource_has_ancestor where rid = '" + str(rid) + "'"
           #print sql
           #self.cursor.execute(sql)
           self.dbapi.execute (self.cursor, sql)
           #result = self.cursor.fetchone()
           result = self.dbapi.fetchone (self.cursor)
       except:
           raise
       if result:
           return
       # here if entry not already in the table
       #  step up the hierarchy of resources, adding each ancestor
       currResource = rid
       while 1:
           query = "select parent_id from resource_item where id='" + \
                       str(currResource) + "'"
           try:
               #self.cursor.execute(query)
               self.dbapi.execute(self.cursor,query)
               #parentID, = self.cursor.fetchone()
               parentID, = self.dbapi.fetchone (self.cursor) 
           except:
               raise
           if parentID == None:
               break
           else:
               try:
                   sql = "insert into resource_has_ancestor (rid,aid) values "+\
                             "(" + str(rid) + "," + str(parentID) + ")"
                   #print sql
                   #self.cursor.execute(sql)
                   self.dbapi.execute(self.cursor, sql)
               except:
                   raise
               currResource = parentID

    def addDescendants(self, rid):
        """Adds the descendants of rid to the resource_has_descendant table
        If resource already has an entry in resource_has_descendants table,
        does nothing.
        """
        if self.debug >= self.NO_WRITE:
           return
        if rid == None:
           return
        # first, check if resource already entered into table -- if so, we're done
        try:
            sql = "select rid from resource_has_descendant where rid = '" + str(rid) + "'"
            #print sql
            #self.cursor.execute(sql)
            self.dbapi.execute(self.cursor,sql)
            #result = self.cursor.fetchone()
            result = self.dbapi.fetchone(self.cursor)
        except:
            raise
        if result:
            return
        # here if entry not already in the table
        #  step down the hierarchy of resources, adding each descendant
        kidList = rid,
        while len(kidList) > 0:
            newKidList = ()
            # get kids
            # print kidList
            for currParent in kidList:
                try:
                    query = "select id from resource_item where parent_id = '"+\
                               str(currParent) + "'"
                    #self.cursor.execute(query)
                    self.dbapi.execute (self.cursor,query)
                    #children = self.cursor.fetchall()
                    children = self.dbapi.fetchall (self.cursor)
                except:
                    raise
                for c, in children:
                    if len(newKidList) == 0:
                        newKidList = c,
                    else:
                        newguy = c,
                        newKidList = newKidList + newguy

            totalNewKids = len(newKidList)
            #print "totalNewKids = " + str(totalNewKids)
            if totalNewKids == 0:
                break
            CXLIMIT = 1000 # cx_oracle limit is 1000 expressions per query
            trials = totalNewKids / 1000 + 1
            starthere = 0
            endhere = min(CXLIMIT, totalNewKids)
            while (trials > 0):
                sql = "insert into resource_has_descendant (rid,did) (SELECT "+\
                      "ri1.id, ri2.id FROM resource_item ri1, resource_item " +\
                      "ri2 WHERE " +\
                      "ri1.id = '" + str(rid) + "' AND ri2.id IN "
                if len(newKidList) == 1:
                    sql += "(" + str(newKidList[0]) + ") ) "
                else:
                    sql += str(newKidList[starthere:endhere]) + ")"
                #print sql
                try:
                    #self.cursor.execute(sql)
                    self.dbapi.execute (self.cursor, sql)
                except:
                    raise
                starthere += CXLIMIT
                endhere += CXLIMIT
                trials -= 1
                #print "starthere:%d endhere:%d trials:%d" \
                #% (starthere,endhere,trials)

            kidList = newKidList

    def applicationHasExecution(self, aid, eid):
       """ Takes an application and an execution id and makes an entry
        in the application_has_execution table.
        """
       if self.debug >= self.NO_WRITE:
          return
       try:
           #Oracle 
           #self.cursor.execute("insert into application_has_execution\
           #             (aid, eid) values \
           #             (:aid, :eid)",  aid = aid, eid = eid)
           #Pg
           #aheParams = {"appid":aid, "exid":eid}
           #self.cursor.execute("insert into application_has_execution \
           #           (aid, eid) values \
           #           (%(appid)s, %(exid)s)", aheParams)
           #9-1-05: non-specific way
           aheParams = {"appid":aid, 
                        "exid":eid}
           sql = "insert into application_has_execution " +\
                 "(aid, eid) " +\
                 "values (:appid, :exid)"
           self.dbapi.execute (self.cursor, sql, aheParams)
       except:
           raise

    # May Deprecated
    # !!CAUTION - does not work right now!
    def executionHasResources(self, eid, resources):
       """ Takes an execution id and a list of resources and populates the
       execution_has_resource table.
       """
       if self.debug >= self.NO_WRITE:
          return
       #insertString = ""
       #insertString = "begin\n"
       try:
           for rid in resources:
               sql = "select type from resource_item where id='" + str(rid) + "'"         
               self.cursor.execute(sql)
               has_type, = self.cursor.fetchone()
               #insertString += "insert into execution_has_resource values ('" + str(eid) + "', '" + \
               #   str(rid) + "', '" + str(has_type) + "');\n "
               sql = "insert into execution_has_resource values ('" + str(eid) + "', '" + \
                  str(rid) + "', '" + str(has_type) + "') "
               self.cursor.execute(sql)
           if self.debug:
               print sql
           #insertString += "end;\n"
           #self.cursor.execute(insertString)
       except:
           raise

    def addResourceToExecution(self, eid, rid, rType):
       """ Adds a new record to the execution_has_resource table if it doesn't already exist.
       """
       if self.debug >= self.NO_CONNECT:
          return False
       sql = "select eid from execution_has_resource where eid='" + \
             str(eid) + "' and rid='" + str(rid) + "'"
       #self.cursor.execute(sql)
       self.dbapi.execute(self.cursor,sql)
       #result = self.cursor.fetchone()
       result = self.dbapi.fetchone(self.cursor)
       if self.debug >= self.NO_WRITE:
          if not result:
             return False
          else:
             return True
       if not result:
          sql = "insert into execution_has_resource values ('" + str(eid)
          sql += "', '" + str(rid) + "', '" + str(rType) + "')"
          #print sql
          try:
              #self.cursor.execute(sql)
              self.dbapi.execute (self.cursor, sql)
              if self.debug:
                  print sql
          except:
              raise
          else:
              return True
       else:
          return False

    # May be Deprecated
    # !! CAUTION -- this function does not work right now
    def associateResourceWithApplication(self, res_id, app_id):
       """Takes a resource_id and an application_id and makes an entry
       in the application_has_resource table.
       """
       if self.debug >= self.NO_WRITE:
          return
       try:
           #self.cursor.execute("insert into application_has_resource \
           #             (application_id, resource_id) values \
           #             (:application_id, :resource_id)", \
           #             application_id = app_id, resource_id = res_id)
           ahrParams = {"aid":app_id, "rid":res_id}
           self.cursor.execute("insert into application_has_resource \
                      (application_id, resource_id) values \
                      (%(aid)s, %(res_id)s)", ahrParams)
       except:
           raise

    # May be Deprecated
    def getHardwareId(self, type, hardwareName, parentId):
       """Returns an id for a piece of hardware based on name.  Currently,
       it only checks to see if the name matches.  However, better
       checking will need to be done in the future - for instance, need
       to check the valid dates of the hardware.
       """
       # For hardware, there is a notion of valid time.  A particular hardware
       # configuration could change (be replaced or whatever)
       # For now we only have valid hardware resources in the DB.  However, in
       # future, we will need to get a hardware id based on valid dates
       # my idea is that the list would contain the attribute value pairs
       # that would constrain validity (start_time=..., end_time=...)
       # ** TODO: fix this
       if self.debug >= self.NO_CONNECT:
          return 0
       try:
           parent_name = getResourceName(self, parentId)
           full_name = parent_name + self.resDelim + hardwareName
           hardware_id = getResourceId(self, type, full_name, parentId)
       except:
           print 'ERROR: could not get hardware ID for ' + hardwareName
           raise
       return hardware_id

    def getFocusFrameId(self ,type_string):
        """Returns the focus_framework_id for the given type_string.
        """
        if self.debug >= self.NO_CONNECT:
           return 0
        try:
            query = "select id from focus_framework where type_string=\'" \
                    + type_string + "\'"
            #self.cursor.execute(query)
            self.dbapi.execute(self.cursor, query)
            #focus_frame_id, = self.cursor.fetchone()
            focus_frame_id, = self.dbapi.fetchone(self.cursor)
        except:
            raise
        return  focus_frame_id

    def getParentResource(self, childId):
        """Returns the parentId of childId, if one exists. If childId is
           None, None is returned. If there is no parent of childId,
           None is returned.
        """
        if self.debug >= self.NO_CONNECT:
           return 0
        parentId = None
        if childId == None:
           return parentId
        try:
            query = "select parent_id from resource_item where id='" + \
                    str(childId) + "'"
            #self.cursor.execute(query)
            self.dbapi.execute(self.cursor, query)
            #result = self.cursor.fetchone()
            result = self.dbapi.fetchone(self.cursor)
            if result == None:
               return result
            else:
               parentId, = result
        except:
            raise
        return parentId

    # May be Deprecated
    def getChildResources(self, parentId): 
        """Returns a list of resource ids that are children of parentId.
           If parentId is None, the empty list is returned.
        """
        if self.debug >= self.NO_CONNECT:
           return 0
        kids = []
        if parentId == None:
           return kids
        try:
           query = "select id from resource_item where parent_id='" +\
                   str(parentId) + "'"
           #self.cursor.execute(query)
           self.dbapi.execute (self.cursor, query)
           #children = self.cursor.fetchall()
           children = self.dbapi.fetchall(self.cursor)
           for c, in children:
              kids.append(c)
        except:
           raise 
        return kids

    def getAncestors(self, resId):
        """Returns a list of resource ids that are the ancestors of resId.
           if resId is None, the empty list is returned.
        """
        if self.debug >= self.NO_CONNECT:
           return 0
        ans = []
        if resId == None:
           return ans
        try:
           parentId = self.getParentResource(resId)
           while parentId:
               ans.append(parentId)
               parentId = self.getParentResource(parentId)
        except:
           raise
        return ans

    # Deprecated
    ##def getExecutionName(self):
    #    #""" Returns a unique integer to serve as the name of an execution
    #    #"""
    #    #sql = "select seq_execution_name.nextval from dual"
    #    #self.cursor.execute(sql)
    #    #name, = self.cursor.fetchone()
    #    #if self.debug:
    #        #print 'execution name is ' + str(int(name))
    #    #return str(int(name))
    #    ## print 'execution name is ' + str((name))
    #    ## return str((name))

    # May be Deprecated
    # !! CAUTION -- does not work right now!
    def getExecutionName(self, trialName=None, appName=None):
        """ Returns a unique name for an execution
        """
        if self.debug >= self.NO_CONNECT:
           return 0
        if trialName and trialName != "None":
           sql = "select count(*) from resource_item where name like '" + self.resDelim + trialName + "-%' and type='execution'"
           self.cursor.execute(sql)
           execs, = self.cursor.fetchone()
           if execs:
              new = execs + 1
           else:
              new = 1
           name = trialName + "-" + str(new) # append a '-X' to trialName where
                                          # X is a number that makes trialName
                                          # unique
           return name
        else:
           if not appName:
              print "need to give application name if not giving trial name"
              raise
           else:
              sql = "select count(*) from resource_item where name like '" +\
                    appName + "-%' and type='execution'"
              self.cursor.execute(sql)
              execs, = self.cursor.fetchone()
              if execs:
                 new = execs + 1
              else:
                 new = 1
              name = appName + "-" + str(new) # append a '-X' to trialName where
                                          # X is a number that makes trialName
                                          # unique
              return name

    def getNewResourceName(self, givenName):
        """ Returns a unique integer to serve as the suffix for the
            name of a resource.
        """
        if self.debug >= self.NO_WRITE:
           return givenName

        if self.dbapi.dbenv == "ORA_CXORACLE":
            sql = "select seq_resource_name.nextval from dual" 
            self.dbapi.execute (self.cursor, sql)
        if self.dbapi.dbenv == "PG_PYGRESQL":
            sql = "select nextval('seq_resource_name')"
            self.dbapi.execute (self.cursor, sql)
        # smithm 2008-7-10
		# Added clause for MySQL
        if self.dbapi.dbenv == "MYSQL":
            self.dbapi.execute (self.cursor, "UPDATE sequence SET prev_value = @rn_value := prev_value + 1 where name = 'seq_resource_name'")
            self.dbapi.execute (self.cursor, "SELECT @rn_value")
        #name, = self.cursor.fetchone()
        name, = self.dbapi.fetchone (self.cursor)
        newName = givenName + "-" + str(int(name))
        #print 'resource name is ' + newName

        return newName

    # May be Deprecated
    # !! CAUTION -- does not work right now!  
    def getBuildName(self):
        """ Returns a unique integer to serve as the name of an build.
        """
        if self.debug >= self.NO_WRITE:
           return 0
          
        #sql = "select seq_build_name.nextval from dual"
        sql = "select nextval('seq_build_name')"
        self.cursor.execute(sql)
        name, = self.cursor.fetchone()
        return str(int(name))

    # May be Deprecated
    def enterResourceAVs(self, id, AVs):
        """Takes an entry identifier, a list of dictionaries of (name,value).
        It enters the AVs list into resource attribute with idName = id.
        Currently enters all attr_type fields as "string"
        Returns: nothing
        """
        if self.debug >= self.NO_WRITE:
            return
        #This is the cx_Oracle way
        #try:
        #    if len(AVs) > 0:
        #        query = "insert into resource_attribute " +\
        #                "(resource_id, name, value, attr_type) "
        #        query += "values (%d, :name, :value, 'string')" % id
        #        self.cursor.executemany(query, AVs)
        #except:
        #    raise

        #This works for pygresql
        #try:
        #    if len(AVs) > 0:
        #        newList = []
        #        for x in AVs:
        #            #print x
        #            dc = {"rid":id,"name":x['name'], "value":x['value'], "type":"string"}
        #            #for stuff in dc.keys():
        #            #    print stuff, '\t', dc[stuff]
        #            newList.append(dc)
        #        #print newList
        #        self.cursor.executemany("insert into resource_attribute \
        #                (resource_id, name, value, attr_type) values \
        #                (%(rid)s, %(name)s, %(value)s, %(type)s)", newList)
        #except:
        #    raise

        # refine the above -- PG
        #try:
        #    if len(AVs) > 0:
        #        query =  "insert into resource_attribute " +\
        #                 "(resource_id, name, value, attr_type) "
        #        query += "values (%d, %%(name)s, %%(value)s, 'string')" % id
        #        self.cursor.executemany(query, AVs)
        #except:
        #    raise

        # refine using PTpyDBAPI class
        try:
            if len(AVs) > 0:
                query =  "insert into resource_attribute " +\
                         "(resource_id, name, value, attr_type) "
                query += "values (%d, :name, :value, 'string')" % id
                #self.cursor.executemany(query, AVs)
                self.dbapi.executemany(self.cursor, query, AVs)
        except:
            raise

    # May be Deprecated
    def enterResourceConstraints(self, from_id, constraintList):
        """Takes a from_resource_id and a list of to_resource_id's and
        makes entries in the resource_constraint table.
        """
        if self.debug:
            print constraintList
        if self.debug >= self.NO_WRITE:
            return
        try:
            for to_id in constraintList:
                query = "insert into resource_constraint (from_resource, to_resource) "
                query += "values (%d, %d)" % (from_id, to_id)
                #self.cursor.execute(query)
                self.dbapi.execute (self.cursor, query)
        except:
            raise

    def findResTypeHierarchy(self, hierName):
        """ checks for an existing hierarchy with a matching name

        returns FocusFramework id  if found, 0 if not found
        """
        print "  findResTypeHierarchy"
        query = "   select id from focus_framework where type_string = '" + hierName + "'"
        if self.debug:
            print query
        if self.debug >= self.NO_CONNECT:
            return 0
        try:
            #self.cursor.execute(query)
            self.dbapi.execute(self.cursor, query)
            #result = self.cursor.fetchone()
            result = self.dbapi.fetchone (self.cursor)
            print "  check for existing: " + str(result)
        except:
            print "    findResTypeHierarchy query failed"
            raise
        else:
            if result == None:
                return 0
            if self.debug:
                print "   findResTypeHierarchy gets " + str(result)
            return result[0]


    def insertResTypeHierarchy(self, hierName):
        """ adds a new resource hierarchy to the focus framework

        returns True if added, False if error
        """
        if self.debug:
            print "  insertResTypeHierarchy"
        if self.debug >= self.NO_WRITE:
            return False
        # first check if type hierarchy has been initialized
        query = "  select id from focus_framework where id = 0"
        try:
            #self.cursor.execute(query)
            self.dbapi.execute (self.cursor, query)
        except:
            print "  insertResTypeHierarchy: check type hierarchy initialization failed"
            raise
        #result = self.cursor.fetchone()
        result = self.dbapi.fetchone (self.cursor) 
        if self.debug:
           print "result is " + str(result)
        if result == None:
            # initialize type hierarchy
            # 06-29-05: This is failing for pperfdb
            #query = "  insert into focus_framework  values (0, '', '')"
            query = "  insert into focus_framework  values (0, '', NULL)"
            try:
                #self.cursor.execute(query)
                self.dbapi.execute(self.cursor, query)
            except:
                print "  insertResTypeHierarchy: db initialize type hierarchy failed"
                return False
            else:
                print "insertResTypeHierarchy: " + query
        # add the new type to the hierarchy
        query = " insert into focus_framework values "
        if self.dbapi.dbenv == "ORA_CXORACLE":
            query += "(seq_focus_framework.nextval, '"
        if self.dbapi.dbenv == "PG_PYGRESQL":
            query += "(nextval('seq_focus_framework'), '"
        # smithm 2008-7-11
        # Added clause for MySQL
        if self.dbapi.dbenv == "MYSQL":
			self.dbapi.execute (self.cursor, "UPDATE sequence SET prev_value = @ff_value := prev_value + 1 where name = 'seq_focus_framework'")
			query += "((SELECT @ff_value), '"
        #query += "(seq_focus_framework.nextval, '"
        #query += "(nextval('seq_focus_framework'), '"
        query += hierName
        query += "', 0)"
        print "  insertResTypeHierarchy: " + query
        try:
            #self.cursor.execute(query)
            self.dbapi.execute(self.cursor, query)
        except:
            print "    insertResTypeHierarchy: insertion failed"
            return False
        else:
            return True

    def findResType(self, resTypeName):
        """ checks for an existing hierarchy with a matching name

        returns FocusFramework id  if found, 0 if not found
        """
        if self.debug >= self.NO_CONNECT:
           return 0
        query = "   select id from focus_framework where type_string = '" + resTypeName + "'"
        if self.debug:
           print "  findResType: " + query
        try:
            #self.cursor.execute(query)
            self.dbapi.execute(self.cursor, query)
            #result = self.cursor.fetchone()
            result = self.dbapi.fetchone(self.cursor)
        except:
            print "    findResType query failed"
            raise
        else:
            if result == None:
                return 0
            print "  check for existing: " + str(result[0])
            if self.debug:
                print "   findResType gets " + str(result)
            return result[0]

    def insertResType(self, resTypeName, parentID):
        """ adds a new resource type to the focus framework

        returns True if added, False if error
        """
        if self.debug:
           print "  insertResType"
        if self.debug >= self.NO_WRITE:
           return False
        # add the new type to the hierarchy
        query = " insert into focus_framework values "
        if self.dbapi.dbenv == "ORA_CXORACLE":
            query += "(seq_focus_framework.nextval, '"
        if self.dbapi.dbenv == "PG_PYGRESQL":
            query += "(nextval('seq_focus_framework'), '"
        # smithm 2008-7-10
		# Added clause for MySQL
        if self.dbapi.dbenv == "MYSQL":
            self.dbapi.execute (self.cursor, "UPDATE sequence SET prev_value = @ff_value := prev_value + 1 where name = 'seq_focus_framework'")
            query += "((SELECT @ff_value), '"
        #query += "(seq_focus_framework.nextval, '" #Oracle
        #query += "(nextval('seq_focus_framework'), '" #Pg
        query += resTypeName
        query += "', " + str(parentID) + ")"

        if self.debug:
            print "  insertResType: " + query
        try:
            #self.cursor.execute(query)
            self.dbapi.execute (self.cursor, query)
        except:
            print "    insertResType: insertion failed"
            return False
        else:
            return True

    def addResType (self, resTypeName):
        """ adds a new resource type to the focus framework

        if a resource type called resTypeName already exists in DB, does nothing
        returns focusframeworkid for new resource type, or 0 if none added
        """
        if self.debug:
            print " addResType: " + resTypeName
        if self.debug >= self.NO_CONNECT:
            return 0
        if self.findResType(resTypeName) > 0:
            print "   type is already in the database"
            return 0
        #if self.NO_WRITE >= 0:
        if self.debug >= self.NO_WRITE:
            print "I am returning here for some reason..."
            return 0
        else:
            print "  type " + resTypeName + " is not found in the database"
            # check that parent type is in database already; if not flag error
            stepone = resTypeName.split(self.resDelim)
            namelen = len(stepone)
            # check for new hierarchies
            if namelen == 1:
                print "debug: namelen is 1: call addResTypeHierarchy"
                result = self.addResTypeHierarchy(resTypeName)
                return result
            parent = self.resDelim.join(stepone[0:namelen-1])
            print "  checking for parent: " + parent
            parentID = self.findResType(parent)
            if parentID == 0:
                print "ERROR:  parent not found"
                return 0
            else:
                # now add the new resource type
                if self.insertResType(resTypeName, parentID):
                    return self.findResType(resTypeName)
                else:
                    print "   ERROR: insertion failed"
                    return 0

    def addResTypeHierarchy (self, hierName):
        """ adds a new resource type hierarchy called hierName

        if a resource type hierarchy called hierName already exists in DB, does nothing
        returns focusframeworkid for new hierarchy, or 0 if none added
        """
        if self.debug:
            print " addResTypeHierarchy: " + hierName
        if self.debug >= self.NO_CONNECT:
            return 0
        if self.findResTypeHierarchy(hierName) > 0:
            print "  type is already in the database"
            return 0
        if self.debug >= self.NO_WRITE:
            return 0
        else:
            print "  type " + hierName + " is not found in the database"
            if self.insertResTypeHierarchy(hierName):
                return self.findResTypeHierarchy(hierName)
            else:
                print "ERROR:" # **
                return 0

    def insertResource(self, resName, resType):
        """ inserts a new resource entry w/ full name resName and full type resType

        fails if resType does not exist.
        returns rid if successful, 0 if not
        """
        if self.debug:
            print "insertResource: " + resName + ", " + resType
        if self.debug >= self.NO_WRITE:
            return 0
        # get parentID
        parentID = None   #06-30-05 pygresql may not like none object in query statements...
        nameElements = resName.split(self.resDelim)
        nameLen = len(nameElements)
        if nameLen > 1: 
            parentName = self.resDelim.join(nameElements[0:nameLen-1])
            parentID = self.findResourceByName(parentName)
            if parentID == 0:
               return 0
        #   print "findResource returns: " + str(parentID) + " for parentName "\
        #           + parentName

        # get focus_frame_id
        ffid = self.getFocusFrameId(resType)
        # add the new resource
        result = self.createResource(ffid, parentID, resName, resType)
        return result


    def findResourceByNameAndType(self, resName, resType):
        """ finds a resource match for name and type. does not check attributes!

        returns resource id if found, 0 if not
        """
        if self.debug >= self.NO_CONNECT:
           return 0
        query = "select id from resource_item where name = '" + resName
        query += "' and type = '" + resType + "'"
        if self.debug:
            print "findResource:   " + query
        try:
            #self.cursor.execute(query)
            self.dbapi.execute (self.cursor, query)
        except:
            return 0
        else:
            #result = self.cursor.fetchone()
            result = self.dbapi.fetchone(self.cursor) 
            if result == None:
                return 0
            else:
                return result[0]

    def addExecution (self, execName, appName):
        """ adds a new execution resource called execName

        associates the execution with application appName
        if application appName doesn't already exist, flags an error
        if execution already exists, does nothing
        returns resource id if added, 0 if not
        """
        if self.debug:
           print "AddExecution: " + execName
        if self.debug >= self.NO_WRITE:
           return 0
        # check if execName already exists, if so, return
        #execExists = self.findResourceByNameAndType(execName, "execution")
        #if execExists > 0:
        #    return 0
        # check appName exists and get its id number
        appExists = self.findResourceByNameAndType(appName, "application")
        if appExists == 0:
            print "  application " + appName + " does not exist."
            return 0
        # add resource for execution
        newbie = self.addResource(execName, "execution")
        if newbie == 0:
            print "error adding new resource"
            return 0
        # add execution to its application
        result = self.applicationHasExecution(appExists, newbie)
        return result

    def addResourceAttribute(self, resName, attName, value, type):
        """ add an attribute-value pair to an existing resource

        returns 1 if added, 0 if nothing changed
        """
        if self.debug >= self.NO_WRITE:
            return 0
        # get rid
        rid = self.findResourceByName(resName)
        if rid == 0:
            print "resource not found"
            return 0
        try:
            query = "select resource_id,name from resource_attribute where "+\
                    "name='" + attName + "' and resource_id='" + str(rid) + "'"\
                    + " and attr_type='" + str(type) + "'"
            #self.cursor.execute(query)
            self.dbapi.execute(self.cursor,query)
            #result = self.cursor.fetchone()
            result = self.dbapi.fetchone(self.cursor)
            if result:
               return 0  # attribute already exists in db
            query = "insert into resource_attribute (resource_id, name, value,"\
                    + "attr_type) values ('" + str(rid) + "','" + attName \
                    + "','" + str(value) + "','" + str(type) + "')"
            #print query
            #self.cursor.execute(query)
            self.dbapi.execute(self.cursor, query) 
            return 1
        except:
            raise

    def addApplication (self, appName):
        """ adds a new application resource called appName

        If a resource of type application called appName already exists, does nothing
        returns resource id if added, 0 if not
        """
        print "AddApplication: " + appName
        if self.debug >= self.NO_WRITE:
           return 0
        return self.addResource(appName, "application")


    def addResource(self, resName, resType):
        """ adds a new resource called resName of type resType

        If a resource with name resName and type resType already exists, does nothing
        returns resource id if added, 0 if not
        """
        if self.debug >= self.NO_WRITE:
            return 0
        exists = self.findResourceByNameAndType(resName, resType)
        if exists > 0:
            return 0
        else:
           result = self.insertResource(resName, resType)
        return result

    def addExecResource(self, resName, resType, execName):
        """ adds a new resource called resName of type resType

        If a resource with name resName and type resType already exists, does nothing
        returns resource id if added, 0 if not
        """
        if self.debug >= self.NO_WRITE:
            return 0
        resId = self.findResourceByNameAndType(resName, resType)
        eId = self.findResourceByNameAndType(execName, "execution")
        if eId == 0:
            print "addExecResource fails: execution not found"
            return 0
        if resId == 0: # resource does not already exist
            # add the new resource record
            resId = self.insertResource(resName, resType)
            if resId == 0:
                print "addExecResource fails: couldn't add resource"
                return 0
        if self.addResourceToExecution(eId, resId, resType):
            return resId
        else:
            return 0

    def addResourceConstraint (self, from_Name, to_Name):
        """add an entry in the resource_constraint table containing the two resource id's

        If either resource id is not valid, does nothing
        returns True if successfully added, False otherwise
        """
        if self.debug >= self.NO_WRITE:
            return False
        # is from_id valid?
        from_id = self.findResourceByName(from_Name)
        if from_id == 0:
            return False
        # is to_id valid?
        to_id = self.findResourceByName(to_Name)
        if to_id == 0:
            return False
        query = "select from_resource,to_resource from resource_constraint "+\
                "where from_resource='" +str(from_id)+ "' and to_resource ='" +\
                str(to_id) + "'"
        #self.cursor.execute(query)
        self.dbapi.execute(self.cursor,query)
        #result = self.cursor.fetchone()
        result = self.dbapi.fetchone(self.cursor)
        #print "addResourceConstraint: result:" + str(result)
        if result:
           return False   # constraint already exists
        # add constraint
        query = "insert into resource_constraint (from_resource, to_resource) "
        query += "values (%d, %d)" % (from_id, to_id)
        try:
            #self.cursor.execute(query)
            self.dbapi.execute(self.cursor, query)
        except:
            print "query failure"
            raise
        else:
            return True

    def findExecutionApplication (self, eid):
        """ Returns the valid application id for the given execution

        Returns 0 if not found
        """
        if self.debug >= self.NO_CONNECT:
             return 0
        query = "select aid from application_has_execution where eid = " + str(eid)
        try:
            #self.cursor.execute(query)
            self.dbapi.execute(self.cursor, query)
        except:
            raise
        else:
            #aid, = self.cursor.fetchone()
            aid, = self.dbapi.fetchone(self.cursor)
            return aid

    def addContextAlias(self, alias, context):
        """ Adds an entry to the contextCache dictionary. If there is already
            an entry for 'alias', then it checks to make sure the context 
            is the same as for the existing entry. If so, it returns 0. 
            Otherwise, a context is created and entered in to the database.
            The new entry is added to the contextCache.
            Returns 0 if no new entry/context is created.
            Returns 1 if a new entry and context are created.
        """


        if alias in self.contextCache:
           # we've already seen this alias. Let's make sure it's for the 
           # same context, though, and it's not a new alias 
           (fullName, contexts) = self.contextCache[alias]
           if fullName == context: 
              # yup, the same, ignore it
              return 0
        if self.debug >= self.NO_WRITE:
            return 0
        # add the context to the database if it doesn't already
        # exist. remember that a context can actually be a list of
        # contexts with different types (e.g. primary, parent)
        # so, we get back a list from parseAndCreateContext
        # each item of this list is a pair (context_id, context_type)
        contexts = self.parseAndCreateContext(context)
        if contexts == 0:
           return 0
        # add this context to contextCache
        # first item in the pair is the full context name
        # second item is the list of (cntxt_id,type) pairs
        self.contextCache[alias] = (context,contexts)
        return 1

    def parseAndCreateContext(self, context):
        """ Takes a context and splits it up into its subcontexts. For each 
            subcontext (e.g. primary, parent, sender, etc.) it checks to see if 
            the subcontext already exists in the database. If so, it gets 
            its id. Otherwise, new entries are created in the database for the
            subcontext.
            Returns 0 on error
            Returns a list of (id, subcontextType) pairs on success
        """

        if self.debug >= self.NO_WRITE:
            return 0
        # parse the context and add it to the database
        contexts = []
        cs = context.split("::") # split into multiple context names
        #print cs
        for c in cs:
            index = c.find("(")
            if index >= 0:     # get the type of context 
               type = c[index+1:len(c)-1]
               name = c[:index]
            else:              # default to primary
               type = "primary"
               name = c
            context_id = self.findFocusByName(name)
            if context_id == 0:
                # create resource_id_list for new context
                resourceNames = name.split(",")
                resourceIDs = []
                for rName in resourceNames:
                    thisRID = self.findResourceByName(rName)
                    if thisRID == 0:
                        print "error forming context for %s" % rName
                        return 0
                    resourceIDs.append(thisRID)
                # add the new focus to the DB
                context_id = self.findOrCreateFocus(resourceIDs)
                if context_id == 0:
                    print "context could not be created"
                    return 0
                # here is support for a new table, focus_has_resource_name
                # we are in the process of changing the primary key of 
                # resource_item from an integer id to the resource's name
                # we plan to have all references to the resource_item table
                # be done by name in the future
                for rName in resourceNames:
                    check = self.addResourceNameToFocus(context_id,rName)
                    if check == 0:
                       print "error adding resource name to context"
                       return 0
                contexts.append((context_id,type))
            else:
                contexts.append((context_id,type))
        #print contexts 
        return contexts

                


    def addPerfResult(self, eName, fNames, perfToolName, metricName, value, units, startTime, endTime, label=None):
        """ Adds a new performance result to the database

        Returns 0 if eName, fName, perfToolName, metricName are not already defined in DB
        Returns perfResultID if new record added, or 0 if nothing changed in the DB
        """
        if self.debug >= self.NO_WRITE:
            return 0
        # get metric_id
        metric_id = self.findResourceByName(metricName)
        if metric_id == 0:
            return 0
        if fNames in self.contextCache:
           (fullName,foci) = self.contextCache[fNames]
        else:
           foci = self.parseAndCreateContext(fNames)
           if foci == 0:
              return 0
           self.contextCache[fNames] = (fNames,foci)

        # add the new performance result
        if startTime == "noValue":
           startTime = None
        if endTime == "noValue":
           endTime = None
        if units == "noValue":
           units = None
        result = self.createPerformanceResult( metric_id, value, startTime,\
                            endTime, units, foci, label)
        return result

    def addResult(self, rName, fNames, perfToolName, metricName, value, units, startTime, endTime, label=None):
        """ Adds a new result to the database

        This method is for the PTDF type RESULT.  RESULT is very close 
        to PERFRESULT, but RESULT can take any resource as its second
        parameter, while performance_result assumes the second parameter is an
        execution resource. 

        Returns 0 if fName, perfToolName, metricName are not already defined in DB
        Returns resultID if new record added, or 0 if nothing changed in the DB

        NOTE: the rName is not used. This is because this function mimics
        addPerfResult, and in that function the corresponding eName is not used.
        """
        if self.debug >= self.NO_WRITE:
            return 0
        # get metric_id
        metric_id = self.findResourceByName(metricName)
        if metric_id == 0:
            return 0
        if fNames in self.contextCache:
           (fullName,foci) = self.contextCache[fNames]
        else:
           foci = self.parseAndCreateContext(fNames)
           if foci == 0:
              return 0
           self.contextCache[fNames] = (fNames,foci)

        # add the new result
        if startTime == "noValue":
           startTime = None
        if endTime == "noValue":
           endTime = None
        if units == "noValue":
           units = None
        #result = self.createResult( metric_id, value, startTime,\
        #                    endTime, units, foci, label)
        result = self.createPerformanceResult( metric_id, value, startTime,\
                                               endTime, units, foci, label)
        return result

    def addComplexResult(self, fNames, perfToolName, metricName, values, units, startTimes, endTimes):
        """ Adds a new complex result to the database

        This method is for the PTDF type COMPLEXRESULT.  COMPLEXRESULT is very close 
        to RESULT, but COMPLEXRESULT has an array of values and timestamps for a single
        focus, metric, and performance tool.
        
        Returns 0 if fName, perfToolName, metricName are not already defined in DB
        Returns complexresultID if new record added, or 0 if nothing changed in the DB
        """
        
        if self.debug >= self.NO_WRITE:
            return 0
        # get metric_id
        metric_id = self.findResourceByName(metricName)
        if metric_id == 0:
            return 0
        if fNames in self.contextCache:
           (fullName,foci) = self.contextCache[fNames]
        else:
           foci = self.parseAndCreateContext(fNames)
           if foci == 0:
              return 0
           self.contextCache[fNames] = (fNames,foci)

        # add the new results
        if startTimes == "noValue":
           startTimes = None
        if endTimes == "noValue":
           endTimes = None
        if units == "noValue":
           units = None

        result = self.createComplexResult( metric_id, foci, values, startTimes, endTimes, units)
        #result = self.createResult( metric_id, value, startTime,\
        #                    endTime, units, foci, label)
        #result = self.createPerformanceResult( metric_id, value, startTime,\
        #                                       endTime, units, foci, label)
        return result

    def getPerfResultsByLabel(self,label,combined=None):
        """Returns a list of performance results from the database.
           It returns all pr's that have a label field that
           matches the one in the argument list.
           If the 'combined' argument is None (default), then both simple and 
           combined perf reses are fetched.
           If 'combined' is True, then only combined perf reses are fetched.
           If 'combined' is False, then only simple perf reses are fetched.
           Returns a list of tuples, each tuple describes one perfRes
             (id,metric,value,units,start_time,end_time,focus_id,label,combined)
           Returns [] if there are no matches.
        """
        # what the GUI would do, with slight changes for selecting based on 'combined' argument
        #sql = "INSERT INTO results_temp (result_id, start_time, end_time, value, units, metric, focus_id, label, combined) SELECT pr.id, pr.start_time, pr.end_time, pr.value, pr.units, riA.name, pr.focus_id, pr.label, pr.combined FROM performance_result pr, resource_item riA, performance_result_has_focus cprhf WHERE pr.id = cprhf.performance_result_id AND riA.id = pr.metric_id and label='%s'"% label
     
        sql = "SELECT pr.id, riA.name, pr.value, pr.units, pr.start_time, pr.end_time, pr.focus_id, pr.label, pr.combined FROM performance_result pr, resource_item riA, performance_result_has_focus cprhf WHERE pr.id = cprhf.performance_result_id AND riA.id = pr.metric_id and label='%s'"% label
        if combined == False:
           sql += " and pr.combined=0"
        elif combined == True:
           sql += " and pr.combined=1"
        elif combined == None:
           pass
        else:
           print "unknown value for 'combined' in PTdataStore:getPerfResultsByLabel: %s" % combined
           return []
    
        self.cursor.execute(sql)
        prs = self.cursor.fetchall()
        return prs

    def getPerfResultsByContext(self,resNameList,anc=False,desc=False,combined=None):
        """Returns a list of performance results from the database.
           It returns all pr's that have all the resources
           in the resourceList argument in their contexts.
           If anc is true, then it also searches for ancestors of the resources
           in the context.
           If desc is true, then it also searches for descendants of the 
           resources in the context
           If 'combined' is None (default), then both combined and simple perf
           reses are returned.
           If 'combined' is True, then only combined perf reses are returned
           If 'combined' is False, then only simple perf reses are returned
           Returns a list of tuples, each tuple describes one perfRes
             (id,metric,value,units,start_time,end_time,focus_id,label,combined)
           Returns [] if there are no matches.
        """
        # what the GUI would do, with minor changes for 'combined' arg
        #sql = "INSERT INTO results_temp(result_id, start_time, end_time, value,units, metric, focus_id, label, combined) SELECT pr.id, pr.start_time, pr.end_time, pr.value, pr.units, riA.name, pr.focus_id, pr.label pr.combined FROM performance_result pr, resource_item riA, performance_result_has_focus cprhf, contexts_temp foci WHERE pr.id = cprhf.performance_result_id AND cprhf.focus_id = foci.focus_id AND riA.id = pr.metric_id "

        self.__createTempTables() # use temp tables to store intermmediate data
        self.__clearAllTempTables()
        for r,t in resNameList:
            self.__addResourceToTempTable(r,t)
            if desc:
               self.__addResourceDescendantsToTempTable(r,t)
            if anc:
               self.__addResourceAncestorsToTempTable(r,t)
        self.__addContextToTempTable()
 
        sql = "SELECT pr.id, riA.name, pr.value, pr.units, pr.start_time, pr.end_time, pr.focus_id, pr.label, pr.combined FROM performance_result pr, resource_item riA, performance_result_has_focus cprhf, contexts_temp foci WHERE pr.id = cprhf.performance_result_id AND cprhf.focus_id = foci.focus_id AND riA.id = pr.metric_id"
        if combined == True:
           sql += " and pr.combined=1"
        elif combined == False:
           sql += " and pr.combined=0"
        elif combined == None:
           pass
        else:
           print "unknown value for 'combined' in PTdataStore:getPerfResultsByContext: %s" % combined
           return []

        #print sql
        self.cursor.execute(sql)
        prs = self.cursor.fetchall()
        return prs

    
    def createCombinedContext(self, contextList):
        """ Takes a list of contextIds and returns a combined
        context for the new combined perf result
        the new combined context is the union of the resources in the 
        primary contexts of the prIds in prList
        """
        # Future note: we talked about noticing when the new combined context
        # contains all the child resources of some parent resource, and 
        # replacing the child resources with the parent. This is not 
        # implemented in this version, because how this should be done is still
        # under debate

        # go through the list of prs and get their resources
        resIdx = ResourceIndex()
        for focus_id in contextList:
            sql = "select name,type from focus_has_resource inner join resource_item on resource_id=resource_item.id where focus_id=%s" % focus_id
            self.cursor.execute(sql)
            reses = self.cursor.fetchall()
            # add each resource to a resourceIndex
            for name,type in reses:
                res = Resource(name,type)
                resIdx.addResource(res)
        # create new context for the pr
        contextReses = resIdx.createContextTemplate()
        # build up the focusname string in PTdf format
        first = True
        for c in contextReses:
            if not first:
               focusName += "," + c.name
            else:
               focusName = c.name
               first = False
        return focusName


    def addCombinedPerfResult(self, fNames, metricName, value, units, startTime, endTime, pr_ids, label=None):
        """ Adds a new combined performance result to the database
        Returns 0 if metricName is not already defined in DB
        Returns perfResultID if new record added, or 0 if nothing changed in the DB
        """
        # assumes that fNames is the new context to be added to the database
        # and is in the format specified for PTdf
        # pr_ids is a list of the performance result id's used to make this new
        # result
        if self.debug >= self.NO_WRITE:
            return 0
        # get metric_id
        metric_id = self.findResourceByName(metricName)
        if metric_id == 0:
            return 0
        if fNames in self.contextCache:
           (fullName,foci) = self.contextCache[fNames]
        else:
           foci = self.parseAndCreateContext(fNames)
           if foci == 0:
              return 0
           self.contextCache[fNames] = (fNames,foci)

        # add the new performance result
        if startTime == "noValue":
           startTime = None
        if endTime == "noValue":
           endTime = None
        if units == "noValue":
           units = None
        result = self.createCombinedPerformanceResult( metric_id, value, \
                      startTime, endTime, units, foci, pr_ids, label)
        return result

    def getCombinedPerfResultSourceData(self, prid):
        """Returns a list of performance result ids that were combined to make 
           the combined performance result 'prid'.
        """ 
        sql = "select pr_id from combined_perf_result_members where c_pr_id=%s" %prid
        self.cursor.execute(sql)
        ret = self.cursor.fetchall()
        return [p for p, in ret] 
 

    def deleteCombinedPerfResult(self, prId):
        """Deletes a single combined performance result from the database that
           has id equal to the argument prId. If this pr was used to make 
           another combined performance result, then it will not be deleted. 
           Checks to see if any other performance results are using the pr's 
           context.  If so, the context is left in the database.
           If there are no other references to the context, it is deleted.
           returns (1,[]) on success
           returns (0,idList) on failure
           idList will either be empty, or will contain a list of prIds that 
           were made from this perfResult. These prIds in idList must be 
           removed before this perfResult can be removed.
        """
        # Deletes entries from performance_result, combined_perf_result_members
        # performance_result_has_focus.
        # if this is the last reference to the context, it deletes from 
        #    focus, focus_has_resource, focus_has_resource_name
 
        # first check to see if any other combined performance result depends
        # on this pr
        sql = "select c_pr_id from combined_perf_result_members where pr_id=%s" %prId
        self.cursor.execute(sql)
        ret = self.cursor.fetchall()
        if ret:
           return (0, [p for p, in ret])

        # now get the context ids for this pr
        sql = "select focus_id from performance_result_has_focus where performance_result_id=%s" % prId
        self.cursor.execute(sql)
        fids = self.cursor.fetchall()

        #  delete from   performance_result_has_focus
        sql = "delete from performance_result_has_focus where performance_result_id=%s" % prId
        self.cursor.execute(sql)

        # delete from combined_perf_result_members
        sql = "delete from combined_perf_result_members where c_pr_id=%s" % prId
        self.cursor.execute(sql)

        # delete from performance_result
        sql = "delete from performance_result where id=%s" % prId
        self.cursor.execute(sql)

        # delete focus only if no one else is using it
        # select count from performance_result has focus for each
        # if it's in there, then some other pr is using it

        for fid, in fids:
           sql = "select performance_result_id from performance_result_has_focus where focus_id=%s" % fid 
           self.cursor.execute(sql)
           prs = self.cursor.fetchall()

           # if there's no refs, then delete
           if len(prs) == 0:
              # delete focus_has_resource
              sql = "delete from focus_has_resource where focus_id=%s" % fid
              self.cursor.execute(sql)
           
              # delete focus_has_resource_name
              sql = "delete from focus_has_resource_name where focus_id=%s" %fid
              self.cursor.execute(sql)
             
              # delete from focus
              sql = "delete from focus where id=%s" % fid
              self.cursor.execute(sql)
        return (1,[])
 

    def storePTDFdata (self, filename):
        """ opens <filename> and reads in contents one line at a time.

        expects contents to be in valid PTdataFormat.
        Returns True if file could be opened for reading, False if not.
        Outputs messages to stdout.
        """
        try:
            pfile = open(filename, 'r')
        except:
            print "readPTDFfile failed: unable to open " + filename+ "for read."
            return False
        lineno = 0
        # valid syntax for each command
        ResTypeCmdLen = 2
        ResHierCmdLen = 2
        AppCmdLen = 2
        ShortResCmdLen = 3
        LongResCmdLen = 4
        ExecCmdLen = 3
        AttValueCmdLen = 5
        ResConsCmdLen = 3
        CntxtCmdLen = 3
        PerfResultCmdLen = 9
        ResultCmdLen = 9
        ComplexResultCmdLen = 8

        word = r'"([^"]+)"|([\S]+)'
        re_word = re.compile(word)

        thisLine = pfile.readline()
        while thisLine != '':
            lineno += 1
            print "\nprocessing input: " + str(lineno) +":"  + thisLine
            # split the line into 'words' by whitespace or by strings enclosed
            # in quotation marks
            currInput = [(qw or sw) for qw, sw in re.findall(re_word,thisLine)]
            if len(currInput) < 1: # skip blank lines
                thisLine = pfile.readline()
                continue
            currCmd = currInput[0].upper()
            if (currCmd == "APPLICATION"):
                if len(currInput) != AppCmdLen:
                    print "PTDF syntax error:  Application <AppName>"
                else:
                    result = self.addApplication(currInput[1])
                    print thisLine
            elif (currCmd == "RESTYPEHIERARCHY"):
                if len(currInput) != ResHierCmdLen:
                    print "PTDF syntax error:  ResTypeHierarchy <resHierarchyName>"
                else:
                    result = self.addResTypeHierarchy(currInput[1])
                    if result == 0:
                        print currInput[0] + " already found in the database"
                    else:
                        print currInput[1] + " added as focus_framework id = " + str(result)
            elif (currCmd == "RESOURCETYPE"):
                print thisLine
                if len(currInput) != ResTypeCmdLen:
                    print "PTDF syntax error:  ResourceType <resTypeName>"
                else:
                    result = self.addResType(currInput[1])
                    if result:
                        print currInput[1] + " added as focus_framework id = " + str(result)
                    else:
                        print "nothing added"
            elif (currCmd == "EXECUTION"):
                if len(currInput) != ExecCmdLen:
                    print "PTDF syntax error:  Execution <execName><appName>"
                else:
                    print thisLine
                    result = self.addExecution(currInput[1], currInput[2])
                    if result:
                        print currInput[1] + "added for application = " + currInput[2]
                    else:
                        print "nothing added"
            elif (currCmd == "RESOURCE"):
                print thisLine
                if len(currInput) == ShortResCmdLen:
                    result = self.addResource(currInput[1], currInput[2])
                    print "*" + thisLine + ": " + str(result)
                elif len(currInput) == LongResCmdLen:
                    result = self.addExecResource(currInput[1], currInput[2], currInput[3])
                    print "*" + thisLine + ": " + str(result)
                else:
                    print "PTDF syntax error:  Resource <resourceName> <resourceTypeName> [< execName>]"
            elif (currCmd == "RESOURCEATTRIBUTE"):
                if len(currInput) != AttValueCmdLen:
                    print "PTDF syntax error:  ResourceAttribute <resName><attribute><value><attributeType>"
                else:
                    print thisLine
                    result = self.addResourceAttribute(currInput[1], currInput[2],
                                                     currInput[3], currInput[4])
                    if result:
                        print currInput[2] + " = " + currInput[3] + \
                              " added for " + currInput[1]
                    else:
                        print "nothing added"
            elif (currCmd == "RESOURCECONSTRAINT"):
                if len(currInput) != ResConsCmdLen:
                    print "PTDF syntax error:  ResourceConstraint <resourceName1> <resourceName2>"
                else:
                    print thisLine
                    result = self.addResourceConstraint(currInput[1], currInput[2])
                    if result:
                        print "resource constraint added from " + currInput[1]\
                        + " to " + currInput[2]
                    else:
                        print "nothing added"
            elif (currCmd == "CONTEXT"):
                if len(currInput) != CntxtCmdLen:
                   print "PTDF syntax error: Context <contextName> "\
                         + "<resourceList>"
                else:
                   print thisLine
                   result = self.addContextAlias(currInput[1], currInput[2]) 
                   if result:
                       print "context alias %s added for %s" % \
                             (currInput[1],currInput[2])
                   else:
                       print "no context alias created"
            elif (currCmd == "PERFRESULT"):
                if len(currInput) != PerfResultCmdLen:
                    print "PTDF syntax error:  PerfResult <execName> "\
                          + "<focusName> <perfToolName> <metricName> <value> "\
                          + "<units> <startTime> <endTime>"
                else:
                    print thisLine
                    result = self.addPerfResult(currInput[1], currInput[2], currInput[3],
                                                currInput[4], currInput[5], currInput[6],
                                                currInput[7], currInput[8])
                    if result:
                        print "performance result added."
                    else:
                        print "nothing added."
            elif (currCmd == "RESULT"):
                if len(currInput) != ResultCmdLen:
                    print "PTDF syntax error:  Result <resourceName> "\
                          + "<focusName> <perfToolName> <metricName> <value> "\
                          + "<units> <startTime> <endTime>"
                else:
                    print thisLine
                    result = self.addResult(currInput[1], currInput[2], currInput[3],
                                            currInput[4], currInput[5], currInput[6],
                                            currInput[7], currInput[8])
                    if result:
                        print "result added."
                    else:
                        print "nothing added."
            elif (currCmd == "COMPLEXRESULT"):
                if len(currInput) != ComplexResultCmdLen:
                    print "PTDF syntax error:  ComplexResult <focusName> "\
                          + "<perfToolName> <metricName> <values> "\
                          + "<units> <startTimes> <endTimes>"
                else:
                    print thisLine
                    result = self.addComplexResult(currInput[1], currInput[2], currInput[3],
                                                   currInput[4], currInput[5], currInput[6],
                                                   currInput[7])       
                    if result:
                        print "complex result added."
                    else:
                        print "nothing added."
            else:
                print "PT syntax error:  unknown PTdataFormat entry: " + thisLine[0]
            thisLine = pfile.readline()
            self.commitTransaction()
        pfile.close()
        return True



    def __createTempTables(self):
       # creates temporary tables for retrieval of performance results
       # first check to see if they've already been created
       # in Oracle and Postgres, these temporary tables are private for each 
       # session, i.e. multiple users won't clobber each other's temp tables
       def findTable(tables,name):
          try:
             idx = tables.index(name.upper())
             return True
          except ValueError:
             return False
       if self.tempTablesCreated == False:
          tables = self.dbapi.getTables(self.cursor)
          if not findTable(tables,"resources_temp"):
             sql = "CREATE  GLOBAL TEMPORARY  TABLE resources_temp (name VARCHAR(255) PRIMARY KEY) ON COMMIT PRESERVE ROWS "
             self.cursor.execute(sql)
          if not findTable(tables,"adds_temp"):
             sql = "CREATE  GLOBAL TEMPORARY  TABLE adds_temp (name VARCHAR(255) PRIMARY KEY) ON COMMIT PRESERVE ROWS "
             self.cursor.execute(sql)
          if not findTable(tables,"contexts_temp"):
             sql = "CREATE  GLOBAL TEMPORARY  TABLE contexts_temp (focus_id INTEGER PRIMARY KEY) ON COMMIT PRESERVE ROWS "
             self.cursor.execute(sql)
          self.tempTablesCreated = True

    def __clearAllTempTables(self):
       # clears data from the temp tables
       sql = "DELETE FROM resources_temp "
       self.cursor.execute(sql)
       sql = "DELETE FROM adds_temp "
       self.cursor.execute(sql)
       sql = "DELETE FROM contexts_temp"
       self.cursor.execute(sql)

    def __clearAddTable(self):
       # clears data from the adds table
       sql = "DELETE FROM adds_temp "
       self.cursor.execute(sql)

    def __clearContextTable(self):
       # clears data from the temporary contexts table
       sql = "DELETE FROM contexts_temp "
       self.cursor.execute(sql)

    def __addResourceToTempTable(self, resName, resType):
       # adds resources to the resources_temp table. 
       # resource must match type and contain resName. 
       sql = "INSERT INTO adds_temp SELECT name FROM resource_item WHERE "
       sql += "type = '%s' AND name = '%s'" %(resType,resName)
       self.cursor.execute(sql)
       sql = "INSERT INTO resources_temp SELECT * FROM adds_temp"
       self.cursor.execute(sql)
       self.__clearAddTable()

    def __addResourceDescendantsToTempTable(self, resName, resType):
       # adds resources that are descendants of resName to the resources_temp
       # table
       sql = "INSERT INTO adds_temp SELECT rid.name FROM resource_item rid, resource_item ria, resource_has_ancestor rha WHERE ria.id = rha.aid AND rid.id = rha.rid AND ria.name IN  (SELECT name FROM resource_item WHERE "
       sql += "type='%s' AND name LIKE '%%%s')" % (resType, resName)
       self.cursor.execute(sql)
       sql = "INSERT INTO resources_temp SELECT * FROM adds_temp"
       self.cursor.execute(sql)
       self.__clearAddTable()

    def __addResourceAncestorsToTempTable(self, resName, resType):
       # adds resources that are ancestors of resName to the resources_temp
       # table
       sql = "INSERT INTO adds_temp SELECT ria.name FROM resource_item ria, resource_item rid, resource_has_descendant rhd WHERE rid.id = rhd.did AND ria.id = rhd.rid AND rid.name IN  (SELECT name FROM resource_item WHERE "
       sql += "type='%s' AND name LIKE '%%%s')" % (resType, resName)
       self.cursor.execute(sql)
       sql = "INSERT INTO resources_temp SELECT * FROM adds_temp"
       self.cursor.execute(sql)
       self.__clearAddTable()

    def __addContextToTempTable(self):
       # searches for contexts that contain all the resources in resources_temp
       # adds them to the contexts_temp table
       self.__clearContextTable()
       sql = "INSERT INTO contexts_temp SELECT focus_id FROM resources_temp t, focus_has_resource_name fhrn WHERE t.name = fhrn.resource_name GROUP BY fhrn.focus_id HAVING COUNT(resource_name) = 1"
       self.cursor.execute(sql)
       
           # Converts str to an integer.  Returns an int.  If str can't be converted
    # returns str
    def __convertToInt(self, str):
        try:
            return int(str)
        except:
            return str
