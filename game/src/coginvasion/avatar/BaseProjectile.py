from panda3d.core import NodePath, Point3, Vec3, NodePath, ModelRoot

from direct.distributed.DistributedSmoothNode import DistributedSmoothNode
from direct.distributed.DistributedSmoothNodeAI import DistributedSmoothNodeAI
from direct.interval.IntervalGlobal import LerpPosInterval
from src.coginvasion.minigame.FlightProjectileInterval import FlightProjectileInterval

from src.coginvasion.phys.PhysicsNodePath import BasePhysicsObject
from src.coginvasion.phys.WorldCollider import WorldCollider
from src.coginvasion.base.Precache import Precacheable, precacheModel, precacheSound
from src.coginvasion.globals import CIGlobals

# ================================================================================

class BaseProjectileShared:
    
    def __init__(self):
        self.ival = None

    def cleanup(self):
        if self.ival:
            self.ival.finish()
            self.ival = None

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

    def impact(self, pos):
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

class BaseProjectileAI(DistributedSmoothNodeAI, BaseProjectileShared, WorldCollider):

    WantNPInit = False

    def __init__(self, air):
        DistributedSmoothNodeAI.__init__(self, air)
        BaseProjectileShared.__init__(self)
        # Defer initialization of WorldCollider, so each projectile
        # can have a unique WorldCollider setup.

    def d_impact(self, pos):
        pos = [pos[0], pos[1], pos[2]]
        self.sendUpdate('impact', [pos])

    def doInitCollider(self):
        WorldCollider.__init__(self, "none", 1.0, needSelfInArgs = True, resultInArgs = True,
                          useSweep = True, startNow = False, initNp = False, mask = CIGlobals.WorldGroup | CIGlobals.CharacterGroup)
        self.world = self.air.getPhysicsWorld(self.zoneId)

    def announceGenerate(self):
        pos = self.getPos(render)
        self.doInitCollider()
        self.reparentTo(render)
        self.setPos(pos)
        DistributedSmoothNodeAI.announceGenerate(self)
        self.stopPosHprBroadcast()
        self.start()
        self.onSpawn()

    def delete(self):
        BaseProjectileShared.cleanup(self)
        self.stop()
        DistributedSmoothNodeAI.delete(self)

# ================================================================================
    
class LinearProjectileShared:

    def __init__(self):
        self.linearDuration = 0.0
        self.linearStart = [0, 0, 0]
        self.linearEnd = [0, 0, 0]
        self.linearTimestamp = 0.0

    def setLinear(self, linearDuration, linearStart, linearEnd, timestamp):
        self.linearDuration = linearDuration
        self.linearStart = linearStart
        self.linearEnd = linearEnd
        self.linearTimestamp = timestamp

        self.setPos(*self.linearStart)

    def playLinear(self):
        ts = globalClockDelta.localElapsedTime(self.linearTimestamp)
        self.ival = LerpPosInterval(self, self.linearDuration, Point3(*self.linearEnd), Point3(*self.linearStart))
        self.ival.start(ts)

    def getLinear(self):
        return [self.linearDuration, self.linearStart, self.linearEnd, self.linearTimestamp]

    def cleanup(self):
        del self.linearDuration
        del self.linearStart
        del self.linearEnd
        del self.linearTimestamp

class LinearProjectile(BaseProjectile, LinearProjectileShared):

    def __init__(self, cr):
        BaseProjectile.__init__(self, cr)
        LinearProjectileShared.__init__(self)

    def onSpawn(self):
        self.playLinear()

    def disable(self):
        LinearProjectileShared.cleanup(self)
        BaseProjectile.disable(self)

class LinearProjectileAI(BaseProjectileAI, LinearProjectileShared):

    def __init__(self, air):
        BaseProjectileAI.__init__(self, air)
        LinearProjectileShared.__init__(self)

    def onSpawn(self):
        self.playLinear()

    def delete(self):
        LinearProjectileShared.cleanup(self)
        BaseProjectileAI.delete(self)

# ================================================================================

class LobProjectileShared:

    def __init__(self):
        self.projDuration = 0
        self.projStart = [0, 0, 0]
        self.projEnd = [0, 0, 0]
        self.projGravity = 1.0
        self.projTimestamp = 0.0

    def setProjectile(self, projDur, projStart, projEnd, projGravity, timestamp):
        self.projDuration = projDur
        self.projStart = projStart
        self.projEnd = projEnd
        self.projGravity = projGravity
        self.projTimestamp = timestamp

        self.setPos(*self.projStart)

    def playProjectile(self):
        ts = globalClockDelta.localElapsedTime(self.projTimestamp)
        self.ival = FlightProjectileInterval(self, startPos = Point3(*self.projStart), endPos = Point3(*self.projEnd),
                                                duration = self.projDuration, gravityMult = self.projGravity)
        self.ival.start(ts)

    def getProjectile(self):
        return [self.projDuration, self.projStart, self.projEnd, self.projGravity, self.projTimestamp]

    def cleanup(self):
        del self.projDuration
        del self.projStart
        del self.projEnd
        del self.projGravity
        del self.projTimestamp

class LobProjectile(BaseProjectile, LobProjectileShared):

    def __init__(self, cr):
        BaseProjectile.__init__(self, cr)
        LobProjectileShared.__init__(self)

    def onSpawn(self):
        self.playProjectile()

    def disable(self):
        LobProjectileShared.cleanup(self)
        BaseProjectile.disable(self)

class LobProjectileAI(BaseProjectileAI, LobProjectileShared):

    def __init__(self, air):
        LobProjectileShared.__init__(self)
        BaseProjectileAI.__init__(self, air)

    def onSpawn(self):
        self.playProjectile()

    def delete(self):
        LobProjectileShared.cleanup(self)
        BaseProjectileAI.delete(self)