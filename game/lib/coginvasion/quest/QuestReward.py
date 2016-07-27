"""

  Filename: QuestReward.py
  Created by: DecodedLogic (13Nov15)

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
import RewardType

class QuestReward:
    notify = directNotify.newCategory('QuestReward')
    
    def __init__(self, rewardType, rewardModifier):
        self.rewardType = rewardType
        self.rewardModifier = rewardModifier
        
    def award(self):
        # This handles rewarding players.
        if self.rewardType == RewardType.JELLYBEANS:
            base.localAvatar.b_setMoney(base.localAvatar.getMoney() + self.rewardModifier)
        elif self.rewardType == RewardType.TELEPORT_ACCESS:
            teleportAccess = base.localAvatar.getTeleportAccess()
            teleportAccess.append(self.rewardModifier)
            base.localAvatar.b_setTeleportAccess(teleportAccess)
        elif self.rewardType == RewardType.LAFF_POINTS:
            base.localAvatar.b_setMaxHealth(base.localAvatar.getMaxHealth() + self.rewardModifier)
            base.localAvatar.b_setHealth(base.localAvatar.getMaxHealth())
            base.localAvatar.d_announceHealth(1, self.rewardModifier)
            
    def getType(self):
        return self.rewardType
    
    def getModifier(self):
        return self.rewardModifier