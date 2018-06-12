"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Street.py
@author Brian Lach
@date July 25, 2015

"""

from panda3d.core import CollisionEntry, Vec3
from panda3d.bullet import BulletRigidBodyNode

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.State import State
from direct.fsm.ClassicFSM import ClassicFSM

from src.coginvasion.hood.Place import Place

from src.coginvasion.globals import CIGlobals

class Street(Place):
    notify = directNotify.newCategory("Street")

    def __init__(self, loader, parentFSM, doneEvent):
        self.parentFSM = parentFSM
        Place.__init__(self, loader, doneEvent)
        self.fsm = ClassicFSM('Street', [State('start', self.enterStart, self.exitStart, ['walk', 'doorOut', 'teleportIn', 'tunnelOut', 'elevatorIn']),
            State('walk', self.enterWalk, self.exitWalk, ['stop', 'tunnelIn', 'shtickerBook', 'teleportOut', 'noAccessFA']),
            State('shtickerBook', self.enterShtickerBook, self.exitShtickerBook, ['teleportOut', 'walk']),
            State('teleportOut', self.enterTeleportOut, self.exitTeleportOut, ['teleportIn', 'stop']),
            State('tunnelOut', self.enterTunnelOut, self.exitTunnelOut, ['walk']),
            State('tunnelIn', self.enterTunnelIn, self.exitTunnelIn, ['stop']),
            State('stop', self.enterStop, self.exitStop, ['walk', 'died', 'teleportOut', 'doorIn']),
            State('doorIn', self.enterDoorIn, self.exitDoorIn, ['stop']),
            State('doorOut', self.enterDoorOut, self.exitDoorOut, ['walk']),
            State('teleportIn', self.enterTeleportIn, self.exitTeleportIn, ['walk', 'stop']),
            State('elevatorIn', self.enterElevatorIn, self.exitElevatorIn, ['walk', 'stop']),
            State('noAccessFA', self.enterNoAccessFA, self.exitNoAccessFA, ['walk', 'stop']),
            State('final', self.enterFinal, self.exitFinal, ['final'])],
            'start', 'final')

    def enterElevatorIn(self, requestStatus):
        taskMgr.add(
            self.elevatorInTask, 'Street.elevatorInTask', extraArgs = [requestStatus['bldgDoId']], appendTask = True)

    def elevatorInTask(self, bldgDoId, task):
        bldg = base.cr.doId2do.get(bldgDoId)
        if bldg:
            if bldg.elevatorNodePath is not None:
                if self._enterElevatorGotElevator():
                    return task.done
        return task.cont

    def _enterElevatorGotElevator(self):
        if not messenger.whoAccepts('insideVictorElevator'):
            return False
        messenger.send('insideVictorElevator')
        return True

    def exitElevatorIn(self):
        taskMgr.remove('Street.elevatorInTask')

    def enter(self, requestStatus, visibilityFlag = 1):

        self.loader.hood.enableOutdoorLighting()
        
        self.fsm.enterInitialState()
        base.playMusic(self.loader.streetSong)
        
        self.loader.geom.reparentTo(render)
        if visibilityFlag:
            self.visibilityOn()
        #self.loader.hood.startSky()
        self.enterZone(requestStatus['zoneId'])
        self.fsm.request(requestStatus['how'], [requestStatus])
        Place.enter(self)
        return

    def exit(self, vis = 1):
        if vis:
            self.visibilityOff()
        self.hideAllVisibles()
        base.disablePhysicsNodes(self.loader.landmarkBlocks)
        base.disablePhysicsNodes(self.loader.geom)
        self.loader.geom.reparentTo(hidden)
        #self.loader.hood.stopSky()

        base.stopMusic()

        self.loader.hood.disableOutdoorLighting()
        
        Place.exit(self)

    def load(self):
        Place.load(self)
        self.parentFSM.getStateNamed('street').addChild(self.fsm)

    def unload(self):
        self.parentFSM.getStateNamed('street').removeChild(self.fsm)
        del self.fsm
        del self.parentFSM
        self.enterZone(None)
        self.ignoreAll()
        Place.unload(self)
        return

    def hideAllVisibles(self):
        for i in self.loader.nodeList:
            base.disablePhysicsNodes(i)
            i.stash()

    def showAllVisibles(self):
        for i in self.loader.nodeList:
            base.enablePhysicsNodes(i)
            i.unstash()

    def visibilityOn(self):
        self.hideAllVisibles()
        taskMgr.add(self.__floorVisTask, "Street.floorVisTask")

    def __floorVisTask(self, task):
        start = camera.getPos(render)
        end = start + (Vec3.down() * 500)
        result = base.physicsWorld.rayTestClosest(start, end, CIGlobals.StreetVisGroup)
        if result.hasHit():
            self.enterZone(result.getNode())
        return task.cont

    def visibilityOff(self):
        taskMgr.remove("Street.floorVisTask")
        self.showAllVisibles()

    def enterZone(self, newZone):
        if isinstance(newZone, BulletRigidBodyNode):
            try:
                newZoneId = int(newZone.getName())
            except:
                self.notify.warning('Invalid floor collision node in street: %s' % newZone.getName())
                return
        elif type(newZone) is int:
            newZoneId = newZone
        else:
            self.notify.warning("Invalid zone: {0}".format(newZone))
            return
        self.doEnterZone(newZoneId)

    def doEnterZone(self, newZoneId):
        visualizeZones = 0
        if self.zoneId != None:
            for i in self.loader.nodeDict[self.zoneId]:
                if newZoneId:
                    if i not in self.loader.nodeDict[newZoneId]:
                        self.loader.fadeOutDict[i].start()
                else:
                    base.disablePhysicsNodes(i)
                    i.stash()

        if newZoneId != None:
            for i in self.loader.nodeDict[newZoneId]:
                if self.zoneId:
                    if i not in self.loader.nodeDict[self.zoneId]:
                        self.loader.fadeInDict[i].start()
                else:
                    if self.loader.fadeOutDict[i].isPlaying():
                        self.loader.fadeOutDict[i].finish()
                    if self.loader.fadeInDict[i].isPlaying():
                        self.loader.fadeInDict[i].finish()
                    base.enablePhysicsNodes(i)
                    i.unstash()

        if newZoneId != self.zoneId:
            if visualizeZones:
                if self.zoneId != None:
                    self.loader.zoneDict[self.zoneId].clearColor()
                if newZoneId != None:
                    self.loader.zoneDict[newZoneId].setColor(0, 0, 1, 1, 100)
            if newZoneId is not None:
                loader = base.cr.playGame.getPlace().loader
                if newZoneId in loader.zoneVisDict:
                    base.cr.sendSetZoneMsg(newZoneId, loader.zoneVisDict[newZoneId])
                else:
                    visList = [newZoneId] + loader.zoneVisDict.values()[0]
                    base.cr.sendSetZoneMsg(newZoneId, visList)
            self.zoneId = newZoneId
        return
