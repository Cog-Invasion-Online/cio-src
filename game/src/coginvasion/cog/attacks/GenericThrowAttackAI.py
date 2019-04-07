"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file GenericThrowAttackAI.py
@author Maverick Liberty
@date April 5, 2019

This is the base class for one of those basic attacks where a Cog throws something.

"""

from panda3d.core import Point3, Vec3

from direct.distributed.ClockDelta import globalClockDelta

from src.coginvasion.attack.BaseAttackAI import BaseAttackAI
from src.coginvasion.cog.attacks.GenericThrowableLinearProjectileAI import GenericThrowableLinearProjectileAI
from src.coginvasion.cog.SuitType import SuitType
from src.coginvasion.globals import CIGlobals
from src.coginvasion.phys import PhysicsUtils

class GenericThrowAttackAI(BaseAttackAI):
    
    def __init__(self, sharedMetadata = None):
        BaseAttackAI.__init__(self, sharedMetadata)
        self.throwOrigin = Point3(0)
        self.traceOrigin = Point3(0)
        self.traceVector = Vec3(0)
        self.didThrow = False
        self.target = None
        
        if not hasattr(self, 'StateThrow'):
            raise RuntimeError('Expected a StateThrow member for GenericThrowAttackAI!')
        
        if not hasattr(self, 'AttackDuration'):
            raise RuntimeError('Expected an `AttackDuration` member to define the duration of the attack.')
        
        if not hasattr(self, 'ThrowAfterTime'):
            raise RuntimeError('Expected a `ThrowAfterTime` member to define when a projectile should be released.')
        
        if not hasattr(self, 'ThrowPower'):
            raise RuntimeError('Expected a `ThrowPower` member to define the power a projectile should be thrown with.')
        
        self.actionLengths.update({self.StateThrow : self.AttackDuration})
        
    def cleanup(self):
        del self.throwOrigin
        del self.traceOrigin
        del self.traceVector
        if self.target:
            self.target = None
        del self.target
        BaseAttackAI.cleanup(self)
        
    def think(self):
        BaseAttackAI.think(self)
        
        time = self.ThrowAfterTime
        if not time:
            try:
                time = self.__calculateThrowAfterTime()
            except: pass
            
        if self.action == self.StateThrow:
        
            if not CIGlobals.isNodePathOk(self.target):
                return

            # Lock onto the target
            self.avatar.headsUp(self.target)
        
            if self.getActionTime() >= time and not self.didThrow:
                self.calibrate(self.target)
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
                
                proj = GenericThrowableLinearProjectileAI(base.air)
                proj.setData(self.ID)
                proj.setLinear(1.5, self.throwOrigin, endPos, globalClockDelta.getFrameNetworkTime())
                proj.generateWithRequired(self.avatar.zoneId)
                proj.addHitCallback(self.onProjectileHit)
                proj.addExclusion(self.avatar)
    
                self.didThrow = True
                
    def __calculateThrowAfterTime(self):
        timings = {
            SuitType.A : 3.083,
            SuitType.B : 3.083,
            SuitType.C : 2.417
        }
        
        time = timings.values()[0]
        
        try:
            time = timings.get(self.avatar.suitPlan.getSuitType())
        except: pass
        
        return time / self.PlayRate
            
    def onSetAction(self, action):
        if action == self.StateThrow:
            self.takeAmmo(-1)
            self.didThrow = False
        elif action == self.StateIdle:
            self.target = None
            
    def calibrate(self, target):
        self.throwOrigin = self.avatar.getPos(render) + (0, 0, self.avatar.getHeight() / 2.0)
        self.traceOrigin = self.throwOrigin
        self.traceVector = ((target.getPos(render) + (0, 0, target.getHeight() / 2.0)) - self.throwOrigin).normalized()
    
    def npcUseAttack(self, target):
        if not self.canUse():
            return
        
        self.target = target
        self.setNextAction(self.StateThrow)
            
    def checkCapable(self, _, squaredDistance):
        return squaredDistance <= 20*20 and squaredDistance > 8*8
        