"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedBattleShopAI.py
@author Maverick Liberty
@date July 14, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from src.coginvasion.shop.DistributedShopAI import DistributedShopAI

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