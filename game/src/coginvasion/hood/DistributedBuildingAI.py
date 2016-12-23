# Filename: DistributedBuildingAI.py
# Created by:  blach (14Dec15)

from direct.distributed.DistributedObjectAI import DistributedObjectAI
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.ClockDelta import globalClockDelta
from direct.fsm import ClassicFSM, State
from direct.task import Task

from src.coginvasion.globals import CIGlobals
from src.coginvasion.hood import ZoneUtil
from src.coginvasion.cog import Dept
from src.coginvasion.cogoffice import SuitBuildingGlobals
from src.coginvasion.cogoffice.DistributedElevatorAI import DistributedElevatorAI
from src.coginvasion.cogoffice.DistributedCogOfficeBattleAI import DistributedCogOfficeBattleAI

from DistributedToonInteriorAI import DistributedToonInteriorAI
from DistributedDoorAI import DistributedDoorAI

from src.coginvasion.cogoffice.ElevatorConstants import *

import random

class DistributedBuildingAI(DistributedObjectAI):
    notify = directNotify.newCategory('DistributedBuildingAI')

    def __init__(self, air, blockNumber, zoneId, canonicalZoneId, hood):
        DistributedObjectAI.__init__(self, air)
        self.block = blockNumber
        self.zoneId = zoneId
        self.hood = hood
        self.canonicalZoneId = canonicalZoneId
        self.victorResponses = None
        self.fsm = ClassicFSM.ClassicFSM('DistributedBuildingAI', [State.State('off', self.enterOff, self.exitOff),
         State.State('waitForVictors', self.enterWaitForVictors, self.exitWaitForVictors),
         State.State('becomingToon', self.enterBecomingToon, self.exitBecomingToon),
         State.State('toon', self.enterToon, self.exitToon),
         State.State('becomingSuit', self.enterBecomingSuit, self.exitBecomingSuit),
         State.State('suit', self.enterSuit, self.exitSuit)], 'off', 'off')
        self.fsm.enterInitialState()
        self.suitDept = 'c'
        self.difficulty = 1
        self.numFloors = 0
        self.frontDoorPoint = None
        self.takenBySuit = False
        self.victorList = [0, 0, 0, 0]

    def cleanup(self):
        if self.isDeleted():
            return
        self.fsm.requestFinalState()
        if hasattr(self, 'interior'):
            self.interior.requestDelete()
            del self.interior
        if hasattr(self, 'elevator'):
            self.elevator.requestDelete()
            del self.elevator
        self.requestDelete()

    def delete(self):
        self.cleanup()
        taskMgr.remove(self.taskName(str(self.block) + 'toonBldg-timer'))
        taskMgr.remove(self.taskName(str(self.block) + '_becomingToon-timer'))
        taskMgr.remove(self.taskName(str(self.block) + '_becomingSuit-timer'))
        DistributedObjectAI.delete(self)
        del self.fsm

    def suitTakeOver(self, suitDept, difficulty, numFloors):
        difficulty = 1
        self.suitDept = suitDept.getClothingPrefix()
        self.difficulty = difficulty
        self.numFloors = numFloors
        self.fsm.request('becomingSuit')

    def enterBecomingSuit(self):
        self.sendUpdate('setSuitData', [self.suitDept, self.difficulty, self.numFloors])
        self.d_setState('becomingSuit')
        name = self.taskName(str(self.block) + '_becomingSuit-timer')
        taskMgr.doMethodLater(SuitBuildingGlobals.TO_SUIT_BLDG_TIME, self.becomingSuitTask, name)

    def exitBecomingSuit(self):
        name = self.taskName(str(self.block) + '_becomingSuit-timer')
        taskMgr.remove(name)
        if hasattr(self, 'interior'):
            self.interior.requestDelete()
            del self.interior
            self.door.requestDelete()
            del self.door
            self.insideDoor.requestDelete()
            del self.insideDoor

    def becomingSuitTask(self, task):
        self.fsm.request('suit')
        return Task.done

    def getExteriorAndInteriorZoneId(self):
        dnaStore = self.air.dnaStoreMap[self.canonicalZoneId]
        zoneId = dnaStore.getZoneFromBlockNumber(self.block)
        zoneId = ZoneUtil.getTrueZoneId(zoneId, self.zoneId)
        interiorZoneId = (zoneId - (zoneId % 100)) + 500 + self.block
        return (zoneId, interiorZoneId)

    def setState(self, state, timestamp = 0):
        self.fsm.request(state)

    def getState(self):
        return [self.fsm.getCurrentState().getName(), globalClockDelta.getRealNetworkTime()]

    def getSuitData(self):
        return [self.suitDept, self.difficulty, self.numFloors]

    def d_setState(self, state):
        self.sendUpdate('setState', [state, globalClockDelta.getRealNetworkTime()])

    def enterSuit(self):
        self.sendUpdate('setSuitData', [self.suitDept, self.difficulty, self.numFloors])
        self.d_setState('suit')
        exteriorZoneId, interiorZoneId = self.getExteriorAndInteriorZoneId()
        self.elevator = DistributedElevatorAI(self.air, self, self.getBlock()[1], ELEVATOR_NORMAL)
        self.elevator.generateWithRequired(exteriorZoneId)
        self.elevator.b_setState('opening')
        self.battle = DistributedCogOfficeBattleAI(self.air, self.numFloors, self.suitDept, self.hood, self, exteriorZoneId)
        self.battle.generateWithRequired(interiorZoneId)

    def exitSuit(self):
        if hasattr(self, 'elevator'):
            self.elevator.requestDelete()
            del self.elevator

    def setVictorList(self, victorList):
        self.victorList = victorList

    def d_setVictorList(self, victorList):
        self.sendUpdate('setVictorList', [victorList])

    def b_setVictorList(self, victorList):
        self.d_setVictorList(victorList)
        self.setVictorList(victorList)

    def getVictorList(self):
        return self.victorList

    def toonTakeOver(self):
        self.fsm.request('becomingToon')
        if hasattr(self, 'battle'):
            self.battle.requestDelete()
            del self.battle

    def getFrontDoorPoint(self):
        return self.frontDoorPoint

    def setFrontDoorPoint(self, point):
        self.frontDoorPoint = point

    def getBlock(self):
        (dummy, interiorZoneId) = self.getExteriorAndInteriorZoneId()
        return [self.block, interiorZoneId]

    def enterBecomingToon(self):
        self.d_setState('becomingToon')
        name = self.taskName(str(self.block) + '_becomingToon-timer')
        taskMgr.doMethodLater(SuitBuildingGlobals.VICTORY_SEQUENCE_TIME, self.becomingToonTask, name)

    def exitBecomingToon(self):
        name = self.taskName(str(self.block) + '_becomingToon-timer')
        taskMgr.remove(name)

    def becomingToonTask(self, task):
        self.fsm.request('toon')
        return Task.done

    def enterToon(self):
        self.takenBySuit = False
        self.d_setState('toon')
        (exteriorZone, interiorZone) = self.getExteriorAndInteriorZoneId()
        self.interior = DistributedToonInteriorAI(self.air, self.block, exteriorZone)
        self.interior.generateWithRequired(interiorZone)
        self.door = DistributedDoorAI(self.air, self.block, interiorZone, 1)
        self.door.generateWithRequired(exteriorZone)

    def toonTimeoutTask(self, task):
        self.suitTakeOver(random.choice([Dept.SALES, Dept.CASH, Dept.LAW, Dept.BOSS]), 0, 0)
        return Task.done

    def exitToon(self):
        if hasattr(self, 'interior'):
            self.interior.requestDelete()
            del self.interior
        if hasattr(self, 'door'):
            self.door.requestDelete()
            del self.door

    def enterWaitForVictors(self, victorList):
        activeToons = []
        for t in victorList:
            toon = None
            if t:
                toon = self.getToon(t)
            if toon is not None:
                activeToons.append(toon)
        for i in xrange(0, 4):
            victor = victorList[i]
            if (victor is None) or (victor not in self.air.doId2do):
                victorList[i] = 0
                continue
        self.b_setVictorList(victorList)
        self.victorResponses = [0, 0, 0, 0]
        self.d_setState('waitForVictors')

    def exitWaitForVictors(self):
        self.victorResponses = None

    def getToon(self, avId):
        return self.air.doId2do.get(avId, None)

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def findVictorIndex(self, avId):
        for i in xrange(len(self.victorList)):
            if self.victorList[i] == avId:
                return i

    def recordVictorResponse(self, avId):
        index = self.findVictorIndex(avId)
        self.victorResponses[index] = avId

    def allVictorsResponded(self):
        if self.victorResponses == self.victorList:
            return 1
        else:
            return 0

    def setVictorReady(self):
        avId = self.air.getAvatarIdFromSender()
        self.recordVictorResponse(avId)
        if self.allVictorsResponded():
            self.toonTakeOver()
