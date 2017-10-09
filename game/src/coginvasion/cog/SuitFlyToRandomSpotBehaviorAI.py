"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file SuitFlyToRandomSpotBehaviorAI.py
@author Maverick Liberty
@date September 06, 2015

"""

from src.coginvasion.cog.SuitHabitualBehaviorAI import SuitHabitualBehaviorAI
from src.coginvasion.globals import CIGlobals

from direct.interval.IntervalGlobal import Sequence, Wait, Func, Parallel
from direct.interval.ProjectileInterval import ProjectileInterval
from direct.interval.LerpInterval import LerpPosInterval
import random

class SuitFlyToRandomSpotBehaviorAI(SuitHabitualBehaviorAI):

    def __init__(self, suit):
        doneEvent = 'suit%s-flyToRandSpot' % (str(suit.doId))
        SuitHabitualBehaviorAI.__init__(self, suit, doneEvent)
        self.canFly = True
        self.isAirborne = False
        self.flyIval = None

    def __healthChange(self, health, prevHealth):
        if hasattr(self, 'suit'):
            if self.suit.isDead() and self.isAirborne:
                if not self.suit or self.suit.isEmpty():
                    self.exit()
                    return
                startPos = self.suit.getPos(render)
                endPos = startPos - (0, 0, 75)
                self.flyIval.pause()
                self.suit.d_stopMoveInterval()
                self.suit.b_setAnimState('flail')
                self.suit.enableMovement()
                self.suit.d_startPosInterval(startPos, endPos, 4.0, 'easeIn')
                self.suit.moveIval = LerpPosInterval(self.suit, duration = 4.0, pos = endPos, startPos = startPos, blendType = 'easeIn')
                self.suit.moveIval.start()

    def enter(self):
        SuitHabitualBehaviorAI.enter(self)
        if not hasattr(self, 'suit') or not self.suit or self.suit.isEmpty():
            self.exit()
            return
        self.accept(self.suit.healthChangeEvent, self.__healthChange)
        pathKeys = CIGlobals.SuitSpawnPoints[self.suit.getHood()].keys()
        pathKey = random.choice(pathKeys)
        endIndex = pathKeys.index(pathKey)
        if not self.suit.getCurrentPath():
            startIndex = -1
        else:
            startIndex = pathKeys.index(self.suit.getCurrentPath())
        self.suit.setCurrentPath(pathKey)
        self.suit.b_setSuitState(0, startIndex, endIndex)
        Sequence(
            Wait(0.5),
            Func(self.flyToNewSpot, pathKey)
        ).start()

    def exit(self):
        SuitHabitualBehaviorAI.exit(self)
        if self.flyIval:
            self.flyIval.pause()
            self.flyIval = None
        if hasattr(self, 'suit') and not hasattr(self.suit, 'DELETED') and self.suit and not self.suit.isEmpty():
            self.ignore(self.suit.healthChangeEvent)
            self.standSuit()

    def unload(self):
        SuitHabitualBehaviorAI.unload(self)
        if self.flyIval:
            self.flyIval.pause()
            self.flyIval = None
        del self.flyIval
        del self.canFly
        del self.isAirborne

    def flyToNewSpot(self, spot):
        if not hasattr(self, 'suit') or not self.suit or self.suit.isEmpty():
            self.exit()
            return
        self.isAirborne = True
        endPos = CIGlobals.SuitSpawnPoints[self.suit.getHood()][spot]
        self.suit.headsUp(endPos)
        startPos = self.suit.getPos(render)
        duration = 5.0
        self.suit.d_startProjInterval(startPos, endPos, duration, 0.25)
        self.flyIval = Parallel(
            # Server Information
            ProjectileInterval(self.suit,
                startPos = startPos,
                endPos = endPos,
                gravityMult = 0.25,
                duration = duration
            ),
            Sequence(
                Wait(9.0),
                Func(self.exit)
            ),
        )
        self.flyIval.start()

    def standSuit(self, withAnim = True):
        if not hasattr(self, 'suit') or not self.suit or self.suit.isEmpty():
            self.exit()
            return
        if withAnim:
            self.suit.b_setAnimState('neutral')
        self.isAirborne = False
        self.canFly = False
        flyCooldown = random.uniform(6.1, 20.0)
        taskMgr.doMethodLater(flyCooldown, self.__toggleCanFly, self.suit.uniqueName('FlyCooldown'))

    def __toggleCanFly(self, task):
        self.canFly = True
        return task.done

    def shouldStart(self):
        # The lower the health, the greater the chance of flying away.
        defaultChance = 0.15
        hpPerct = 1 - (float(self.suit.getHealth()) / float(self.suit.getMaxHealth()))
        chanceIncreases = 0
        if hpPerct > 0:
            chanceIncreases = int(float(hpPerct) / 0.25)
            for _ in xrange(chanceIncreases):
                defaultChance += 0.15
        return self.canFly and random.random() < defaultChance

    def isAirborne(self):
        return self.isAirborne
