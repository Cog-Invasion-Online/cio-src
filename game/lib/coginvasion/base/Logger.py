########################################
# Filename: Logger.py
# Created by: blach (27Jul14)
########################################

import os
import sys
import time

class Logger:
	
	def __init__(self, orig, log):
		self.orig = orig
		self.log = log
		
	def write(self, string):
		#string = "[" + str(time.strftime("%m-%d-%Y %H:%M:%S")) + "] " + string
		self.log.write(string)
		self.log.flush()
		try:
			self.orig.write(string)
			self.orig.flush()
		except:
			pass
		
	def flush(self):
		self.log.flush()
		try: self.orig.flush()
		except: pass
		
class Starter:
	
	def __init__(self, log_prefix="coginvasion-", log_extension=".log", path="logs/"):
		log_suffix = time.strftime("%d-%m-%Y-%H-%M-%S")
		if not os.path.exists(path):
			os.mkdir(path)
		logfile = os.path.join(path, log_prefix + log_suffix + log_extension)
		log = open(logfile, "a")
		logOut = Logger(sys.stdout, log)
		logErr = Logger(sys.stderr, log)
		sys.stdout = logOut
		sys.stderr = logErr
