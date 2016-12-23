########################################
# Filename: SuitPanicBehavior.py
# Created by: DecodedLogic (02Sep15)
########################################

from src.coginvasion.cog.SuitPathBehavior import SuitPathBehavior
import random

class SuitPanicBehavior(SuitPathBehavior):
    RUNAWAY_SPEED = 0.1
    RUNAWAY_SAFE_DISTANCE = 50
    
    def __init__(self, suit):
        SuitPathBehavior.__init__(self, suit, exitOnWalkFinish = False)
        self.toonsInRange = []
        self.isPanicked = False
        self.closestToon = None
        self.runAwayTaskName = self.suit.uniqueName('runAway')
        self.tickPanicTaskName = self.suit.uniqueName('tickPanic')
        self.panicHealthPerct = 0.35
        self.maxPanicTime = None
        self.panicTime = 0
        self.resetMaxPanicTime()
        
    def enter(self):
        SuitPathBehavior.enter(self)
        # Let's get out of here!
        self.closestToon = self.getClosestToon()
        if self.suit.getDistance(self.closestToon) <= self.RUNAWAY_SAFE_DISTANCE:
            self.createPath(durationFactor = self.RUNAWAY_SPEED, fromCurPos = True)
            self.isPanicked = True
        
    def __walkDone(self):
        SuitPathBehavior.__walkDone(self)
        if self.suit.getDistance(self.closestToon) >= self.RUNAWAY_SAFE_DISTANCE:
            self.exit()
        else:
            self.createPath(durationFactor = self.RUNAWAY_SPEED, fromCurPos = True)
        
    def exit(self):
        SuitPathBehavior.exit(self)
        self.toonsInRange = []
        self.isPanicked = False
        self.closestToon = None
        self.resetMaxPanicTime()
        
    def unload(self):
        SuitPathBehavior.unload(self)
        self.toonsInRange = []
        del self.toonsInRange
        del self.isPanicked
        del self.closestToon
        del self.runAwayTaskName
        del self.tickPanicTaskName
        del self.panicHealthPerct
        del self.maxPanicTime
        del self.panicTime
        
    def resetMaxPanicTime(self):
        self.maxPanicTime = random.randint(6, 12)
        
    def __tickPanic(self, task):
        task.delayTime = 1
        self.panicTime += 1
        if self.panicTime >= self.maxPanicTime:
            self.clearWalkTrack()
            self.exit()
            return task.done
        return task.cont
        
    def shouldStart(self):
        weakLevel = 6
        toonRange = 15
        
        if not self.isPanicked:
            self.toonsInRange = []
        
        # Let's search for toons in range.
        for av in self.suit.air.doId2do.values():
            if av.__class__.__name__ == 'DistributedToonAI':
                if av.zoneId == self.suit.zoneId:
                    if self.suit.getDistance(av) <= toonRange:
                        self.toonsInRange.append(av)
        
        healthPerct = (self.suit.getHealth() / self.suit.getMaxHealth())
        if self.suit.getLevel() <= weakLevel and len(self.toonsInRange) >= 2:
            return True
        elif self.suit.getLevel() > weakLevel and healthPerct <= self.panicHealthPerct and len(self.toonsInRange) > 0:
            return True
        self.toonsInRange = []
        return False
    
    def getClosestToon(self):
        distances = []
        for toon in self.toonsInRange:
            distances.append(toon.getDistance(self.suit))
        distances.sort()
        for i in range(len(self.toonsInRange)):
            toon = self.toonsInRange[i]
            if toon.getDistance(self.suit) == distances[0]:
                return toon
            
    def getPanicHealthPercentage(self):
        return self.panicHealthPerct