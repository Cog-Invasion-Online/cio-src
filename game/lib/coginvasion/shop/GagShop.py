"""

  Filename: GagShop.py
  Created by: DecodedLogic (13Jul15)

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from lib.coginvasion.shop.Shop import Shop
from lib.coginvasion.shop.ItemType import ItemType
from lib.coginvasion.gags import GagGlobals
from lib.coginvasion.gags.WholeCreamPie import WholeCreamPie
from lib.coginvasion.gags.WholeFruitPie import WholeFruitPie
from lib.coginvasion.gags.BirthdayCake import BirthdayCake
from lib.coginvasion.gags.CreamPieSlice import CreamPieSlice
from lib.coginvasion.gags.TNT import TNT
from lib.coginvasion.gags.SeltzerBottle import SeltzerBottle
from lib.coginvasion.gags.WeddingCake import WeddingCake
from lib.coginvasion.gags.FruitPieSlice import FruitPieSlice
from lib.coginvasion.gags.GrandPiano import GrandPiano
from lib.coginvasion.gags.BambooCane import BambooCane
from lib.coginvasion.gags.JugglingBalls import JugglingBalls
from lib.coginvasion.gags.Megaphone import Megaphone
from lib.coginvasion.gags.Cupcake import Cupcake
from lib.coginvasion.gags.Safe import Safe
from lib.coginvasion.gags.TrapDoor import TrapDoor
from lib.coginvasion.gags.Lipstick import Lipstick
from lib.coginvasion.gags.Quicksand import Quicksand
from lib.coginvasion.gags.Foghorn import Foghorn
from lib.coginvasion.gags.Aoogah import Aoogah
from lib.coginvasion.gags.ElephantHorn import ElephantHorn
from lib.coginvasion.gags.Opera import Opera
from lib.coginvasion.gags.BikeHorn import BikeHorn
from lib.coginvasion.gags.Whistle import Whistle
from lib.coginvasion.gags.Bugle import Bugle
from lib.coginvasion.gags.PixieDust import PixieDust
from lib.coginvasion.gags.Anvil import Anvil
from lib.coginvasion.gags.FlowerPot import FlowerPot
from lib.coginvasion.gags.Sandbag import Sandbag
from lib.coginvasion.gags.Geyser import Geyser
from lib.coginvasion.gags.BigWeight import BigWeight
from lib.coginvasion.gags.StormCloud import StormCloud
from lib.coginvasion.gags.WaterGlass import WaterGlass
from lib.coginvasion.gags.WaterGun import WaterGun
from lib.coginvasion.gags.FireHose import FireHose
from lib.coginvasion.gags.SquirtingFlower import SquirtingFlower
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
        self.distShop.addItem(WholeCreamPie, ItemType.GAG, 3, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.WholeCreamPie]))
        self.distShop.addItem(BirthdayCake, ItemType.GAG, 6, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.BirthdayCake]))
        self.distShop.addItem(CreamPieSlice, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.CreamPieSlice]))
        self.distShop.addItem(TNT, ItemType.GAG, 12, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.TNT]))
        self.distShop.addItem(SeltzerBottle, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.SeltzerBottle]))
        self.distShop.addItem(WholeFruitPie, ItemType.GAG, 4, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.WholeFruitPie]))
        self.distShop.addItem(WeddingCake, ItemType.GAG, 100, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.WeddingCake]))
        self.distShop.addItem(FruitPieSlice, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.FruitPieSlice]))
        self.distShop.addItem(GrandPiano, ItemType.GAG, 12, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.GrandPiano]))
        self.distShop.addItem(BambooCane, ItemType.GAG, 12, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.BambooCane]))
        self.distShop.addItem(JugglingBalls, ItemType.GAG, 25, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.JugglingBalls]))
        self.distShop.addItem(Safe, ItemType.GAG, 15, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.Safe]))
        self.distShop.addItem(Megaphone, ItemType.GAG, 12, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.Megaphone]))
        self.distShop.addItem(Cupcake, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.Cupcake]))
        self.distShop.addItem(TrapDoor, ItemType.GAG, 3, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.TrapDoor]))
        self.distShop.addItem(Quicksand, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.Quicksand]))
        self.distShop.addItem(Lipstick, ItemType.GAG, 8, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.Lipstick]))
        self.distShop.addItem(Foghorn, ItemType.GAG, 6, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.Foghorn]))
        self.distShop.addItem(Aoogah, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.Aoogah]))
        self.distShop.addItem(ElephantHorn, ItemType.GAG, 3, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.ElephantHorn]))
        self.distShop.addItem(Opera, ItemType.GAG, 100, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.Opera]))
        self.distShop.addItem(BikeHorn, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.BikeHorn]))
        self.distShop.addItem(Whistle, ItemType.GAG, 2, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.Whistle]))
        self.distShop.addItem(Bugle, ItemType.GAG, 6, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.Bugle]))
        self.distShop.addItem(PixieDust, ItemType.GAG, 18, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.PixieDust]))
        self.distShop.addItem(Anvil, ItemType.GAG, 2, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.Anvil]))
        self.distShop.addItem(FlowerPot, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.FlowerPot]))
        self.distShop.addItem(Sandbag, ItemType.GAG, 2, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.Sandbag]))
        self.distShop.addItem(Geyser, ItemType.GAG, 50, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.Geyser]))
        self.distShop.addItem(BigWeight, ItemType.GAG, 8, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.BigWeight]))
        self.distShop.addItem(StormCloud, ItemType.GAG, 6, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.StormCloud]))
        self.distShop.addItem(WaterGlass, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.WaterGlass]))
        self.distShop.addItem(WaterGun, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.WaterGun]))
        self.distShop.addItem(FireHose, ItemType.GAG, 3, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.FireHose]))
        self.distShop.addItem(SquirtingFlower, ItemType.GAG, 1, invIcons.find(GagGlobals.InventoryIconByName[CIGlobals.SquirtFlower]))
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

    def update(self, page = None):
        Shop.update(self, page)

    def enter(self):
        Shop.enter(self)
        self.originalSupply = base.localAvatar.getBackpackAmmo()

    def exit(self):
        Shop.exit(self)
        self.originalSupply = {}
