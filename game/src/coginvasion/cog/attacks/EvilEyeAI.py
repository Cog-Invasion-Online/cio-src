from panda3d.core import Point3, Vec3

from direct.distributed.ClockDelta import globalClockDelta

from src.coginvasion.attack.BaseAttackAI import BaseAttackAI
from src.coginvasion.cog.attacks.EvilEyeShared import EvilEyeShared
from src.coginvasion.cog.attacks.EvilEyeProjectileAI import EvilEyeProjectileAI
from src.coginvasion.attack.Attacks import ATTACK_EVIL_EYE
from src.coginvasion.globals import CIGlobals
from src.coginvasion.phys import PhysicsUtils

class EvilEyeAI(BaseAttackAI, EvilEyeShared):
    Name = "Evil-Eye"
    ID = ATTACK_EVIL_EYE
    ThrowPower = 100.0
    
    def __init__(self):
        BaseAttackAI.__init__(self)
        self.actionLengths.update({self.StateAttack   : 4.0})
        
        self.ammo = 100
        self.maxAmmo = 100
        self.baseDamage = 21.0
        self.throwOrigin = Point3(0)
        self.traceOrigin = Point3(0)
        self.traceVector = Vec3(0)
        self.didAttack = False
        
    def think(self):
        BaseAttackAI.think(self)
        
        time = 2.81
        
        if self.action == self.StateAttack and self.getActionTime() >= time and not self.didAttack:
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
            
            proj = EvilEyeProjectileAI(base.air)
            proj.setLinear(1.5, self.throwOrigin, endPos, globalClockDelta.getFrameNetworkTime())
            proj.generateWithRequired(self.avatar.zoneId)
            proj.addHitCallback(self.onProjectileHit)
            proj.addExclusion(self.avatar)

            self.didAttack = True
            
    def onSetAction(self, action):
        if action == self.StateAttack:
            self.takeAmmo(-1)
            self.didAttack = False
            
    def npcUseAttack(self, target):
        if not self.canUse():
            return
        
        self.throwOrigin = self.avatar.getPos(render) + self.avatar.getEyePosition()
        self.traceOrigin = self.throwOrigin
        self.traceVector = ((target.getPos(render) + (0, 0, target.getHeight() / 2.0)) - self.throwOrigin).normalized()
        self.setNextAction(self.StateAttack)
    
    def checkCapable(self, dot, squaredDistance):
        return squaredDistance <= 20*20 and squaredDistance > 8*8
