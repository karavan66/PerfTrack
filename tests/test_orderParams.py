#!/usr/bin/env python
# test_orderParams.py
# Michael Smith
# 2008-7-12
#
# This module test the __orderParams method provide by the ptPyDBAPI module

import unittest
from ptPyDBAPI import *

class OrderParamTest(unittest.TestCase):

# dict that is in correct order
# dict that is not in correct order
# dict with single key
# empty dict
# dict with single key that is incorrect
# dict with mulitple keys, but one is incorrect
# dict with missing key
# sql statement with no parameter values
# sql statement with less parameter values than found in dictionary
# sql statement with more parameter values than found in dictionary

    # Tests the normal case
    def testNormal(self):
        ptdb = PTpyDBAPI()
        sql = "insert into resource_item" +\
            "(id, focus_framework_id, type, parent_id, name, ff)" +\
            " values (:rid, :fid, :ftype, :par_id, :fname, :ffw)"
        dict = {"rid":1,
                "fid":3,
                "ftype":"some_type",
                "par_id":10,
                "fname":"full_name",
                "ffw":"focus_frame"}
        returnList = [1, 3, "some_type", 10, "full_name", "focus_frame"]
        self.assertEqual(ptdb.orderParams(sql, dict), returnList)
        
    # Test the normal case were the dictionary ordering does not match the
    # parameter ordering in the SQL statement.
    def testNormalUnordered(self):
        ptdb = PTpyDBAPI()
        sql = "insert into resource_item" +\
            "(id, focus_framework_id, type, parent_id, name, ff)" +\
            " values (:rid, :fid, :ftype, :par_id, :fname, :ffw)"
        dict = {"rid":1,
                "fid":3,
                "ftype":"some_type",
                "par_id":10,
                "fname":"full_name",
                "ffw":"focus_frame"}
        returnList = [1, 3, "some_type", 10, "full_name", "focus_frame"]
        self.assertEqual(ptdb.orderParams(sql, dict), returnList)
    
    # Tests a normal case were the dictionary contains a single key and the
    # SQL statement contains a single parameter
    def testNormalSingle(self):
        ptdb = PTpyDBAPI()
        sql = "insert into resource_item (id ) values (:rid)"
        dict = {"rid":1}
        returnList = [1]
        self.assertEqual(ptdb.orderParams(sql, dict), returnList)
    
    # Test an abnormal case were the dictionary is empty
    def testEmptyDict(self):
        ptdb = PTpyDBAPI()
        sql = "insert into resource_item" +\
            "(id, focus_framework_id, type, parent_id, name, ff)" +\
            " values (:rid, :fid, :ftype, :par_id, :fname, :ffw)"
        dict = {}
        returnList = None
        self.assertEqual(ptdb.orderParams(sql, dict), returnList)    
    
    # Test an abnormal case were the dictionary contains a single key
    # that is incorrect.
    def testSingleIncorrectKey(self):
        ptdb = PTpyDBAPI()
        sql = "insert into resource_item (id ) values (:rid)"
        dict = {"bad":1}
        returnList = None
        self.assertEqual(ptdb.orderParams(sql, dict), returnList)
        
    # Test an abnormal case were the dictionary contains an incorrect key
    def testIncorrectKey(self):
        ptdb = PTpyDBAPI()
        sql = "insert into resource_item" +\
            "(id, focus_framework_id, type, parent_id, name, ff)" +\
            " values (:rid, :fid, :ftype, :par_id, :fname, :ffw)"
        dict = {"rid":1,
                "fid":3,
                "ftype":"some_type",
                "bad_id":10,
                "fname":"full_name",
                "ffw":"focus_frame"}
        returnList = None
        self.assertEqual(ptdb.orderParams(sql, dict), returnList)

    # Test an abnormal case were the dictionary is missing a key
    def testMissingKey(self):
        ptdb = PTpyDBAPI()
        sql = "insert into resource_item" +\
            "(id, focus_framework_id, type, parent_id, name, ff)" +\
            " values (:rid, :fid, :ftype, :par_id, :fname, :ffw)"
        dict = {"rid":1,
                "fid":3,
                "ftype":"some_type",
                "fname":"full_name",
                "ffw":"focus_frame"}
        returnList = None
        self.assertEqual(ptdb.orderParams(sql, dict), returnList)
    
    # Test an abnormal case were the SQL statement contains no parameter values
    def testNoParam(self):
        ptdb = PTpyDBAPI()
        sql = "insert into resource_item" +\
            "(id, focus_framework_id, type, parent_id, name, ff)" +\
            " values ()"
        dict = {"rid":1,
                "fid":3,
                "ftype":"some_type",
                "par_id":10,
                "fname":"full_name",
                "ffw":"focus_frame"}
        returnList = None
        self.assertEqual(ptdb.orderParams(sql, dict), returnList)
    
    # Test an abnormal case were the SQL statement contins less parameter
    # values than found in the dictionary
    def testLessParam(self):
        ptdb = PTpyDBAPI()
        sql = "insert into resource_item" +\
            "(id, focus_framework_id, type, parent_id, name, ff)" +\
            " values (:rid, :fid, :ftype, :par_id, :ffw)"
        dict = {"rid":1,
                "fid":3,
                "ftype":"some_type",
                "par_id":10,
                "fname":"full_name",
                "ffw":"focus_frame"}
        returnList = None
        self.assertEqual(ptdb.orderParams(sql, dict), returnList)
        
    # Test an abnormal case were the SQL statement contains more parameter
    # values than found in the dictionarly
    def testMoreParam(self):
        ptdb = PTpyDBAPI()
        sql = "insert into resource_item" +\
            "(id, focus_framework_id, type, parent_id, name, ff)" +\
            " values (:rid, :fid, :ftype, :par_id, :fname, :ffw, :bad)"
        dict = {"rid":1,
                "fid":3,
                "ftype":"some_type",
                "par_id":10,
                "fname":"full_name",
                "ffw":"focus_frame"}
        returnList = None
        self.assertEqual(ptdb.orderParams(sql, dict), returnList)
        
if __name__ == '__main__':
    unittest.main()
