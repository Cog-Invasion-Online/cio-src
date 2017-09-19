"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedDeliveryGameBarrel.py
@author Brian Lach
@date July 7, 2017

"""

from direct.distributed.DistributedNode import DistributedNode

class DistributedDeliveryGameBarrel(DistributedNode):
    barrelscale = 0.15
    barrelpoints = [(1.05, 2.68, 0.84), (0, 2.68, 0.84), (-1.05, 2.68, 0.84),
                    (1.05, 3.68, 0.84), (0, 3.68, 0.84), (-1.05, 3.68, 0.84),
                    (1.05, 4.68, 0.84), (0, 4.68, 0.84), (-1.05, 4.68, 0.84),
                    (1.05, 5.68, 0.84), (0, 5.68, 0.84), (-1.05, 5.68, 0.84),
                    (1.05, 6.68, 0.84), (0, 6.68, 0.84), (-1.05, 6.68, 0.84),
                    (1.05, 7.68, 0.84), (0, 7.68, 0.84), (-1.05, 7.68, 0.84)]

    def __init__(self, cr):
        DistributedNode.__init__(self, cr)
        self.barrel = loader.loadModel('phase_4/models/cogHQ/gagTank.bam')
        self.barrel.setScale(self.barrelscale)
        self.barrel.setH(180)
        self.barrel.reparentTo(self)
        self.truckId = 0
        self.barrelPosIndex = 0

    def setTruck(self, truckId, posIndex):
        truck = self.cr.doId2do.get(truckId)
        if truck:
            self.reparentTo(truck)
            self.setPos(*self.barrelpoints[posIndex])
        self.truckId = truckId
        self.barrelPosIndex = posIndex

    def getTruck(self):
        return [self.truckId, self.barrelPosIndex]

    def giveToPlayer(self, avId):
        if avId == base.localAvatar.doId:
            if not base.localAvatar.hasBarrel:
                base.localAvatar.hasBarrel = True
                base.playSfx(base.minigame.soundPickUpBarrel)
                base.minigame.truckBarrelIsFrom = truckId
            else:
                return
        av = self.cr.doId2do.get(avId)
        if av:
            av.setForcedTorsoAnim('catchneutral')
            self.reparentTo(av.find('**/def_joint_right_hold'))
            self.setScale(0.3)
            self.setP(90)
            self.setZ(0.35)