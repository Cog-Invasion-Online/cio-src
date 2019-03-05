from panda3d.direct import STInt16
from panda3d.core import Point3, Vec3, VBase4

from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from direct.distributed.ClockDelta import globalClockDelta
from direct.interval.IntervalGlobal import Sequence, ActorInterval, Func, Parallel, Wait

from src.coginvasion.avatar.BaseAttacks import BaseAttack, BaseAttackAI
from src.coginvasion.avatar.Attacks import ATTACK_HOLD_RIGHT, ATTACK_CLIPONTIE
from src.coginvasion.avatar.BaseProjectile import LinearProjectile, LinearProjectileAI, BaseProjectileAI
from src.coginvasion.avatar.TakeDamageInfo import TakeDamageInfo
from src.coginvasion.cog.ai.RelationshipsAI import RELATIONSHIP_FRIEND
from src.coginvasion.base.Precache import precacheSound
from src.coginvasion.gags import GagGlobals
from src.coginvasion.globals import CIGlobals
from src.coginvasion.phys import PhysicsUtils
from src.coginvasion.phys.WorldCollider import WorldCollider

import random

class ClipOnTieProjectile(LinearProjectile):
    ModelPath = "phase_5/models/props/power-tie.bam"
    ModelScale = 4
    ImpactSoundPath = "phase_5/audio/sfx/SA_powertie_impact.ogg"
    ThrowSoundPath = "phase_5/audio/sfx/SA_powertie_throw.ogg"

    def __init__(self, cr):
        LinearProjectile.__init__(self, cr)
        self.throwSound = None

    def disable(self):
        if self.throwSound:
            base.audio3d.detachSound(self.throwSound)
        self.throwSound = None
        LinearProjectile.disable(self)

    def announceGenerate(self):
        LinearProjectile.announceGenerate(self)

        if not self.throwSound:
            self.throwSound = base.loadSfxOnNode(self.ThrowSoundPath, self)
        self.throwSound.play()

        vecEnd = Point3(*self.linearStart)
        vecStart = Point3(*self.linearEnd)
        throwDir = (vecEnd - vecStart).normalized()
        self.model.reparentTo(render)
        self.model.setPos(0, 0, 0)
        self.model.headsUp(throwDir)
        rot = self.model.getHpr(render)
        self.model.reparentTo(self)
        self.model.setHpr(rot[0], 0, 0)

    def impact(self, pos):
        base.audio3d.attachSoundToObject(self.impactSound, self)
        self.impactSound.play()

class ClipOnTieProjectileAI(LinearProjectileAI):

    def doInitCollider(self):
        WorldCollider.__init__(self, "wholeCreamPieCollider", 1.0, needSelfInArgs = True,
                          useSweep = True, resultInArgs = True, startNow = False,
                          mask = CIGlobals.WorldGroup | CIGlobals.CharacterGroup)
        self.world = self.air.getPhysicsWorld(self.zoneId)

class ClipOnTieShared:
    StateThrow = 1

class ClipOnTie(BaseAttack, ClipOnTieShared):
    ModelPath = "phase_5/models/props/power-tie.bam"
    ModelScale = 4
    Hold = ATTACK_HOLD_RIGHT

    Name = "Clip-On-Tie"
    ID = ATTACK_CLIPONTIE

    ReleasePlayRateMultiplier = 1.0
    ThrowObjectFrame = 68
    PlayRate = 1.5

    def equip(self):
        if not BaseAttack.equip(self):
            return False

        return True
        
    def unEquip(self):
        if not BaseAttack.unEquip(self):
            return False
            
        self.avatar.doingActivity = False
            
        return True

    def setAction(self, action):
        BaseAttack.setAction(self, action)

        self.model.show()
        self.model.setR(180)

        self.avatar.doingActivity = False

        if action == self.StateThrow:

            self.avatar.doingActivity = True
            
            time = 0.0#3.0 * 0.667
            sf = self.ThrowObjectFrame#0

            self.setAnimTrack(
                Parallel(self.getAnimationTrack('throw-paper', startFrame=sf,
                                       playRate=(self.PlayRate * self.ReleasePlayRateMultiplier), fullBody = False),
                         Sequence(Wait(time), Func(self.model.hide))),
                startNow = True)

class ClipOnTieAI(BaseAttackAI, ClipOnTieShared):

    Name = "Clip-On-Tie"
    ID = ATTACK_CLIPONTIE

    ThrowPower = 200.0

    def __init__(self):
        BaseAttackAI.__init__(self)
        self.actionLengths.update({self.StateThrow  :   6.0 * 0.6667})

        self.throwOrigin = Point3(0)
        self.traceOrigin = Point3(0)
        self.traceVector = Vec3(0)

        self.ammo = 100
        self.maxAmmo = 100

        self.baseDamage = 20

        self.didThrow = False

    def equip(self):
        if not BaseAttackAI.equip(self):
            return False

        self.b_setAction(self.StateIdle)

        return True

    def determineNextAction(self, completedAction):
        return self.StateIdle

    def __onProjectileHit(self, contact, collider, intoNP):
        avNP = intoNP.getParent()

        collider.d_impact(contact.getHitPos())

        currProj = collider.getPos(render)
        dmgInfo = TakeDamageInfo(self.avatar, self.getID(),
                                 self.calcDamage((currProj - collider.getInitialPos()).length()),
                                 currProj, collider.getInitialPos())

        for obj in base.air.avatars[self.avatar.zoneId]:
            if CIGlobals.isAvatar(obj) and obj.getKey() == avNP.getKey() and self.avatar.getRelationshipTo(obj) != RELATIONSHIP_FRIEND:
                # Make sure we don't friendly fire
                obj.takeDamage(dmgInfo)
                break

        collider.requestDelete()

    def think(self):
        BaseAttackAI.think(self)
        
        time = 0.0#3.0 * 0.6667
        if self.action == self.StateThrow and self.getActionTime() >= time and not self.didThrow:
            # Trace a line from the trace origin outward along the trace direction
            # to find out what we hit, and adjust the direction of the projectile launch
            traceEnd = self.traceOrigin + (self.traceVector * 10000)
            hit = PhysicsUtils.rayTestClosestNotMe(self.avatar,
                                                   self.traceOrigin,
                                                   traceEnd,
                                                   CIGlobals.WorldGroup | CIGlobals.CharacterGroup,
                                                   self.avatar.getBattleZone().getPhysicsWorld())
            if hit is not None:
                hitPos = hit.getHitPos()
            else:
                hitPos = traceEnd

            vecThrow = (hitPos - self.throwOrigin).normalized()
            endPos = self.throwOrigin + (vecThrow * self.ThrowPower)
            
            proj = ClipOnTieProjectileAI(base.air)
            proj.setLinear(1.5, self.throwOrigin, endPos, globalClockDelta.getFrameNetworkTime())
            proj.generateWithRequired(self.avatar.zoneId)
            proj.addHitCallback(self.__onProjectileHit)
            proj.addExclusion(self.avatar)

            self.didThrow = True

    def setAction(self, action):
        BaseAttackAI.setAction(self, action)

        if action == self.StateThrow:
            self.takeAmmo(-1)
            self.didThrow = False

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
        return squaredDistance <= 20*20

