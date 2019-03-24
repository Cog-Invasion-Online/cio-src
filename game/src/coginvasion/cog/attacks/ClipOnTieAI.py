from panda3d.core import Point3, Vec3

from direct.distributed.ClockDelta import globalClockDelta

from src.coginvasion.cog.attacks.ClipOnTieShared import ClipOnTieShared
from src.coginvasion.cog.attacks import ClipOnTieProjectileAI
from src.coginvasion.attack.BaseAttackAI import BaseAttackAI
from src.coginvasion.attack.Attacks import ATTACK_CLIPONTIE
from src.coginvasion.attack.TakeDamageInfo import TakeDamageInfo
from src.coginvasion.cog.ai.RelationshipsAI import RELATIONSHIP_FRIEND
from src.coginvasion.globals import CIGlobals
from src.coginvasion.phys import PhysicsUtils

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

    def onSetAction(self, action):
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
        return squaredDistance <= 20*20 and squaredDistance > 8*8
