"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Fired_AI.py
@author Brian Lach
@date March 31, 2019

"""

from src.coginvasion.attack.BaseAttackAI import BaseAttackAI
from src.coginvasion.attack.Attacks import ATTACK_FIRED
from src.coginvasion.attack.LobProjectileAI import LobProjectileAI
from src.coginvasion.globals import CIGlobals
from src.coginvasion.phys.WorldCollider import WorldCollider
from Fired_Shared import Fired_Shared

class FiredProjectileAI(LobProjectileAI):

    def doInitCollider(self):

        WorldCollider.__init__(self, "FiredProjectileCollider", 0.75, needSelfInArgs = True,
                          useSweep = True, resultInArgs = True, startNow = False, mask = CIGlobals.WorldGroup | CIGlobals.CharacterGroup)
        self.world = self.air.getPhysicsWorld(self.zoneId)

class FiredAI(BaseAttackAI, Fired_Shared):

    Name = "Fired"
    ID = ATTACK_FIRED

    MaxFlames = 10
    FlameSpeed = 30.0

    def __init__(self):
        BaseAttackAI.__init__(self)
        self.actionLengths.update({self.StateBegin: 1.0,
                                   self.StateAttack: self.EmitFlameIval * self.MaxFlames,
                                   self.StateEnd: 1.0})

        self.baseDamage = 5

        self.lastFireTime = 0.0
        self.target = None

    def determineNextAction(self, completedAction):
        if completedAction == self.StateBegin:
            return self.StateAttack
        elif completedAction == self.StateAttack:
            return self.StateEnd
        
        return self.StateIdle

    def npcUseAttack(self, target):
        if not self.canUse():
            return

        self.target = target
        self.lastFireTime = 0.0
        self.setNextAction(self.StateBegin)

    def checkCapable(self, dot, squaredDistance):
        return squaredDistance <= 60.0*60.0 and squaredDistance >= 15*15

    def think(self):
        BaseAttackAI.think(self)

        if self.action == self.StateAttack:
            now = globalClock.getFrameTime()
            if (CIGlobals.isNodePathOk(self.target) and
                now - self.lastFireTime >= self.EmitFlameIval):

                startPos = self.avatar.getPos() + self.avatar.getEyePosition()
                endPos = self.target.getPos() + self.target.getEyePosition()
                distance = (endPos - startPos).length()
                duration = distance / self.FlameSpeed

                flame = FiredProjectileAI(base.air)
                flame.setProjectile(duration, startPos, endPos, 1.07,
                                    globalClockDelta.getFrameNetworkTime())
                flame.generateWithRequired(self.avatar.zoneId)
                flame.addHitCallback(self.onProjectileHit)
                flame.addExclusion(self.avatar)

                self.lastFireTime = now
            