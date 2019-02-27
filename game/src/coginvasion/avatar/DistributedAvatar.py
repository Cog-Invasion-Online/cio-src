"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedAvatar.py
@author Brian Lach
@date November 02, 2014

"""

from panda3d.core import TextNode

from direct.distributed.DistributedSmoothNode import DistributedSmoothNode
from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.avatar.Avatar import Avatar
from src.coginvasion.avatar.AvatarShared import AvatarShared
from src.coginvasion.globals import CIGlobals

class DistributedAvatar(DistributedSmoothNode, Avatar):
    notify = directNotify.newCategory("DistributedAvatar")

    EXTRAS = ["IMMUNITY LOSS!", "COMBO BONUS!", "WEAKNESS BONUS!", "MISSED!"]

    def __init__(self, cr):
        Avatar.__init__(self)
        DistributedSmoothNode.__init__(self, cr)

    def doSmoothTask(self, task):
        self.smoother.computeAndApplySmoothPosHpr(self, self)
        if not hasattr(base, 'localAvatar') or self.doId != base.localAvatar.doId:
            self.setSpeed(self.smoother.getSmoothForwardVelocity(),
                          self.smoother.getSmoothRotationalVelocity(),
                          self.smoother.getSmoothLateralVelocity())
        return task.cont

    def b_setMoveBits(self, bits):
        self.sendUpdate('setMoveBits', [bits])
        self.moveBits = bits

    def b_splash(self, x, y, z):
        self.sendUpdate('splash', [x, y, z])
        self.splash(x, y, z)

    def setName(self, name):
        Avatar.setName(self, name)

    def setChat(self, chat):
        Avatar.setChat(self, chat)

    def b_setChat(self, chat):
        self.d_setChat(chat)
        self.setChat(chat)

    def announceGenerate(self):
        DistributedSmoothNode.announceGenerate(self)
        AvatarShared.announceGenerate(self)
        self.setPythonTag('avatar', self.doId)
        self.setParent(CIGlobals.SPHidden)
        self.loadAvatar()

    def generate(self):
        DistributedSmoothNode.generate(self)

    def disable(self):
        DistributedSmoothNode.disable(self)
        Avatar.disable(self)
        self.detachNode()
        return

    def delete(self):
        DistributedSmoothNode.delete(self)
        Avatar.delete(self)
