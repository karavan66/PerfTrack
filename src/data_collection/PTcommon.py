# PerfTrack Version 1.0     September 1, 2005
# See PTLICENSE for distribution information. 

import re,socket
import os,sys

from PTexception import PTexception

def getMachineName(ptds, machine, type):
    build_machine_id = ptds.findResourceByShortNameAndShortType(type, machine)
    #print "machine_id: %s, machine: %s, type:%s" %(build_machine_id,machine,type)
    if build_machine_id == -1:
       raise PTexception("getMachineName found multiple matches for %s with type %s" % (machine,type))
    if build_machine_id == None:
       raise PTexception("PTcommon:getMachineName None object returned for %s with type %s" % (machine,type))
    name = ptds.getResourceName(build_machine_id)
    type = ptds.getResourceType(build_machine_id)
    return name,type

def getNextAttrVal(attrs,idx):
    #get next attr value/pair or begin/end marker
    if idx >= len(attrs):
        raise PTexception("getNextAttrVal: attempting to read past end of list")
    ATTRS = attrs[idx]
    name = ATTRS[0]
    value = ""
    if(len(ATTRS) == 2):
       value = ATTRS[1]
    idx = idx + 1
    value = value.strip()
    name = name.strip()
    return (idx,name,value)


def fixListFormat(listString):
    "takes listString of the form: [\'val1\', \'val2\'] \
     and returns a string \'val1,val2\'"

    temp = listString.strip('[').strip(']')
    temp = temp.split(',')
    retStr = ""
    for t in temp:
        if retStr != "":
           retStr += ' '
        retStr += t.strip().strip('\'').strip('\'')
    #print retStr
    return retStr

def StringToList(prefix, delim, String):
    "takes an String of the form: ENVVAR=VALUEdelimENVVAR2=VALUE2delim\
     and splits it up (by the delim) into a list of attr value pairs \
     where attr = prefixENVVAR  and value = VALUE "

    envList = []
    temp = String.split(delim) #split by the delimiter
    for t in temp:
        t2 = t.split('=')  #split up ENVVAR and VALUE
        (a,v) = (prefix + t2[0], t2[1].strip())
        #print '(%s,%s)' % (a,v)
        envList.append((a,v))
    return envList

def cws(theString):
    """If theString contains whitespace, theString is returned enclosed in\"\"
       Else, theString is returned."""
    if re.search("\s+",theString):
        theString = theString.replace("\\", "\\\\")
        theString = theString.replace("\"", "\\\"")
        theString = "\"" + theString + "\""
    return theString

def appendListUnique(element,list):
     """ Appends element to list if element does not already exist in the 
         list 
     """
     try:  #list.index() throws exception if not found
        list.index(element)
     except ValueError:
        list.append(element)


def insertListUnique(element,list):
     """ Prepends element to list if element does not already exist in the 
         list 
     """
     try:  #list.index() throws exception if not found
        list.index(element)
     except ValueError:
        list.insert(0,element)

def isIP(addy):
    """ Returns True if addy is IP address, False, if not. """
    # if the string is XXX.XXX.XXX.XXX, where X are all numbers, then
    # it's an IP address.
    chunks = addy.split('.')
    if len(chunks) != 4:
       return False
    ret = True
    for c in chunks:
        if not c.isdigit():
           ret = False
           break
    return ret


def mapIPtoNode(ip):
    """ Attempts to get the hostname of the machine with ip address ip."""
    try:
       (hostname, aliaslist, ipaddrlist) = socket.gethostbyaddr(ip)
    except socket.gaierror (error, string):
       raise PTexception("toolParser.paradynParse: could not get node name"\
                       " for IP address %d. System error msg: %s" % \
                       (ip, string))
    else:
       return hostname


def my_exec2(cmd1,cmd2):
     """Executes cmd1 and gives it arguments in cmd2 (cmd2 is just a string
        containing the arguments)
        Returns stdout, stderr and the return status of cmd1
     """
     # popen2 is deprecated after python 2.3, so we have to check
     # and use subprocess if 2.4 or greater
     version = sys.version
     tmp = version.split()[0].split(".")
     versionNum = tmp[0] + "." + tmp[1] # grab major and minor version
     version = ""
     if(float(versionNum) < 2.4):
          popen2 = __import__("popen2")
          version = "old"
     else:
          subprocess = __import__("subprocess") 
          version = "new"
     Cmd = cmd1.strip() + ' ' + cmd2
     #print "my_exec2 cmd is " + Cmd
     if(version == "old"):
        x = popen2.Popen3(Cmd, True)
        x.tochild.close()
        childout = x.fromchild.read().strip()
        childerr = x.childerr.read().strip()
        retval = x.wait()
        status = os.WEXITSTATUS(retval)
        #if (status != 0):
           #print "exec failed for " + Cmd
        return (childout, childerr, retval)
     else:
        x = subprocess.Popen(Cmd, shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds=True)
        chldErr = x.stderr.read().strip()
        chldOut = x.stdout.read().strip()
        x.wait()
        retval = x.returncode
        return (chldOut, chldErr, retval)



    

