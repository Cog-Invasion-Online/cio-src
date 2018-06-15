"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedDeliveryTruckAI.py
@author Brian Lach
@date October 4, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedNodeAI import DistributedNodeAI

from src.coginvasion.globals import CIGlobals

class DistributedDeliveryTruckAI(DistributedNodeAI):
    notify = directNotify.newCategory('DistributedDeliveryTruckAI')

    truckTransByIndex = {0: [(-22.73, 0.0, 0.0), (203.25, 0.0, 0.0)],
                         1: [(21.0, 0.0, 0.0), (160.0, 0.0, 0.0)]}

    def __init__(self, air, mg, index):
        DistributedNodeAI.__init__(self, air)
        self.numBarrels = 0
        self.dBarrels = []
        self.hasReportedAllGone = False
        self.index = index
        self.mg = mg

    def suitPickUpBarrel(self, suitId):
        if self.numBarrels > 0:
            self.mg.sendUpdate('giveBarrelToSuit', [suitId])
            self.b_setNumBarrels(self.getNumBarrels() - 1)
            self.mg.b_setBarrelsRemaining(self.mg.getBarrelsRemaining() - 1)
            self.mg.b_setBarrelsStolen(self.mg.getBarrelsStolen() + 1)

    def requestBarrel(self):
        avId = self.air.getAvatarIdFromSender()
        if self.numBarrels > 0:
            self.dBarrels[len(self.dBarrels) - 1].sendUpdate('giveToPlayer', [avId])
            self.dBarrels.remove(self.dBarrels[len(self.dBarrels) - 1])
            self.numBarrels -= 1

    def barrelDroppedOff(self):
        if self.numBarrels == 0 and not self.hasReportedAllGone:
            self.mg.truckOutOfBarrels()
            self.hasReportedAllGone = True

    def setNumBarrels(self, num):
        self.numBarrels = num
        if num <= 0:
            self.mg.truckRanOutOfBarrels(self.index)

    def d_setNumBarrels(self, num):
        self.sendUpdate('setNumBarrels', [num])

    def b_setNumBarrels(self, num):
        self.d_setNumBarrels(num)
        self.setNumBarrels(num)

    def getNumBarrels(self):
        return self.numBarrels

    def getIndex(self):
        return self.index

    def announceGenerate(self):
        DistributedNodeAI.announceGenerate(self)
        pos, hpr = self.truckTransByIndex[self.index]
        self.d_setPos(*pos)
        self.d_setHpr(*hpr)
        self.b_setParent(CIGlobals.SPRender)

    def delete(self):
        self.numBarrels = None
        self.mg = None
        self.index = None
        self.hasReportedAllGone = None
        DistributedNodeAI.delete(self)
