import os, re, time, sys

# Base Super Class
class baseAttrib:
        def attribFuncReq(self):
		# This function must be implemented by the child class
		# if not everything should break.
                none #Requirements function implemented by child class

        def attribFunc(self):
		# This function must be implemented by the child class
		# if not everything should break.
                none #Attribute function implemented by child class

	def attribDefaultName(self):
		# So, we are assuming that an attribute class
		# will know the atribute name that it
		# is retrieving the attribute for. This can be
		# over-ridden by the loacl database (Config file)
		# or a call to the PTDB.
		# If the child class does not implement we return
		# an 'unknown' value.
		return "noDefault_Unknown"

	def attribDefaultResourceType(self):
		# So, we are assuming that an attribute class
		# will know the resource type that it
		# is retrieving the attribute for. This can be
		# over-ridden by the loacl database (Config file)
		# or a call to the PTDB.
		# If the child class does not implement we return
		# an 'unknown' value.
		return "noDefault_Unknown"

	def attribDefaultResourceName(self):
		# So, we are assuming that an attribute class
		# will know the resource type that it
		# is retrieving the attribute for. This can be
		# over-ridden by the loacl database (Config file)
		# or a call to the PTDB.
		# If the child class does not implement we return
		# an 'unknown' value.
		return "noDefault_Unknown"

# FUNCTIONS
# +++++++++++++++++++++++++++++++
# +++++++++++++++++++++++++++++++

# Function: Execute command
# Preconditions: None
# Postconditions: None
#
# returns the output of a command executed on the 
# host system
def execCmdGetOutput(cmdToExec):
	f = os.popen(cmdToExec,"r")
	sys.stdout.flush()
	output = f.read()
	f.close()
	return output

# Function: Is a Word in a Line
# Preconditions: None
# Postconditions: None
#
# Returns the word if the word is found, else returns 0 length word
def wordInLine(wordToFind,lineToCheck):
        for key in lineToCheck.split():
                if key == wordToFind:
                        return key
        return ''
