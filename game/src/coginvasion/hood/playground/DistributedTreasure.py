"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedTreasure.py
@author Maverick Liberty
@date July 15, 2015

"""

from direct.distributed.DistributedObject import DistributedObject
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Sequence, LerpPosInterval, LerpColorScaleInterval, Func
from direct.task.Task import Task
from panda3d.core import NodePath, CollisionSphere, CollisionNode, Point3, VBase4
from panda3d.direct import HideInterval, ShowInterval
from src.coginvasion.globals import CIGlobals

class DistributedTreasure(DistributedObject):
    notify = directNotify.newCategory('DistributedTreasure')

    WinterTreasureMdl = 'phase_6/models/karting/qbox.bam'

    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        self.grabSoundPath = None
        self.rejectSoundPath = 'phase_4/audio/sfx/ring_miss.ogg'
        self.dropShadow = None
        self.treasureTrack = None
        self.nodePath = None
        self.modelPath = None
        self.modelChildString = None
        self.sphereRadius = 2.0
        self.scale = 1.0
        self.zOffset = 0.0
        self.playSoundForRemoteToons = True
        self.fly = True
        self.shadow = True
        self.billboard = False
        self.av = None
        
        self.spinTaskName = None

    def announceGenerate(self):
        DistributedObject.announceGenerate(self)
        self.spinTaskName = self.uniqueName('treasureRotate')

        if base.cr.isChristmas():
            self.modelPath = DistributedTreasure.WinterTreasureMdl

        self.loadModel(self.modelPath, self.modelChildString)
        self.startAnimation()
        self.nodePath.reparentTo(render)
        self.accept(self.uniqueName('entertreasureSphere'), self.handleEnterSphere)

    def loadModel(self, mdlPath, childString = None):
        self.grabSound = base.loadSfx(self.grabSoundPath)
        self.rejectSound = base.loadSfx(self.rejectSoundPath)
        if self.nodePath == None:
            self.makeNodePath()
        else:
            self.treasure.getChildren().detach()
        model = loader.loadModel(mdlPath)
        if base.cr.isChristmas():
            model.setTransparency(1)
        if childString:
            model = model.find('**/' + childString)
        model.instanceTo(self.treasure)
        if base.cr.isChristmas():
            self.treasure.setScale(1.5, 1.5, 1.5)
            self.treasure.setZ(0.8)
            taskMgr.add(self.__spinTreasure, self.spinTaskName)

    def makeNodePath(self):
        self.nodePath = NodePath('treasure')
        if self.billboard: self.nodePath.setBillboardPointEye()
        self.nodePath.setScale(0.9 * self.scale)
        self.treasure = self.nodePath.attachNewNode('treasure')
        if self.shadow:
            if not self.dropShadow:
                self.dropShadow = loader.loadModel('phase_3/models/props/drop_shadow.bam')
                self.dropShadow.setColor(0, 0, 0, 0.5)
                self.dropShadow.setPos(0, 0, 0.025)
                self.dropShadow.setScale(0.4 * self.scale)
                self.dropShadow.flattenLight()
            self.dropShadow.reparentTo(self.nodePath)
        collSphere = CollisionSphere(0, 0, 0, self.sphereRadius)
        collSphere.setTangible(0)
        collNode = CollisionNode(self.uniqueName('treasureSphere'))
        collNode.setIntoCollideMask(CIGlobals.WallBitmask)
        collNode.addSolid(collSphere)
        self.collNodePath = self.nodePath.attachNewNode(collNode)
        self.collNodePath.stash()
        
    def __spinTreasure(self, task):
        self.treasure.setH(20.0 * task.time)
        return Task.cont

    def handleEnterSphere(self, collEntry = None):
        localAvId = base.localAvatar.doId
        if not self.fly:
            self.setGrab(localAvId)
        self.d_requestGrab()

    def setPosition(self, x, y, z):
        if not self.nodePath:
            self.makeNodePath()
        self.nodePath.reparentTo(render)
        self.nodePath.setPos(x, y, z + self.zOffset)
        self.collNodePath.unstash()

    def setReject(self):
        self.cleanupTrack()
        base.playSfx(self.rejectSound, node = self.nodePath)
        self.treasureTrack = Sequence(LerpColorScaleInterval(self.nodePath, 0.8, colorScale = VBase4(0, 0, 0, 0),
                                                             startColorScale = VBase4(1, 1, 1, 1), blendType = 'easeIn'),
                                      LerpColorScaleInterval(self.nodePath, 0.2, colorScale = VBase4(1, 1, 1, 1),
                                                             startColorScale = VBase4(0, 0, 0, 0), blendType = 'easeOut',
                                                             name = self.uniqueName('treasureFlyTrack')))
        self.treasureTrack.start()

    def setGrab(self, avId):
        self.collNodePath.stash()
        self.avId = avId
        if self.cr.doId2do.has_key(avId):
            self.av = self.cr.doId2do[avId]
        else:
            self.nodePath.detachNode()
            return
        if self.playSoundForRemoteToons or self.avId == base.localAvatar.doId:
            base.playSfx(self.grabSound, node = self.nodePath)
        if not self.fly:
            self.nodePath.detachNode()
            return
        self.cleanupTrack()
        taskMgr.remove(str(self.spinTaskName))
        avatarGoneName = self.av.uniqueName('disable')
        self.accept(avatarGoneName, self.handleUnexpectedExit)
        flyTime = 1.0
        track = Sequence(LerpPosInterval(self.nodePath, flyTime, pos = Point3(0, 0, self.av.nametag3d.getZ(self.av) + 0.3), startPos = self.nodePath.getPos(self.av), blendType = 'easeInOut'),
                         Func(self.nodePath.detachNode), Func(self.ignore, avatarGoneName))
        if self.shadow:
            self.treasureTrack = Sequence(HideInterval(self.dropShadow), track, ShowInterval(self.dropShadow), name = self.uniqueName('treasureFlyTrack'))
        else:
            self.treasureTrack = Sequence(track, name = self.uniqueName('treasureFlyTrack'))
        self.nodePath.reparentTo(self.av)
        self.treasureTrack.start()

    def handleUnexpectedExit(self):
        self.notify.warning('%s disconnected while collecting treasure.' % (str(self.avId)))
        self.cleanupTrack()

    def d_requestGrab(self):
        self.sendUpdate('requestGrab', [])

    def startAnimation(self):
        pass

    def disable(self):
        self.ignoreAll()
        self.nodePath.detachNode()
        DistributedObject.disable(self)

    def cleanupTrack(self):
        if self.treasureTrack:
            self.treasureTrack.finish()
            self.treasureTrack = None
        self.spinTaskName = None

    def delete(self):
        self.cleanupTrack()
        DistributedObject.delete(self)
        self.nodePath.removeNode()
