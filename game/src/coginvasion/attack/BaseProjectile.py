from panda3d.core import Point3, Vec3, NodePath, ModelRoot

from direct.distributed.DistributedSmoothNode import DistributedSmoothNode

from src.coginvasion.phys.PhysicsNodePath import BasePhysicsObject
from src.coginvasion.base.Precache import Precacheable, precacheModel, precacheSound
from src.coginvasion.attack.BaseProjectileShared import BaseProjectileShared

class BaseProjectile(DistributedSmoothNode, BaseProjectileShared, BasePhysicsObject, Precacheable):
    """
    A projectile.
    This impl just renders the projectile model at the positions reported by the server.
    """

    ModelPath = None
    ModelOrigin = Point3(0, 0, 0)
    ModelAngles = Vec3(0, 0, 0)
    ModelScale = Vec3(1, 1, 1)

    ImpactSoundPath = None

    def __init__(self, cr):
        DistributedSmoothNode.__init__(self, cr)
        BaseProjectileShared.__init__(self)
        BasePhysicsObject.__init__(self)
        NodePath.__init__(self, ModelRoot("BaseProjectile"))

        self.model = None
        self.impactSound = None

    def impact(self, pos, lastPos):
        pass

    @classmethod
    def doPrecache(cls):
        if cls.ModelPath:
            precacheModel(cls.ModelPath)
        if cls.ImpactSoundPath:
            precacheSound(cls.ImpactSoundPath)

    def wantsSmoothing(self):
        return 0

    def disable(self):
        self.stopWaterCheck()
        self.cleanupPhysics()
        if self.model:
            self.model.removeNode()
            self.model = None
        self.impactSound = None
        BaseProjectileShared.cleanup(self)
        DistributedSmoothNode.disable(self)

    def announceGenerate(self):
        DistributedSmoothNode.announceGenerate(self)
        self.stopSmooth()
        if self.ImpactSoundPath:
            self.impactSound = base.audio3d.loadSfx(self.ImpactSoundPath)
        if self.ModelPath:
            self.model = loader.loadModel(self.ModelPath)
            self.model.reparentTo(self)
            self.model.setPos(self.ModelOrigin)
            self.model.setHpr(self.ModelAngles)
            self.model.setScale(self.ModelScale)
        self.reparentTo(render)
        self.onSpawn()
        self.startWaterCheck()
