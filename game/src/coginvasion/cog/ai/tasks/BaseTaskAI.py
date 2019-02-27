"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file BaseTaskAI.py
@author Brian Lach
@date February 19, 2019

"""

from src.coginvasion.cog.ai.ScheduleResultsAI import *

class BaseTaskAI:

    def __init__(self, npc):
        self.npc = npc
        self.startTime = 0.0
        self.running = False

    def isRunning(self):
        return self.running

    def getElapsedTime(self):
        if not self.isRunning():
            return 0.0

        return globalClock.getFrameTime() - self.getStartTime()

    def getStartTime(self):
        return self.startTime

    def startTask(self):
        self.startTime = globalClock.getFrameTime()
        self.running = True

    def runTask(self):
        return SCHED_COMPLETE

    def stopTask(self):
        self.running = False
        self.startTime = 0.0

    def setNPC(self, npc):
        self.npc = npc

    def getNPC(self):
        return self.npc

    def cleanup(self):
        del self.npc
        del self.startTime
        del self.running