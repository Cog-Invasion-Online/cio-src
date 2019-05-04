"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedToon.py
@author Brian Lach
@date June 17, 2014

Revamped on June 15, 2018.

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedSmoothNode import DistributedSmoothNode
from direct.distributed.ClockDelta import globalClockDelta
from direct.distributed.DelayDeletable import DelayDeletable
from direct.distributed import DelayDelete

from src.coginvasion.avatar.DistributedAvatar import DistributedAvatar
from src.coginvasion.toon import Toon

import random
import types

class DistributedToon(Toon.Toon, DistributedAvatar, DelayDeletable):
    notify = directNotify.newCategory('DistributedToon')

    LMHead = 0
    LMCage = 1
    LMOff = 2

    def __init__(self, cr):
        try:
            self.DistributedToon_initialized
            return
        except:
            self.DistributedToon_initialized = 1
        Toon.Toon.__init__(self, cr)
        DistributedAvatar.__init__(self, cr)

        self.lookMode = self.LMOff
        self.cageBone = None
        self.lookTask = None
        self.anim = ""

        return
        
    def handleHitByToon(self, player, gagId, distance):
        # I was hit by another toon.
        # This is a little strange because this function is called on the toon that got hit
        # but we send an update on the toon that did the hitting.
        #player.sendUpdate('toonHitByGag', [self.doId, gagId])
        pass

    def setupNameTag(self, tempName = None):
        Toon.Toon.setupNameTag(self, tempName)
        self.nametag.getNametag3d().setClickEvent('toonClicked', [self.doId])
        self.nametag.getNametag2d().setClickEvent('toonClicked', [self.doId])

    def stopLookTask(self):
        if self.lookTask:
            self.lookTask.remove()
            self.lookTask = None

    def startLookTask(self):
        self.stopLookTask()
        self.lookTask = taskMgr.add(self.updateLookPitch, self.uniqueName('updateLookPitch'))

    def setLookMode(self, mode):
        self.lookMode = mode

        if self.lookMode == self.LMCage:
            head = self.getPart('head')
            if head and not head.isEmpty():
                oldPitch = head.getP(self)
                head.setP(self, 0)
            cage = self.getCageBone()
            if cage and not cage.isEmpty():
                cage.setP(self, oldPitch)
        elif self.lookMode == self.LMHead:
            # transfer from cage to head
            cage = self.getCageBone()
            if cage and not cage.isEmpty():
                oldPitch = self.getCageBone().getP(self)
                self.resetCageBone()
            head = self.getPart('head')
            if head and not head.isEmpty():
                head.setP(self, oldPitch)

        if self.lookMode != self.LMOff:
            self.startLookTask()
        else:
            self.stopLookTask()

    def getLookMode(self):
        return self.lookMode

    def getCageBone(self, makeIfEmpty = True):
        if self.isEmpty():
            return None

        cageBone = self.find("**/def_cageA")
        if cageBone.isEmpty() and makeIfEmpty:
            cageBone = self.controlJoint(None, "torso", "def_cageA")

        return cageBone

    def resetCageBone(self):
        if self.isEmpty():
            return

        cageBone = self.find("**/def_cageA")
        if not cageBone.isEmpty():
            self.releaseJoint("torso", "def_cageA")
            cageBone.detachNode()

    def __updateHead(self, cage):
        head = self.getPart('head')
        if head and not head.isEmpty():
            if cage:
                head.setHpr(self, 0, self.lookPitch, 0)
            else:
                head.setP(self.lookPitch)

    def updateLookPitch(self, task):
        if self.lookMode == self.LMHead:
            self.__updateHead(False)

        elif self.lookMode == self.LMCage:
            bone = self.getCageBone()
            if bone and not bone.isEmpty():
                bone.setHpr(self, 0, self.lookPitch, 0)
            self.__updateHead(True)

        return task.cont

    def lookAtObject(self, h, p, r, blink=1):
        head = self.getPart('head')
        
        if not head or (head and head.getHpr() == (h, p, r)):
            return
        
        Toon.Toon.lerpLookAt(self, head, tuple((h, p, r)))
        if blink:
            maxBlinks = random.randint(1, 2)
            numBlinks = 0
            delay = 0
            for blink in range(maxBlinks):
                if numBlinks == 0:
                    taskMgr.add(self.doBlink, self.uniqueName("blinkOnTurn"))
                else:
                    delay += 0.22
                    taskMgr.doMethodLater(delay, self.doBlink, self.doBlinkTaskName)
                numBlinks += 1

    def b_lookAtObject(self, h, p, r, blink=1):
        self.d_lookAtObject(h, p, r, blink)
        self.lookAtObject(h, p, r, blink)

    def d_lookAtObject(self, h, p, r, blink=1):
        self.sendUpdate('lookAtObject', [h, p, r, blink])

    def setAnimState(self, anim, timestamp = None, callback = None, extraArgs = []):
        self.anim = anim
        if timestamp is None:
            ts = 0.0
        else:
            ts = globalClockDelta.localElapsedTime(timestamp)
        if self.animFSM.getStateNamed(anim):            
            self.animFSM.request(anim, [ts, callback, extraArgs])

    def b_setAnimState(self, anim):
        self.d_setAnimState(anim)
        self.setAnimState(anim, None)

    def d_setAnimState(self, anim):
        timestamp = globalClockDelta.getFrameNetworkTime()
        self.sendUpdate('setAnimState', [anim, timestamp])

    def getAnimState(self):
        return [self.anim, 0.0]

    def setName(self, name):
        Toon.Toon.setName(self, name)
        if self.cr.isShowingPlayerIds:
            self.showAvId()

    def d_setName(self, name):
        self.sendUpdate('setName', [name])

    def b_setName(self, name):
        self.d_setName(name)
        self.setName(name)

    def showAvId(self):
        self.setDisplayName(self.getName() + "\n" + str(self.doId))

    def showName(self):
        self.setDisplayName(self.getName())

    def setDisplayName(self, name):
        self.setupNameTag(tempName = name)

    def wrtReparentTo(self, parent):
        DistributedSmoothNode.wrtReparentTo(self, parent)

    def announceGenerate(self):
        DistributedAvatar.announceGenerate(self)
        if self.animFSM.getCurrentState().getName() == 'off':
            self.setAnimState('Happy')

    def generate(self):
        DistributedAvatar.generate(self)
        self.startSmooth()

    def disable(self):
        self.stopLookTask()

        taskMgr.remove(self.uniqueName('blinkOnTurn'))
        if self.track != None:
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        self.ignore('showAvId')
        self.ignore('showName')
        self.stopSmooth()
        Toon.Toon.disable(self)
        DistributedAvatar.disable(self)

    def delete(self):
        try:
            self.DistributedToon_deleted
        except:
            self.DistributedToon_deleted = 1
            del self.track
            Toon.Toon.delete(self)
            DistributedAvatar.delete(self)
        return
