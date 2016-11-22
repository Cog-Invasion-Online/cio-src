"""

  Filename: GagShop.py
  Created by: DecodedLogic (13Jul15)

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from lib.coginvasion.shop.Shop import Shop
from lib.coginvasion.shop.ItemType import ItemType
from lib.coginvasion.gags import GagGlobals
from lib.coginvasion.globals import CIGlobals

class GagShop(Shop):
    notify = directNotify.newCategory('GagShop')

    def __init__(self, distShop, doneEvent, wantFullShop = False):
        Shop.__init__(self, distShop, doneEvent, wantFullShop = wantFullShop)
        self.distShop = distShop
        self.backpack = base.localAvatar.getBackpack()
        self.setup()

    def setup(self):
        invIcons = loader.loadModel("phase_3.5/models/gui/inventory_icons.bam")
        self.distShop.addItem(CIGlobals.WholeCreamPie, ItemType.GAG, 3, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.WholeCreamPie]))
        self.distShop.addItem(CIGlobals.BirthdayCake, ItemType.GAG, 6, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.BirthdayCake]))
        self.distShop.addItem(CIGlobals.CreamPieSlice, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.CreamPieSlice]))
        self.distShop.addItem(CIGlobals.TNT, ItemType.GAG, 12, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.TNT]))
        self.distShop.addItem(CIGlobals.SeltzerBottle, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.SeltzerBottle]))
        self.distShop.addItem(CIGlobals.WholeFruitPie, ItemType.GAG, 4, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.WholeFruitPie]))
        self.distShop.addItem(CIGlobals.WeddingCake, ItemType.GAG, 100, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.WeddingCake]))
        self.distShop.addItem(CIGlobals.FruitPieSlice, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.FruitPieSlice]))
        self.distShop.addItem(CIGlobals.GrandPiano, ItemType.GAG, 12, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.GrandPiano]))
        self.distShop.addItem(CIGlobals.BambooCane, ItemType.GAG, 12, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.BambooCane]))
        self.distShop.addItem(CIGlobals.JugglingBalls, ItemType.GAG, 25, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.JugglingBalls]))
        self.distShop.addItem(CIGlobals.Safe, ItemType.GAG, 15, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.Safe]))
        self.distShop.addItem(CIGlobals.Megaphone, ItemType.GAG, 12, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.Megaphone]))
        self.distShop.addItem(CIGlobals.Cupcake, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.Cupcake]))
        self.distShop.addItem(CIGlobals.TrapDoor, ItemType.GAG, 3, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.TrapDoor]))
        self.distShop.addItem(CIGlobals.Quicksand, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.Quicksand]))
        self.distShop.addItem(CIGlobals.Lipstick, ItemType.GAG, 8, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.Lipstick]))
        self.distShop.addItem(CIGlobals.Foghorn, ItemType.GAG, 6, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.Foghorn]))
        self.distShop.addItem(CIGlobals.Aoogah, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.Aoogah]))
        self.distShop.addItem(CIGlobals.ElephantHorn, ItemType.GAG, 3, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.ElephantHorn]))
        self.distShop.addItem(CIGlobals.Opera, ItemType.GAG, 100, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.Opera]))
        self.distShop.addItem(CIGlobals.BikeHorn, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.BikeHorn]))
        self.distShop.addItem(CIGlobals.Whistle, ItemType.GAG, 2, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.Whistle]))
        self.distShop.addItem(CIGlobals.Bugle, ItemType.GAG, 6, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.Bugle]))
        self.distShop.addItem(CIGlobals.PixieDust, ItemType.GAG, 18, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.PixieDust]))
        self.distShop.addItem(CIGlobals.Anvil, ItemType.GAG, 2, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.Anvil]))
        self.distShop.addItem(CIGlobals.FlowerPot, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.FlowerPot]))
        self.distShop.addItem(CIGlobals.Sandbag, ItemType.GAG, 2, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.Sandbag]))
        self.distShop.addItem(CIGlobals.Geyser, ItemType.GAG, 50, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.Geyser]))
        self.distShop.addItem(CIGlobals.BigWeight, ItemType.GAG, 8, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.BigWeight]))
        self.distShop.addItem(CIGlobals.StormCloud, ItemType.GAG, 6, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.StormCloud]))
        self.distShop.addItem(CIGlobals.WaterGlass, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.WaterGlass]))
        self.distShop.addItem(CIGlobals.WaterGun, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.WaterGun]))
        self.distShop.addItem(CIGlobals.FireHose, ItemType.GAG, 3, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.FireHose]))
        self.distShop.addItem(CIGlobals.SquirtFlower, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.SquirtFlower]))
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
                ammoList.append(base.localAvatar.getBackpack().getSupply(GagGlobals.getGagByID(gagId)))
        self.distShop.sendUpdate('confirmPurchase', [gagIds, ammoList, base.localAvatar.getMoney()])
        Shop.confirmPurchase(self)

    def cancelPurchase(self):
        if hasattr(self.originalSupply, 'keys'):
            gagIds = self.originalSupply.keys()
            for gagId in gagIds:
                base.localAvatar.setGagAmmo(gagId, self.originalSupply.get(gagId))
            self.originalSupply = {}
        Shop.cancelPurchase(self)

    def update(self):
        Shop.update(self)

    def enter(self):
        Shop.enter(self)
        self.originalSupply = base.localAvatar.getBackpackAmmo()

    def exit(self):
        Shop.exit(self)
        self.originalSupply = {}
