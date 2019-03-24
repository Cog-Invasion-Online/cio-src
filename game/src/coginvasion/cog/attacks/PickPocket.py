"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file PickPocket.py
@author Brian Lach
@date March 24, 2019

@desc "Melee" attack. The Cog grabs something from the Toon.

"""

from direct.interval.IntervalGlobal import Parallel, Sequence, Wait, Func

from src.coginvasion.avatar.BaseAttacks import BaseAttack, BaseAttackAI
from src.coginvasion.avatar.Attacks import ATTACK_PICKPOCKET, ATTACK_HOLD_NONE
from src.coginvasion.base.Precache import precacheSound

class PickPocketShared:
    StateAttack = 1
    
class PickPocket(BaseAttack, PickPocketShared):
    Hold = ATTACK_HOLD_NONE
    Name = "Pick-Pocket"
    ID = ATTACK_PICKPOCKET

    PickSoundPath = "phase_5/audio/sfx/SA_pick_pocket.ogg"

    def __init__(self):
        BaseAttack.__init__(self)
        self.pickSound = None

    @classmethod
    def doPrecache(cls):
        super(PickPocket, cls).doPrecache()
        precacheSound(cls.PickSoundPath)

    def equip(self):
        if not BaseAttack.equip(self):
            return False

        if not self.pickSound:
            self.pickSound = base.loadSfxOnNode(self.PickSoundPath, self.avatar)

        return True

    def cleanup(self):
        base.audio3d.detachSound(self.pickSound)
        del self.pickSound
        BaseAttack.cleanup(self)

    def unEquip(self):
        if not BaseAttack.unEquip(self):
            return False
            
        self.avatar.doingActivity = False
            
        return True

    def onSetAction(self, action):
        self.avatar.doingActivity = False
        if action == self.StateAttack:
            self.avatar.doingActivity = True
            self.setAnimTrack(Parallel(self.getAnimationTrack('pickpocket', fullBody = False),
                                       Sequence(Wait(0.4), Func(self.pickSound.play))),
                              startNow = True)
    
class PickPocket_AI(BaseAttackAI, PickPocketShared):
    Name = "Pick-Pocket"
    ID = ATTACK_PICKPOCKET

    PickTime = 0.4
    PickRange = 5.0

    def __init__(self):
        BaseAttackAI.__init__(self)
        self.actionLengths.update({self.StateAttack  :   3.0})
        self.baseDamage = 10.0
        self.traceOrigin = None
        self.traceVector = None
        self.didPick = False

    def equip(self):
        if not BaseAttackAI.equip(self):
            return False
        
        self.b_setAction(self.StateIdle)

        return True

    def cleanup(self):
        del self.traceOrigin
        del self.traceVector
        BaseAttackAI.cleanup(self)

    def think(self):
        BaseAttackAI.think(self)
        
        if (self.action == self.StateAttack and
            self.getActionTime() >= self.PickTime and
            not self.didPick):
            
            self.didPick = True
            self.doTraceAndDamage(self.traceOrigin, self.traceVector, self.PickRange)

    def checkCapable(self, dot, squaredDistance):
        return squaredDistance <= 8*8 and dot >= 0.8

    def canUse(self):
        return self.getAction() == self.StateIdle
        
    def onSetAction(self, action):
        if action == self.StateAttack:
            self.didPick = False

    def npcUseAttack(self, target):
        if not self.canUse():
            return

        self.traceOrigin = self.avatar.getPos() + (0, 0, self.avatar.getHeight() / 2)
        self.traceVector = ((target.getPos() + (0, 0, target.getHeight() / 2.0)) - self.traceOrigin).normalized()
        self.setNextAction(self.StateAttack)
