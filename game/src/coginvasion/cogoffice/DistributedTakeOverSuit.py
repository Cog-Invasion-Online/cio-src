"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedTakeOverSuit.py
@author Brian Lach
@date June 14, 2016

"""

from panda3d.core import Point3

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.interval.IntervalGlobal import LerpPosInterval, Parallel, Sequence, Wait, Func
from direct.distributed.ClockDelta import globalClockDelta

from src.coginvasion.cog.DistributedSuit import DistributedSuit

class DistributedTakeOverSuit(DistributedSuit):
    notify = directNotify.newCategory("DistributedTakeOverSuit")

    StartPosFromDoor = Point3(1.6, -10, -0.5)
    AtDoorPos = Point3(1.6, -1, 0)

    def __init__(self, cr):
        DistributedSuit.__init__(self, cr)
        self.showNametagInMargins = True
        self.doorDoId = None
        self.door = None
        self.takeOverTrack = None
        self.fsm = ClassicFSM('DTOS-fsm',
                              [State('off', self.enterOff, self.exitOff),
                               State('takeOver', self.enterTakeOver, self.exitTakeOver)],
                              'off', 'off')
        self.fsm.enterInitialState()

    def interruptTakeOver(self):
        if self.takeOverTrack:
            self.takeOverTrack.pause()
            self.takeOverTrack = None

    def setState(self, state, timestamp):
        ts = globalClockDelta.localElapsedTime(timestamp)
        self.fsm.request(state, [ts])

    def disable(self):
        taskMgr.remove('posTask')
        self.fsm.requestFinalState()
        self.fsm = None
        self.doorDoId = None
        self.door = None
        if self.takeOverTrack:
            self.takeOverTrack.finish()
            self.takeOverTrack = None

        DistributedSuit.disable(self)

    def setDoorDoId(self, doId):
        self.doorDoId = doId
        self.door = self.cr.doId2do.get(doId)
        if self.door is None:
            taskMgr.add(self.__pollDoor, self.uniqueName('pollDoor'))

    def stateAndTimestamp(self, state, timestamp):
        self.setState(state, timestamp)

    def __pollDoor(self, task):
        self.door = self.cr.doId2do.get(self.doorDoId)
        if self.door:
            self.sendUpdate('requestStateAndTimestamp')
            return task.done
        return task.cont

    def getDoorDoId(self):
        return self.doorDoId

    def enterOff(self, ts = 0):
        pass

    def exitOff(self):
        pass

    def enterTakeOver(self, ts = 0):
        if not self.door:
            return
        self.stopSmooth()
        self.hasSpawned = False
        self.doingActivity = True
        self.reparentTo(self.door.doorNode)
        self.setHpr(0, 0, 0)
        self.takeOverTrack = Parallel(
            Sequence(
                Func(self.animFSM.request, 'flyDown', [ts]),
                Wait(6.834),
                Func(self.loop, 'neutral'),
                Wait(0.5),
                Func(self.loop, 'walk'),
                LerpPosInterval(self, duration = 2.0, pos = render.getRelativePoint(self.door.doorNode, self.AtDoorPos),
                                startPos = render.getRelativePoint(self.door.doorNode, self.StartPosFromDoor)),
                Func(self.loop, 'neutral'),
                Wait(0.3),
                Func(self.loop, 'walk'),
                LerpPosInterval(self, duration = 0.5, pos = self.door.enterWalkBackPos,
                                startPos = self.AtDoorPos),
                Func(self.loop, 'neutral'),
                Wait(1.0),
                Func(self.loop, 'walk'),
                LerpPosInterval(self, duration = 1.0, pos = self.door.enterWalkInPos,
                                startPos = self.door.enterWalkBackPos)),
            LerpPosInterval(self,
                            duration = 4.375,
                            pos = render.getRelativePoint(self.door.doorNode, self.StartPosFromDoor),
                            startPos = render.getRelativePoint(self.door.doorNode, self.StartPosFromDoor) + (0, 0, 6.5 * 4.8))
        )
        self.takeOverTrack.start(ts)

    def exitTakeOver(self):
        self.doingActivity = False
        if self.takeOverTrack:
            self.takeOverTrack.pause()
            self.takeOverTrack = None
