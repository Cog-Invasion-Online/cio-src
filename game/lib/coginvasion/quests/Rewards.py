"""

Copyright (c) Cog Invasion Online. All rights reserved.

@file Rewards.py
@author Brian Lach
@date 2016-07-29

"""

from lib.coginvasion.globals import CIGlobals
import QuestGlobals

###################################
# Reward types
Nothing = 0
Jellybeans = 1
Access = 2
Health = 3
GagTrackProgress = 4
GagSlot = 5
###################################

class Reward:
    # This is the NPC speech or the QuestNote text for this reward.
    Dialogue = "nothing"

    # Custom NPC speech before giving out the reward (e.g "You have earned %s.")
    # Leave this at None to use the default ones defined in QuestGlobals.NPCDialogue.Reward
    CustomDialogueBase = None

    def __init__(self, rewardType, rewardValue):
        self.rewardType = rewardType
        self.rewardValue = rewardValue

    def giveReward(self, avatar):
        # Override in your child class to do specific stuff for your reward.
        pass

    def fillInDialogue(self):
        if '%d' in self.Dialogue:
            return self.Dialogue % self.rewardValue

        return self.Dialogue

class HealthReward(Reward):
    Dialogue = "a %d point Laff boost"

    def giveReward(self, avatar):
        avatar.b_setMaxHealth(avatar.getMaxHealth() + self.rewardValue)
        avatar.b_setHealth(avatar.getMaxHealth())
        avatar.d_announceHealth(1, self.rewardValue)

class JellybeanReward(Reward):
    Dialogue = "%d jellybeans"

    def giveReward(self, avatar):
        avatar.b_setMoney(avatar.getMoney() + self.rewardValue)

class GagSlotReward(Reward):
    Dialogue = "the %s Gag Slot"
    CustomDialogueBase = "You have unlocked %s."

    def giveReward(self, avatar):
        avatar.b_setNumGagSlots(self.rewardValue)

    def fillInDialogue(self):
        return self.Dialogue % QuestGlobals.getOrdinal(self.rewardValue)

class AccessReward(Reward):
    Dialogue = "access to %s"

    def giveReward(self, avatar):
        avatar.b_setHoodsDiscovered(avatar.getHoodsDiscovered() + [self.rewardValue])

    def fillInDialogue(self):
        return self.Dialogue % CIGlobals.ZoneId2Hood[self.rewardValue]

RewardType2RewardClass = {
    Health:     HealthReward,
    Jellybeans: JellybeanReward,
    GagSlot:    GagSlotReward,
    Access:     AccessReward
}
