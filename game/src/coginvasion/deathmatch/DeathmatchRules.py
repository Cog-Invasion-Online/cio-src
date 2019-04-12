"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DeathmatchRules.py
@author Brian Lach
@date April 11, 2019

"""

from direct.interval.IntervalGlobal import Sequence, Wait, Func

from src.coginvasion.battle.GameRules import GameRules

class DeathmatchRules(GameRules):
    
    def useBackpack(self):
        return False
        
    def useRealHealth(self):
        return False
    
    def onPlayerDied(self):
        base.localAvatar.stopPlay()
        base.localAvatar.doFirstPersonCameraTransition()
        Sequence(Wait(2.0), Func(self.battleZone.sendUpdate, 'requestRespawn')).start()
        
    def onPlayerRespawn(self):
        base.localAvatar.startPlay(gags = True, laff = True)
