# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information.

# PTds.py
# Contains the class definition for PTdataStore

#import sys, cx_Oracle, string, re 
#import sys, pgdb, string, re

import sys, string, re, array
from ptPyDBAPI import *             #class to support Python DB API 2.0
from ptdfParser import PTDFParser
from lru_cache import lru_cache, lru_method
import logging

class NoDBResultException(Exception):
    def __init__(self, error):
        self.err = error

class CachedQuery:
    def __init__(self, sql, default, enabled=True):
        self.cached = dict()
        self.sql = sql
        self.default = default
        self.cache_enabled = enabled

    def query(self, dbapi, cursor, keys):
        frozen = frozenset(keys.items())
        logging.debug("cached %s :: %s", self.sql, frozen)
        if (self.cache_enabled and frozen in self.cached):
            logging.debug("found key result for %s :: %s", frozen, self.cached[frozen])
            return self.cached[frozen]
        else:
            try:
                dbapi.execute(cursor, self.sql, keys)
            except:
                return self.default

            result = dbapi.fetchone(cursor) 
            if result == None:
                return self.default
            else:
                self.cached[frozen] = result[0]
                return result[0]

class LRUQuery:
    def __init__(self, sql, default, size = 64):
        self.sql = sql
        self.default = default
        self.cached_method = lru_cache(maxsize=size)(self.__lru_query)

    def __lru_query(self, dbapi, cursor, frozen_keys):
        logging.debug("Getting cacheable result %s", frozen_keys)
        dbapi.execute(cursor, self.sql, dict(frozen_keys))
        result = dbapi.fetchone(cursor)
        if result == None:
            logging.debug("Skipping out of cache to prevent caching of null results")
            raise NoDBResultException("") #Prevents caching of result
        else:
            logging.debug("Got Cacheable result %s", result[0])
            return result[0]

    def cache_info(self):
        return self.cached_method.cache_info()

    def query(self, dbapi, cursor, keys):
        frozen = frozenset(keys.items())
        try:
            logging.debug("Attempting to get cached item %s", frozen)
            return self.cached_method(dbapi, cursor, frozen)
        except NoDBResultException:
            pass

        return self.default


class PTdataStore:
    """ Access methods for storing, querying, and retrieving PerfTrack data from a database.
    RDBMs/packages supported:  Postgresql/PyGreSql(DB API 2.0); Oracle/cx_oracle.
    """
    # debug levels
    NO_DEBUG = 0 # no debug turned on
    NO_COMMIT = 1 # will not commit transactions, sequence numbers will change
    NO_WRITE = 5  # will only read from db, no sequence numbers will change
    NO_CONNECT = 10 # will not connect to the database

    def __init__(self, data_delim='|'):
        self.cache_enabled = True
        self.cursor = None          # object for using db 
        self.connection = None      # object for db connection
        self.debug = self.NO_DEBUG  
        self.dbapi = PTpyDBAPI()    # instantiate PTpyDBAPI class 
        self.contextCache = {}      # cache contexts for easy lookup
        self.tempTablesCreated = False     # keep a record of whether we have 
                                           # created the temporary tables for
                                           # retrieving performance results
        self.resid = LRUQuery(
            "select id from resource_item where name=:name and type=:type", 0)
        self.resource_type = LRUQuery(
            "select type from resource_item where id=:id", "")
        self.resource_by_name = LRUQuery(
            "select id from resource_item where name=:name", 0)
        self.resource_name_by_id = LRUQuery(
            "select name from resource_item where id=:id", "")
        self.focus_by_id = LRUQuery(
            "select id from focus where focusName=:focusname", 0, 0)
        self.descendent_id = LRUQuery(
            "select rid from resource_has_descendant where rid=:rid", 0, 0)
        self.parent_id = LRUQuery(
            "select parent_id from resource_item where id=:id", 0)
        self.framework_id = LRUQuery(
            "select id from focus_framework where type_string=:type", 0)

        self.cached = [self.resid, self.resource_type, \
                           self.resource_by_name, self.resource_name_by_id, \
                           self.focus_by_id, \
                           self.descendent_id, \
                           self.parent_id, \
                           self.framework_id ]

        #logging.basicConfig(level=logging.DEBUG)
        logging.basicConfig()
        self.log = logging.getLogger(__name__)
        self.dataDelim = data_delim
        self.dbDelim = "|"
        
    def cache_info(self):
        for x in self.cached:
            print ("%s : %s" % (x.cache_info(), x.sql))

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
            self.debug("Debugging Enabled")
            self.debug = debugFlag
        if debugFlag < self.NO_CONNECT:
            self.connection = self.dbapi.connect(pt_db = ctb_db,
                                                 pt_dsn = ctb_dsn,
                                                 pt_host = ctb_host,
                                                 pt_pwd = ctb_pwd,
                                                 pt_user = ctb_user)
            self.cursor = self.dbapi.getCursor(self.connection)
            return True
        return False 

    def closeDB(self):
        if self.debug == self.NO_CONNECT:
            return
        else:
            self.dbapi.closeCrs(self.cursor)
            self.dbapi.closeCnx(self.connection)

    def abortTransaction(self):
        if self.debug == self.NO_CONNECT:
            return
        else:
            self.dbapi.rollback(self.connection)

    def commitTransaction(self):
        if self.debug >= self.NO_COMMIT:
            return
        else:
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

        self.log.debug(query)

        if self.debug >= self.NO_CONNECT:
            return
        try:
            self.dbapi.execute(self.cursor, query)
            temp = self.dbapi.fetchone(self.cursor)
            if (temp != None):
                res_id = temp[0]
            else: 
                res_id = 0
        except:
            self.log.error("Could not execute query in getResourceId: %s", query)
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
            elif self.dbapi.dbenv == "PG_PYGRESQL":
                self.dbapi.execute (self.cursor, "select nextval('seq_resource_item')")
            elif self.dbapi.dbenv == "MYSQL":
                self.dbapi.execute (self.cursor, "UPDATE sequence SET prev_value = @ri_value := prev_value + 1 where name = 'seq_resource_item'")
                self.dbapi.execute (self.cursor, "SELECT @ri_value")
				
            res_id, = self.dbapi.fetchone(self.cursor)
            res_id = self.__convertToInt(res_id)

            # get focus framework id
            if (focus_frame_id):
                ff = 1
            else:
                ff = 0
            if focus_frame_id == None:
                focus_frame_id = 0

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
            thisid = self.descendent_id.query(self.dbapi, self.cursor, {'rid':aid})
            if thisid > 0:
                try:
                    sql = "insert into resource_has_descendant (rid,did) values " +\
                          "(" + str(aid) + "," + str(res_id) + ")"
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
            full_name = parent_name + self.dbDelim + name
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

        if self.debug >= self.NO_CONNECT:
           return 0
        
        return self.resource_by_name.query(self.dbapi, self.cursor, {'name':fullName})

    # May be Deprecated 
    def findResource(self, parent_id, type, name, attributeList=[]):
        "Search for resource by full name"

        if self.debug >= self.NO_CONNECT:
            return None
        if parent_id:
            parent_name = self.getResourceName(parent_id)
            full_name = parent_name + self.dbDelim + name
        else:
            full_name = name
        id = self.getResourceId(type, full_name, parent_id)
        if id:
            self.log.debug("id: %s for %s", id, full_name)
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
            self.log.error("Could not execute query in findResourceByShortNameAndType: %s", query)
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
            self.log.error("Could not execute query in findResourceByShortNameAndShortType: %s", query)
            raise

    def getResourceName(self, id):
        """ Takes a resource id and returns the resource's name.
        If id is None, the empty string is returned.
        """
        if self.debug >= self.NO_CONNECT:
           return ""

        return self.resource_name_by_id.query(self.dbapi, self.cursor, {'id':id})

    def getResourceType(self, id):
        """ Takes a resource id and returns the resource's type.

        If id is None, the empty string is returned.
        """
        if self.debug >= self.NO_CONNECT:
            return ""
        return self.resource_type.query(self.dbapi, self.cursor, {'id':id})

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

        try:
            for f,t in foci:
                if t == "primary":
                    focus_id = f
                    break
            if self.dbapi.dbenv == "ORA_CXORACLE":
                self.dbapi.execute(self.cursor, "select seq_performance_result.nextval from dual")
            elif self.dbapi.dbenv == "PG_PYGRESQL":
                self.dbapi.execute (self.cursor, "select nextval('seq_performance_result')")
            elif self.dbapi.dbenv == "MYSQL":
                self.dbapi.execute (self.cursor, "UPDATE sequence SET prev_value = @pr_value := prev_value + 1 where name = 'seq_performance_result'")
                self.dbapi.execute (self.cursor, "SELECT @pr_value")
            else:
                raise Exception("Unknown database type")

            perfRes_id, = self.cursor.fetchone()
            perfRes_id = self.__convertToInt(perfRes_id)
            
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

            self.log.debug("stTimeCount: %s, val1: %s, val2: %s, val3: %s, val4: %s", sTimeCount, startInput[0], startInput[2], startInput[3], startInput[4])
            
            i = 0
            valSum = 0
            while (i < valCount):
                valSum = valSum + float(valueInput[i].strip('[]'))
                i = i + 1                
            avgValue = valSum/valCount
            
            j = 0
            while (j < sTimeCount):
                startInput[j] = startInput[j].strip('[]')
                j = j + 1
            startInput.sort()
            start_time = startInput[0].strip('\'')

            k = 0
            while (k < eTimeCount):
                endInput[k] = endInput[k].strip('[]')
                k = k + 1
            endInput.sort()
            end_time = endInput[eTimeCount-1].strip('\'')

            self.log.debug("Result Id: %s", result_id)
            cplxperfResParam = {"rid":result_id}
            
            sql = "insert into complex_perf_result " +\
                  "(result_id, result_value.value," +\
                  "result_value.start_time, result_value.end_time) values " +\
                  "(:rid, ARRAY" + value_array + ", " +\
                  "ARRAY" + start_times + ", ARRAY" + end_times + ")"

            self.dbapi.execute(self.cursor, sql, cplxperfResParam)

            result = self.createPerformanceResult( metric_id, avgValue, start_time, end_time, units, foci, result_id)    

        except:
            raise
        return result_id

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

        result = self.focus_by_id.query(self.dbapi, self.cursor, {'focusname':focusname})
        self.log.debug("result is %s", result)
        return result

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
        self.log.debug("%s", sql)
        if self.debug >= self.NO_WRITE:
           return 0

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
          self.dbapi.execute(self.cursor, sql)
          result = self.dbapi.fetchone (self.cursor)
        except:
           raise
        if result == None:
           return 0

        self.debug("result is %s", result)
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
           elif self.dbapi.dbenv == "PG_PYGRESQL":
               sql = "select nextval('seq_focus')"
               self.dbapi.execute (self.cursor, sql)
           elif self.dbapi.dbenv == "MYSQL":
               self.dbapi.execute (self.cursor, "UPDATE sequence SET prev_value = @f_value := prev_value + 1 where name = 'seq_focus'")
               self.dbapi.execute (self.cursor, "SELECT @f_value")
           else:
               raise Exception("Unknown Database Type")

           focus_id, = self.dbapi.fetchone(self.cursor)
           focus_id = self.__convertToInt(focus_id) 

           focusParams = {"fid":focus_id, 
                          "fname":focusname}
           sql = "insert into focus " +\
                 "(id, focusname) " +\
                 "values (:fid, :fname)"
           self.dbapi.execute(self.cursor, sql, focusParams)

           for resource in resource_info:
               self.log.debug("resource is : %s focus is : %s", resource, str(focus_id))
               if resource != 0: # for now there may be zero entries in the focus
                                  # list to deal with missing information
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
           self.dbapi.execute (self.cursor, sql)
           result = self.dbapi.fetchone (self.cursor)
       except:
           raise
       if result:
           return
       # here if entry not already in the table
       #  step up the hierarchy of resources, adding each ancestor
       currResource = rid
       while 1:
           parentID = self.parent_id.query(self.dbapi, self.cursor, {'id':currResource})
           if parentID == None:
               break
           else:
               try:
                   sql = "insert into resource_has_ancestor (rid,aid) values "+\
                             "(" + str(rid) + "," + str(parentID) + ")"
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
        if (self.descendent_id.query(self.dbapi, self.cursor, {'rid':rid}) > 0):
            return

        # here if entry not already in the table
        #  step down the hierarchy of resources, adding each descendant
        kidList = rid,
        while len(kidList) > 0:
            newKidList = ()
            # get kids
            for currParent in kidList:
                try:
                    query = "select id from resource_item where parent_id = '"+\
                               str(currParent) + "'"
                    self.dbapi.execute (self.cursor,query)
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

                self.dbapi.execute (self.cursor, sql)

                starthere += CXLIMIT
                endhere += CXLIMIT
                trials -= 1

            kidList = newKidList

    def applicationHasExecution(self, aid, eid):
       """ Takes an application and an execution id and makes an entry
        in the application_has_execution table.
        """
       if self.debug >= self.NO_WRITE:
          return
       try:
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
       try:
           for rid in resources:
               sql = "select type from resource_item where id='" + str(rid) + "'"         
               self.cursor.execute(sql)
               has_type, = self.cursor.fetchone()
               sql = "insert into execution_has_resource values ('" + str(eid) + "', '" + \
                  str(rid) + "', '" + str(has_type) + "') "
               self.cursor.execute(sql)
               self.log.debug(sql)
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
           self.dbapi.execute(self.cursor, sql)
           self.log.debug(sql)
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
           full_name = parent_name + self.dbDelim + hardwareName
           hardware_id = getResourceId(self, type, full_name, parentId)
       except:
           self.log.error("could not get hardware ID for %s", hardwareName)
           raise
       return hardware_id

    def getFocusFrameId(self ,type_string):
        """Returns the focus_framework_id for the given type_string.
        """
        if self.debug >= self.NO_CONNECT:
           return 0
        return self.framework_id.query(self.dbapi, self.cursor, {'type':type_string})

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
        
        result = self.parent_id.query(self.dbapi, self.cursor, {'id':childId})
        if result == 0:
            return None
        else:
            return result

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

    # May be Deprecated
    # !! CAUTION -- does not work right now!
    def getExecutionName(self, trialName=None, appName=None):
        """ Returns a unique name for an execution
        """
        if self.debug >= self.NO_CONNECT:
           return 0
        if trialName and trialName != "None":
           sql = "select count(*) from resource_item where name like '" + self.dbDelim + trialName + "-%' and type='execution'"
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
               self.log.error("need to give application name if not giving trial name")
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
        elif self.dbapi.dbenv == "PG_PYGRESQL":
            sql = "select nextval('seq_resource_name')"
            self.dbapi.execute (self.cursor, sql)
        elif self.dbapi.dbenv == "MYSQL":
            self.dbapi.execute (self.cursor, "UPDATE sequence SET prev_value = @rn_value := prev_value + 1 where name = 'seq_resource_name'")
            self.dbapi.execute (self.cursor, "SELECT @rn_value")
        else:
            raise Exception("Unknown Database Type")

        name, = self.dbapi.fetchone (self.cursor)
        newName = givenName + "-" + str(int(name))

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

        try:
            if len(AVs) > 0:
                query =  "insert into resource_attribute " +\
                         "(resource_id, name, value, attr_type) "
                query += "values (%d, :name, :value, 'string')" % id
                self.dbapi.executemany(self.cursor, query, AVs)
        except:
            raise

    # May be Deprecated
    def enterResourceConstraints(self, from_id, constraintList):
        """Takes a from_resource_id and a list of to_resource_id's and
        makes entries in the resource_constraint table.
        """
        self.log.debug(constraintList)
        if self.debug >= self.NO_WRITE:
            return

        for to_id in constraintList:
            query = "insert into resource_constraint (from_resource, to_resource) "
            query += "values (%d, %d)" % (from_id, to_id)
            self.dbapi.execute (self.cursor, query)

    def findResTypeHierarchy(self, hierName):
        """ checks for an existing hierarchy with a matching name

        returns FocusFramework id  if found, 0 if not found
        """
        query = "   select id from focus_framework where type_string = '" + hierName + "'"

        self.log.debug(query)
        if self.debug >= self.NO_CONNECT:
            return 0
        try:
            self.dbapi.execute(self.cursor, query)
            result = self.dbapi.fetchone (self.cursor)
            self.log.debug("check for existing: %s", str(result))
        except:
            self.log.error("findResTypeHierarchy query failed")
            raise
        else:
            if result == None:
                return 0
            self.log.debug("findResTypeHierarchy gets %s", str(result))
            return result[0]


    def insertResTypeHierarchy(self, hierName):
        """ adds a new resource hierarchy to the focus framework

        returns True if added, False if error
        """
        self.log.debug("insertResTypeHierarchy")
        if self.debug >= self.NO_WRITE:
            return False
        # first check if type hierarchy has been initialized
        query = "  select id from focus_framework where id = 0"
        try:
            self.dbapi.execute (self.cursor, query)
        except:
            self.log.error("insertResTypeHierarchy: check type hierarchy initialization failed")
            raise

        result = self.dbapi.fetchone (self.cursor) 
        self.log.debug("result is %s", str(result))

        if result == None:
            # initialize type hierarchy
            # 06-29-05: This is failing for pperfdb
            query = "  insert into focus_framework  values (0, '', NULL)"
            try:
                self.dbapi.execute(self.cursor, query)
            except:
                self.log.error("insertResTypeHierarchy: db initialize type hierarchy failed")
                return False
            else:
                self.log.debug("insertResTypeHierarchy: %s", query)

        # add the new type to the hierarchy
        query = " insert into focus_framework values "
        if self.dbapi.dbenv == "ORA_CXORACLE":
            query += "(seq_focus_framework.nextval, '"
        elif self.dbapi.dbenv == "PG_PYGRESQL":
            query += "(nextval('seq_focus_framework'), '"
        elif self.dbapi.dbenv == "MYSQL":
            self.dbapi.execute (self.cursor, "UPDATE sequence SET prev_value = @ff_value := prev_value + 1 where name = 'seq_focus_framework'")
            query += "((SELECT @ff_value), '"
        else:
            raise Exception("Unknown Database Type")

        query += hierName
        query += "', 0)"
        self.log.debug("insertResTypeHierarchy: %s", query)
        try:
            self.dbapi.execute(self.cursor, query)
        except:
            self.log.error("insertResTypeHierarchy: insertion failed")
            return False
        else:
            return True

    def findResType(self, resTypeName):
        """ checks for an existing hierarchy with a matching name

        returns FocusFramework id  if found, 0 if not found
        """
        if self.debug >= self.NO_CONNECT:
           return 0

        query = "select id from focus_framework where type_string = '" + resTypeName + "'"
        self.log.debug("findResType: %s",query)

        try:
            self.dbapi.execute(self.cursor, query)
            result = self.dbapi.fetchone(self.cursor)
        except:
            self.log.error("findResType query failed")
            raise
        else:
            if result == None:
                return 0
            self.log.debug("check for existing res type: %s", str(result[0]))
            self.log.debug("findResType gets %s", str(result))
            return result[0]

    def insertResType(self, resTypeName, parentID):
        """ adds a new resource type to the focus framework

        returns True if added, False if error
        """
        self.log.debug("insertResType")
        if self.debug >= self.NO_WRITE:
           return False
        # add the new type to the hierarchy
        query = " insert into focus_framework values "
        if self.dbapi.dbenv == "ORA_CXORACLE":
            query += "(seq_focus_framework.nextval, '"
        elif self.dbapi.dbenv == "PG_PYGRESQL":
            query += "(nextval('seq_focus_framework'), '"
        elif self.dbapi.dbenv == "MYSQL":
            self.dbapi.execute (self.cursor, "UPDATE sequence SET prev_value = @ff_value := prev_value + 1 where name = 'seq_focus_framework'")
            query += "((SELECT @ff_value), '"
        else:
            raise Exception("Unknown Database Type")

        query += resTypeName
        query += "', " + str(parentID) + ")"

        self.log.debug("insertResType: %s", query)
        try:
            self.dbapi.execute (self.cursor, query)
        except:
            self.log.error("insertResType: insertion failed")
            return False
        else:
            return True

    def addResType (self, resTypeName):
        """ adds a new resource type to the focus framework

        if a resource type called resTypeName already exists in DB, does nothing
        returns focusframeworkid for new resource type, or 0 if none added
        """
        self.log.debug("addResType: %s", resTypeName)

        if self.debug >= self.NO_CONNECT:
            return 0
        if self.findResType(resTypeName) > 0:
            self.log.info("type is already in the database: %s", resTypeName)
            return 0
        if self.debug >= self.NO_WRITE:
            self.log.debug("I am returning here for some reason...")
            return 0
        else:
            self.log.info("type %s is not found in the database", resTypeName)
            # check that parent type is in database already; if not flag error
            stepone = resTypeName.split(self.dbDelim)
            namelen = len(stepone)
            # check for new hierarchies
            if namelen == 1:
                self.log.debug("namelen is 1: call addResTypeHierarchy")
                result = self.addResTypeHierarchy(resTypeName)
                return result
            parent = self.dbDelim.join(stepone[0:-1])
            self.log.info("checking for parent: %s", parent)
            parentID = self.findResType(parent)
            if parentID == 0:
                self.log.error("parent not found for %s", parent)
                return 0
            else:
                # now add the new resource type
                if self.insertResType(resTypeName, parentID):
                    return self.findResType(resTypeName)
                else:
                    self.log.error("insertion failed")
                    return 0

    def addResTypeHierarchy (self, hierName):
        """ adds a new resource type hierarchy called hierName

        if a resource type hierarchy called hierName already exists in DB, does nothing
        returns focusframeworkid for new hierarchy, or 0 if none added
        """
        self.log.debug("addResTypeHierarchy: %s", hierName)

        if self.debug >= self.NO_CONNECT:
            return 0
        if self.findResTypeHierarchy(hierName) > 0:
            self.log.info("type is already in the database")
            return 0
        if self.debug >= self.NO_WRITE:
            return 0
        else:
            self.log.info("type %s is not found in the database", hierName)
            if self.insertResTypeHierarchy(hierName):
                return self.findResTypeHierarchy(hierName)
            else:
                self.log.error("Hiername not successfully inserted")
                return 0

    def insertResource(self, resName, resType):
        """ inserts a new resource entry w/ full name resName and full type resType

        fails if resType does not exist.
        returns rid if successful, 0 if not
        """
        self.log.debug("insertResource: %s, %s", resName, resType)

        if self.debug >= self.NO_WRITE:
            return 0
        # get parentID
        parentID = None
        nameElements = resName.split(self.dbDelim)
        nameLen = len(nameElements)
        if nameLen > 1: 
            parentName = self.dbDelim.join(nameElements[0:nameLen-1])
            parentID = self.findResourceByName(parentName)
            if parentID == 0:
               return 0

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
        
        return self.resid.query(self.dbapi, self.cursor, {'name':resName, 'type':resType})

    def addExecution (self, execName, appName):
        """ adds a new execution resource called execName

        associates the execution with application appName
        if application appName doesn't already exist, flags an error
        if execution already exists, does nothing
        returns resource id if added, 0 if not
        """
        self.log.debug("AddExecution: %s", execName)
        if self.debug >= self.NO_WRITE:
           return 0
        # check appName exists and get its id number
        appExists = self.findResourceByNameAndType(appName, "application")
        if appExists == 0:
            self.log.error("application %s does not exist.", appName)
            return 0
        # add resource for execution
        newbie = self.addResource(execName, "execution")
        if newbie == 0:
            self.log.error("error adding new resource")
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
            self.log.error("resource not found %s", resName)
            return 0
        query = "select resource_id,name from resource_attribute where "+\
                "name='" + attName + "' and resource_id='" + str(rid) + "'"\
                + " and attr_type='" + str(type) + "'"
        self.dbapi.execute(self.cursor,query)
        result = self.dbapi.fetchone(self.cursor)
        if result:
           return 0  # attribute already exists in db
        query = "insert into resource_attribute (resource_id, name, value,"\
                + "attr_type) values ('" + str(rid) + "','" + attName \
                + "','" + str(value) + "','" + str(type) + "')"
        self.dbapi.execute(self.cursor, query) 
        return 1

    def addApplication (self, appName):
        """ adds a new application resource called appName

        If a resource of type application called appName already exists, does nothing
        returns resource id if added, 0 if not
        """
        self.log.info("AddApplication: %s", appName)
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
            self.log.error("addExecResource fails: execution not found")
            return 0
        if resId == 0: # resource does not already exist
            # add the new resource record
            resId = self.insertResource(resName, resType)
            if resId == 0:
                self.log.error("addExecResource fails: couldn't add resource")
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

        self.dbapi.execute(self.cursor,query)

        result = self.dbapi.fetchone(self.cursor)

        if result:
           return False   # constraint already exists
        # add constraint
        query = "insert into resource_constraint (from_resource, to_resource) "
        query += "values (%d, %d)" % (from_id, to_id)
        try:
            self.dbapi.execute(self.cursor, query)
        except:
            self.log.error("query failure")
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
            self.dbapi.execute(self.cursor, query)
        except:
            raise
        else:
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
                        self.log.error("error forming context for %s", rName)
                        return 0
                    resourceIDs.append(thisRID)
                # add the new focus to the DB
                context_id = self.findOrCreateFocus(resourceIDs)
                if context_id == 0:
                    self.log.error("context could not be created")
                    return 0
                # here is support for a new table, focus_has_resource_name
                # we are in the process of changing the primary key of 
                # resource_item from an integer id to the resource's name
                # we plan to have all references to the resource_item table
                # be done by name in the future
                for rName in resourceNames:
                    check = self.addResourceNameToFocus(context_id,rName)
                    if check == 0:
                        self.log.error("error adding resource name to context")
                        return 0
                contexts.append((context_id,type))
            else:
                contexts.append((context_id,type))
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
        result = self.createPerformanceResult( metric_id, value, startTime,
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

        sql = "SELECT pr.id, riA.name, pr.value, pr.units, pr.start_time, pr.end_time, pr.focus_id, pr.label, pr.combined FROM performance_result pr, resource_item riA, performance_result_has_focus cprhf WHERE pr.id = cprhf.performance_result_id AND riA.id = pr.metric_id and label='%s'"% label
        if combined == False:
           sql += " and pr.combined=0"
        elif combined == True:
           sql += " and pr.combined=1"
        elif combined == None:
           pass
        else:
            self.log.error("unknown value for 'combined' in PTdataStore:getPerfResultsByLabel: %s", combined)
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
            self.log.error("unknown value for 'combined' in PTdataStore:getPerfResultsByContext: %s", combined)
            return []

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
            self.log.error("readPTDFfile failed: unable to open %s for read.", filename)
            return False
        parser = PTDFParser(self)
        parser.parse(pfile.read())
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
