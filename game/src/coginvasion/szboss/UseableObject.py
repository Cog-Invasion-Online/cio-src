from panda3d.core import NodePath, Point3, TransformState
from panda3d.bullet import BulletBoxShape, BulletRigidBodyNode, BulletGhostNode

from Useable import Useable
from src.coginvasion.phys.PhysicsNodePath import PhysicsNodePath
from src.coginvasion.phys import PhysicsUtils
from src.coginvasion.globals import CIGlobals

class UseableObject(PhysicsNodePath, Useable):
    
    def __init__(self, autoPhysBox = True):
        PhysicsNodePath.__init__(self, 'useableObject')
        Useable.__init__(self)
        
        self.autoPhysBox = autoPhysBox
        self.hasPhysGeom = False
        
        self.maxDistance = 10.0
        
        self.shapeGroup = CIGlobals.UseableGroup
        
    def getUseableBounds(self, min, max):
        self.calcTightBounds(min, max)

    def playerIsTouching(self):
        if not self.bodyNode:
            return False
            
        result = base.physicsWorld.contactTestPair(
                base.localAvatar.walkControls.controller.getCapsule().node(), self.bodyNode)
        touching = result.getNumContacts() != 0
        return touching
        
    def load(self, physName = 'useableObject'):
        if self.autoPhysBox:
            min = Point3(0)
            max = Point3(0)
            self.getUseableBounds(min, max)

            min -= Point3(0.1, 0.1, 0.1)
            max += Point3(0.1, 0.1, 0.1)

            extents = PhysicsUtils.extentsFromMinMax(min, max)

            shape = BulletBoxShape(extents)
            # Use the box as a trigger and collision geometry.
            if self.hasPhysGeom:
                bodyNode = BulletGhostNode(physName)
            else:
                bodyNode = BulletRigidBodyNode(physName)
            bodyNode.setKinematic(True)

            if not self.underneathSelf:
                center = PhysicsUtils.centerFromMinMax(min, max)
                bodyNode.addShape(shape, TransformState.makePos(center))
            else:
                bodyNode.addShape(shape)

            self.setupPhysics(bodyNode)
        else:
            for np in self.findAllMatches("**/+BulletRigidBodyNode"):
                np.setPythonTag('useableObject', self)
                np.setCollideMask(np.getCollideMask() | CIGlobals.UseableGroup)
                
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
        
        
