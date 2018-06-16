"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedArcadeBattleZoneAI.py
@author Maverick Liberty
@date June 15, 2018

This is the AI flavor the distributed arcade battle zone object.

"""

from src.coginvasion.battle.DistributedBattleZoneAI import DistributedBattleZoneAI
from src.coginvasion.battle import BattleGlobals

class DistributedArcadeBattleZoneAI(DistributedBattleZoneAI):
    
    def __init__(self, air):
        DistributedBattleZoneAI.__init__(self, air)
        self.battleType = BattleGlobals.BTArcade
        self.matchData = None
