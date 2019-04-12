"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file GameRulesAI.py
@author Brian Lach
@date April 10, 2019

"""

class GameRulesAI:

    def __init__(self, battleZone):
        self.battleZone = battleZone

    def cleanup(self):
        del self.battleZone

    def givesExperience(self):
        """
        Should this battle reward players with experience for using gags?
        """
        return True

    def countsTowardsQuests(self):
        """
        Should this battle count towards quest progress?
        """
        return True
        
    def useBackpack(self):
        return True

    def setupPlayerAttackList(self, player):
        """
        Setup the list of attacks for this player.
        The default behavior is to use the backpack (Gags unlocked on Toon).
        """
        if self.useBackpack():
            player.rebuildBackpack()

    def restorePlayerBackpack(self, player):
        player.rebuildBackpack()
        
    def useRealHealth(self):
        return True

    def canDamage(self, avatarA, avatarB, attackUsed):
        if attackUsed.FriendlyFire:
            return True

        from src.coginvasion.cog.ai.AIGlobal import RELATIONSHIP_FRIEND
        return avatarA.getRelationshipTo(avatarB) != RELATIONSHIP_FRIEND

    def onPlayerDied(self, plyr):
        pass
