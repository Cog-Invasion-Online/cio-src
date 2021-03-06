"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedDoor.py
@author Brian Lach
@date July 27, 2015

"""

from panda3d.core import Point3, Vec4

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed import DistributedObject, ClockDelta, DelayDelete
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.interval.IntervalGlobal import Parallel, ParallelEndTogether, Sequence
from direct.interval.IntervalGlobal import Wait, Func, LerpQuatInterval, SoundInterval
from direct.interval.IntervalGlobal import LerpPosInterval, LerpPosHprInterval

from src.coginvasion.hood.ZoneUtil import DonaldsDreamland

class DistributedDoor(DistributedObject.DistributedObject):
    notify = directNotify.newCategory("DistributedDoor")
    notify.setInfo(True)
    INT_STANDARD = 0
    EXT_STANDARD = 1
    INT_HQ = 2
    EXT_HQ = 3
    EXT_GAGSHOP = 4
    
    LIT_INTERIOR_COLOR = Vec4(1.0, 236.0 / 255.0, 142.0 / 255.0, 1.0)

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        self.rightFSM = ClassicFSM(
            'DistributedDoor_right',
            [
                State('off', self.enterOff, self.exitOff),
                State('closed', self.enterRightDoorClosed, self.exitRightDoorClosed, ['opening']),
                State('opening', self.enterRightDoorOpening, self.exitRightDoorOpening, ['open']),
                State('open', self.enterRightDoorOpen, self.exitRightDoorOpen, ['closing']),
                State('closing', self.enterRightDoorClosing, self.exitRightDoorClosing, ['closed'])
            ],
            'off', 'off'
        )
        self.rightFSM.enterInitialState()
        self.leftFSM = ClassicFSM(
            'DistributedDoor_left',
            [
                State('off', self.enterOff, self.exitOff),
                State('closed', self.enterLeftDoorClosed, self.exitLeftDoorClosed, ['opening']),
                State('opening', self.enterLeftDoorOpening, self.exitLeftDoorOpening, ['open']),
                State('open', self.enterLeftDoorOpen, self.exitLeftDoorOpen, ['closing']),
                State('closing', self.enterLeftDoorClosing, self.exitLeftDoorClosing, ['closed'])
            ],
            'off', 'off'
        )
        self.leftFSM.enterInitialState()
        self.avatarTracks = []
        self.leftDoorState = ''
        self.rightDoorState = ''
        self.toZone = 0
        self.block = 0
        self.doorType = 0
        self.doorIndex = 0
        self.leftTrack = None
        self.rightTrack = None
        self.building = None
        self.doorNode = None
        self.leftDoor = None
        self.rightDoor = None
        self.doorOpenSound = None
        self.doorShutSound = None
        self.enterDoorWalkBackNode = None
        self.enterDoorWalkInNode = None
        self.exitDoorWalkFromNode = None
        self.exitDoorWalkToNode = None
        self.ready = False
        self.nodeProblemPolled = False
        self.suitTakingOver = 0

    def setSuitTakingOver(self, flag):
        self.suitTakingOver = flag

    def getSuitTakingOver(self):
        return self.suitTakingOver

    def setDoorIndex(self, index):
        self.doorIndex = index

    def getDoorIndex(self):
        return self.doorIndex

    def getLeftDoorOpenH(self):
        num = 0
        if self.getDoorType() == self.INT_STANDARD or self.getDoorType() == self.INT_HQ:
            num =  70
        elif self.getDoorType() == self.EXT_STANDARD or self.getDoorType() == self.EXT_HQ:
            num = -110
        if (self.getDoorIndex() == 1 and not self.doorType == self.EXT_HQ or
        self.getDoorIndex() == 0 and self.doorType in [self.EXT_HQ, self.EXT_GAGSHOP]):
            return num - 180
        else:
            return num

    def getLeftDoorClosedH(self):
        num = 0
        if self.getDoorType() == self.INT_STANDARD or self.getDoorType() == self.INT_HQ:
            num = 180
        elif self.getDoorType() == self.EXT_STANDARD or self.getDoorType() == self.EXT_HQ:
            num = 0
        if (self.getDoorIndex() == 1 and not self.doorType == self.EXT_HQ or
        self.getDoorIndex() == 0 and self.doorType in [self.EXT_HQ, self.EXT_GAGSHOP]):
            return num - 180
        else:
            return num

    def getRightDoorOpenH(self):
        num = 0
        if self.getDoorType() == self.INT_STANDARD or self.getDoorType() == self.INT_HQ:
            num = -70
        elif self.getDoorType() == self.EXT_STANDARD or self.getDoorType() == self.EXT_HQ or self.getDoorType() == self.EXT_GAGSHOP:
            num = 110
        if (self.getDoorIndex() == 1 and not self.doorType == self.EXT_HQ or
        self.getDoorIndex() == 0 and self.doorType in [self.EXT_HQ, self.EXT_GAGSHOP]):
            return num - 180
        else:
            return num

    def getRightDoorClosedH(self):
        num = 0
        if self.getDoorType() == self.INT_STANDARD or self.getDoorType() == self.INT_HQ:
            num = 180
        elif self.getDoorType() == self.EXT_STANDARD or self.getDoorType() == self.EXT_HQ or self.getDoorType() == self.EXT_GAGSHOP:
            num = 0
        if (self.getDoorIndex() == 1 and not self.doorType == self.EXT_HQ or
        self.getDoorIndex() == 0 and self.doorType in [self.EXT_HQ, self.EXT_GAGSHOP]):
            return num - 180
        else:
            return num

    def enterOff(self, ts = 0):
        pass

    def exitOff(self):
        pass

    def enterRightDoorClosed(self, ts = 0):
        self.rightDoor.setH(self.getRightDoorClosedH())
        self.toggleDoorHole('Right', show = False)

    def exitRightDoorClosed(self):
        pass

    def enterRightDoorOpen(self, ts = 0):
        self.rightDoor.setH(self.getRightDoorOpenH())

    def exitRightDoorOpen(self):
        pass

    def enterRightDoorClosing(self, ts = 0):
        if self.rightTrack:
            self.rightTrack.finish()
            self.rightTrack = None
        self.rightTrack = Sequence(LerpQuatInterval(self.rightDoor, duration = 1.0, quat = (self.getRightDoorClosedH(), 0, 0),
            startHpr = (self.getRightDoorOpenH(), 0, 0), blendType = 'easeIn'),
            Func(base.playSfx, self.doorShutSound, 0, 1, None, 0.0, self.rightDoor))
        self.rightTrack.start()

    def exitRightDoorClosing(self):
        if self.rightTrack:
            self.rightTrack.finish()
            self.rightTrack = None

    def enterRightDoorOpening(self, ts = 0):
        self.toggleDoorHole('Right', show = True)
        self.rightDoor.show()
        if self.rightTrack:
            self.rightTrack.finish()
            self.rightTrack = None
        self.rightTrack = Sequence(Wait(0.5), Parallel(LerpQuatInterval(self.rightDoor, duration = 0.7, quat = (self.getRightDoorOpenH(), 0, 0),
            startHpr = (self.getRightDoorClosedH(), 0, 0), blendType = 'easeInOut'), SoundInterval(self.doorOpenSound, node = self.rightDoor)))
        self.rightTrack.start()

    def exitRightDoorOpening(self):
        if self.rightTrack:
            self.rightTrack.finish()
            self.rightTrack = None

    def enterLeftDoorClosed(self, ts = 0):
        self.leftDoor.setH(self.getLeftDoorClosedH())
        self.toggleDoorHole('Left', show = False)

    def exitLeftDoorClosed(self):
        pass

    def enterLeftDoorOpen(self, ts = 0):
        self.leftDoor.setH(self.getLeftDoorOpenH())

    def exitLeftDoorOpen(self):
        pass

    def enterLeftDoorClosing(self, ts = 0):
        if self.leftTrack:
            self.leftTrack.finish()
            self.leftTrack = None
        self.leftTrack = Sequence(LerpQuatInterval(
            self.leftDoor, duration = 1.0, quat = (self.getLeftDoorClosedH(), 0, 0),
            startHpr = (self.getLeftDoorOpenH(), 0, 0), blendType = 'easeIn'),
            Func(base.playSfx, self.doorShutSound, 0, 1, None, 0.0, self.leftDoor))
        self.leftTrack.start()

    def exitLeftDoorClosing(self):
        if self.leftTrack:
            self.leftTrack.finish()
            self.leftTrack = None

    def enterLeftDoorOpening(self, ts = 0):
        self.toggleDoorHole('Left', show = True)
        self.leftDoor.show()
        if self.leftTrack:
            self.leftTrack.finish()
            self.leftTrack = None
        self.leftTrack = Sequence(Wait(0.5), Parallel(LerpQuatInterval(self.leftDoor, duration = 0.7, quat = (self.getLeftDoorOpenH(), 0, 0),
            startHpr = (self.getLeftDoorClosedH(), 0, 0), blendType = 'easeInOut'), SoundInterval(self.doorOpenSound, node = self.leftDoor)))
        self.leftTrack.start()

    def exitLeftDoorOpening(self):
        if self.leftTrack:
            self.leftTrack.finish()
            self.leftTrack = None

    def setDoorType(self, door):
        self.doorType = door

    def getDoorType(self):
        return self.doorType

    def setBlock(self, block):
        self.block = block

    def getBlock(self):
        return self.block

    def setToZone(self, zone):
        self.toZone = zone

    def getToZone(self):
        return self.toZone

    def setLeftDoorState(self, state, timestamp):
        ts = ClockDelta.globalClockDelta.localElapsedTime(timestamp)
        self.leftDoorState = state
        if self.building:
            self.leftFSM.request(state, [ts])

    def getLeftDoorState(self):
        return self.leftDoorState

    def setRightDoorState(self, state, timestamp):
        ts = ClockDelta.globalClockDelta.localElapsedTime(timestamp)
        self.rightDoorState = state
        if self.building:
            self.rightFSM.request(state, [ts])

    def getRightDoorState(self):
        return self.rightDoorState

    def findBuilding(self):
        bldg = None
        if self.getDoorType() == self.EXT_STANDARD or self.getDoorType() == self.EXT_HQ or self.getDoorType() == self.EXT_GAGSHOP:
            bldg = self.cr.playGame.hood.loader.geom.find('**/??' + str(self.getBlock()) + ':*_landmark_*_DNARoot;+s')
        elif self.getDoorType() == self.INT_STANDARD:
            bldg = render.find('**/leftDoor;+s').getParent()
        elif self.getDoorType() == self.INT_HQ:
            bldg = render.find('**/door_origin_0').getParent()
        return bldg

    def findDoorNodePath(self):
        doorNode = None
        if self.getDoorType() in [self.EXT_STANDARD, self.EXT_GAGSHOP]:
            doorNode = self.building.find('**/*door_origin')
        elif self.getDoorType() == self.EXT_HQ:
            doorNode = self.building.find('**/door_origin_' + str(self.doorIndex))
        elif self.getDoorType() == self.INT_STANDARD:
            doorNode = render.find('**/door_origin')
        elif self.getDoorType() == self.INT_HQ:
            doorNode = render.find('**/door_origin_' + str(self.doorIndex))
        return doorNode

    def findDoorNode(self, string):
        if self.doorType != self.INT_HQ:
            foundNode = self.building.find('**/door_' + str(self.getDoorIndex()) + '/**/' + string + '*;+s+i')
            
            if foundNode.isEmpty():
                foundNode = self.building.find('**/' + string + '*;+s+i')

        else:
            foundNode = render.find('**/door_' + str(self.getDoorIndex()) + '/**/' + string + '*;+s+i')
            if foundNode.isEmpty():
                foundNode = render.find('**/' + string + '*;+s+i')

        return foundNode

    def getTriggerName(self):
        if self.getDoorType() == self.INT_STANDARD or self.getDoorType() == self.EXT_STANDARD or self.getDoorType() == self.EXT_GAGSHOP:
            return 'door_trigger_' + str(self.getBlock())
        elif self.getDoorType() == self.INT_HQ or self.getDoorType() == self.EXT_HQ:
            return 'door_trigger_' + str(self.block) + '0' + str(self.doorIndex)

    def getEnterTriggerEvent(self):
        return 'enter' + self.getTriggerName()

    def getExitTriggerEvent(self):
        return 'exit' + self.getTriggerName()

    def __pollBuilding(self, task):
        try:
            self.building = self.findBuilding()
        except:
            return task.cont
        if self.building.isEmpty():
            return task.cont
        self.generated()
        return task.done

    def _handleTrigger(self, ghostNode):
        if not self.getSuitTakingOver():
            self.cr.playGame.getPlace().fsm.request('stop')
            base.localAvatar.walkControls.setCollisionsActive(0)
            self.sendUpdate('requestEnter', [])

    def getAvatarEnterTrack(self, av):
        track = Sequence(name = av.uniqueName('avatarEnterDoorTrack'))
        track.append(Func(av.setAnimState, 'walkBack'))
        track.append(
            ParallelEndTogether(
                LerpPosInterval(
                    av,
                    duration = 0.5,
                    blendType = 'easeInOut',
                    pos = self.enterWalkBackPos,
                    startPos = av.getPos(render)
                ),
                LerpQuatInterval(
                    av,
                    duration = 0.5,
                    hpr = self.doorNode.getHpr(render),
                    startHpr = av.getHpr(render)
                )
            )
        )
        track.append(Func(av.setPlayRate, 1.0, 'walk'))
        track.append(Func(av.loop, 'neutral'))
        track.append(Wait(1.0))
        track.append(Func(av.loop, 'walk'))
        parallel = Parallel()
        parallel.append(
            LerpPosInterval(
                av,
                duration = 1.0,
                blendType = 'easeInOut',
                pos = self.enterWalkInPos,
                startPos = self.enterWalkBackPos
            )
        )
        if base.localAvatar.doId == av.doId:
            parallel.append(LerpPosHprInterval(nodePath = camera, other = av, duration = 1.0,
                                               pos = (0, -8, av.getHeight()), hpr = (0, 0, 0),
                                               blendType = 'easeInOut'))
            parallel.append(Sequence(Wait(0.5), Func(self.sendGoingIn), Wait(1.0)))
        track.append(parallel)
        if base.localAvatar.doId == av.doId:
            track.append(Func(self.sendWentInDoor))
        track.setDoneEvent(track.getName())
        track.delayDelete = DelayDelete.DelayDelete(av, track.getName())
        self.acceptOnce(track.getDoneEvent(), self.__avatarTrackDone, [track])
        return track

    def sendGoingIn(self):
        messenger.send('DistributedDoor_localAvatarGoingInDoor')
        
    def sendWentInDoor(self):
        messenger.send('DistributedDoor_localAvatarWentInDoor')

    def getAvatarExitTrack(self, av):
        track = Sequence(name = av.uniqueName('avatarExitDoorTrack'))
        track.append(Wait(1.3))
        track.append(Func(av.setAnimState, 'walk'))
        av.setPos(self.exitWalkFromPos)
        av.headsUp(self.exitWalkToPos)
        track.append(
            LerpPosInterval(
                av,
                duration = 1.2,
                blendType = 'easeInOut',
                pos = self.exitWalkToPos,
                startPos = av.getPos(render)
            )
        )
        track.append(Func(av.loop, 'neutral'))
        if base.localAvatar.doId == av.doId:
            track.append(Func(messenger.send, 'DistributedDoor_localAvatarCameOutOfDoor'))
        else:
            track.append(Func(av.startSmooth))
        track.setDoneEvent(track.getName())
        track.delayDelete = DelayDelete.DelayDelete(av, track.getName())
        self.acceptOnce(track.getDoneEvent(), self.__avatarTrackDone, [track])
        return track

    def __avatarTrackDone(self, track):
        if track:
            DelayDelete.cleanupDelayDeletes(track)
            if self.avatarTracks:
                self.avatarTracks.remove(track)

    def enterDoor(self, avatarId, timestamp):
        if not self.building:
            return
        ts = ClockDelta.globalClockDelta.localElapsedTime(timestamp)
        if avatarId == base.localAvatar.doId:
            self.cr.playGame.getPlace().fsm.request('doorIn', [self])
        av = self.cr.doId2do.get(avatarId)
        if av:
            av.stopSmooth()
            track = self.getAvatarEnterTrack(av)
            self.avatarTracks.append(track)
            track.start()

    def exitDoor(self, avatarId, timestamp):
        if not self.building:
            return
        ts = ClockDelta.globalClockDelta.localElapsedTime(timestamp)
        av = self.cr.doId2do.get(avatarId)
        if av:
            if av.doId != base.localAvatar.doId:
                av.stopSmooth()
            track = self.getAvatarExitTrack(av)
            self.avatarTracks.append(track)
            track.start()

    def announceGenerate(self):
        DistributedObject.DistributedObject.announceGenerate(self)
        try:
            self.building = self.findBuilding()
            self.generated()
        except:
            self.startBuildingPoll()
            return
        if self.building.isEmpty():
            self.startBuildingPoll()
            return

    def startBuildingPoll(self):
        base.taskMgr.add(self.__pollBuilding, self.uniqueName('pollBuilding'))

    def fixHQTrigger(self):
        trig = self.building.find('**/door_' + str(self.doorIndex) + '/**/door_trigger*')
        if not trig.isEmpty():
            trig.node().setName(self.getTriggerName())

    def generated(self):
        self.doorNode = self.findDoorNodePath()
        self.rightDoor = self.findDoorNode('rightDoor')
        self.leftDoor = self.findDoorNode('leftDoor')
        self.toggleDoorHole('Right', show = False)
        self.toggleDoorHole('Left', show = False)
        
        self.enterWalkBackPos = render.getRelativePoint(self.doorNode, Point3(1.6, -5.5, 0.0))
        self.enterWalkInPos = render.getRelativePoint(self.doorNode, Point3(1.6, 3.0, 0.0))
        self.exitWalkFromPos = render.getRelativePoint(self.doorNode, Point3(-1.6, 3.0, 0.0))
        self.exitWalkToPos = render.getRelativePoint(self.doorNode, Point3(-1.6, -5.5, 0.0))

        self.doorOpenSound = base.audio3d.loadSfx('phase_3.5/audio/sfx/Door_Open_1.ogg')
        self.doorShutSound = base.audio3d.loadSfx('phase_3.5/audio/sfx/Door_Close_1.ogg')
        base.audio3d.attachSoundToObject(self.doorOpenSound, self.doorNode)
        base.audio3d.attachSoundToObject(self.doorShutSound, self.doorNode)

        if self.doorType == self.EXT_HQ:
            self.fixHQTrigger()

        self.acceptOnce(self.getEnterTriggerEvent(), self._handleTrigger)

        self.ready = True

    def toggleDoorHole(self, side, show = False):
        side = side.title()
        if self.building:
            isDDL = self.cr.playGame.hood.id == DonaldsDreamland
            isExt = self.getDoorType() in [self.EXT_GAGSHOP, self.EXT_HQ, self.EXT_STANDARD]
            holeColor = self.LIT_INTERIOR_COLOR if (isExt and isDDL) else (0.0, 0.0, 0.0, 1.0)
            
            if self.getDoorType() == self.EXT_HQ:
                hole = self.building.find('**/doorFrameHole%s_%d' % (side, self.doorIndex))
                geom = self.building.find('**/doorFrameHole%sGeom_%d' % (side, self.doorIndex))
                
                if not hole or hole.isEmpty():
                    doorFlats = self.building.findAllMatches('**/door_fla*;+s+i')
                    
                    for doorFlat in doorFlats:
                        if not doorFlat.isEmpty() and int(doorFlat.getName()[len(doorFlat.getName()) - 1]) == self.doorIndex:
                            # Let's reset the material to the default white.
                            doorFlat.setBSPMaterial('phase_14/materials/white.mat', 1)

                            # This is a hacky way to make sure the flat part is behind the door.
                            # This took me like 2 hours to figure out this workaround. Don't question it
                            # with some stupid #setPos() trash, depth write/depth test, or any of that. This works.
                            doorFlat.setSy(0.995)

                            hole = doorFlat
                            break

            elif self.getDoorType() == self.INT_HQ:
                hole = render.find('**/door_' + str(self.doorIndex) + '/**/doorFrameHole%s;+s+i' % side)
                geom = render.find('**/door_' + str(self.doorIndex) + '/**/doorFrameHole%sGeom;+s+i' % side)
            else:
                hole = self.building.find('**/doorFrameHole%s' % side)
                geom = self.building.find('**/doorFrameHole%sGeom' % side)
                
            nodes = [hole, geom]
            
            for node in nodes:
                if node and not node.isEmpty():
                    if show:
                        node.show()
                    else:
                        node.hide()

                    node.setColor(holeColor, 1)

    def printBuildingPos(self):
        self.notify.info(self.building.getPos(render))

    def disable(self):
        self.ignore(self.getEnterTriggerEvent())
        base.taskMgr.remove(self.uniqueName('pollBuilding'))
        for track in self.avatarTracks:
            track.finish()
        self.avatarTracks = None
        self.building = None
        self.doorNode = None
        self.rightDoor = None
        self.leftDoor = None
        self.ready = None
        self.toZone = None
        if self.leftTrack:
            self.leftTrack.finish()
            self.leftTrack = None
        if self.rightTrack:
            self.rightTrack.finish()
            self.rightTrack = None
        if self.enterDoorWalkBackNode:
            self.enterDoorWalkBackNode.removeNode()
            self.enterDoorWalkBackNode = None
        if self.enterDoorWalkInNode:
            self.enterDoorWalkInNode.removeNode()
            self.enterDoorWalkInNode = None
        if self.exitDoorWalkFromNode:
            self.exitDoorWalkFromNode.removeNode()
            self.exitDoorWalkFromNode = None
        if self.exitDoorWalkToNode:
            self.exitDoorWalkToNode.removeNode()
            self.exitDoorWalkToNode = None
        self.doorOpenSound = None
        self.doorShutSound = None

        self.leftDoorState = None
        self.rightDoorState = None
        self.block = None
        self.doorType = None
        self.doorIndex = None
        self.nodeProblemPolled = None
        self.suitTakingOver = None

        DistributedObject.DistributedObject.disable(self)
