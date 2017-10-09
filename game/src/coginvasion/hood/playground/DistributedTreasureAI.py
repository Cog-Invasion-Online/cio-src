"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedTreasureAI.py
@author Maverick Liberty
@date July 15, 2015

"""

from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedTreasureAI(DistributedObjectAI):

    def __init__(self, air, treasurePlanner, x, y, z):
        DistributedObjectAI.__init__(self, air)
        self.treasurePlanner = treasurePlanner
        self.pos = x, y, z

    def requestGrab(self):
        avId = self.air.getAvatarIdFromSender()
        self.treasurePlanner.grabAttempt(avId, self.getDoId())

    def validAvatar(self, av):
        return True

    def d_setGrab(self, avId):
        self.sendUpdate('setGrab', [avId])

    def d_setReject(self):
        self.sendUpdate('setReject', [])

    def getPosition(self):
        return self.pos

    def setPosition(self, x, y, z):
        self.pos = x, y, z

    def d_setPosition(self, x, y, z):
        self.sendUpdate('setPosition', [x, y, z])

    def b_setPosition(self, x, y, z):
        self.setPosition(x, y, z)
        self.d_setPosition(x, y, z)
