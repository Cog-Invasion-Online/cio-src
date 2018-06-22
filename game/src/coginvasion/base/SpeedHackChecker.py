"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file SpeedHackChecker.py
@author Brian Lach
@date April 19, 2015

"""

import sys
import time
from panda3d.core import TrueClock

lastSpeedHackCheck = time.time()
lastTrueClockTime = TrueClock.getGlobalPtr().getLongTime()
timeEpsilon = 0.05 # How much clock discrepancy do we consider speed hacking
speedHackMaxTime = 1.0 # Max number of seconds we can allow this discrepency before disconnecting
speedHackBeginTime = -1

def __speedHackCheckTask(task):
    global lastSpeedHackCheck
    global lastTrueClockTime
    now = time.time()
    elapsed = now - lastSpeedHackCheck
    tcElapsed = TrueClock.getGlobalPtr().getLongTime() - lastTrueClockTime

    if tcElapsed > (elapsed + timeEpsilon):
        # Possible speed hacking.
        if speedHackBeginTime == -1:
            speedHackBeginTime = now
        elif now - speedHackBeginTime >= speedHackMaxTime:
            # The clock discrepency has been going on for a bit,
            # they are more than likely speed hacking.
            print "Detected speed hacks, closing game."
            sys.exit()
            return task.done
    else:
        speedHackBeginTime = -1

    lastSpeedHackCheck = time.time()
    lastTrueClockTime = TrueClock.getGlobalPtr().getLongTime()
    return task.cont

def startChecking():
    taskMgr.add(__speedHackCheckTask, "speedHackCheckTask")

def stopChecking():
    taskMgr.remove("speedHackCheckTask")
