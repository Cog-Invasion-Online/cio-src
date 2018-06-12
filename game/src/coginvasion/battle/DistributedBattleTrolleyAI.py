"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedBattleTrolleyAI.py
@author Brian Lach
@date October 28, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.distributed.ClockDelta import globalClockDelta
from direct.fsm import ClassicFSM, State

class DistributedBattleTrolleyAI(DistributedObjectAI):
    notify = directNotify.newCategory('DistributedBattleTrolleyAI')

    NUM_SLOTS = base.config.GetInt('trolley-slots', 8)

    def __init__(self, air, toZone, index):
        DistributedObjectAI.__init__(self, air)
        self.fsm = ClassicFSM.ClassicFSM('DBTrolleyAI', [State.State('off', self.enterOff, self.exitOff),
         State.State('wait', self.enterWait, self.exitWait),
         State.State('waitCountdown', self.enterWaitCountdown, self.exitWaitCountdown),
         State.State('leaving', self.enterLeaving, self.exitLeaving),
         State.State('arriving', self.enterArriving, self.exitArriving)], 'wait', 'off')
        self.fsm.enterInitialState()
        self.toZone = toZone
        self.index = index

        if DistributedBattleTrolleyAI.NUM_SLOTS == 8:
            self.slots = [0, 1, 2, 3, 4, 5, 6, 7]
        else:
            self.slots = [4, 5, 6, 7]

        self.slotTakenByAvatarId = {}
        self.state = 'off'
        self.stateTimestamp = 0

    def getToZone(self):
        return self.toZone
        
    def getIndex(self):
        return self.index

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterWait(self):
        pass

    def exitWait(self):
        pass

    def enterWaitCountdown(self):
        base.taskMgr.doMethodLater(10.0, self.__sendOffToons, self.uniqueName('sendOffToons'))

    def __sendOffToons(self, task):
        self.b_setState('leaving')
        return task.done
        
    def trolleyArriving(self):
        self.b_setState('arriving')

    def exitWaitCountdown(self):
        base.taskMgr.remove(self.uniqueName('sendOffToons'))

    def enterLeaving(self):
        base.taskMgr.doMethodLater(5.0, self.__trolleyLeft, self.uniqueName('trolleyLeft'))

    def __trolleyLeft(self, task):
        self.slotTakenByAvatarId = {}
        self.b_setState("arriving")
        return task.done

    def exitLeaving(self):
        base.taskMgr.remove(self.uniqueName('trolleyLeft'))

    def enterArriving(self):
        base.taskMgr.doMethodLater(5.0, self.__trolleyArrived, self.uniqueName('trolleyArrived'))

    def __trolleyArrived(self, task):
        self.slotTakenByAvatarId = {}
        self.b_setState('wait')
        return task.done

    def exitArriving(self):
        base.taskMgr.remove(self.uniqueName('trolleyArrived'))

    def setState(self, stateName):
        self.state = stateName
        self.fsm.request(stateName)

    def d_setState(self, stateName):
        self.stateTimestamp = globalClockDelta.getRealNetworkTime()
        self.sendUpdate('setState', [stateName, self.stateTimestamp])

    def b_setState(self, stateName):
        self.d_setState(stateName)
        self.setState(stateName)

    def getState(self):
        return [self.state, self.stateTimestamp]

    def requestBoard(self):
        avId = self.air.getAvatarIdFromSender()
        if len(self.slotTakenByAvatarId) < self.NUM_SLOTS and not avId in self.slotTakenByAvatarId.keys() and self.fsm.getCurrentState().getName() in ['wait', 'waitCountdown']:
            slotToFill = -1
            for slotNum in self.slots:
                if not slotNum in self.slotTakenByAvatarId.values():
                    slotToFill = slotNum
                    break
            self.sendUpdate('fillSlot', [slotToFill, avId])
            self.slotTakenByAvatarId[avId] = slotToFill
            if len(self.slotTakenByAvatarId) == 1:
                self.b_setState("waitCountdown")
        else:
            self.sendUpdateToAvatarId(avId, 'rejectBoard', [])

    def requestHopOff(self):
        avId = self.air.getAvatarIdFromSender()
        if avId in self.slotTakenByAvatarId.keys() and self.fsm.getCurrentState().getName() in ['wait', 'waitCountdown']:
            slot = self.slotTakenByAvatarId[avId]
            del self.slotTakenByAvatarId[avId]
            self.sendUpdate('emptySlot', [slot, avId])
            if len(self.slotTakenByAvatarId) == 0:
                self.b_setState("wait")
