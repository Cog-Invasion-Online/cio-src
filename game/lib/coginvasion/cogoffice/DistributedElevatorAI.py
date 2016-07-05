# Filename: DistributedElevatorAI.py
# Created by:  blach (14Dec15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.distributed.ClockDelta import globalClockDelta
from direct.fsm import ClassicFSM, State
from direct.task import Task

from ElevatorConstants import *

class DistributedElevatorAI(DistributedObjectAI):
    notify = directNotify.newCategory('DistributedElevatorAI')

    def __init__(self, air, bldg, toZoneId, elevatorType):
        DistributedObjectAI.__init__(self, air)
        self.bldg = bldg
        self.bldgDoId = self.bldg.doId
        self.toZoneId = toZoneId
        self.type = elevatorType
        self.fsm = ClassicFSM.ClassicFSM('DistributedElevatorAI', [State.State('off', self.enterOff, self.exitOff),
         State.State('opening', self.enterOpening, self.exitOpening),
         State.State('waitEmpty', self.enterWaitEmpty, self.exitWaitEmpty),
         State.State('waitCountdown', self.enterWaitCountdown, self.exitWaitCountdown),
         State.State('closing', self.enterClosing, self.exitClosing),
         State.State('closed', self.enterClosed, self.exitClosed)], 'off', 'off')
        self.fsm.enterInitialState()
        self.slots = [0, 1, 2, 3]
        self.slotTakenByAvatarId = {}
        self.stateTimestamp = 0
        
    def delete(self):
        self.fsm.requestFinalState()
        self.fsm = None
        self.bldg = None
        self.bldgDoId = None
        self.toZoneId = None
        self.type = None
        self.slots = None
        self.slotTakenByAvatarId = None
        self.stateTimeStamp = None
        DistributedObjectAI.delete(self)

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterOpening(self):
        base.taskMgr.doMethodLater(ElevatorData[self.type]['openTime'], self.openingTask, self.uniqueName('openingTask'))

    def openingTask(self, task):
        state = 'waitEmpty'
        if self.type == ELEVATOR_INT:
            state = 'waitCountdown'
        self.b_setState(state)
        return Task.done

    def exitOpening(self):
        base.taskMgr.remove(self.uniqueName('openingTask'))

    def enterWaitEmpty(self):
        pass

    def exitWaitEmpty(self):
        pass

    def enterWaitCountdown(self):
        base.taskMgr.doMethodLater(ElevatorData[self.type]['countdown'], self.waitCountdownTask, self.uniqueName('waitCountdownTask'))

    def waitCountdownTask(self, task):
        self.b_setState('closing')
        return Task.done

    def exitWaitCountdown(self):
        base.taskMgr.remove(self.uniqueName('waitCountdownTask'))

    def enterClosing(self):
        base.taskMgr.doMethodLater(ElevatorData[self.type]['closeTime'], self.closingTask, self.uniqueName('closingTask'))

    def closingTask(self, task):
        self.bldg.battle.b_setAvatars(self.getSortedAvatarList())
        self.slotTakenByAvatarId = {}
        self.b_setState('closed')
        return task.done

    def exitClosing(self):
        base.taskMgr.remove(self.uniqueName('closingTask'))

    def enterClosed(self):
        pass

    def exitClosed(self):
        pass

    def setState(self, state):
        self.fsm.request(state)

    def d_setState(self, state):
        self.stateTimestamp = globalClockDelta.getRealNetworkTime()
        self.sendUpdate('setState', [state, self.stateTimestamp])

    def b_setState(self, state):
        self.d_setState(state)
        self.setState(state)

    def requestStateAndTimestamp(self):
        avId = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId(avId, 'stateAndTimestamp', [self.fsm.getCurrentState().getName(), self.stateTimestamp])
        array = self.getSortedAvatarList()
        self.sendUpdateToAvatarId(avId, 'setToonsInElevator', [array])

    def getSortedAvatarList(self):
        array = []
        for avId, slot in self.slotTakenByAvatarId.items():
            array.append(avId)
        array.sort(key = lambda avId: self.slotTakenByAvatarId[avId])
        return array

    def getBldgDoId(self):
        return self.bldgDoId

    def getToZoneId(self):
        return self.toZoneId

    def getElevatorType(self):
        return self.type
        
    def allAvatarsBoardedTask(self, task):
        if self.type == ELEVATOR_INT:
            if len(self.slotTakenByAvatarId.values()) == len(self.bldg.avIds):
                self.b_setState('closing')
        return task.done

    def requestEnter(self):
        avId = self.air.getAvatarIdFromSender()
        if len(self.slotTakenByAvatarId) < len(ElevatorPoints) and not avId in self.slotTakenByAvatarId.keys() and self.fsm.getCurrentState().getName() in ['waitEmpty', 'waitCountdown']:
            if len(self.slotTakenByAvatarId) == 0 and self.type != ELEVATOR_INT:
                # First avatar aboard! Start counting down!
                self.b_setState('waitCountdown')
            slotToFill = -1
            for slotNum in self.slots:
                if not slotNum in self.slotTakenByAvatarId.values():
                    slotToFill = slotNum
                    break
            self.sendUpdate('fillSlot', [slotToFill, avId])
            self.slotTakenByAvatarId[avId] = slotToFill
            if self.type == ELEVATOR_INT:
                if len(self.slotTakenByAvatarId.values()) == len(self.bldg.avIds):
                    base.taskMgr.remove(self.uniqueName('allAvatarsBoardedTask'))
                    base.taskMgr.doMethodLater(0.7, self.allAvatarsBoardedTask, self.uniqueName('allAvatarsBoardedTask'))
        else:
            self.sendUpdateToAvatarId(avId, 'enterRejected', [])

    def requestExit(self):
        avId = self.air.getAvatarIdFromSender()
        if avId in self.slotTakenByAvatarId.keys() and self.fsm.getCurrentState().getName() in ['waitEmpty', 'waitCountdown']:
            slot = self.slotTakenByAvatarId[avId]
            del self.slotTakenByAvatarId[avId]
            self.sendUpdate('emptySlot', [slot, avId])
            if len(self.slotTakenByAvatarId) == 0 and self.type != ELEVATOR_INT:
                # Everyone left! Stop the timer!
                self.b_setState('waitEmpty')
