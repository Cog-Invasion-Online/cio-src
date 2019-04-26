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
from src.coginvasion.phys.WorldColliderAI import WorldColliderAI
from Fired_Shared import Fired_Shared

class FiredProjectileAI(LobProjectileAI):

    def doInitCollider(self):

        WorldColliderAI.__init__(self, "FiredProjectileCollider", 0.75, needSelfInArgs = True,
                          useSweep = True, resultInArgs = True, startNow = False,
                          mask = CIGlobals.WorldGroup | CIGlobals.CharacterGroup)
        self.world = self.air.getPhysicsWorld(self.zoneId)

    def diffuseFlame(self):
        self.d_impact(self.getPos())
        self.requestDelete()

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

        self.lastFireTime = 0.0
        self.target = None

    def getBaseDamage(self):
        return 5
        
    def getTauntChance(self):
        return 0.5
        
    def getTauntPhrases(self):
        return ["I hope you brought some marshmallows.",
                "It's going to get rather warm around here.",
                "This should take the chill out of the air.",
                "I hope you're cold blooded.",
                "Hot, hot and hotter.",
                "You better stop, drop, and roll!",
                "You're outta here.",
                "How does \"well-done\" sound?",
                "Can you say ouch?",
                "Hope you wore sunscreen.",
                "Do you feel a little toasty?",
                "You're going down in flames.",
                "You'll go out in a blaze.",
                "You're a flash in the pan.",
                "I think I have a bit of a flare about me.",
                "I just sparkle, don't I?",
                "Oh look, a crispy critter.",
                "You shouldn't run around half baked."]

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
        return squaredDistance >= 25*25 and squaredDistance <= 40*40

    def think(self):
        BaseAttackAI.think(self)

        if self.action == self.StateAttack:
            if not CIGlobals.isNodePathOk(self.target):
                return

            # Lock onto the target
            self.avatar.headsUp(self.target)

            now = globalClock.getFrameTime()
            if now - self.lastFireTime >= self.EmitFlameIval:
                startPos = self.avatar.getPos() + self.avatar.getEyePosition()
                endPos = self.target.getPos() + self.target.getEyePosition()
                distance = (endPos - startPos).length()
                duration = distance / self.FlameSpeed

                flame = FiredProjectileAI(base.air)
                flame.setProjectile(duration, startPos, endPos, 0.9,
                                    globalClockDelta.getFrameNetworkTime())
                flame.generateWithRequired(self.avatar.zoneId)
                flame.addHitCallback(self.onProjectileHit)
                flame.addExclusion(self.avatar)

                self.lastFireTime = now
            
