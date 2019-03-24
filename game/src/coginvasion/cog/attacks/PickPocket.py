"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file PickPocket.py
@author Brian Lach
@date March 24, 2019

@desc "Melee" attack. The Cog grabs something from the Toon.

"""

from direct.interval.IntervalGlobal import Parallel, Sequence, Wait, Func

from PickPocketShared import PickPocketShared
from src.coginvasion.attack.BaseAttack import BaseAttack
from src.coginvasion.attack.Attacks import ATTACK_PICKPOCKET, ATTACK_HOLD_NONE
from src.coginvasion.base.Precache import precacheSound
    
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
