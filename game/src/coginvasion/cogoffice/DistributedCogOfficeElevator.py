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
from src.coginvasion.szboss.DistributedEntity import DistributedEntity

from ElevatorConstants import LIGHT_ON_COLOR, LIGHT_OFF_COLOR

class Elevator:

    BLDG = 0
    COGDO = 1

    def __init__(self, etype):
        if etype == Elevator.BLDG:
            self.elevatorMdl = loader.loadModel("phase_4/models/modules/elevator.bam")
        elif etype == Elevator.COGDO:
            self.elevatorMdl = loader.loadModel('phase_7/models/modules/cogoffice_elevator.bam')
            
        self.elevatorMdl.reparentTo(render)
        base.enablePhysicsNodes(self.elevatorMdl)
        self.leftDoor = getLeftDoor(self.elevatorMdl)
        self.rightDoor = getRightDoor(self.elevatorMdl)

    def getRightDoor(self):
        return self.rightDoor

    def getLeftDoor(self):
        return self.leftDoor

    def getElevatorModel(self):
        return self.elevatorMdl

    def cleanup(self):
        base.disableAndRemovePhysicsNodes(self.elevatorMdl)
        self.elevatorMdl.removeNode()
        del self.elevatorMdl
        
        del self.rightDoor
        del self.leftDoor

class DistributedCogOfficeElevator(DistributedElevator, DistributedEntity):
    notify = directNotify.newCategory('DistributedCogOfficeElevator')

    # In this class, self.thebldg is the DistributedCogOfficeBattle associated with this elevator.

    def __init__(self, cr):
        DistributedEntity.__init__(self, cr)
        DistributedElevator.__init__(self, cr)
        self.index = None
        self.type = None
        self.elev = None

    def setIndex(self, index):
        self.index = index

    def getIndex(self):
        return self.index

    def getLeftDoor(self):
        return self.elev.getLeftDoor()

    def getRightDoor(self):
        return self.elev.getRightDoor()
        
    def announceGenerate(self):
        DistributedEntity.announceGenerate(self)

        self.elev = Elevator(base.bspLoader.getEntityValueInt(self.entnum, "type"))
        self.elev.elevatorMdl.setPos(self.cEntity.getOrigin())
        self.elev.elevatorMdl.setHpr(self.cEntity.getAngles())
        #if self.index == 1:
        #    self.elev.elevatorMdl.hide()

        DistributedElevator.announceGenerate(self)

    def postAnnounceGenerate(self):
        DistributedElevator.postAnnounceGenerate(self, makeIvals = False)

        npc = self.elev.elevatorMdl.findAllMatches('**/floor_light_?;+s')
        for i in xrange(npc.getNumPaths()):
            np = npc.getPath(i)
            floor = int(np.getName()[-1:]) - 1
            if floor < self.thebldg.numFloors:
                np.setColor(LIGHT_OFF_COLOR)
            else:
                np.hide()
            if self.thebldg.currentFloor == floor:
                np.setColor(LIGHT_ON_COLOR)

        self.thebldg.elevators[self.index] = self.elev
        # We've polled the building and found it, tell the building that this elevator is ready.
        #self.thebldg.elevatorReady()
        #self.accept(self.thebldg.uniqueName('prepareElevator'), self.__prepareElevator)
        self.__prepareElevator()

    def disable(self):
        self.ignore(self.thebldg.uniqueName('prepareElevator'))
        self.elev.cleanup()
        del self.elev
        if self.thebldg:
            if self.thebldg.elevators:
                self.thebldg.elevators[self.index] = None
        DistributedEntity.disable(self)
        DistributedElevator.disable(self)

    def __prepareElevator(self):
        self.countdownTextNP.reparentTo(self.getElevatorModel())
        self.elevatorSphereNodePath.reparentTo(self.getElevatorModel())
        base.physicsWorld.attach(self.elevatorSphereNode)
        self.makeIvals()
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
        return self.elev.getElevatorModel()
