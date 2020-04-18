"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedPhysicsEntityAI.py
@author Brian Lach
@date June 15, 2018

"""

from direct.distributed.DistributedSmoothNodeAI import DistributedSmoothNodeAI
from PhysicsNodePathAI import PhysicsNodePathAI

class DistributedPhysicsEntityAI(DistributedSmoothNodeAI, PhysicsNodePathAI):
    
    def __init__(self, air):
        DistributedSmoothNodeAI.__init__(self, air)
        PhysicsNodePathAI.__init__(self, 'physEntity')

    def doSetupPhysics(self):
        self.setupPhysics(self.getPhysBody(), False)
        self.addToPhysicsWorld(self.air.getPhysicsWorld(self.zoneId))

    def getPhysBody(self):
        return None

    def announceGenerate(self):
        self.doSetupPhysics()
        DistributedSmoothNodeAI.announceGenerate(self)
        self.startPosHprBroadcast()#0.1) # every 100 ms we should broadcast pos

    def delete(self):
        self.stopPosHprBroadcast()
        self.cleanupPhysics()
        DistributedSmoothNodeAI.delete(self)

