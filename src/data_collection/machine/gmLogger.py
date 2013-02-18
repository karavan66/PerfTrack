#!/usr/bin/env python
import time

class gmlog:
	def gmLogWrite(self,condition,message):
		logFileName = "gmlog.log"
		logLine = time.asctime(time.localtime())

		if condition == 0:
			logLine = logLine + "|STATUS|"
		elif condition == 1:
			logLine = logLine + "|ERROR|"
		elif condition == 2:
			logLine = logLine + "|START|"
		elif condition == 3:
			logLine = logLine + "|END|"
		else:
			logLine = logLine + "|UNKNWON CONDITION|"

		f=open('hostSystemLog', 'a')
		f.write(logLine + message + '\n')
		f.close()
