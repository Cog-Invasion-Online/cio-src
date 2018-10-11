"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedCogOfficeSuit.py
@author Brian Lach
@date December 17, 2015

"""

from panda3d.core import Point3

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.ClockDelta import globalClockDelta
from direct.fsm import ClassicFSM, State

from src.coginvasion.npc.NPCWalker import NPCWalkInterval
from src.coginvasion.cog.DistributedSuit import DistributedSuit
from CogOfficeConstants import *

class DistributedCogOfficeSuit(DistributedSuit):
    notify = directNotify.newCategory('DistributedCogOfficeSuit')

    def __init__(self, cr):
        DistributedSuit.__init__(self, cr)
        self.fsm = ClassicFSM.ClassicFSM('DistributedCogOfficeSuitAI', [State.State('off', self.enterOff, self.exitOff),
         State.State('guard', self.enterGuard, self.exitGuard, ['think']),
         State.State('think', self.enterThink, self.exitThink, ['off']),
         State.State('chair', self.enterChair, self.exitChair, ['chair2battle']),
         State.State('chair2battle', self.enterChair2Battle, self.exitChair2Battle, ['think'])], 'off', 'off')
        self.fsm.enterInitialState()
        self.battleDoId = None
        self.battle = None
        self.hangoutPoint = [0, (0, 0, 0), 0]
        self.guardPoint = self.chairPoint = [(0, 0, 0), 0]

    def setHangoutPoint(self, hasHangout, pos, h):
        self.hangoutPoint = [hasHangout, pos, h]

    def setGuardPoint(self, pos, h):
        self.guardPoint = [pos, h]

    def setChairPoint(self, pos, h):
        self.chairPoint = [pos, h]

    def setBattleDoId(self, doId):
        self.battleDoId = doId

    def getBattle(self):
        self.battle = self.cr.doId2do.get(self.battleDoId)

    def announceGenerate(self):
        self.getBattle()
        DistributedSuit.announceGenerate(self)

    def disable(self):
        self.fsm.requestFinalState()
        del self.fsm
        DistributedSuit.disable(self)

    def getPoints(self, name):
        if self.battle.currentRoom in self.battle.UNIQUE_FLOORS:
            points = POINTS[self.battle.deptClass][self.battle.currentRoom][name]
        else:
            points = POINTS[self.battle.currentRoom][name]
        return points

    def enterOff(self, extraArgs = [], ts = 0):
        pass

    def exitOff(self):
        pass

    def enterGuard(self, ts):
        self.show()
        self.cleanupPropeller()
        points = self.getPoints('guard')
        
        if self.hangoutPoint[0]:
            # This cog is going to be at a hangout point.
            self.setPosHpr(self.hangoutPoint[1][0], self.hangoutPoint[1][1], self.hangoutPoint[1][2],
                           self.hangoutPoint[2], 0, 0)
        else:
            # This cog will be in regular guard position.
            self.setPosHpr(self.guardPoint[0][0], self.guardPoint[0][1], self.guardPoint[0][2],
                           self.guardPoint[1], 0, 0)

        self.setAnimState('neutral')

    def exitGuard(self):
        pass

    def enterThink(self, ts):
        pass

    def exitThink(self):
        pass

    def enterChair(self, ts):
        self.show()
        self.cleanupPropeller()
        points = self.getPoints('chairs')
        self.setPosHpr(self.chairPoint[0][0], self.chairPoint[0][1], self.chairPoint[0][2], self.chairPoint[1], 0, 0)
        self.setAnimState('sit')
        self.disableRay()

    def exitChair(self):
        pass

    def enterChair2Battle(self, extraArgs, ts):
        pos = self.guardPoint[0]
        self.startProjInterval(self.getX(), self.getY(), self.getZ(), pos[0], pos[1], pos[2], 5.0, 0.05, ts)

    def exitChair2Battle(self):
        if self.moveIval:
            self.ignore(self.moveIval.getDoneEvent())
            self.moveIval.finish()
            self.moveIval = None

    def setState(self, state, timestamp):
        self.fsm.request(state, [globalClockDelta.localElapsedTime(timestamp)])
