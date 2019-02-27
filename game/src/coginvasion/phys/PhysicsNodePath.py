from panda3d.core import NodePath, BitMask32, Vec3
from panda3d.bullet import BulletRigidBodyNode, BulletGhostNode

from src.coginvasion.globals import CIGlobals

class BasePhysicsObject:

    def __init__(self):
        self.bodyNode = None
        self.bodyNP = None
        self.shapeGroup = BitMask32.allOn()
        self.underneathSelf = False

    def addToPhysicsWorld(self, world):
        print self.__class__.__name__, "Adding", self.bodyNode, "to physics world", world
        if self.bodyNode:
            world.attach(self.bodyNode)

    def removeFromPhysicsWorld(self, world):
        if self.bodyNode:
            world.remove(self.bodyNode)

    def cleanupPhysics(self):
        if self.bodyNode and hasattr(base, 'physicsWorld'):
            self.removeFromPhysicsWorld(base.physicsWorld)
        if self.bodyNP and not self.bodyNP.isEmpty():
            if self.underneathSelf:
                self.bodyNP.removeNode()
            self.bodyNP = None
            self.bodyNode = None

    def setupPhysics(self, bodyNode, underneathSelf = False):
        self.cleanupPhysics()

        self.underneathSelf = underneathSelf

        self.bodyNode = bodyNode

        assert self.bodyNode is not None

        parent = self.getParent()
        self.bodyNP = parent.attachNewNode(self.bodyNode)
        self.bodyNP.setCollideMask(self.shapeGroup)
        if not underneathSelf:
            self.reparentTo(self.bodyNP)
            self.assign(self.bodyNP)
        else:
            self.bodyNP.reparentTo(self)
        if hasattr(base, 'physicsWorld'):
            self.addToPhysicsWorld(base.physicsWorld)

class PhysicsNodePath(BasePhysicsObject, NodePath):

    def __init__(self, *args, **kwargs):
        BasePhysicsObject.__init__(self)
        NodePath.__init__(self, *args, **kwargs)
            