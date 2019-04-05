"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file GagShop.py
@author Maverick Liberty
@date July 13, 2015

"""


from direct.directnotify.DirectNotifyGlobal import directNotify
from src.coginvasion.shop.Shop import Shop
from src.coginvasion.shop.ItemType import ItemType
from src.coginvasion.gags import GagGlobals

class GagShop(Shop):
    notify = directNotify.newCategory('GagShop')

    def __init__(self, distShop, doneEvent, wantFullShop = False):
        Shop.__init__(self, distShop, doneEvent, wantFullShop = wantFullShop)
        self.distShop = distShop
        self.backpack = None
        self.setup()

    def setup(self):
        invIcons = loader.loadModel("phase_3.5/models/gui/inventory_icons.bam")
        self.distShop.addItem(GagGlobals.WholeCreamPie, ItemType.GAG, 3, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.WholeCreamPie]))
        self.distShop.addItem(GagGlobals.BirthdayCake, ItemType.GAG, 6, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.BirthdayCake]))
        self.distShop.addItem(GagGlobals.CreamPieSlice, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.CreamPieSlice]))
        self.distShop.addItem(GagGlobals.TNT, ItemType.GAG, 12, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.TNT]))
        self.distShop.addItem(GagGlobals.SeltzerBottle, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.SeltzerBottle]))
        self.distShop.addItem(GagGlobals.WholeFruitPie, ItemType.GAG, 4, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.WholeFruitPie]))
        self.distShop.addItem(GagGlobals.WeddingCake, ItemType.GAG, 100, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.WeddingCake]))
        self.distShop.addItem(GagGlobals.FruitPieSlice, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.FruitPieSlice]))
        self.distShop.addItem(GagGlobals.GrandPiano, ItemType.GAG, 12, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.GrandPiano]))
        self.distShop.addItem(GagGlobals.BambooCane, ItemType.GAG, 12, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.BambooCane]))
        self.distShop.addItem(GagGlobals.JugglingBalls, ItemType.GAG, 25, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.JugglingBalls]))
        self.distShop.addItem(GagGlobals.Safe, ItemType.GAG, 15, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.Safe]))
        self.distShop.addItem(GagGlobals.Megaphone, ItemType.GAG, 12, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.Megaphone]))
        self.distShop.addItem(GagGlobals.Cupcake, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.Cupcake]))
        self.distShop.addItem(GagGlobals.TrapDoor, ItemType.GAG, 3, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.TrapDoor]))
        self.distShop.addItem(GagGlobals.Quicksand, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.Quicksand]))
        self.distShop.addItem(GagGlobals.Lipstick, ItemType.GAG, 8, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.Lipstick]))
        self.distShop.addItem(GagGlobals.Foghorn, ItemType.GAG, 6, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.Foghorn]))
        self.distShop.addItem(GagGlobals.Aoogah, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.Aoogah]))
        self.distShop.addItem(GagGlobals.ElephantHorn, ItemType.GAG, 3, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.ElephantHorn]))
        self.distShop.addItem(GagGlobals.Opera, ItemType.GAG, 100, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.Opera]))
        self.distShop.addItem(GagGlobals.BikeHorn, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.BikeHorn]))
        self.distShop.addItem(GagGlobals.Whistle, ItemType.GAG, 2, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.Whistle]))
        self.distShop.addItem(GagGlobals.Bugle, ItemType.GAG, 6, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.Bugle]))
        self.distShop.addItem(GagGlobals.PixieDust, ItemType.GAG, 18, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.PixieDust]))
        self.distShop.addItem(GagGlobals.Anvil, ItemType.GAG, 2, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.Anvil]))
        self.distShop.addItem(GagGlobals.FlowerPot, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.FlowerPot]))
        self.distShop.addItem(GagGlobals.Sandbag, ItemType.GAG, 2, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.Sandbag]))
        self.distShop.addItem(GagGlobals.Geyser, ItemType.GAG, 50, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.Geyser]))
        self.distShop.addItem(GagGlobals.BigWeight, ItemType.GAG, 8, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.BigWeight]))
        self.distShop.addItem(GagGlobals.StormCloud, ItemType.GAG, 6, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.StormCloud]))
        self.distShop.addItem(GagGlobals.WaterGlass, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.WaterGlass]))
        self.distShop.addItem(GagGlobals.WaterGun, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.WaterGun]))
        self.distShop.addItem(GagGlobals.FireHose, ItemType.GAG, 3, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.FireHose]))
        self.distShop.addItem(GagGlobals.SquirtFlower, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[GagGlobals.SquirtFlower]))
        self.items = self.distShop.getItems()
        Shop.setup(self)
        invIcons.removeNode()
        del invIcons

    def confirmPurchase(self):
        ammoList = []
        if not hasattr(self.originalSupply, 'keys'):
            gagIds = []
        else:
            gagIds = self.originalSupply.keys()
            for gagId in gagIds:
                ammoList.append(base.localAvatar.getBackpack().getSupply(gagId))
        self.distShop.sendUpdate('confirmPurchase', [gagIds, ammoList, base.localAvatar.getMoney()])
        Shop.confirmPurchase(self)

    def cancelPurchase(self):
        if hasattr(self.originalSupply, 'keys'):
            gagIds = self.originalSupply.keys()
            for gagId in gagIds:
                base.localAvatar.updateAttackAmmo(gagId, self.originalSupply.get(gagId))
            self.originalSupply = {}
        Shop.cancelPurchase(self)

    def update(self):
        Shop.update(self)

    def enter(self):
        Shop.enter(self)
        self.originalSupply = base.localAvatar.getBackpackAmmo()
        self.backpack = base.localAvatar.getBackpack()

    def exit(self):
        Shop.exit(self)
        self.originalSupply = {}
