import psutil
import os
import types

virusProcess = "cheat"

while 1:
	for process in psutil.process_iter():
		print process.name()
		try:
			if virusProcess in process.name():
				print "Killing process %s" % process.name()
				process.kill()
		except psutil.Error:
			pass
	print "Couldn't find it"
