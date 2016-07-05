"""

  Filename: DistributedBattleShopAI.py
  Created by: DecodedLogic (14Jul15)

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from lib.coginvasion.shop.DistributedShopAI import DistributedShopAI

class DistributedBattleShopAI(DistributedShopAI):
    notify = directNotify.newCategory('DistributedBattleShopAI')

    def __init__(self, air):
        DistributedShopAI.__init__(self, air)

    def confirmPurchase(self, upgrades, money):
        avId = self.air.getAvatarIdFromSender()
        DistributedShopAI.confirmPurchase(self, avId, money)
        for value in upgrades:
            if value > 1:
                self.air.eject(avId, 0, "Trying to purchase more than one of the same power up.")
                return
        obj = self.air.doId2do.get(avId)
        obj.b_setPUInventory(upgrades)