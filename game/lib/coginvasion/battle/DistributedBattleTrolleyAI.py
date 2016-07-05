# Filename: DistributedBattleTrolleyAI.py
# Created by:  blach (28Oct15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.distributed.ClockDelta import globalClockDelta
from direct.fsm import ClassicFSM, State

from lib.coginvasion.suit import CogBattleGlobals
from lib.coginvasion.suit.DistributedCogBattleAI import DistributedCogBattleAI

class DistributedBattleTrolleyAI(DistributedObjectAI):
    notify = directNotify.newCategory('DistributedBattleTrolleyAI')

    NUM_SLOTS = base.config.GetInt('trolley-slots', 8)

    def __init__(self, air, hoodIndex):
        DistributedObjectAI.__init__(self, air)
        self.fsm = ClassicFSM.ClassicFSM('DBTrolleyAI', [State.State('off', self.enterOff, self.exitOff),
         State.State('wait', self.enterWait, self.exitWait),
         State.State('waitCountdown', self.enterWaitCountdown, self.exitWaitCountdown),
         State.State('leaving', self.enterLeaving, self.exitLeaving),
         State.State('arriving', self.enterArriving, self.exitArriving)], 'wait', 'off')
        self.fsm.enterInitialState()
        self.hoodIndex = hoodIndex

        if DistributedBattleTrolleyAI.NUM_SLOTS == 8:
            self.slots = [0, 1, 2, 3, 4, 5, 6, 7]
        else:
            self.slots = [4, 5, 6, 7]

        self.slotTakenByAvatarId = {}
        self.state = 'off'
        self.stateTimestamp = 0

    def getHoodIndex(self):
        return self.hoodIndex

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

    def exitWaitCountdown(self):
        base.taskMgr.remove(self.uniqueName('sendOffToons'))

    def enterLeaving(self):
        base.taskMgr.doMethodLater(5.0, self.__trolleyLeft, self.uniqueName('trolleyLeft'))

    def __trolleyLeft(self, task):
        self.createBattle()
        self.slotTakenByAvatarId = {}
        self.b_setState('arriving')
        return task.done

    def createBattle(self):
		zone = base.air.allocateZone()
		avIdArray = []
		for avId in self.slotTakenByAvatarId.keys():
			avIdArray.append(avId)
		battle = DistributedCogBattleAI(self.air)
		battle.generateWithRequired(zone)
		battle.setNumPlayers(len(self.slotTakenByAvatarId))
		battle.b_setHoodIndex(self.getHoodIndex())
		battle.b_setTotalCogs(CogBattleGlobals.HoodIndex2TotalCogs[self.getHoodIndex()])
		battle.b_setCogsRemaining(CogBattleGlobals.HoodIndex2TotalCogs[self.getHoodIndex()])
		battle.setAvIdArray(avIdArray)
		for avId in self.slotTakenByAvatarId.keys():
			self.sendUpdateToAvatarId(avId, 'headOff', [zone])

    def exitLeaving(self):
        base.taskMgr.remove(self.uniqueName('trolleyLeft'))

    def enterArriving(self):
        base.taskMgr.doMethodLater(5.0, self.__trolleyArrived, self.uniqueName('trolleyArrived'))

    def __trolleyArrived(self, task):
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
            if len(self.slotTakenByAvatarId) == 0:
                # First avatar aboard! Start counting down!
                self.b_setState('waitCountdown')
            slotToFill = -1
            for slotNum in self.slots:
                if not slotNum in self.slotTakenByAvatarId.values():
                    slotToFill = slotNum
                    break
            self.sendUpdate('fillSlot', [slotToFill, avId])
            self.slotTakenByAvatarId[avId] = slotToFill
        else:
            self.sendUpdateToAvatarId(avId, 'rejectBoard', [])

    def requestHopOff(self):
        avId = self.air.getAvatarIdFromSender()
        if avId in self.slotTakenByAvatarId.keys() and self.fsm.getCurrentState().getName() in ['wait', 'waitCountdown']:
            slot = self.slotTakenByAvatarId[avId]
            del self.slotTakenByAvatarId[avId]
            self.sendUpdate('emptySlot', [slot, avId])
            if len(self.slotTakenByAvatarId) == 0:
                # Everyone left! Stop the timer!
                self.b_setState('wait')
