"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DeathmatchRulesAI.py
@author Brian Lach
@date April 11, 2019

"""

from src.coginvasion.battle.GameRulesAI import GameRulesAI

class DeathmatchRulesAI(GameRulesAI):
    
    def givesExperience(self):
        return False
        
    def countsTowardsQuests(self):
        return False
        
    def useBackpack(self):
        return False
        
    def setupPlayerAttackList(self, player):
        player.b_setAttackIds([])
        
    def useRealHealth(self):
        return False
        
    def canDamage(self, avatarA, avatarB, attackUsed):
        return True
        
    def respawnPlayer(self, player):
        
        from src.coginvasion.attack.Attacks import ATTACK_HL2PISTOL, ATTACK_HL2SHOTGUN, ATTACK_GAG_TNT
        player.b_setAttackIds([ATTACK_HL2PISTOL, ATTACK_HL2SHOTGUN, ATTACK_GAG_TNT])
        
        player.b_setMaxHealth(100)
        player.b_setHealth(100)
        
        import random
        spawns = self.battleZone.bspLoader.findAllEntities("info_player_start")
        spawn = random.choice(spawns)
        player.setPos(spawn.cEntity.getOrigin())
        player.setHpr(spawn.cEntity.getAngles())
        player.b_clearSmoothing()
        player.sendCurrentPosition()
        
        self.battleZone.sendUpdateToAvatarId(player.doId, 'respawn', [])
        
    def onPlayerDied(self, player):
        #self.respawnPlayer(player)
        pass
