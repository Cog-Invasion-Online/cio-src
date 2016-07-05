########################################
# Filename: DistributedRestockBarrelAI.py
# Created by: DecodedLogic (28Feb16)
########################################

from direct.distributed.DistributedNodeAI import DistributedNodeAI

class DistributedRestockBarrelAI(DistributedNodeAI):
    
    def __init__(self, air):
        DistributedNodeAI.__init__(self, air)
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