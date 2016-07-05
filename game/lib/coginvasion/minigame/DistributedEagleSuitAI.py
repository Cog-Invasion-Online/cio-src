# Filename: DistributedEagleSuitAI.py
# Created by:  blach (08Jul15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import LerpPosInterval, Sequence, Wait, Func

from lib.coginvasion.npc.NPCWalker import NPCWalkInterval
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.cog.DistributedSuitAI import DistributedSuitAI
import EagleGameGlobals as EGG

import random

class DistributedEagleSuitAI(DistributedSuitAI):
    notify = directNotify.newCategory("DistributedEagleSuitAI")

    def __init__(self, air):
        DistributedSuitAI.__init__(self, air)
        self.mg = None
        self.flyTrack = None
        self.currentFlyPoint = None
        self.flySpeed = 0.0

    def setMinigame(self, mg):
        self.mg = mg

    def getMinigame(self):
        return self.mg

    def handleGotHit(self):
        self.b_setAnimState('flail')
        if self.flyTrack:
            self.ignore(self.flyTrack.getDoneEvent())
            self.flyTrack.pause()
            self.flyTrack = None
        self.sendUpdate('fallAndExplode', [])
        self.b_setSuitState(6, -1, -1)
        self.flyTrack = Sequence(
            LerpPosInterval(
                self,
                duration = 4.0,
                pos = self.getPos(render) - (0, 0, 75),
                startPos = self.getPos(render),
                blendType = 'easeIn'
            ),
            Wait(1.5),
            Func(self.killMe)
        )
        self.flyTrack.start()

    def killMe(self):
        self.disable()
        self.requestDelete()

    def setFlySpeed(self, value):
        self.flySpeed = value

    def b_setFlySpeed(self, value):
        self.sendUpdate('setFlySpeed', [value])
        self.setFlySpeed(value)

    def getFlySpeed(self):
        return self.flySpeed

    def spawn(self):
        # spawn() also exists in DistributedSuitAI, but we're not doing
        # anything that a normal suit would do here, so don't even call
        # DistributedSuitAI.spawn.

        if not self.getMinigame():
            self.notify.error("Tried to spawn before self.mg was set!")
        
        self.b_setAnimState('flyNeutral')
        point = random.choice(EGG.EAGLE_FLY_POINTS)
        self.setPos(point)
        self.d_setPos(*point)

        self.b_setFlySpeed(EGG.ROUND_2_EAGLE_SPEED[self.getMinigame().getRound()])

        self.createFlyPath()
        self.b_setParent(CIGlobals.SPRender)

    def createFlyPath(self):
        self.b_setAnimState('flyNeutral')
        if self.flyTrack:
            self.ignore(self.flyTrack.getDoneEvent())
            self.flyTrack.pause()
            self.flyTrack = None
        point = random.choice(EGG.EAGLE_FLY_POINTS)
        if self.currentFlyPoint == point:
            self.createFlyPath()
            return
        if self.currentFlyPoint == None:
            point_list = list(EGG.EAGLE_FLY_POINTS)
            point_list.remove(point)
            startIndex = point_list.index(random.choice(point_list))
        else:
            startIndex = -1
        self.b_setSuitState(5, startIndex, EGG.EAGLE_FLY_POINTS.index(point))
        mgRound = self.getMinigame().getRound()
        if mgRound:
            self.flyTrack = NPCWalkInterval(self, point,
                durationFactor = EGG.ROUND_2_EAGLE_SPEED[mgRound],
                startPos = self.getPos(render), fluid = 1, name = self.uniqueName('DEagleSuitAI-flyTrack'))
            self.flyTrack.setDoneEvent(self.flyTrack.getName())
            self.acceptOnce(self.flyTrack.getDoneEvent(), self.handleFlyDone)
            self.flyTrack.start()
            self.currentFlyPoint = point
        else: return

    def handleFlyDone(self):
        self.createFlyPath()

    def delete(self):
        del self.currentFlyPoint
        del self.mg
        if self.flyTrack:
            self.ignore(self.flyTrack.getDoneEvent())
            self.flyTrack.pause()
            self.flyTrack = None
        DistributedSuitAI.delete(self)
