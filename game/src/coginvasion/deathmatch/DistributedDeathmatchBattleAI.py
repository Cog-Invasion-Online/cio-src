"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedDeathmatchBattleAI.py
@author Brian Lach
@date April 11, 2019

"""

from src.coginvasion.battle.DistributedBattleZoneAI import DistributedBattleZoneAI
from DeathmatchRulesAI import DeathmatchRulesAI

class DistributedDeathmatchBattleAI(DistributedBattleZoneAI):

    def makeGameRules(self):
        return DeathmatchRulesAI(self)

    def generate(self):
        DistributedBattleZoneAI.generate(self)
        
        from src.coginvasion.deathmatch.DistributedGagPickupAI import DistributedGagPickupAI
        self.bspLoader.linkServerEntityToClass("gag_pickup", DistributedGagPickupAI)
        
    def handleAvatarLeave(self, avatar, reason):
        DistributedBattleZoneAI.handleAvatarLeave(self, avatar, reason)

        if hasattr(self, 'watchingAvatarIds') and len(self.watchingAvatarIds) == 0:
            self.requestDelete()
        
    def readyToStart(self):
        pass

    def loadedMap(self):
        avId = self.air.getAvatarIdFromSender()
        inst = self.getAvatarInstance(avId)
        if inst:
            self.gameRules.respawnPlayer(inst.avatar)

    def requestRespawn(self):
        avId = self.air.getAvatarIdFromSender()
        inst = self.getAvatarInstance(avId)
        if inst:
            self.gameRules.respawnPlayer(inst.avatar)

    def announceGenerate(self):
        DistributedBattleZoneAI.announceGenerate(self)
        self.b_setMap("sellbot_third_floor")
