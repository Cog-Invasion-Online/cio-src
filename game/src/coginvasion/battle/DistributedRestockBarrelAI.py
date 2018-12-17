"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedRestockBarrelAI.py
@author Maverick Liberty
@date February 28, 2016

"""

from direct.distributed.DistributedNodeAI import DistributedNodeAI

from src.coginvasion.szboss.DistributedEntityAI import DistributedEntityAI

class DistributedRestockBarrelAI(DistributedEntityAI):
    
    def __init__(self, air, dispatch):
        DistributedEntityAI.__init__(self, air, dispatch)
        self.usedAvIds = []
        
    def d_setGrab(self, avId):
        self.sendUpdate('setGrab', [avId])
        
    def requestGrab(self):
        avId = self.air.getAvatarIdFromSender()
        if avId not in self.usedAvIds:
            self.usedAvIds.append(avId)
            self.d_setGrab(avId)
        else:
            self.sendUpdate('setReject', [])