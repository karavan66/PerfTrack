#!/usr/bin/env python

class PassFail:
   def __init__(self):
      self.passed_count = 0
      self.failed_count = 0

   def passed(self, msg=""):
      if msg == "":
         print ("PASS: %s" % msg)
      
      self.passed_count += 1

   def failed(self, msg=""):
      if msg != "":
         print ("FAIL: %s" % msg)
      else:
         print ("FAIL")
      self.failed_count += 1

   def test_info(self):
      print ("Tests Passed: %s Tests Failed %s" % (self.passed_count, self.failed_count))
