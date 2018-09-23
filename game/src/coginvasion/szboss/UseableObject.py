from panda3d.core import NodePath, Point3, TransformState
from panda3d.bullet import BulletBoxShape, BulletRigidBodyNode, BulletGhostNode

from Useable import Useable
from src.coginvasion.phys.PhysicsNodePath import PhysicsNodePath
from src.coginvasion.phys import PhysicsUtils

class UseableObject(PhysicsNodePath, Useable):
    
    def __init__(self, autoPhysBox = True):
        PhysicsNodePath.__init__(self, 'useableObject')
        Useable.__init__(self)
        
        self.autoPhysBox = autoPhysBox
        self.hasPhysGeom = False
        
        self.maxDistance = 10.0
        
    def getUseableBounds(self, min, max):
        self.calcTightBounds(min, max)

    def playerIsTouching(self):
        if not self.bodyNode:
            return False
            
        result = base.physicsWorld.contactTestPair(
                base.localAvatar.walkControls.controller.capsuleNP.node(), self.bodyNode)
        touching = result.getNumContacts() != 0
        return touching
        
    def load(self):
        if self.autoPhysBox:
            min = Point3(0)
            max = Point3(0)
            self.getUseableBounds(min, max)

            min -= Point3(0.1, 0.1, 0.1)
            max += Point3(0.1, 0.1, 0.1)

            center = PhysicsUtils.centerFromMinMax(min, max)
            extents = PhysicsUtils.extentsFromMinMax(min, max)

            shape = BulletBoxShape(extents)
            # Use the box as a trigger and collision geometry.
            if self.hasPhysGeom:
                bodyNode = BulletGhostNode('useableObject')
            else:
                bodyNode = BulletRigidBodyNode('useableObject')
            bodyNode.setKinematic(True)
            bodyNode.addShape(shape, TransformState.makePos(center))

            self.setupPhysics(bodyNode)
        if self.bodyNP:
            self.bodyNP.setPythonTag('useableObject', self)

    def removeNode(self):
        self.autoPhysBox = None
        self.hasPhysGeom = None
        self.maxDistance = None
        self.wasTouching = None
        self.cleanupPhysics()
        PhysicsNodePath.removeNode(self)
        
    #def canUse(self):
    #    return base.localAvatar.getDistance(self) <= self.maxDistance
        
        
