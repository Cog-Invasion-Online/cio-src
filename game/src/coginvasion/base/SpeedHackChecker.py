########################################
# Filename: SpeedHackChecker.py
# Created by: blach (19Apr15)
########################################

import sys
import time
from pandac.PandaModules import TrueClock

lastSpeedHackCheck = time.time()
lastTrueClockTime = TrueClock.getGlobalPtr().getLongTime()

def __speedHackCheckTask(task):
	global lastSpeedHackCheck
	global lastTrueClockTime
	elapsed = time.time() - lastSpeedHackCheck
	tcElapsed = TrueClock.getGlobalPtr().getLongTime() - lastTrueClockTime
	
	if tcElapsed > (elapsed + 0.05):
		print "Detected speed hacks, closing game."
		sys.exit()
		return task.done
	
	lastSpeedHackCheck = time.time()
	lastTrueClockTime = TrueClock.getGlobalPtr().getLongTime()
	return task.cont

def startChecking():
	taskMgr.add(__speedHackCheckTask, "speedHackCheckTask")
	
def stopChecking():
	taskMgr.remove("speedHackCheckTask")
