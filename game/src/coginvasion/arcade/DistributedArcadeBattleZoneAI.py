"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedArcadeBattleZoneAI.py
@author Maverick Liberty
@date June 15, 2018

This is the AI flavor of the distributed arcade battle zone object.

"""

from src.coginvasion.battle.DistributedBattleZoneAI import DistributedBattleZoneAI
from src.coginvasion.battle.DistributedPieTurretManagerAI import DistributedPieTurretManagerAI
from src.coginvasion.battle import BattleGlobals

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State

class DistributedArcadeBattleZoneAI(DistributedBattleZoneAI):
    notify = directNotify.newCategory('DistributedArcadeBattleZoneAI')
    
    def __init__(self, air):
        DistributedBattleZoneAI.__init__(self, air)
        self.battleType = BattleGlobals.BTArcade
        self.matchData = None
        self.fsm = ClassicFSM('DistributedArcadeBattleZoneAI', [
            State('off', self.enterOff, self.exitOff),
        ], 'off', 'off')
        self.readyAvatars = []
        
        # Variables related to turrets
        self.turretMgr = None
        
    def announceGenerate(self):
        DistributedBattleZoneAI.announceGenerate(self)
        self.turretMgr = DistributedPieTurretManagerAI(self.air)
        self.turretMgr.generateWithRequired(self.zoneId)
        self.fsm.enterInitialState()
        
    def enterOff(self):
        pass
    
    def exitOff(self):
        pass
