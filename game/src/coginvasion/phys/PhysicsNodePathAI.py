from panda3d.core import NodePath

from BasePhysicsObjectShared import BasePhysicsObjectShared
        
class BasePhysicsObjectAI(BasePhysicsObjectShared):
    pass
	
class PhysicsNodePathAI(BasePhysicsObjectAI, NodePath):

    def __init__(self, *args, **kwargs):
        BasePhysicsObjectAI.__init__(self)
        NodePath.__init__(self, *args, **kwargs)