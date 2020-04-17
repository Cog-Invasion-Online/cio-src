"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedCogOfficeBattle.py
@author Brian Lach
@date December 15, 2015

"""

from panda3d.core import Vec3, NodePath, Point3

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.ClockDelta import globalClockDelta
from direct.interval.IntervalGlobal import LerpQuatInterval
from direct.fsm import ClassicFSM, State

from src.coginvasion.battle.DistributedBattleZone import DistributedBattleZone
from src.coginvasion.minigame import DistributedMinigame
from src.coginvasion.nametag import NametagGlobals
from src.coginvasion.globals import CIGlobals
from src.coginvasion.npc.NPCWalker import NPCWalkInterval
from src.coginvasion.cog import SuitGlobals
from src.coginvasion.base.Lighting import IndoorLightingConfig
from src.coginvasion.hood import ZoneUtil
from ElevatorUtils import *
from ElevatorConstants import *
from CogOfficeConstants import *
import random

class DistributedCogOfficeBattle(DistributedBattleZone):
    notify = directNotify.newCategory('DistributedCogOfficeBattle')

    TOP_FLOOR_TAUNT = "I'm the boss."

    def __init__(self, cr):
        DistributedBattleZone.__init__(self, cr)
        self.currentFloor = None
        self.numFloors = None
        self.dept = None
        self.deptClass = None
        self.exteriorZoneId = None
        self.bldgDoId = None
        # Use the same text from eagle summit
        self.floorNameText = DistributedMinigame.getAlertText((0.75, 0.75, 0.75, 1.0), 0.15)
        self.elevators = [None, None]
        self.elevatorResponses = 0
        self.tauntSuitId = 0
        self.openSfx = base.loadSfx('phase_5/audio/sfx/elevator_door_open.ogg')
        self.closeSfx = base.loadSfx('phase_5/audio/sfx/elevator_door_close.ogg')
        
        self.rideElevatorMusic = 'tt_elevator'
        self.bottomFloorsMusic = ['encntr_suit_winning', 'encntr_general_bg_indoor']
        self.topFloorMusic = ['encntr_suit_winning_indoor', 'BossBot_CEO_v2']
        self.intermissionMusic = 'encntr_toon_winning_indoor'
        self.winMusic = 'encntr_toon_winning'
        
        self.fsm = ClassicFSM.ClassicFSM('DistributedCogOfficeBattle', [State.State('off', self.enterOff, self.exitOff),
         State.State('floorIntermission', self.enterFloorIntermission, self.exitFloorIntermission),
         State.State('bldgComplete', self.enterBldgComplete, self.exitBldgComplete),
         State.State('battle', self.enterBattle, self.exitBattle),
         State.State('rideElevator', self.enterRideElevator, self.exitRideElevator),
         State.State('faceOff', self.enterFaceOff, self.exitFaceOff),
         State.State('victory', self.enterVictory, self.exitVictory)], 'off', 'off')
        self.fsm.enterInitialState()
        
    def setCurrentFloor(self, floor):
        self.currentFloor = floor
        
    def getCurrentFloor(self):
        return self.currentFloor

    def setTauntSuitId(self, id):
        self.tauntSuitId = id

    def getTauntSuitId(self):
        return self.tauntSuitId

    def isTopFloor(self):
        return self.currentFloor >= self.numFloors - 1

    def enterBldgComplete(self):
        pass

    def exitBldgComplete(self):
        pass

    def doFaceoff(self, tauntIndex, timestamp):
        self.fsm.request('faceOff', [tauntIndex, globalClockDelta.localElapsedTime(timestamp)])
        
    def rewardSequenceComplete(self, timestamp):
        DistributedBattleZone.rewardSequenceComplete(self, timestamp)
        base.taskMgr.doMethodLater(0.1, self.victoryTask, self.uniqueName('victoryTask'))

    def enterVictory(self, ts):
        base.playMusic(self.winMusic, looping = 1)

    def victoryTask(self, task):
        requestStatus = {
            'zoneId': self.exteriorZoneId,
            'hoodId': self.cr.playGame.hood.id,
            'bldgDoId': self.bldgDoId,
            'loader': 'townLoader',
            'where': 'street',
            'world': ZoneUtil.CogTropolis,
            'shardId': None,
            'wantLaffMeter': 1,
            'avId': base.localAvatar.doId,
            'how': 'elevatorIn'
        }
        self.cr.playGame.getPlace().fsm.request('teleportOut', [requestStatus])
        return task.done

    def exitVictory(self):
        base.taskMgr.remove(self.uniqueName('victoryTask'))

    def setExteriorZoneId(self, zoneId):
        self.exteriorZoneId = zoneId

    def setBldgDoId(self, doId):
        self.bldgDoId = doId

    def d_readyForNextFloor(self):
        self.sendUpdate('readyForNextFloor')
        
    def getNumElevators(self):
        elevs = 0
        for i in xrange(len(self.elevators)):
            if self.elevators[i] is not None:
                elevs += 1
        return elevs

    def setNumFloors(self, num):
        self.numFloors = num

    def setState(self, state, timestamp):
        self.fsm.request(state, [globalClockDelta.localElapsedTime(timestamp)])

    def setDept(self, dept):
        self.dept = dept
        if dept == 'c':
            self.deptClass = Dept.BOSS
        elif dept == 'l':
            self.deptClass = Dept.LAW
        elif dept == 's':
            self.deptClass = Dept.SALES
        elif dept == 'm':
            self.deptClass = Dept.CASH
            
    def enterOff(self, ts = 0):
        pass

    def exitOff(self):
        pass

    def enterFaceOff(self, tauntIndex, ts):

        tauntSuit = self.suits.get(self.tauntSuitId)

        if self.isTopFloor():
            song = self.topFloorMusic
            taunt = DistributedCogOfficeBattle.TOP_FLOOR_TAUNT
        else:
            song = self.bottomFloorsMusic
            taunt = SuitGlobals.FaceoffTaunts[tauntSuit.suitPlan.getName()][tauntIndex]

        base.playMusic(song, looping = 1)

        base.camLens.setMinFov(30.0 / (4./3.))
        
        def posCamera_run():
            pos, lookAt = base.localAvatar.walkControls.fpsCam.getThirdPersonBattleCam()
            base.camera.setPos(pos)
            base.camera.lookAt(lookAt)

        camera.reparentTo(tauntSuit)
        height = tauntSuit.getHeight()
        offsetPnt = Point3(0, 0, height)
        MidTauntCamHeight = height * 0.66
        MidTauntCamHeightLim = height - 1.8
        if MidTauntCamHeight < MidTauntCamHeightLim:
            MidTauntCamHeight = MidTauntCamHeightLim
        TauntCamY = 18
        TauntCamX = 0
        TauntCamHeight = random.choice((MidTauntCamHeight, 1, 11))
        camera.setPos(TauntCamX, TauntCamY, TauntCamHeight)
        camera.lookAt(tauntSuit, offsetPnt)

        self.faceOffTrack = Sequence()
        self.faceOffTrack.append(Func(tauntSuit.setAutoClearChat, False))
        self.faceOffTrack.append(Func(tauntSuit.setChat, taunt))
        self.faceOffTrack.append(Wait(3.5))
        self.faceOffTrack.append(Func(tauntSuit.nametag.clearChatText))
        self.faceOffTrack.append(Func(tauntSuit.setAutoClearChat, True))
        self.faceOffTrack.append(Func(base.camLens.setMinFov, CIGlobals.DefaultCameraFov / (4./3.)))
        self.faceOffTrack.append(Func(base.localAvatar.attachCamera))
        self.faceOffTrack.append(Func(posCamera_run))
        
        faceoffs = base.bspLoader.findAllEntities("cogoffice_faceoff_point")
        
        runTrack = Parallel()
        for i in xrange(len(self.avIds)):
            avId = self.avIds[i]
            toon = self.cr.doId2do.get(avId)
            if toon:
                toon.stopSmooth()
                toon.wrtReparentTo(render)
                faceoff = faceoffs[i]
                pos = faceoff.cEntity.getOrigin()
                hpr = faceoff.cEntity.getAngles()
                toon.headsUp(pos)
                track = Sequence(
                    Func(toon.setAnimState, 'run'),
                    LerpPosInterval(toon, duration = 1.5, pos = pos,
                        startPos = toon.getPos(render)),
                    Func(toon.setAnimState, 'walk'),
                    LerpQuatInterval(toon, duration = 1.0, hpr = hpr,
                        startHpr = lambda toon = toon: toon.getHpr(render)),
                    Func(toon.setAnimState, 'neutral'))
                if avId != base.localAvatar.doId:
                    track.append(Func(toon.startSmooth))
                runTrack.append(track)

        #for suit in self.suits.values():
        #    if suit.hangoutPoint[0]:
        #        track = Sequence(
        #            Func(suit.setAnimState, 'walk'),
        #            NPCWalkInterval(
        #                suit, Point3(suit.guardPoint[0][0], suit.guardPoint[0][1], suit.guardPoint[0][2]), durationFactor = 0.19),
        #            Func(suit.setHpr, Vec3(suit.guardPoint[1], 0, 0)),
        #            Func(suit.setAnimState, 'neutral'))
        #        runTrack.append(track)

        self.faceOffTrack.append(runTrack)
        self.faceOffTrack.start(ts)

    def exitFaceOff(self):
        self.faceOffTrack.finish()
        del self.faceOffTrack

    def enterRideElevator(self, ts):
        elevator = self.elevators[0]

        NametagGlobals.setWant2dNametags(False)

        tauntSuit = self.suits.get(self.tauntSuitId)
        if tauntSuit:
            tauntSuit.headsUp(self.elevators[0].getElevatorModel())
        
        base.camLens.setFov(CIGlobals.OriginalCameraFov)
        camera.reparentTo(elevator.getElevatorModel())
        camera.setPos(0, 14, 4)
        camera.setHpr(180, 0, 0)

        base.playMusic(self.rideElevatorMusic, looping = 1)
        base.transitions.refreshGraphicsEngine()
        base.transitions.irisIn(t = 1.5, blendType = 'easeOut')
        
        self.elevatorTrack = getRideElevatorInterval()
        self.elevatorTrack.append(Func(self.__doFloorTextPulse))
        self.elevatorTrack.append(getOpenInterval(self, elevator.getLeftDoor(), elevator.getRightDoor(), self.openSfx, None))
        self.elevatorTrack.start(ts)

    def __doFloorTextPulse(self):
        # worldspawn `message` property
        worldspawn = base.bspLoader.getCEntity(0)
        floorTitle = worldspawn.getEntityValue("message")

        self.floorNameText.setText(floorTitle)
        ival = DistributedMinigame.getAlertPulse(self.floorNameText, 0.17, 0.15)
        ival.start()

    def exitRideElevator(self):
        if hasattr(self, 'elevatorTrack'):
            self.elevatorTrack.finish()
            del self.elevatorTrack
        base.stopMusic()
        base.camLens.setMinFov(CIGlobals.DefaultCameraFov / (4./3.))

    def enterBattle(self, ts):
        NametagGlobals.setWant2dNametags(True)

        base.localAvatar.walkControls.setCollisionsActive(1)
        self.cr.playGame.getPlace().fsm.request('walk')
        base.localAvatar.hideBookButton()

    def exitBattle(self):
        base.stopMusic()
        taskMgr.remove(self.uniqueName('monitorHP'))

    def enterFloorIntermission(self, ts):
        base.localAvatar.showBookButton()
        base.playMusic(self.intermissionMusic, looping = 1)

    def exitFloorIntermission(self):
        base.stopMusic()

    def generate(self):
        DistributedBattleZone.generate(self)

        import Entities
        base.bspLoader.linkEntityToClass("cogoffice_faceoff_point", Entities.FaceOffPoint)

    def disable(self):
        base.cleanupBSPLevel()
        
        self.fsm.requestFinalState()
        del self.fsm
        if self.floorNameText:
            self.floorNameText.destroy()
            self.floorNameText = None
        self.currentFloor = None
        self.elevators = None
        self.dept = None
        self.deptClass = None
        self.openSfx = None
        self.closeSfx = None
        self.rideElevatorMusic = None
        self.bottomFloorsMusic = None
        self.intermissionMusic = None
        self.bldgDoId = None
        self.exteriorZoneId = None
        base.stopMusic()
        DistributedBattleZone.disable(self)

    def setMap(self, map):
        self.currentRoom = map
        
        DistributedBattleZone.setMap(self, map)

    def cleanupElevators(self):
        self.elevators = [None, None]
