"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedButterflyAI.py
@author Brian Lach
@date December 28, 2017

"""

from direct.distributed.DistributedNodeAI import DistributedNodeAI
from direct.distributed.ClockDelta import globalClockDelta
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State

import ButterflyGlobals

import random

class DistributedButterflyAI(DistributedNodeAI):
    notify = directNotify.newCategory('DistributedButterflyAI')

    def __init__(self, air, hood, wingType):
        DistributedNodeAI.__init__(self, air)
        self.hood = hood
        self.wingType = wingType
        self.state = 0
        self.stateChangeTimestamp = 0.0
        self.fromLoc = 0
        self.toLoc = 0

        self.fsm = ClassicFSM('DBFAI', [State('off', self.enterOff, self.exitOff),
                                        State('sit', self.enterSit, self.exitSit),
                                        State('fly', self.enterFly, self.exitFly)],
                              'off', 'off')
        self.fsm.enterInitialState()

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterSit(self, fromLoc, toLoc):
        taskMgr.doMethodLater(random.uniform(*ButterflyGlobals.SitTime), self.__flySomewhere, self.uniqueName('stopSittingTask'))

    def __flySomewhere(self, task):
        toLoc = ButterflyGlobals.Spots[self.hood].index(random.choice(ButterflyGlobals.Spots[self.hood]))
        fromLoc = self.toLoc

        self.b_setState(2, fromLoc, toLoc)
        return task.done

    def exitSit(self):
        taskMgr.remove(self.uniqueName('stopSittingTask'))

    def enterFly(self, fromLoc, toLoc):
        distance = (ButterflyGlobals.Spots[self.hood][toLoc] - ButterflyGlobals.Spots[self.hood][fromLoc]).length()
        time = distance / ButterflyGlobals.Speed
        taskMgr.doMethodLater(time, self.__land, self.uniqueName('landTask'))

    def __land(self, task):
        self.b_setState(1, self.toLoc, self.toLoc)
        return task.done

    def exitFly(self):
        taskMgr.remove(self.uniqueName('landTask'))

    def setState(self, state, fromLoc, toLoc):
        self.state = state
        self.fromLoc = fromLoc
        self.toLoc = toLoc
        self.fsm.request(ButterflyGlobals.StateIdx2State[state], [fromLoc, toLoc])

    def b_setState(self, state, fromLoc, toLoc):
        self.setState(state, fromLoc, toLoc)
        self.d_setState(state, fromLoc, toLoc)

    def d_setState(self, state, fromLoc, toLoc):
        self.stateChangeTimestamp = globalClockDelta.getRealNetworkTime()
        self.sendUpdate('setState', [state, fromLoc, toLoc, self.stateChangeTimestamp])

    def getState(self):
        return [self.state, self.fromLoc, self.toLoc, self.stateChangeTimestamp]

    def getWingType(self):
        return self.wingType

    def getHood(self):
        return self.hood

    def announceGenerate(self):
        DistributedNodeAI.announceGenerate(self)
        loc = ButterflyGlobals.Spots[self.hood].index(random.choice(ButterflyGlobals.Spots[self.hood]))
        self.b_setState(1, loc, loc)

    def delete(self):
        self.fsm.requestFinalState()
        self.hood = None
        self.state = None
        self.toLoc = None
        self.fromLoc = None
        self.stateChangeTimestamp = None
        self.wingType = None
        DistributedNodeAI.delete(self)
