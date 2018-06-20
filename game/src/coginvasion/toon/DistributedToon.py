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

class DistributedToon(Toon.Toon, DistributedAvatar, DistributedSmoothNode, DelayDeletable):
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
        DistributedSmoothNode.__init__(self, cr)
        self.animState2animId = {}
        for index in range(len(self.animFSM.getStates())):
            self.animState2animId[self.animFSM.getStates()[index].getName()] = index
        self.animId2animState = {v: k for k, v in self.animState2animId.items()}

        self.lookMode = self.LMOff
        self.lookPitch = 0
        self.cageBone = None
        self.lookTask = None

        return

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
            oldPitch = head.getP(self)
            head.setP(self, 0)
            self.getCageBone().setP(self, oldPitch)
        elif self.lookMode == self.LMHead:
            # transfer from cage to head
            oldPitch = self.getCageBone().getP(self)
            self.resetCageBone()
            self.getPart('head').setP(self, oldPitch)

        if self.lookMode != self.LMOff:
            self.startLookTask()
        else:
            self.stopLookTask()

    def getLookMode(self):
        return self.mode

    def setLookPitch(self, pitch):
        self.lookPitch = pitch

    def getLookPitch(self):
        return self.lookPitch

    def getCageBone(self, makeIfEmpty = True):
        cageBone = self.find("**/def_cageA")
        if cageBone.isEmpty() and makeIfEmpty:
            cageBone = self.controlJoint(None, "torso", "def_cageA")
        return cageBone

    def resetCageBone(self):
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
            bone.setHpr(self, 0, self.lookPitch, 0)
            self.__updateHead(True)

        return task.cont

    def doSmoothTask(self, task):
        self.smoother.computeAndApplySmoothPosHpr(self, self)
        if not hasattr(base, 'localAvatar'):
            return task.done
        else:
            if self.doId != base.localAvatar.doId:
                self.setSpeed(self.smoother.getSmoothForwardVelocity(),
                              self.smoother.getSmoothRotationalVelocity(),
                              self.smoother.getSmoothLateralVelocity())
        return task.cont

    def lookAtObject(self, h, p, r, blink=1):
        if self.getPart('head').getHpr() == (h, p, r):
            return
        Toon.Toon.lerpLookAt(self, self.getPart('head'), tuple((h, p, r)))
        if blink:
            self.stopBlink()
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
            taskMgr.doMethodLater(delay, self.__startBlinkAfterLook, self.uniqueName("sBAL"))

    def __startBlinkAfterLook(self, task):
        self.startBlink()
        return task.done

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

        if type(anim) == types.IntType:
            anim = self.animId2animState[anim]
        if self.animFSM.getStateNamed(anim):
            self.animFSM.request(anim, [ts, callback, extraArgs])

    def b_setAnimState(self, anim):
        self.d_setAnimState(anim)
        self.setAnimState(anim, None)

    def d_setAnimState(self, anim):
        if type(anim) == types.StringType:
            anim = self.animState2animId[anim]
        timestamp = globalClockDelta.getFrameNetworkTime()
        self.sendUpdate('setAnimState', [anim, timestamp])

    def getAnimState(self):
        return self.anim

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
            self.setAnimState('neutral')
        self.startBlink()

    def generate(self):
        DistributedAvatar.generate(self)
        DistributedSmoothNode.generate(self)
        self.startSmooth()

    def disable(self):
        self.animState2animId = None
        self.animId2animState = None

        taskMgr.remove(self.uniqueName('sBAL'))
        taskMgr.remove(self.uniqueName('blinkOnTurn'))
        if self.track != None:
            self.track.finish()
            DelayDelete.cleanupDelayDeletes(self.track)
            self.track = None
        self.stopBlink()
        self.ignore('showAvId')
        self.ignore('showName')
        self.stopSmooth()
        Toon.Toon.disable(self)
        DistributedAvatar.disable(self)
        DistributedSmoothNode.disable(self)

    def delete(self):
        try:
            self.DistributedToon_deleted
        except:
            self.DistributedToon_deleted = 1
            del self.animState2animId
            del self.animId2animState
            del self.track
            Toon.Toon.delete(self)
            DistributedAvatar.delete(self)
            DistributedSmoothNode.delete(self)
        return
