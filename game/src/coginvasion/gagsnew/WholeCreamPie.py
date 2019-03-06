from panda3d.direct import STInt16
from panda3d.core import Point3, Vec3, VBase4

from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from direct.distributed.ClockDelta import globalClockDelta
from direct.interval.IntervalGlobal import Sequence, ActorInterval, Func, Parallel

from BaseGag import BaseGag, BaseGagAI
from src.coginvasion.avatar.Attacks import ATTACK_HOLD_RIGHT, ATTACK_GAG_WHOLECREAMPIE
from src.coginvasion.avatar.BaseProjectile import LobProjectile, LobProjectileAI, BaseProjectileAI
from src.coginvasion.avatar.TakeDamageInfo import TakeDamageInfo
from src.coginvasion.cog.ai.RelationshipsAI import RELATIONSHIP_FRIEND
from src.coginvasion.base.Precache import precacheSound
from src.coginvasion.gags import GagGlobals
from src.coginvasion.globals import CIGlobals
from src.coginvasion.phys import PhysicsUtils
from src.coginvasion.phys.WorldCollider import WorldCollider

import random

class WholeCreamPieProjectile(LobProjectile):
    ModelPath = "phase_14/models/props/creampie.bam"
    ModelScale = 0.85
    ImpactSoundPath = "phase_4/audio/sfx/AA_wholepie_only.ogg"

    SplatColor = VBase4(250.0 / 255.0, 241.0 / 255.0, 24.0 / 255.0, 1.0)
    SplatScale = 0.5

    def announceGenerate(self):
        LobProjectile.announceGenerate(self)

        vecEnd = Point3(*self.projEnd) + (0, 0, 90)
        vecStart = Point3(*self.projStart)
        throwDir = (vecEnd - vecStart).normalized()
        self.model.reparentTo(render)
        self.model.setPos(0, 0, 0)
        self.model.headsUp(throwDir)
        rot = self.model.getHpr(render)
        self.model.reparentTo(self)
        self.model.setHpr(rot[0], -90, 0)

    def impact(self, pos):
        CIGlobals.makeSplat(pos, self.SplatColor, self.SplatScale, self.impactSound)

class WholeCreamPieProjectileAI(LobProjectileAI):

    def doInitCollider(self):

        WorldCollider.__init__(self, "wholeCreamPieCollider", 1.0, needSelfInArgs = True,
                          useSweep = True, resultInArgs = True, startNow = False, mask = CIGlobals.WorldGroup | CIGlobals.CharacterGroup)
        self.world = self.air.getPhysicsWorld(self.zoneId)

class WholeCreamPieShared:
    StateDraw = 1
    StateThrow = 2

class WholeCreamPie(BaseGag, WholeCreamPieShared):
    ModelPath = "phase_14/models/props/creampie.bam"
    ModelScale = 0.85
    Hold = ATTACK_HOLD_RIGHT

    Name = GagGlobals.WholeCreamPie
    ID = ATTACK_GAG_WHOLECREAMPIE

    ModelVMOrigin = (0.07, 0.17, -0.01)
    ModelVMAngles = (0, -100, -10)
    ModelVMScale = ModelScale * 0.567

    ReleaseSpeed = 1.0
    ReleasePlayRateMultiplier = 1.0
    BobStartFrame = 30
    BobEndFrame = 40
    BobPlayRateMultiplier = 0.25
    ThrowObjectFrame = 62
    FinalThrowFrame = 90

    ThrowSoundPath = "phase_3.5/audio/sfx/AA_pie_throw_only.ogg"

    def __init__(self):
        BaseGag.__init__(self)
        self.throwSound = None

    @classmethod
    def doPrecache(cls):
        super(WholeCreamPie, cls).doPrecache()
        precacheSound(cls.ThrowSoundPath)

    def getViewPunch(self):
        return Vec3(random.uniform(.5, 1), random.uniform(-.5, -1), 0)

    def addPrimaryPressData(self, dg):
        # Send our precise hand position to the server
        # so the pie launches from the correct spot.
        CIGlobals.putVec3(dg, self.avatar.getRightHandNode().getPos(render))
        CIGlobals.putVec3(dg, camera.getPos(render))
        CIGlobals.putVec3(dg, camera.getQuat(render).getForward())

    def equip(self):
        if not BaseGag.equip(self):
            return False

        if not self.throwSound:
            self.throwSound = base.loadSfxOnNode(self.ThrowSoundPath, self.avatar)

        return True

    def cleanup(self):
        if self.throwSound:
            self.throwSound.stop()
            base.audio3d.detachSound(self.throwSound)
            self.throwSound = None
        BaseGag.cleanup(self)

    def __doDraw(self):
        self.doDrawNoHold('pie', 0, self.BobStartFrame, self.PlayRate)

    def __doHold(self):
        self.doHold('pie', self.BobStartFrame, self.BobEndFrame, self.PlayRate * self.BobPlayRateMultiplier)

    def setAction(self, action):
        BaseGag.setAction(self, action)
        
        if self.isFirstPerson():
            vm = self.getViewModel()
            vm.show()
            vmGag = self.getVMGag()
            vmGag.show()
            fpsCam = self.getFPSCam()

        self.model.show()

        if action == self.StateThrow:

            if self.throwSound:
                self.throwSound.play()

            if self.isFirstPerson():
                vmGag.hide()
                fpsCam.setVMAnimTrack(Sequence(ActorInterval(vm, "tnt_throw", startFrame = 27),
                                               Func(vm.hide)))
                fpsCam.addViewPunch(self.getViewPunch())

            self.model.hide()

            self.setAnimTrack(
                self.getAnimationTrack('pie', startFrame=self.ThrowObjectFrame,
                                       playRate=(self.PlayRate * self.ReleasePlayRateMultiplier)),
                startNow = True)

        elif action == self.StateDraw:
            if self.isFirstPerson():
                fpsCam.setVMAnimTrack(Sequence(ActorInterval(vm, "pie_draw")))
            self.__doDraw()

        elif action == self.StateIdle:
            if self.isFirstPerson():
                fpsCam.setVMAnimTrack(Sequence(Func(vm.loop, "pie_idle")))
            self.__doHold()

class WholeCreamPieAI(BaseGagAI, WholeCreamPieShared):

    Name = GagGlobals.WholeCreamPie
    ID = ATTACK_GAG_WHOLECREAMPIE

    ThrowPower = 200.0

    def __init__(self):
        BaseGagAI.__init__(self)
        self.actionLengths.update({self.StateDraw   :   0.5,
                                   self.StateThrow  :   1.0})

        self.throwOrigin = Point3(0)
        self.traceOrigin = Point3(0)
        self.traceVector = Vec3(0)

        self.ammo = 100
        self.maxAmmo = 100
        
        self.baseDamage = 30

        self.__projs = []

        self.throwTime = 0

    def equip(self):
        if not BaseGagAI.equip(self):
            return False

        self.throwTime = globalClock.getFrameTime()

        # Draw the whole cream pie!
        self.b_setAction(self.StateDraw)

        return True

    def determineNextAction(self, completedAction):
        if completedAction == self.StateDraw:
            return self.StateIdle
        elif completedAction == self.StateThrow:
            return self.StateDraw

        return self.StateIdle

    def __onProjectileHit(self, contact, collider, intoNP):
        avNP = intoNP.getParent()
        #print contact, collider, intoNP

        collider.d_impact(contact.getHitPos())

        currProj = collider.getPos(render)
        dmgInfo = TakeDamageInfo(self.avatar, self.getID(),
                                 self.calcDamage((currProj - collider.getInitialPos()).length()),
                                 currProj, collider.getInitialPos())

        for obj in base.air.avatars[self.avatar.zoneId]:
            if CIGlobals.isAvatar(obj) and obj.getKey() == avNP.getKey() and self.avatar.getRelationshipTo(obj) != RELATIONSHIP_FRIEND:
                # Make sure we don't friendly fire
                #print obj, "take damage", dmgInfo.damageAmount
                obj.takeDamage(dmgInfo)
                break

        collider.requestDelete()
        self.__projs.remove(collider)

    def setAction(self, action):
        BaseGagAI.setAction(self, action)

        if action == self.StateThrow:
            self.takeAmmo(-1)

            throwVector = PhysicsUtils.getThrowVector(self.traceOrigin,
                                                      self.traceVector,
                                                      self.throwOrigin,
                                                      self.avatar,
                                                      self.avatar.getBattleZone().getPhysicsWorld())
            endPos = CIGlobals.extrude(self.throwOrigin, self.ThrowPower, throwVector) - (0, 0, 90)
            
            proj = WholeCreamPieProjectileAI(base.air)
            proj.setProjectile(2.5, self.throwOrigin, endPos, 1.07, globalClockDelta.getFrameNetworkTime())
            proj.generateWithRequired(self.avatar.zoneId)
            proj.addHitCallback(self.__onProjectileHit)
            proj.addExclusion(self.avatar)
            self.__projs.append(proj)

            self.throwTime = globalClock.getFrameTime()
            
    def canUse(self):
        return self.hasAmmo() and (globalClock.getFrameTime() - self.throwTime >= 0.5)

    def primaryFirePress(self, data):
        if not self.canUse():
            return

        dg = PyDatagram(data)
        dgi = PyDatagramIterator(dg)
        self.throwOrigin = CIGlobals.getVec3(dgi)
        self.traceOrigin = CIGlobals.getVec3(dgi)
        self.traceVector = CIGlobals.getVec3(dgi)
        self.b_setAction(self.StateThrow)

    def npcUseAttack(self, target):
        #print "NPC Use attack:", self.avatar, self.action, self.getAmmo()
        if not self.canUse():
            #print "Can't use"
            return

        #print "using pie"

        #self.headsUp(target)
        self.throwOrigin = self.avatar.getPos(render) + (0, 0, self.avatar.getHeight() / 2.0)
        self.traceOrigin = self.throwOrigin
        self.traceVector = ((target.getPos(render) + (0, 0, target.getHeight() / 2.0)) - self.throwOrigin).normalized()
        self.setNextAction(self.StateThrow)

    def checkCapable(self, dot, squaredDistance):
        return squaredDistance <= 10*10
