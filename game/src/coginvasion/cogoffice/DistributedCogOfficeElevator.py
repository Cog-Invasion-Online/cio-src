"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedCogOfficeElevator.py
@author Brian Lach
@date December 15, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.hood import ZoneUtil
from ElevatorConstants import *
from ElevatorUtils import *
from DistributedElevator import DistributedElevator

class DistributedCogOfficeElevator(DistributedElevator):
    notify = directNotify.newCategory('DistributedCogOfficeElevator')

    # In this class, self.thebldg is the DistributedCogOfficeBattle associated with this elevator.

    def __init__(self, cr):
        DistributedElevator.__init__(self, cr)
        self.index = None

    def setIndex(self, index):
        self.index = index

    def getIndex(self):
        return self.index

    def getLeftDoor(self):
        return self.thebldg.elevators[self.index].getLeftDoor()

    def getRightDoor(self):
        return self.thebldg.elevators[self.index].getRightDoor()

    def postAnnounceGenerate(self):
        DistributedElevator.postAnnounceGenerate(self)
        # We've polled the building and found it, tell the building that this elevator is ready.
        self.thebldg.elevatorReady()
        self.accept(self.thebldg.uniqueName('prepareElevator'), self.__prepareElevator)

    def disable(self):
        self.ignore(self.thebldg.uniqueName('prepareElevator'))
        DistributedElevator.disable(self)

    def __prepareElevator(self):
        self.countdownTextNP.reparentTo(self.getElevatorModel())
        self.elevatorSphereNodePath.reparentTo(self.getElevatorModel())
        base.physicsWorld.attach(self.elevatorSphereNode)
        self.openDoors = getOpenInterval(self, self.getLeftDoor(), self.getRightDoor(), self.openSfx, None, self.type)
        self.closeDoors = getCloseInterval(self, self.getLeftDoor(), self.getRightDoor(), self.closeSfx, None, self.type)
        self.closeDoors = Sequence(self.closeDoors, Func(self.onDoorCloseFinish))
        closeDoors(self.getLeftDoor(), self.getRightDoor())

    def putToonsInElevator(self):
        for i in xrange(len(self.thebldg.avIds)):
            avId = self.thebldg.avIds[i]
            toon = self.cr.doId2do.get(avId)
            if toon:
                toon.stopSmooth()
                toon.animFSM.request('neutral')
                toon.reparentTo(self.getElevatorModel())
                if self.thebldg.currentFloor == 0:
                    toon.setPos(ElevatorPoints[i])
                toon.setHpr(180, 0, 0)

    def onDoorCloseFinish(self):
        print "Door close finish for index {0}".format(self.index)
        print "Are we on this elevator? {0}".format(self.localAvOnElevator)
        if self.index == 1:
            if self.localAvOnElevator:
                print "Ready for next floor."
                base.transitions.fadeScreen(1)
                self.thebldg.d_readyForNextFloor()
                self.localAvOnElevator = False
            else:
                print "Heading back to the playground."
                requestStatus = {'zoneId': ZoneUtil.getZoneId(ZoneUtil.getHoodId(self.zoneId, street = 1)),
                            'hoodId': self.cr.playGame.hood.hoodId,
                            'where': 'playground',
                            'avId': base.localAvatar.doId,
                            'loader': 'safeZoneLoader',
                            'shardId': None,
                            'wantLaffMeter': 1,
                            'world': base.cr.playGame.getCurrentWorldName(),
                            'how': 'teleportIn'}
                self.cr.playGame.getPlace().doneStatus = requestStatus
                messenger.send(self.cr.playGame.getPlace().doneEvent)

    def getElevatorModel(self):
        return self.thebldg.elevators[self.index].getElevatorModel()
