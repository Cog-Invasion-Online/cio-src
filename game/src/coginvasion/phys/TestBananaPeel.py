from panda3d.bullet import BulletRigidBodyNode, BulletSphereShape, BulletCylinderShape, ZUp, BulletBoxShape
from panda3d.core import TransformState, Vec3, Point3, BitMask32

from src.coginvasion.phys.PhysicsNodePath import PhysicsNodePath
from src.coginvasion.globals import CIGlobals

import random

class TestBananaPeel(PhysicsNodePath):
    """Showcase the physics engine with a banana peel."""

    def __init__(self):
        PhysicsNodePath.__init__(self, 'bpeel')

        self.shapeGroup = BitMask32.allOn()

        sph = BulletSphereShape(0.4)
        rbnode = BulletRigidBodyNode('bpeel_body')
        rbnode.setMass(5.0)
        rbnode.addShape(sph)
        rbnode.setCcdMotionThreshold(1e-7)
        rbnode.setCcdSweptSphereRadius(0.4)

        self.mdl = loader.loadModel("phase_5/models/props/baseball.bam")
        self.mdl.setScale(6.0)
        self.mdl.reparentTo(self)
        self.mdl.showThrough(CIGlobals.ShadowCameraBitmask)

        self.setupPhysics(rbnode)

        #self.makeShadow(0.2)

        self.reparentTo(render)
        self.setPos(base.localAvatar.getPos(render))
        self.setQuat(base.localAvatar.getQuat(render))

        dir = self.getQuat(render).xform(Vec3.forward())
        amp = 20
        self.node().setLinearVelocity(dir * amp)

class TestCan(PhysicsNodePath):

    def __init__(self):
        PhysicsNodePath.__init__(self, 'can')

        self.shapeGroup = BitMask32.allOn()

        sph = BulletCylinderShape(0.5, 1.2, ZUp)
        rbnode = BulletRigidBodyNode('can_body')
        rbnode.setMass(10.0)
        rbnode.addShape(sph)
        rbnode.setCcdMotionThreshold(1e-7)
        rbnode.setCcdSweptSphereRadius(0.5)

        self.mdl = loader.loadModel("phase_5/models/props/can.bam")
        self.mdl.setScale(11.0)
        self.mdl.setZ(-0.55)
        self.mdl.reparentTo(self)
        self.mdl.showThrough(CIGlobals.ShadowCameraBitmask)

        self.setupPhysics(rbnode)

        #self.makeShadow(0.2)

        self.reparentTo(render)
        self.setPos(base.localAvatar.getPos(render))
        self.setQuat(base.localAvatar.getQuat(render))

        dir = self.getQuat(render).xform(Vec3.forward())
        amp = 10
        self.node().setLinearVelocity(dir * amp)

class TestSafe(PhysicsNodePath):
    def __init__(self):
        PhysicsNodePath.__init__(self, 'can')

        self.shapeGroup = BitMask32.allOn()

        sph = BulletBoxShape(Vec3(2, 2, 2))
        rbnode = BulletRigidBodyNode('can_body')
        rbnode.setMass(100.0)
        rbnode.addShape(sph, TransformState.makePos(Point3(0, 0, 1)))
        rbnode.setCcdMotionThreshold(1e-7)
        rbnode.setCcdSweptSphereRadius(0.5)

        self.mdl = loader.loadModel("phase_5/models/props/safe-mod.bam")
        self.mdl.setScale(6)
        self.mdl.setZ(-1)
        self.mdl.reparentTo(self)
        self.mdl.showThrough(CIGlobals.ShadowCameraBitmask)

        self.setupPhysics(rbnode)

        #self.makeShadow(0.2)

        self.reparentTo(render)
        self.setPos(base.localAvatar.getPos(render) + (0, 0, 20))
        self.setQuat(base.localAvatar.getQuat(render))
