"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedPhysicsEntity.py
@author Brian Lach
@date June 15, 2018

"""

from panda3d.core import ModelRoot

from direct.distributed.DistributedSmoothNode import DistributedSmoothNode

from PhysicsNodePath import PhysicsNodePath

class DistributedPhysicsEntity(DistributedSmoothNode, PhysicsNodePath):

    def __init__(self, cr):
        DistributedSmoothNode.__init__(self, cr)
        PhysicsNodePath.__init__(self, ModelRoot('physEntity'))

    def doSetupPhysics(self):
        self.setupPhysics(self.getPhysBody(), True)

    def getPhysBody(self):
        return None

    def announceGenerate(self):
        self.doSetupPhysics()
        DistributedSmoothNode.announceGenerate(self)
        self.activateSmoothing(True, True)
        self.reparentTo(render)
        self.startSmooth()

    def disable(self):
        self.stopSmooth()
        self.cleanupPhysics()
        DistributedSmoothNode.disable(self)
