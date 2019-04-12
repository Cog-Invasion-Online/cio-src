"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file GameRules.py
@author Brian Lach
@date April 10, 2019

"""

class GameRules:
    
    def __init__(self, battleZone):
        self.battleZone = battleZone

    def cleanup(self):
        del self.battleZone
        
    def useRealHealth(self):
        return True
        
    def useBackpack(self):
        return True
        
    def getNormalSpeed(self):
        return 320 / 16.0
        
    def getWalkSpeed(self):
        return 190 / 16.0
        
    def getRunSpeed(self):
        return 416 / 16.0
        
    def getStaticFriction(self):
        return 0.8
        
    def getDynamicFriction(self):
        return 0.3

    def onPlayerDied(self):
        """
        Called upon the local avatar dying.
        """
        from src.coginvasion.hood import ZoneUtil
        if (base.cr.playGame.hood.id != ZoneUtil.getHoodId(base.localAvatar.zoneId)):
            base.cr.playGame.getPlace().fsm.request('died', [{}, base.localAvatar.diedStateDone])
