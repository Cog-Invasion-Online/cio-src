"""

  Filename: DistributedGagShopAI.py
  Created by: DecodedLogic (14Jul15)

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from lib.coginvasion.shop.DistributedShopAI import DistributedShopAI

class DistributedGagShopAI(DistributedShopAI):
    notify = directNotify.newCategory('DistributedGagShopAI')

    def __init__(self, air):
        DistributedShopAI.__init__(self, air)

    def confirmPurchase(self, gagIds, ammoList, money):
        avId = self.air.getAvatarIdFromSender()
        DistributedShopAI.confirmPurchase(self, avId, money)
        av = self.air.doId2do.get(avId)
        if av:
            for i in range(len(gagIds)):
                gagId = gagIds[i]
                ammo = ammoList[i]
                av.b_setGagAmmo(gagId, ammo)
