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
from src.coginvasion.globals import CIGlobals

class DistributedAvatar(DistributedSmoothNode, Avatar):
    notify = directNotify.newCategory("DistributedAvatar")

    EXTRAS = ["IMMUNITY LOSS!", "COMBO BONUS!", "WEAKNESS BONUS!", "MISSED!"]

    def __init__(self, cr):
        try:
            self.DistributedAvatar_initialized
            return
        except:
            self.DistributedAvatar_initialized = 1
        Avatar.__init__(self)
        DistributedSmoothNode.__init__(self, cr)
        self.place = 0
        self.hood = None
        self.moveBits = 0
        return

    def b_setMoveBits(self, bits):
        self.sendUpdate('setMoveBits', [bits])
        self.moveBits = bits

    def getMoveBits(self):
        return self.moveBits

    def b_splash(self, x, y, z):
        self.sendUpdate('splash', [x, y, z])
        self.splash(x, y, z)

    def setHood(self, hood):
        self.hood = hood

    def getHood(self):
        return self.hood

    def setName(self, name):
        Avatar.setName(self, name)

    def setChat(self, chat):
        Avatar.setChat(self, chat)

    def d_setChat(self, chat):
        self.sendUpdate("setChat", [chat])

    def b_setChat(self, chat):
        self.d_setChat(chat)
        self.setChat(chat)

    def setPlace(self, place):
        self.place = place

    def getPlace(self):
        return self.place

    def announceGenerate(self):
        DistributedSmoothNode.announceGenerate(self)
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
        self.hood = None
        self.place = None
