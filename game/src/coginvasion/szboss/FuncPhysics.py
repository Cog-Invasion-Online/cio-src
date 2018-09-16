from panda3d.core import NodePath, Point3, TransformState
from panda3d.bullet import BulletRigidBodyNode, BulletBoxShape

from src.coginvasion.phys import PhysicsUtils

from Entity import Entity

class FuncPhysics(Entity):

    def __init__(self):
        Entity.__init__(self)
        self.assign(NodePath('func_physics'))
        
    def load(self):
        Entity.load(self)
        loader = self.cEntity.getLoader()
        entnum = self.cEntity.getEntnum()
        rbnode = BulletRigidBodyNode('func_physics')
        mass = loader.getEntityValueFloat(entnum, "mass")
        rbnode.setMass(100)
        min = Point3(0)
        max = Point3(0)
        self.cEntity.getModelBounds(min, max)
        center = PhysicsUtils.centerFromMinMax(min, max)
        extents = PhysicsUtils.extentsFromMinMax(min, max)
        shape = BulletBoxShape(extents)
        rbnode.addShape(shape)
        self.assign(base.bspLoader.getResult().find("**/brushroot").attachNewNode(rbnode))
        self.setPos(center)
        self.cEntity.getModelNp().wrtReparentTo(self)
        base.physicsWorld.attachRigidBody(rbnode)
        
    def unload(self):
        Entity.unload(self)
        if not self.isEmpty():
            base.physicsWorld.remove(self.node())
