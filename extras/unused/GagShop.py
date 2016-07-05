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

class GagShop(Shop):
    notify = directNotify.newCategory('GagShop')

    def __init__(self, distShop, doneEvent):
        Shop.__init__(self, distShop, doneEvent)
        self.distShop = distShop
        self.backpack = base.localAvatar.getBackpack()
        self.originalSupply = {}
        self.setup()

    def setup(self):
        invIcons = loader.loadModel("phase_3.5/models/gui/inventory_icons.bam")
        self.distShop.addItem(WholeCreamPie, ItemType.GAG, 2, invIcons.find('**/inventory_creampie'))
        self.distShop.addItem(BirthdayCake, ItemType.GAG, 5, invIcons.find('**/inventory_cake'))
        self.distShop.addItem(CreamPieSlice, ItemType.GAG, 1, invIcons.find('**/inventory_cream_pie_slice'))
        self.distShop.addItem(TNT, ItemType.GAG, 20, invIcons.find('**/inventory_tnt'))
        self.distShop.addItem(SeltzerBottle, ItemType.GAG, 2, invIcons.find('**/inventory_seltzer_bottle'))
        self.distShop.addItem(WholeFruitPie, ItemType.GAG, 3, invIcons.find('**/inventory_fruitpie'))
        self.distShop.addItem(WeddingCake, ItemType.GAG, 100, invIcons.find('**/inventory_wedding'))
        self.distShop.addItem(FruitPieSlice, ItemType.GAG, 1, invIcons.find('**/inventory_fruit_pie_slice'))
        self.distShop.addItem(GrandPiano, ItemType.GAG, 15, invIcons.find('**/inventory_piano'))
        self.distShop.addItem(BambooCane, ItemType.GAG, 25, invIcons.find('**/inventory_bamboo_cane'))
        self.distShop.addItem(JugglingBalls, ItemType.GAG, 45, invIcons.find('**/inventory_juggling_cubes'))
        self.distShop.addItem(Megaphone, ItemType.GAG, 15, invIcons.find('**/inventory_megaphone'))
        self.items = self.distShop.getItems()
        Shop.setup(self)
        invIcons.removeNode()
        del invIcons

    def confirmPurchase(self):
        ammoList = []
        gagIds = []
        for gag in self.backpack.getGags():
            gagId = GagGlobals.getIDByName(gag.getName())
            gagIds.append(gagId)
            ammoList.append(self.backpack.getSupply(gag.getName()))
        self.distShop.sendUpdate('confirmPurchase', [gagIds, ammoList, base.localAvatar.getMoney()])
        Shop.confirmPurchase(self)

    def cancelPurchase(self):
        for gagName, supply in self.originalSupply.iteritems(): base.localAvatar.getBackpack().setSupply(supply, gagName)
        base.localAvatar.updateBackpackAmmo()
        Shop.cancelPurchase(self)

    def update(self):
        Shop.update(self)

    def enter(self):
        Shop.enter(self)

    def exit(self):
        Shop.exit(self)
        self.originalSupply = {}
