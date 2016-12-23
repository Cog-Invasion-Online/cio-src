# Filename: DistributedClerkNPCToon.py
# Created by:  blach (06Nov15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.shop.GagShop import GagShop
from src.coginvasion.shop.ItemType import ItemType
from DistributedNPCToon import DistributedNPCToon

import random

class DistributedClerkNPCToon(DistributedNPCToon):
    notify = directNotify.newCategory('DistributedClerkNPCToon')

    def __init__(self, cr):
        DistributedNPCToon.__init__(self, cr)
        self.destroyEvent = 'destroyShop-' + str(random.randint(0, 1000))
        self.items = {}
        self.inShop = False
        self.shop = GagShop(self, 'gagShopDone', wantFullShop = True)

    def addItem(self, item, itemType, price, itemImage, upgradeID = None, maxUpgrades = None, heal = 0, healCooldown = 0, showTitle = False):
        if itemType != ItemType.HEAL:
            data = {item : {'type' : itemType, 'image' : itemImage, 'price' : price, 'upgradeID' : upgradeID, 'maxUpgrades' : maxUpgrades}}
        else:
            data = {item : {'type' : itemType, 'image' : itemImage, 'price' : price, 'heal' : heal, 'healCooldown' : healCooldown, 'showTitle' : showTitle}}
        self.items.update(data)

    def removeItem(self, item):
        self.items.remove(item)

    def getItems(self):
        return self.items

    def enterAccepted(self):
        self.doCameraNPCInteraction()
        self.cameraTrack.setDoneEvent(self.uniqueName('clerkInteractionCam'))
        self.acceptOnce(self.cameraTrack.getDoneEvent(), self.__showShop)

    def __showShop(self):
        self.shop.load()
        self.shop.enter()
        self.acceptOnce(self.shop.doneEvent, self.handleShopDone)
        self.inShop = True

    def handleShopDone(self):
        self.shop.exit()
        self.shop.unload()
        self.d_requestExit()
        self.inShop = False

    def disable(self):
        if self.cameraTrack:
            self.ignore(self.cameraTrack.getDoneEvent())
        if self.inShop and self.shop:
            self.shop.exit()
            self.shop.unload()
            self.shop = None
        DistributedNPCToon.disable(self)
