"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Logger.py
@author Brian Lach
@date July 27, 2014

"""

import os
import sys
import time

from pandac.PandaModules import Notify, MultiplexStream, Filename

class Logger:
    
    def __init__(self, orig, log):
        self.orig = orig
        self.log = log
        self.closed = orig.closed
        
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
        self.logfile = logfile
        log = open(logfile, "a")
        logOut = Logger(sys.stdout, log)
        logErr = Logger(sys.stderr, log)
        sys.stdout = logOut
        sys.stderr = logErr
        

    def startNotifyLogging(self):
        
        self.nout = MultiplexStream()
        Notify.ptr().setOstreamPtr(self.nout, 0)
        self.nout.addFile(Filename(self.logfile))
        self.nout.addStandardOutput()
        sys.stdout.console = True
        sys.stderr.console = True
