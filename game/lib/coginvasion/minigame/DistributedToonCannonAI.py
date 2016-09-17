# Filename: DistributedToonCannonAI.py
# Created by:  blach (06Jul15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.DistributedNodeAI import DistributedNodeAI

class DistributedToonCannonAI(DistributedNodeAI):
    notify = directNotify.newCategory("DistributedToonCannonAI")

    def __init__(self, air):
        DistributedNodeAI.__init__(self, air)
        self.avatar = 0

    def putAvatarInTurret(self, avId):
        self.avatar = avId
        
    def d_setOwner(self, avId):
        self.sendUpdate('setOwner', [avId])
        
    def getOwner(self):
        return self.avatar

    def delete(self):
        del self.avatar
        DistributedNodeAI.delete(self)
