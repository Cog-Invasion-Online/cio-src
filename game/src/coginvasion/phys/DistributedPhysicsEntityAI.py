"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedPhysicsEntityAI.py
@author Brian Lach
@date June 15, 2018

"""

from direct.distributed.DistributedSmoothNodeAI import DistributedSmoothNodeAI
from PhysicsNodePath import PhysicsNodePath

class DistributedPhysicsEntityAI(DistributedSmoothNodeAI, PhysicsNodePath):
    
    def __init__(self, air):
        DistributedSmoothNodeAI.__init__(self, air)
        PhysicsNodePath.__init__(self, 'physEntity')

    def doSetupPhysics(self):
        self.setupPhysics(self.getPhysBody(), False)

    def getPhysBody(self):
        return None

    def announceGenerate(self):
        self.doSetupPhysics()
        DistributedSmoothNodeAI.announceGenerate(self)
        self.activateSmoothing(True, False)
        self.startPosHprBroadcast(0.075) # broadcast every 75 milliseconds

    def delete(self):
        self.stopPosHprBroadcast()
        self.cleanupPhysics()
        DistributedSmoothNodeAI.delete(self)

