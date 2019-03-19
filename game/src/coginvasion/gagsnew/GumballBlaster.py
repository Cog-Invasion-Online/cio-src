
from panda3d.core import Vec3, VBase4, Point3
from panda3d.bullet import BulletSphereShape, BulletRigidBodyNode

from BaseHitscan import BaseHitscan, BaseHitscanAI
from src.coginvasion.avatar.Attacks import ATTACK_GUMBALLBLASTER, ATTACK_HOLD_LEFT
from src.coginvasion.cog.ai.RelationshipsAI import RELATIONSHIP_FRIEND
from src.coginvasion.gags import GagGlobals
from src.coginvasion.base.Precache import precacheSound
from src.coginvasion.phys import PhysicsUtils
from src.coginvasion.avatar.BaseProjectile import LobProjectile, LobProjectileAI
from src.coginvasion.avatar.TakeDamageInfo import TakeDamageInfo
from src.coginvasion.globals import CIGlobals
from src.coginvasion.phys.WorldCollider import WorldCollider

from direct.interval.IntervalGlobal import ActorInterval, Func
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

import random

class GumballProjectile(LobProjectile):

    ModelPath = "models/smiley.egg.pz"
    ModelScale = 0.15
    ImpactSoundPath = "phase_14/audio/sfx/gumball_pop.ogg"

    SplatColor = VBase4(250.0 / 255.0, 241.0 / 255.0, 24.0 / 255.0, 1.0)
    SplatScale = 0.25

    def announceGenerate(self):
        LobProjectile.announceGenerate(self)
        self.model.setLightOff()
        self.model.setBSPMaterial("phase_14/materials/models/gumball.mat", 1)
        self.color = VBase4(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), 1.0)
        self.model.setColorScale(self.color, 1)

    def impact(self, pos):
        CIGlobals.makeSplat(pos, self.color, self.SplatScale, self.impactSound)

class GumballProjectileAI(LobProjectileAI):

    def doInitCollider(self):

        WorldCollider.__init__(self, "GumballCollider", 0.15, needSelfInArgs = True,
                          useSweep = True, resultInArgs = True, startNow = False, mask = CIGlobals.WorldGroup | CIGlobals.CharacterGroup)
        self.world = self.air.getPhysicsWorld(self.zoneId)

class GumballBlaster(BaseHitscan):
    ID = ATTACK_GUMBALLBLASTER
    Name = GagGlobals.GumballBlaster
    Hold = ATTACK_HOLD_LEFT

    ModelPath = "phase_14/models/props/gumballShooter.bam"
    ModelVMOrigin = (-0.53, 0.28, 0.52)
    ModelVMAngles = (72.68, 350.58, 351.82)
    ModelVMScale = 0.169

    FireSoundPath = "phase_14/audio/sfx/gumball_fire.ogg"

    AutoFireDelay = 0.1

    def __init__(self):
        BaseHitscan.__init__(self)

        self.firing = False
        self.lastFire = 0.0
        self.vmSpinNode = None

        self.fireSound = base.audio3d.loadSfx(self.FireSoundPath)

    @classmethod
    def doPrecache(cls):
        super(GumballBlaster, cls).doPrecache()
        precacheSound(cls.FireSoundPath)

    def think(self):
        if not self.isLocal():
            return

        now = globalClock.getFrameTime()
        if self.firing and now - self.lastFire > self.AutoFireDelay:
            self.primaryFirePress()

    def addPrimaryPressData(self, dg):
        BaseHitscan.addPrimaryPressData(self, dg)
        CIGlobals.putVec3(dg, self.getVMGag().find("**/Emitter1").getPos(render))

    def primaryFirePress(self, data = None):
        self.firing = True
        self.lastFire = globalClock.getFrameTime()
        BaseHitscan.primaryFirePress(self, data)

    def primaryFireRelease(self, data = None):
        self.firing = False
        BaseHitscan.primaryFireRelease(self, data)

    def equip(self):
        if not BaseHitscan.equip(self):
            return False

        if self.isFirstPerson():
            self.getFPSCam().setViewModelFOV(54.0)
            balls = loader.loadModel("phase_14/models/props/gumballShooter_balls.bam")
            balls.reparentTo(self.getVMGag())
            for gumball in balls.findAllMatches("**/+GeomNode"):
                gumball.setColorScale(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), 1.0, 1)
            balls.flattenStrong()

        base.audio3d.attachSoundToObject(self.fireSound, self.avatar)
    
        return True

    def unEquip(self):
        if not BaseHitscan.unEquip(self):
            return False

        if self.isFirstPerson():
            self.getFPSCam().restoreViewModelFOV()

            if self.vmSpinNode:
                self.vmSpinNode.detachNode()
                self.vmSpinNode = None

        base.audio3d.detachSound(self.fireSound)

        return True

    def cleanup(self):
        self.firing = None
        self.lastFire = None
        self.fireSound = None
        self.vmSpinNode = None
        BaseHitscan.cleanup(self)

    def onSetAction(self, action):

        if action == self.StateFire:
            self.fireSound.play()

        if self.isFirstPerson():
            fpsCam = self.getFPSCam()
            vm = self.getViewModel()

            if action == self.StateIdle:
                fpsCam.setVMAnimTrack(Func(vm.loop, "gumball_idle"))
            elif action == self.StateDraw:
                fpsCam.setVMAnimTrack(ActorInterval(vm, "gumball_draw"))
            elif action == self.StateFire:
                fpsCam.addViewPunch(Vec3(random.uniform(-0.5, 0.5), random.uniform(1, 2), 0.0))
                fpsCam.setVMAnimTrack(ActorInterval(vm, "gumball_fire"))
                if self.vmSpinNode:
                    self.vmSpinNode.hprInterval(0.5, (0, 0, 360), (0, 0, 0)).play()

class GumballBlaster_AI(BaseHitscanAI):
    ID = ATTACK_GUMBALLBLASTER
    Name = GagGlobals.GumballBlaster

    FireDelay = 0.1
    AttackRange = 10000

    UsesAmmo = True
    HasClip = False

    FirePower = 200.0

    def __init__(self):
        BaseHitscanAI.__init__(self)
        self.actionLengths.update({self.StateDraw: 0.7085,
                                   self.StateFire: 0.5417})
        self.ammo = 150
        self.maxAmmo = 150
        self.baseDamage = 5

        self.fireOrigin = Point3(0)

    def canUse(self):
        return self.hasAmmo() and self.action in [self.StateIdle, self.StateFire]

    def primaryFirePress(self, data):
        if not self.canUse():
            return

        dg = PyDatagram(data)
        dgi = PyDatagramIterator(dg)
        self.traceOrigin = CIGlobals.getVec3(dgi)
        self.traceVector = CIGlobals.getVec3(dgi)
        self.fireOrigin = CIGlobals.getVec3(dgi)
        self.setNextAction(self.StateFire)

    def __onProjectileHit(self, contact, collider, intoNP):
        avNP = intoNP.getParent()

        collider.d_impact(contact.getHitPos())

        currProj = collider.getPos(render)
        dmgInfo = TakeDamageInfo(self.avatar, self.getID(),
                                 self.calcDamage((currProj - collider.getInitialPos()).length()),
                                 currProj, collider.getInitialPos())

        for obj in base.air.avatars[self.avatar.zoneId]:
            if CIGlobals.isAvatar(obj) and obj.getKey() == avNP.getKey() and self.avatar.getRelationshipTo(obj) != RELATIONSHIP_FRIEND:
                obj.takeDamage(dmgInfo)
                break

        collider.requestDelete()

    def onSetAction(self, action):
        if action == self.StateFire:
            #self.takeAmmo(-1)

            throwVector = PhysicsUtils.getThrowVector(self.traceOrigin,
                                                      self.traceVector,
                                                      self.fireOrigin,
                                                      self.avatar,
                                                      self.avatar.getBattleZone().getPhysicsWorld())
            endPos = CIGlobals.extrude(self.fireOrigin, self.FirePower, throwVector) - (0, 0, 90)
            
            proj = GumballProjectileAI(base.air)
            proj.setProjectile(2.5, self.fireOrigin, endPos, 1.07, globalClockDelta.getFrameNetworkTime())
            proj.generateWithRequired(self.avatar.zoneId)
            proj.addHitCallback(self.__onProjectileHit)
            proj.addExclusion(self.avatar)

