# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information. 

class PTexception(Exception):
    def __init__(self, value=None):
        self.value = value
    def __str__(self):
        return repr(self.value)
  
