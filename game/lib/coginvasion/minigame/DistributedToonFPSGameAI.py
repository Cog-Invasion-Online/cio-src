"""

  Filename: DistributedToonFPSGameAI.py
  Created by: blach (30Mar15)

"""

from DistributedMinigameAI import DistributedMinigameAI
from direct.directnotify.DirectNotifyGlobal import directNotify

class DistributedToonFPSGameAI(DistributedMinigameAI):
    notify = directNotify.newCategory("DistributedToonFPSGame")

    def __init__(self, air):
        try:
            self.DistributedToonFPSGameAI_initialized
            return
        except:
            self.DistributedToonFPSGameAI_initialized = 1
        DistributedMinigameAI.__init__(self, air)

    def avatarHitByBullet(self, avId, dmg):
        sender = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        if av:
            av.d_announceHealth(0, dmg)
        self.sendUpdateToAvatarId(avId, "damage", [dmg, sender])
