"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedRestockBarrelAI.py
@author Maverick Liberty
@date February 28, 2016

"""

from direct.distributed.DistributedNodeAI import DistributedNodeAI

from src.coginvasion.szboss.DistributedEntityAI import DistributedEntityAI

class DistributedRestockBarrelAI(DistributedEntityAI, DistributedNodeAI):
    
    def __init__(self, air, dispatch):
        DistributedEntityAI.__init__(self, air, dispatch)
        DistributedNodeAI.__init__(self, air)
        self.usedAvIds = []
        
    def announceGenerate(self):
        DistributedEntityAI.announceGenerate(self)
        DistributedNodeAI.announceGenerate(self)
        
        assert self.cEntity
        self.setPos(self.cEntity.getOrigin())
        self.setHpr(self.cEntity.getAngles())
        pos = self.getPos()
        hpr = self.getHpr()
        self.d_setPosHpr(pos[0], pos[1], pos[2], hpr[0], hpr[1], hpr[2])
        
    def delete(self):
        DistributedEntityAI.delete(self)
        DistributedNodeAI.delete(self)
        
    def generate(self):
        DistributedEntityAI.generate(self)
        DistributedNodeAI.generate(self)
        
    def d_setGrab(self, avId):
        self.sendUpdate('setGrab', [avId])
        
    def getGrab(self):
        return 0
        
    def getLabel(self):
        return 0
        
    def requestGrab(self, avId = None):
        npc = (avId is not None)
        if avId is None:
            avId = self.air.getAvatarIdFromSender()
        if npc or avId not in self.usedAvIds:
            if not npc:
                self.usedAvIds.append(avId)
            self.d_setGrab(avId)
        else:
            self.sendUpdate('setReject', [])
