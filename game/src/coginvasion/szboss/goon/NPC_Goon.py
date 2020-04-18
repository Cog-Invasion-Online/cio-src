from panda3d.core import Vec3, Vec4

from direct.interval.IntervalGlobal import Sequence, Wait, Func, ActorInterval, Parallel, LerpAnimInterval

from src.coginvasion.phys.Ragdoll import Ragdoll, RagdollLimbShapeDesc
from src.coginvasion.globals import CIGlobals
from src.coginvasion.avatar.DistributedAvatar import DistributedAvatar
from src.coginvasion.avatar.BaseActivity import BaseActivity
from src.coginvasion.avatar.Activities import *

class GoonRagdoll(Ragdoll):

    def setupLimbs(self):

        mass = 25

        # mike wazowski body
        self.addLimb("joint22", mass, shapes = [RagdollLimbShapeDesc(length = 0.7, radius = 0.7, localPos = (0, 0, 0.75), localHpr = (0, 0, 0))])

        # Left thigh
        self.addLimb("joint1", mass, shapes = [RagdollLimbShapeDesc(length = 1, radius = 0.2, localPos = (0.5, 0, 0), localHpr = (0, 0, -90))])
        # Left leg
        self.addLimb("joint2", mass, shapes = [RagdollLimbShapeDesc(length = 1, radius = 0.2, localPos = (0.5, 0, 0), localHpr = (0, 0, -90))])
        # Left foot
        self.addLimb("joint4", mass, shapes = [RagdollLimbShapeDesc(length = 1.5, radius = 0.3, localPos = (0.35, 0.2, 0), localHpr = (-30, 0, -95))])

        # Right thigh
        self.addLimb("joint6", mass, shapes = [RagdollLimbShapeDesc(length = 1, radius = 0.2, localPos = (0.5, 0, 0), localHpr = (0, 0, -90))])
        # Right leg
        self.addLimb("joint2_3", mass, shapes = [RagdollLimbShapeDesc(length = 1, radius = 0.2, localPos = (0.5, 0, 0), localHpr = (0, 0, -90))])
        # Right foot
        self.addLimb("joint4_4", mass, shapes = [RagdollLimbShapeDesc(length = 1.5, radius = 0.3, localPos = (0.35, 0, -0.2), localHpr = (0, 0, 60))])

    def setupJoints(self):
        # Left leg
        self.addJoint("joint22", "joint1", ((0.5,0,0), (0,0,90)), ((0,0,0), (0,0,0)), swing=(55, 0), twist= 45)
        self.addJoint("joint1", "joint2", ((1,0,0), (0,90,90)), ((0,0,0), (0,0,0)), swing=(0, 70), twist=0)
        self.addJoint("joint2", "joint4", ((1,0,0), (-90,0,-90)), ((0,0,0), (0,0,0)), swing=(0, 45), twist=0)
        # Right leg
        self.addJoint("joint22", "joint6", ((-0.5,0,0), (0,0,90)), ((0,0,0), (0,0,0)), swing=(55, 0), twist= 45)
        self.addJoint("joint6", "joint2_3", ((1,0,0), (0,90,90)), ((0,0,0), (0,0,0)), swing=(0, 70), twist=0)
        self.addJoint("joint2_3", "joint4_4", ((1,0,0), (0,0,0)), ((0,0,0), (0,0,0)), swing=(0, 45), twist=0)
        
    def getMainLimb(self):
        return "joint22"

class Goon_WakeAngry(BaseActivity):
    
    def doActivity(self):
        return Sequence(Func(self.avatar.playSound, "wakeup"),
                        ActorInterval(self.avatar, "wakeup"))
                        
class Goon_FireLaser(BaseActivity):
    
    def doActivity(self):
        return Sequence(Func(self.avatar.pose, "collapse", 1), Parallel(
                    Sequence(LerpAnimInterval(self.avatar, 0.25, self.avatar.standWalkRunReverse[0][0], "collapse"),
                            ActorInterval(self.avatar, "collapse", startFrame = 1, endFrame = 5, playRate = 0.8),
                            ActorInterval(self.avatar, "collapse", startFrame = 5, endFrame = 22, playRate = 0.7),
                            ActorInterval(self.avatar, "collapse", startFrame = 22, endFrame = 5, playRate = 0.7),
                            LerpAnimInterval(self.avatar, 0.25, "collapse", self.avatar.standWalkRunReverse[0][0])),

                    Sequence(Wait(0.1), Func(self.avatar.playSound, "whip")),
                    Sequence(Wait(0.55), Func(self.avatar.playSound, "shoot"))))

class NPC_Goon(DistributedAvatar):

    HatType_Security = 0
    HatType_Construction = 1
    HatType_Nothing = 2

    EyeColorLerpRatio = 0.3

    GoonieActorDef = ["phase_9/models/char/Cog_Goonie-zero.bam",
                       {"walk": "phase_9/models/char/Cog_Goonie-walk.bam",
                        "idle": "phase_9/models/char/Cog_Goonie-recovery.bam",
                        "scan": "phase_9/models/char/Cog_Goonie-recovery.bam",
                        "wakeup": "phase_9/models/char/Cog_Goonie-recovery.bam",
                        "collapse": "phase_9/models/char/Cog_Goonie-collapse.bam",
                        "zero": "phase_9/models/char/Cog_Goonie-zero.bam"}]

    def __init__(self, cr):
        DistributedAvatar.__init__(self, cr)
        self.eyeNode = None
        self.hatNode = None
        self.hatType = self.HatType_Security

        self.activities = {ACT_WAKE_ANGRY: Goon_WakeAngry(self),
                           ACT_RANGE_ATTACK1: Goon_FireLaser(self)}

        self.eyeColor = Vec3(0)
        self.idealEyeColor = Vec3(0)

        # Do some mixing on the idle animation
        self.moveAnimProperties['idle'] = {'method': 'pingpong', 'args': {'fromFrame': 94, 'toFrame': 96}}

        self.standWalkRunReverse = [('idle', 'walk', 0.0, 5.0, 1.0, 1.0)]

    def setHatType(self, type):
        self.hatType = type

    def getHatType(self):
        return self.hatType

    def setIdealEyeColor(self, r, g, b):
        self.idealEyeColor = Vec3(r, g, b)

    def getIdealEyeColor(self):
        return self.idealEyeColor

    def think(self):
        DistributedAvatar.think(self)

        # Update interpolated eye color
        if (self.idealEyeColor - self.eyeColor).lengthSquared() > 0.05*0.05:
            self.eyeColor = CIGlobals.lerpWithRatio(self.idealEyeColor, self.eyeColor, self.EyeColorLerpRatio)
            self.eyeNode.setColorScale(Vec4(self.eyeColor, 1.0), 1)

    @classmethod
    def doPrecache(cls):
        super(cls, NPC_Goon).doPrecache()
        from src.coginvasion.base.Precache import precacheActor
        precacheActor(cls.GoonieActorDef)

    def loadGoonie(self):
        self.setupPhysics()
        self.loadModel(self.GoonieActorDef[0], "goon")
        self.loadAnims(self.GoonieActorDef[1], "goon")
        self.getGeomNode().setH(180)
        
        self.hide(CIGlobals.ShadowCameraBitmask | CIGlobals.ReflectionCameraBitmask)

        self.find("**/hard_hat").setTwoSided(True)
        self.find("**/security_hat").setTwoSided(True)

        self.eyeNode = self.find("**/eye")
        self.eyeNode.setLightOff(1)

        # For the antenna
        self.find("**/unknown406").show()
        self.find("**/unknown406").setTwoSided(True)

        if self.hatType == self.HatType_Security:
            self.hatNode = self.find("**/security_hat")
            self.find("**/hard_hat").stash()
        elif self.hatType == self.HatType_Construction:
            self.hatNode = self.find("**/hard_hat")
            self.find("**/security_hat").stash()
        elif self.hatType == self.HatType_Nothing:
            self.find("**/hard_hat").stash()
            self.find("**/security_hat").stash()

        self.addSound("die",    "phase_14/audio/sfx/CHQ_GOON_hunker_down_fix.ogg")
        self.addSound("detect", "phase_9/audio/sfx/CHQ_GOON_tractor_beam_alarmed.ogg")
        self.addSound("wakeup", "phase_9/audio/sfx/CHQ_GOON_rattle_shake.ogg")
        self.addSound("idle",   "phase_9/audio/sfx/CHQ_FACT_stomper_raise.ogg")
        self.addSound("whip",   "phase_5/audio/sfx/General_device_appear.ogg")
        self.addSound("shoot",  "phase_5/audio/sfx/lightning_1.ogg")

        self.ragdoll = GoonRagdoll(self, "goon")
        self.ragdoll.setup()

    def announceGenerate(self):
        DistributedAvatar.announceGenerate(self)
        self.loadGoonie()
        self.startSmooth()
        self.reparentTo(render)
        
    def disable(self):
        self.stopSmooth()
        self.eyeNode = None
        self.hatType = None
        self.eyeColor = None
        self.idealEyeColor = None
        self.hatNode = None
        DistributedAvatar.disable(self)
