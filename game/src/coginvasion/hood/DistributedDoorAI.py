"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedDoorAI.py
@author Brian Lach
@date July 27, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed import DistributedObjectAI, ClockDelta

class DistributedDoorAI(DistributedObjectAI.DistributedObjectAI):
    notify = directNotify.newCategory("DistributedDoorAI")

    OPEN_TO_CLOSE_TIME = 1.0
    CLOSE_TO_OPEN_TIME = 1.7
    OPEN_TIME = 1.5

    def __init__(self, air, block, toZone, doorType = 1, doorIndex = 0):
        DistributedObjectAI.DistributedObjectAI.__init__(self, air)
        self.block = block
        self.toZone = toZone
        self.doorType = doorType
        self.doorIndex = doorIndex
        self.rightDoorStates = ['closed', 'open', 'closing', 'opening']
        self.leftDoorStates = ['closed', 'open', 'closing', 'opening']
        self.leftDoorState = ''
        self.rightDoorState = ''
        self.rightDoorCloseToOpenTask = None
        self.rightDoorOpenTask = None
        self.rightDoorOpenToCloseTask = None
        self.leftDoorCloseToOpenTask = None
        self.leftDoorOpenTask = None
        self.leftDoorOpenToCloseTask = None
        self.suitTakingOver = 0

    def b_setSuitTakingOver(self, flag):
        self.sendUpdate('setSuitTakingOver', [flag])
        self.suitTakingOver = flag

    def getSuitTakingOver(self):
        return self.suitTakingOver

    def getDoorIndex(self):
        return self.doorIndex

    def announceGenerate(self):
        DistributedObjectAI.DistributedObjectAI.announceGenerate(self)
        self.b_setLeftDoorState('closed')
        self.b_setRightDoorState('closed')

    def delete(self):
        self.__removeAllLeft()
        self.__removeAllRight()
        self.leftDoorStates = None
        self.rightDoorStates = None
        self.block = None
        self.toZone = None
        self.rightDoorState = None
        self.leftDoorState = None
        self.toBlock = None
        self.suitTakingOver = None
        DistributedObjectAI.DistributedObjectAI.delete(self)

    def setDoorType(self, doorType):
        self.doorType = doorType

    def d_setDoorType(self, doorType):
        self.sendUpdate('setDoorType', [doorType])

    def b_setDoorType(self, doorType):
        self.d_setDoorType(doorType)
        self.setDoorType(doorType)

    def getDoorType(self):
        return self.doorType

    def setBlock(self, block):
        self.block = block

    def d_setBlock(self, block):
        self.sendUpdate('setBlock', [block])

    def b_setBlock(self, block):
        self.d_setBlock(block)
        self.setBlock(block)

    def getBlock(self):
        return self.block

    def setToZone(self, zone):
        self.toZone = zone

    def d_setToZone(self, zone):
        self.sendUpdate('setToZone', [zone])

    def b_setToZone(self, zone):
        self.d_setToZone(zone)
        self.setToZone(zone)

    def getToZone(self):
        return self.toZone

    def setRightDoorState(self, state):
        self.rightDoorState = state

    def d_setRightDoorState(self, state):
        timestamp = ClockDelta.globalClockDelta.getRealNetworkTime()
        self.sendUpdate('setRightDoorState', [state, timestamp])

    def b_setRightDoorState(self, state):
        self.d_setRightDoorState(state)
        self.setRightDoorState(state)

    def getRightDoorState(self):
        return self.rightDoorState

    def setLeftDoorState(self, state):
        self.leftDoorState = state

    def d_setLeftDoorState(self, state):
        timestamp = ClockDelta.globalClockDelta.getRealNetworkTime()
        self.sendUpdate('setLeftDoorState', [state, timestamp])

    def b_setLeftDoorState(self, state):
        self.d_setLeftDoorState(state)
        self.setLeftDoorState(state)

    def getLeftDoorState(self):
        return self.leftDoorState

    def __removeAllRight(self):
        self.__removeRightOpenToClose()
        self.__removeRightOpen()
        self.__removeRightCloseToOpen()

    def __removeAllLeft(self):
        self.__removeLeftOpenToClose()
        self.__removeLeftOpen()
        self.__removeLeftCloseToOpen()

    def __removeRightOpenToClose(self):
        if self.rightDoorOpenToCloseTask:
            base.taskMgr.remove(self.rightDoorOpenToCloseTask)
            self.rightDoorOpenToCloseTask = None

    def __removeRightCloseToOpen(self):
        if self.rightDoorCloseToOpenTask:
            base.taskMgr.remove(self.rightDoorCloseToOpenTask)
            self.rightDoorCloseToOpenTask = None

    def __removeRightOpen(self):
        if self.rightDoorOpenTask:
            base.taskMgr.remove(self.rightDoorOpenTask)
            self.rightDoorOpenTask = None

    def __removeLeftOpenToClose(self):
        if self.leftDoorOpenToCloseTask:
            base.taskMgr.remove(self.leftDoorOpenToCloseTask)
            self.leftDoorOpenToCloseTask = None

    def __removeLeftCloseToOpen(self):
        if self.leftDoorCloseToOpenTask:
            base.taskMgr.remove(self.leftDoorCloseToOpenTask)
            self.leftDoorCloseToOpenTask = None

    def __removeLeftOpen(self):
        if self.leftDoorOpenTask:
            base.taskMgr.remove(self.leftDoorOpenTask)
            self.leftDoorOpenTask = None

    def _rightCloseToOpenDone(self, task):
        self.__removeRightCloseToOpen()
        self.b_setRightDoorState('open')
        self.rightDoorOpenTask = base.taskMgr.doMethodLater(self.OPEN_TIME,
            self._rightOpenDone, self.uniqueName('rightOpenDone'))

    def _rightOpenDone(self, task):
        self.__removeRightOpen()
        self.b_setRightDoorState('closing')
        self.rightOpenToCloseTask = base.taskMgr.doMethodLater(self.OPEN_TO_CLOSE_TIME,
            self._rightOpenToCloseDone, self.uniqueName('rightOpenToCloseDone'))

    def _rightOpenToCloseDone(self, task):
        self.__removeRightOpenToClose()
        self.b_setRightDoorState('closed')

    def requestEnter(self, isTakeOverSuit = False):
        if not isTakeOverSuit:
            avId = self.air.getAvatarIdFromSender()
            timestamp = ClockDelta.globalClockDelta.getRealNetworkTime()
            self.sendUpdate('enterDoor', [avId, timestamp])
        if self.rightDoorState == 'closed':
            self.b_setRightDoorState('opening')
        self.__removeRightOpen()
        self.__removeRightOpenToClose()
        self.rightDoorCloseToOpenTask = base.taskMgr.doMethodLater(self.CLOSE_TO_OPEN_TIME,
            self._rightCloseToOpenDone, self.uniqueName('rightCloseToOpenDone'))

    def _leftCloseToOpenDone(self, task):
        self.__removeLeftCloseToOpen()
        self.b_setLeftDoorState('open')
        self.leftDoorOpenTask = base.taskMgr.doMethodLater(self.OPEN_TIME,
            self._leftOpenDone, self.uniqueName('leftOpenDone'))

    def _leftOpenDone(self, task):
        self.__removeLeftOpen()
        self.b_setLeftDoorState('closing')
        self.leftOpenToCloseTask = base.taskMgr.doMethodLater(self.OPEN_TO_CLOSE_TIME,
            self._leftOpenToCloseDone, self.uniqueName('leftOpenToCloseDone'))

    def _leftOpenToCloseDone(self, task):
        self.__removeLeftOpenToClose()
        self.b_setLeftDoorState('closed')

    def requestExit(self):
        avId = self.air.getAvatarIdFromSender()
        timestamp = ClockDelta.globalClockDelta.getRealNetworkTime()
        self.sendUpdate('exitDoor', [avId, timestamp])
        if self.leftDoorState == 'closed':
            self.b_setLeftDoorState('opening')
        self.__removeLeftOpen()
        self.__removeLeftOpenToClose()
        self.leftDoorCloseToOpenTask = base.taskMgr.doMethodLater(self.CLOSE_TO_OPEN_TIME,
            self._leftCloseToOpenDone, self.uniqueName('leftCloseToOpenDone'))
