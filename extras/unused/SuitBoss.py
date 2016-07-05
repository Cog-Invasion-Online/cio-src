"""

  Filename: SuitBoss.py
  Created by: blach (21Sep14)

"""

from panda3d.core import *
from lib.coginvasion.globals import CIGlobals
from direct.interval.IntervalGlobal import *
import random

class SuitBoss:

    def __init__(self, suitbase):
        self.suitbase = suitbase
        self.isFlying = False
        self.spot = self.suitbase.currentPath

    def startBoss(self):
        delay = random.randint(5, 20)
        taskMgr.doMethodLater(delay, self.flyTask, self.suitbase.uniqueName("flyTask"))

    def stopBoss(self):
        taskMgr.remove(self.suitbase.uniqueName("flyTask"))

    def flyTask(self, task):
        delay = random.uniform(6.1, 20.0)
        # We can't fly away if we're attacking
        if not self.suitbase.getAttacking():
            self.flyToNewSpot()
        task.delayTime = delay
        return task.again

    def flyToNewSpot(self):
        path_key_list = CIGlobals.SuitSpawnPoints[self.suitbase.hood].keys()
        path_key = random.choice(path_key_list)
        endIndex = CIGlobals.SuitSpawnPoints[self.suitbase.hood].keys().index(path_key)
        if not self.spot:
            startIndex = -1
        else:
            startIndex = CIGlobals.SuitSpawnPoints[self.suitbase.hood].keys().index(self.spot)
        self.spot = path_key
        self.suitbase.b_setSuitState(0, startIndex, endIndex)
        taskMgr.doMethodLater(0.5, self.flyAwayToNewSpot, "fatns", extraArgs = [path_key], appendTask = True)
        self.setFlying(True)

    def flyAwayToNewSpot(self, path_key, task):
        self.suitbase.headsUp(CIGlobals.SuitSpawnPoints[self.suitbase.hood][self.spot])
        suitTrack = ProjectileInterval(self.suitbase,
                                    startPos = (self.suitbase.getPos(render)),
                                    endPos = CIGlobals.SuitSpawnPoints[self.suitbase.hood][self.spot],
                                    gravityMult = 0.25, duration = 3.5)
        suitTrack.start()
        taskMgr.doMethodLater(6, self.standBoss, "standBoss")
        return task.done

    def standBoss(self, task):
        self.suitbase.b_setAnimState("neutral")
        self.setFlying(False)
        return task.done

    def setFlying(self, value):
        self.isFlying = value

    def getFlying(self):
        return self.isFlying
