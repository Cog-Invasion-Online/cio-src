# Filename: DistributedElevator.py
# Created by:  blach (14Dec15)

from pandac.PandaModules import Point3, TextNode, VBase4, CollisionSphere, CollisionNode

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedObject import DistributedObject
from direct.distributed.ClockDelta import globalClockDelta
from direct.fsm import ClassicFSM, State
from direct.interval.IntervalGlobal import LerpPosHprInterval, Sequence, Wait, Func, LerpPosInterval, LerpHprInterval
from direct.gui.DirectGui import DirectButton

from src.coginvasion.globals import CIGlobals
from ElevatorConstants import *
from ElevatorUtils import *

class DistributedElevator(DistributedObject):
    notify = directNotify.newCategory('DistributedElevator')

    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        self.openSfx = base.loadSfx('phase_5/audio/sfx/elevator_door_open.ogg')
        self.closeSfx = base.loadSfx('phase_5/audio/sfx/elevator_door_close.ogg')
        self.elevatorPoints = ElevatorPoints
        self.type = ELEVATOR_NORMAL
        self.countdownTime = ElevatorData[self.type]['countdown']
        self.localAvOnElevator = False
        self.thebldg = None
        self.bldgDoId = None
        self.toZoneId = None
        self.elevatorModel = None
        self.countdownTextNP = None
        self.toonsInElevator = []
        self.hopOffButton = None
        self.fsm = ClassicFSM.ClassicFSM('DistributedElevator', [State.State('off', self.enterOff, self.exitOff),
         State.State('opening', self.enterOpening, self.exitOpening),
         State.State('waitEmpty', self.enterWaitEmpty, self.exitWaitEmpty),
         State.State('waitCountdown', self.enterWaitCountdown, self.exitWaitCountdown),
         State.State('closing', self.enterClosing, self.exitClosing),
         State.State('closed', self.enterClosed, self.exitClosed)], 'off', 'off')
        self.fsm.enterInitialState()

    def setElevatorType(self, etype):
        self.type = etype

    def getElevatorType(self):
        return self.type

    def setBldgDoId(self, doId):
        self.bldgDoId = doId

    def getBldgDoId(self):
        return self.bldgDoId

    def setToZoneId(self, zoneId):
        self.toZoneId = zoneId

    def getToZoneId(self):
        return self.toZoneId

    def enterOpening(self, ts = 0):
        self.openDoors.start(ts)

    def exitOpening(self):
        self.openDoors.finish()

    def enterClosing(self, ts = 0):
        if self.localAvOnElevator:
            self.hideHopOffButton()
        self.closeDoors.start(ts)

    def exitClosing(self):
        self.closeDoors.finish()

    def enterClosed(self, ts = 0):
        closeDoors(self.getLeftDoor(), self.getRightDoor())

    def exitClosed(self):
        pass

    def __handleElevatorTrigger(self, entry):
        if not self.localAvOnElevator:
            self.cr.playGame.getPlace().fsm.request('stop')
            self.sendUpdate('requestEnter')

    def enterWaitEmpty(self, ts = 0):
        if not self.localAvOnElevator:
            self.acceptOnce('enter' + self.uniqueName('elevatorSphere'), self.__handleElevatorTrigger)
        openDoors(self.getLeftDoor(), self.getRightDoor())

    def exitWaitEmpty(self):
        self.ignore('enter' + self.uniqueName('elevatorSphere'))

    def enterWaitCountdown(self, ts = 0):
        if not self.localAvOnElevator:
            self.acceptOnce('enter' + self.uniqueName('elevatorSphere'), self.__handleElevatorTrigger)
        openDoors(self.getLeftDoor(), self.getRightDoor())
        if self.countdownTextNP:
            self.countdownTextNP.show()
            self.countdownTrack = Sequence()
            time = int(ElevatorData[self.type]['countdown'])
            for i in range(time):
                self.countdownTrack.append(Func(self.countdownTextNP.node().setText, str(time - i)))
                self.countdownTrack.append(Wait(1.0))
            self.countdownTrack.start(ts)

    def exitWaitCountdown(self):
        if self.countdownTextNP:
            self.countdownTextNP.hide()
        self.countdownTrack.finish()
        del self.countdownTrack

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def getLeftDoor(self):
        # Can be overridden by inheritors.
        return self.thebldg.leftDoor

    def getRightDoor(self):
        return self.thebldg.rightDoor

    def startPoll(self):
        # Start polling for the building
        taskMgr.add(self.__pollBuilding, self.uniqueName('pollBuilding'))

    def __pollBuilding(self, task):
        self.getTheBldg()
        if self.thebldg:
            self.postAnnounceGenerate()
            return task.done
        return task.cont

    def stopPoll(self):
        taskMgr.remove(self.uniqueName('pollBuilding'))

    def announceGenerate(self):
        DistributedObject.announceGenerate(self)
        self.getTheBldg()
        if not self.thebldg:
            self.startPoll()
            return
        self.postAnnounceGenerate()

    def postAnnounceGenerate(self):
        self.leftDoor = self.getLeftDoor()
        self.rightDoor = self.getRightDoor()
        self.setupElevator()
        self.setupCountdownText()
        self.sendUpdate('requestStateAndTimestamp')

    def setState(self, state, timestamp):
        if not self.thebldg:
            return
        self.fsm.request(state, [globalClockDelta.localElapsedTime(timestamp)])

    def stateAndTimestamp(self, state, timestamp):
        self.fsm.request(state, [globalClockDelta.localElapsedTime(timestamp)])

    def setupCountdownText(self):
        tn = TextNode('countdownText')
        tn.setFont(CIGlobals.getMickeyFont())
        tn.setTextColor(VBase4(0.5, 0.5, 0.5, 1.0))
        tn.setAlign(TextNode.ACenter)
        self.countdownTextNP = self.getElevatorModel().attachNewNode(tn)
        self.countdownTextNP.setScale(2)
        self.countdownTextNP.setPos(0, 1, 7)
        #self.countdownTextNP.setH(180)

    def setupElevator(self):
        collisionRadius = ElevatorData[self.type]['collRadius']
        self.elevatorSphere = CollisionSphere(0, 5, 0, collisionRadius)
        self.elevatorSphere.setTangible(0)
        self.elevatorSphereNode = CollisionNode(self.uniqueName('elevatorSphere'))
        self.elevatorSphereNode.setIntoCollideMask(CIGlobals.WallBitmask)
        self.elevatorSphereNode.addSolid(self.elevatorSphere)
        self.elevatorSphereNodePath = self.getElevatorModel().attachNewNode(self.elevatorSphereNode)
        self.elevatorSphereNodePath.reparentTo(self.getElevatorModel())
        self.openDoors = getOpenInterval(self, self.getLeftDoor(), self.getRightDoor(), self.openSfx, None, self.type)
        self.closeDoors = getCloseInterval(self, self.getLeftDoor(), self.getRightDoor(), self.closeSfx, None, self.type)
        self.closeDoors = Sequence(self.closeDoors, Func(self.onDoorCloseFinish))

    def disable(self):
        self.stopPoll()
        if hasattr(self, 'openDoors'):
            self.openDoors.pause()
        if hasattr(self, 'closeDoors'):
            self.closeDoors.pause()
        self.ignore('enter' + self.uniqueName('elevatorSphere'))
        self.elevatorSphereNodePath.removeNode()
        del self.elevatorSphereNodePath
        del self.elevatorSphereNode
        del self.elevatorSphere
        self.fsm.request('off')
        self.openSfx = None
        self.closeSfx = None
        self.elevatorPoints = None
        self.type = None
        self.countdownTime = None
        self.localAvOnElevator = None
        self.thebldg = None
        self.bldgDoId = None
        self.toZoneId = None
        self.elevatorModel = None
        self.toonsInElevator = None
        self.hopOffButton = None
        self.leftDoor = None
        self.rightDoor = None
        self.openDoors = None
        self.closeDoors = None
        if self.countdownTextNP:
            self.countdownTextNP.removeNode()
            self.countdownTextNP = None
        DistributedObject.disable(self)

    def onDoorCloseFinish(self):
        if self.localAvOnElevator:
            base.transitions.fadeScreen(1.0)
            base.localAvatar.wrtReparentTo(render)

            loader = 'suitInterior'
            where = 'suitInterior'
            how = 'IDK'
            world = base.cr.playGame.getCurrentWorldName()


            if self.thebldg.fsm.getCurrentState().getName() == 'bldgComplete':
                loader = 'townLoader'
                where = 'street'
                how = 'elevatorIn'
                world = CIGlobals.CogTropolis

            requestStatus = {
                'zoneId' : self.getToZoneId(),
                'hoodId' : self.cr.playGame.hood.hoodId,
                'where' : where,
                'avId' : base.localAvatar.doId,
                'loader' : loader,
                'shardId' : None,
                'wantLaffMeter' : 1,
                'world' : world,
                'how' : how
            }

            self.cr.playGame.getPlace().doneStatus = requestStatus
            messenger.send(self.cr.playGame.getPlace().doneEvent)

    def doMusic(self):
        self.elevMusic = base.loadMusic('phase_7/audio/bgm/tt_elevator.mid')
        base.playMusic(self.elevMusic, looping = 1, volume = 0.8)

    def fillSlot(self, index, avId):
        toon = self.cr.doId2do.get(avId)
        if toon:
            point = ElevatorPoints[index]
            toon.stopSmooth()
            toon.wrtReparentTo(self.getElevatorModel())
            toon.headsUp(point)
            track = Sequence()
            track.append(Func(toon.animFSM.request, 'run'))
            track.append(LerpPosInterval(toon, duration = 0.5, pos = point,
                         startPos = toon.getPos(self.getElevatorModel())))
            track.append(LerpHprInterval(toon, duration = 0.1, hpr = (180, 0, 0),
                         startHpr = toon.getHpr(self.getElevatorModel())))
            track.append(Func(toon.animFSM.request, 'neutral'))
            if avId == base.localAvatar.doId:
                self.localAvOnElevator = True
                track.append(Func(self.showHopOffButton))
                base.localAvatar.stopSmartCamera()
                base.localAvatar.walkControls.setCollisionsActive(0)
                base.camera.wrtReparentTo(self.getElevatorModel())
                cameraBoardTrack = LerpPosHprInterval(camera, 1.5, Point3(0, -16, 5.5), Point3(0, 0, 0))
                cameraBoardTrack.start()
            track.start()

    def emptySlot(self, index, avId):
        toon = self.cr.doId2do.get(avId)
        if toon:
            OutPoint = ElevatorOutPoints[index]
            InPoint = ElevatorPoints[index]
            toon.stopSmooth()
            toon.headsUp(OutPoint)
            track = Sequence(
                Func(toon.animFSM.request, 'run'),
                LerpPosInterval(toon, duration = 0.5, pos = OutPoint, startPos = InPoint),
                Func(toon.animFSM.request, 'neutral'),
                Func(toon.startSmooth))
            if avId == base.localAvatar.doId:
                self.localAvOnElevator = False
                track.append(Func(self.freedom))
            track.start()

    def freedom(self):
        if self.fsm.getCurrentState().getName() in ['waitEmpty', 'waitCountdown']:
            self.acceptOnce('enter' + self.uniqueName('elevatorSphere'), self.__handleElevatorTrigger)
        base.localAvatar.walkControls.setCollisionsActive(1)
        self.cr.playGame.getPlace().fsm.request('walk')

    def setToonsInElevator(self, toonsInElevator):
        for i in xrange(len(toonsInElevator)):
            avId = toonsInElevator[i]
            toon = self.cr.doId2do.get(avId)
            if toon:
                toon.reparentTo(self.getElevatorModel())
                toon.stopSmooth()
                point = ElevatorPoints[i]
                toon.setPos(point)
                toon.setHpr(180, 0, 0)
                toon.animFSM.request('neutral')

    def getTheBldg(self):
        self.thebldg = self.cr.doId2do.get(self.bldgDoId)
        
        print self.thebldg.__class__
        print 'Has Elevators: %s' % hasattr(self.thebldg, 'elevators')

    def getElevatorModel(self):
        return self.thebldg.getElevatorModel()

    def enterRejected(self):
        self.cr.playGame.getPlace().fsm.request('walk')

    def showHopOffButton(self):
        gui = loader.loadModel('phase_3.5/models/gui/inventory_gui.bam')
        upButton = gui.find('**/InventoryButtonUp')
        downButton = gui.find('**/InventoryButtonDown')
        rlvrButton = gui.find('**/InventoryButtonRollover')
        self.hopOffBtn = DirectButton(
            relief = None, text = "Hop off", text_fg = (0.9, 0.9, 0.9, 1),
            text_pos = (0, -0.23), text_scale = 0.75, image = (upButton, downButton, rlvrButton),
            image_color = (0.5, 0.5, 0.5, 1), image_scale = (20, 1, 11), pos = (0, 0, 0.8),
            scale = 0.15, command = self.handleHopOffButton)

    def hideHopOffButton(self):
        if hasattr(self, 'hopOffBtn'):
            self.hopOffBtn.destroy()
            del self.hopOffBtn

    def handleHopOffButton(self):
        self.hideHopOffButton()
        self.sendUpdate('requestExit')
