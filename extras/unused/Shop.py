"""

  Filename: Shop.py
  Created by: DecodedLogic (13Jul15)

"""

from direct.fsm.StateData import StateData
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectButton, OnscreenImage, DGG
from direct.interval.IntervalGlobal import Sequence, Wait, Func
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.shop.ItemType import ItemType
from panda3d.core import Vec4, TransparencyAttrib
import math

GRAYED_OUT_COLOR = Vec4(0.25, 0.25, 0.25, 1)
NORMAL_COLOR = Vec4(1, 1, 1, 1)

class Shop(StateData):
    notify = directNotify.newCategory('Shop')

    def __init__(self, distShop, doneEvent):
        StateData.__init__(self, doneEvent)
        self.distShop = distShop
        self.avMoney = base.localAvatar.getMoney()
        self.pages = 1
        self.window = None

    def confirmPurchase(self):
        messenger.send(self.doneEvent)

    def cancelPurchase(self):
        messenger.send(self.doneEvent)
        base.localAvatar.setMoney(self.avMoney)

    def purchaseItem(self, item):
        items = self.items
        price = 0
        itemType = None
        upgradeID = None
        maxUpgrades = None
        for index in range(len(items)):
            iItem = items.keys()[index]
            if iItem == item:
                price = items.values()[index].get('price')
                itemType = items.values()[index].get('type')
                if 'upgradeID' in items.values()[index]:
                    upgradeID = items.values()[index].get('upgradeID')
                if 'maxUpgrades' in items.values()[index]:
                    maxUpgrades = items.values()[index].get('maxUpgrades')
        if base.localAvatar.getMoney() < price:
            Shop.handleNoMoney(self, duration = 2)
        if itemType == ItemType.GAG:
            name = item().getName()
            supply = self.backpack.getSupply(name)
            if supply < self.backpack.getMaxSupply(name):
                self.originalSupply.update({name : supply})
                gagIds = []
                ammoList = []
                for gag in self.backpack.getGags():
                    gagIds.append(gag.getID())
                    supply = self.backpack.getSupply(gag.getName())
                    if gag.getName() == name:
                        ammoList.append(supply + 1)
                    else: ammoList.append(supply)
                if base.localAvatar.getMoney() - price > 0:
                    base.localAvatar.setMoney(base.localAvatar.getMoney() - price)
                    base.localAvatar.setBackpackAmmo(gagIds, ammoList)
                    self.window.showInfo('Purchased a %s' % (name), duration = 3)
                    base.localAvatar.updateBackpackAmmo()
                else:
                    self.handleNoMoney()
        elif itemType == ItemType.UPGRADE:
            upgrade = base.localAvatar.getPUInventory()[upgradeID]
            if upgrade < maxUpgrades:
                if base.localAvatar.getMoney() - price > 0:
                    base.localAvatar.setMoney(base.localAvatar.getMoney() - price)
                    upgrade = upgrade + 1
                else:
                    self.handleNoMoney()
            base.localAvatar.setPUInventory([upgrade])
            if upgradeID == 0:
                if not base.localAvatar.getMyBattle().getTurretManager().myTurret:
                    base.localAvatar.getMyBattle().getTurretManager().createTurretButton()
        elif itemType == ItemType.HEAL:
            if base.localAvatar.getHealth() < base.localAvatar.getMaxHealth():
                health = items.values()[index].get('heal')
                healAmount = health
                if base.localAvatar.getHealth() + health > base.localAvatar.getMaxHealth():
                    healAmount = base.localAvatar.getMaxHealth()
                self.distShop.d_requestHealth(healAmount)
        self.update()

    def update(self):
        if self.window:
            self.window.updatePages()
            if base.localAvatar.getMoney() == 0: self.handleNoMoney()

    def handleNoMoney(self, duration = -1):
        self.window.showInfo('You need more jellybeans!', negative = 1, duration = duration)

    def setup(self):
        pass

    def enter(self):
        StateData.enter(self)
        self.avMoney = base.localAvatar.getMoney()
        self.window = ShopWindow(self, image = 'phase_4/maps/FrameBlankA.jpg')
        self.window.setup()
        self.window.setOKCommand(self.confirmPurchase)
        self.window.setCancelCommand(self.cancelPurchase)
        self.window.makePages(self.distShop.getItems())
        self.window.setPage(0)

    def exit(self):
        StateData.exit(self)
        if self.window: self.window.delete()

class Page(DirectFrame):

    def __init__(self, window):
        DirectFrame.__init__(self, parent = window, sortOrder = 1)
        self.itemEntries = {}
        self.items = {}

    def update(self):
        for item, values in self.items.iteritems():
            entry = self.itemEntries.get(item)
            itemType = values.get('type')
            if itemType == ItemType.GAG:
                name = item().getName()
                inBackpack = False
                for gag in base.localAvatar.getBackpack().getGags():
                    if gag.getName() == name:
                        entry[0].setColorScale(NORMAL_COLOR)
                        inBackpack = True
                if not inBackpack:
                    entry[0].setColorScale(GRAYED_OUT_COLOR)
                supply = base.localAvatar.getBackpack().getSupply(name)
                maxSupply = base.localAvatar.getBackpack().getMaxSupply(name)
                entry[1]['text'] = '%s/%s\n%s JBS' % (str(supply), str(maxSupply), str(values.get('price')))
            elif itemType == ItemType.UPGRADE:
                upgradeID = values.get('upgradeID')
                supply = base.localAvatar.getPUInventory()[upgradeID]
                maxSupply = values.get('maxUpgrades')
                entry[1]['text'] = '%s/%s\n%s JBS' % (str(supply), str(maxSupply), str(values.get('price')))
            elif itemType == ItemType.HEAL:
                if base.localAvatar.getHealth() == base.localAvatar.getMaxHealth():
                    entry[0].setColorScale(GRAYED_OUT_COLOR)
                else:
                    entry[0].setColorScale(NORMAL_COLOR)

    def addItemEntry(self, item, entry):
        self.itemEntries.update({item : entry})

    def addItem(self, item):
        self.items.update(item)

    def destroy(self):
        self.items = {}
        del self.items
        for key, entry in self.itemEntries.iteritems():
            entry[0].destroy()
            entry[1].destroy()
            self.itemEntries[key] = None
        DirectFrame.destroy(self)

class ShopWindow(OnscreenImage):

    def __init__(self, shop, image):
        OnscreenImage.__init__(self, image = image, scale = (0.9, 1, 0.7))
        self.shop = shop
        self.title = None
        self.okBtn = None
        self.clBtn = None
        self.infoLbl = None
        self.nPage = -1
        self.nPages = 0
        self.nextPage = 1
        self.prevPage = 0
        self.pages = []
        self.isSetup = False

    def setup(self, title = 'CHOOSE WHAT YOU WANT TO BUY'):
        font = CIGlobals.getMickeyFont()
        txtFg = (0, 0, 0, 1)
        txtScale = 0.05
        txtPos = (0, -0.1)
        buttons = loader.loadModel('phase_3.5/models/gui/QT_buttons.bam')
        self.title = DirectLabel(text = title, relief = None, pos = (0, 0, 0.5), text_wordwrap = 10, text_font = font,
                                 text_fg = (1, 1, 0, 1), scale = 0.1, parent = self)
        self.infoLbl = DirectLabel(text = 'Welcome!', relief = None, text_scale = 0.075, text_fg = txtFg, text_shadow = (0, 0, 0, 1),
                                   pos = (0, 0, 0.225))
        self.okBtn = DirectButton(geom = CIGlobals.getOkayBtnGeom(), relief = None, text = 'OK', text_fg = txtFg,
                                  text_scale = txtScale, text_pos = txtPos, pos = (-0.1, 0, -0.5), parent = self)
        self.clBtn = DirectButton(geom = CIGlobals.getCancelBtnGeom(), relief = None, text = 'Cancel', text_fg = txtFg,
                                  text_scale = txtScale, text_pos = txtPos, pos = (0.1, 0, -0.5), parent = self)
        buttonGeom = (buttons.find('**/QT_back'), buttons.find('**/QT_back'), buttons.find('**/QT_back'), buttons.find('**/QT_back'))
        self.backBtn = DirectButton(geom = buttonGeom, relief = None, scale = 0.05, pos = (-0.3, 0, -0.25), parent = self, command = self.setPage, extraArgs = [self.prevPage])
        self.nextBtn = DirectButton(geom = buttonGeom, relief = None, scale = 0.05, pos = (0.3, 0, -0.25), hpr = (0, 0, 180), command = self.setPage, extraArgs = [self.nextPage], parent = self)
        self.hideInfo()

    def makePages(self, items):
        if self.isSetup: return
        self.nPages = int(math.ceil((len(items) / 4)))
        print "%s pages are needed." % (self.nPages)
        if len(items) % 4 != 0:
            self.nPages += 1
        itemPos = [(-0.45, 0, 0), (-0.15, 0, 0), (0.15, 0, 0), (0.45, 0, 0)]
        pageIndex = 0
        itemIndex = 0
        index = 1
        for _ in range(self.nPages):
            page = Page(self)
            self.pages.append(page)
        for item, values in items.iteritems():
            pos = itemPos[itemIndex]
            itemImage = values.get('image')
            page = self.pages[pageIndex]
            itemType = values.get('type')
            supply = 0
            maxSupply = 0
            if itemType == ItemType.GAG:
                button = DirectButton(
                        geom = (itemImage), scale = 1.3, pos = pos,
                        relief = None, parent = page,
                        command = self.shop.purchaseItem, extraArgs = [item]
                )
                supply = base.localAvatar.getBackpack().getSupply(item().getName())
                maxSupply = base.localAvatar.getBackpack().getMaxSupply(item().getName())
                buttonLabel = DirectLabel(
                        text = '%s/%s\n%s JBS' % (str(supply), str(maxSupply),
                        str(values.get('price'))), relief = None,
                        parent = button, text_scale = 0.05, pos = (0, 0, -0.11)
                )
            elif itemType == ItemType.UPGRADE:
                button = DirectButton(
                        image = (itemImage), scale = 0.15, pos = pos, relief = None,
                        parent = page, command = self.shop.purchaseItem,
                        extraArgs = [item]
                )
                button.setTransparency(TransparencyAttrib.MAlpha)
                upgradeID = values.get('upgradeID')
                supply = base.localAvatar.getPUInventory()[upgradeID]
                maxSupply = values.get('maxUpgrades')
                if upgradeID == 0 and base.localAvatar.getMyBattle().getTurretManager().myTurret:
                    supply = 1
                buttonLabel = DirectLabel(
                         text = '%s/%s\n%s JBS' % (str(supply), str(maxSupply),
                         str(values.get('price'))), relief = None,
                         parent = button, text_scale = 0.5, pos = (0, 0, -1.2)
                )
            elif itemType == ItemType.HEAL:
                label = '%s' % (item)
                if 'showTitle' in values:
                    label = '%s\n%s JBS' % (item, values.get('price'))
                button = DirectButton(
                          image = (itemImage), scale = 0.105, pos = pos,
                          relief = None, parent = page,
                          command = self.shop.purchaseItem, extraArgs = [item]
                )
                button.setTransparency(TransparencyAttrib.MAlpha)
                buttonLabel = DirectLabel(
                          text = label, relief = None, parent = button,
                          text_scale = 0.75, pos = (0, 0, -1.6)
                )
            page.addItemEntry(item, [button, buttonLabel])
            page.addItem({item : values})
            if index % 4 == 0:
                index = 1
                pageIndex += 1
                itemIndex = 0
            else:
                itemIndex = itemIndex + 1
                index += 1
        if self.nPages == 1:
            self.backBtn.hide()
            self.nextBtn.hide()
        for page in self.pages:
            page.hide()
            page.update()
        self.isSetup = True

    def updatePages(self):
        for page in self.pages:
            page.update()

    def setPage(self, page):
        if page < 0 or page > self.nPages: return
        if self.nPage != -1:
            self.pages[self.nPage].hide()
        if page == 0:
            self.backBtn.setColorScale(GRAYED_OUT_COLOR)
        if (page + 1) > self.nPages:
            self.nextBtn.setColorScale(GRAYED_OUT_COLOR)
        else:
            self.nextBtn.setColorScale(NORMAL_COLOR)
        if (page - 1) > -1:
            self.backBtn.setColorScale(NORMAL_COLOR)
        self.nPage = page
        self.prevPage = (page - 1)
        self.nextPage = (page + 1)
        self.pages[page].show()

    def setBackBtn(self, enabled):
        if self.backBtn:
            if not enabled:
                self.backBtn['frameColor'] = GRAYED_OUT_COLOR
                self.backBtn['state'] = DGG.DISABLED
            else:
                self.backBtn['frameColor'] = NORMAL_COLOR
                self.backBtn['state'] = DGG.NORMAL

    def setNextBtn(self, enabled):
        if self.nextBtn:
            if not enabled:
                self.nextBtn['frameColor'] = GRAYED_OUT_COLOR
                self.nextBtn['state'] = DGG.DISABLED
            else:
                self.nextBtn['frameColor'] = NORMAL_COLOR
                self.nextBtn['state'] = DGG.NORMAL

    def setOKCommand(self, command):
        if self.okBtn: self.okBtn['command'] = command

    def setCancelCommand(self, command):
        if self.clBtn: self.clBtn['command'] = command

    def showInfo(self, text, negative = 0, duration = -1):
        self.infoLbl.show()
        if negative:
            self.infoLbl['text_fg'] = (0.9, 0, 0, 1)
        else: self.infoLbl['text_fg'] = (0, 0, 0, 1)
        self.infoLbl['text'] = text
        if duration > -1: Sequence(Wait(duration), Func(self.hideInfo)).start()

    def hideInfo(self):
        if self.infoLbl: self.infoLbl.hide()

    def delete(self):
        elements = [self.title, self.okBtn, self.clBtn, self.infoLbl, self.backBtn, self.nextBtn]
        for element in elements:
            element.destroy()
        del elements
        for page in self.pages:
            page.destroy()
            self.pages.remove(page)
        self.title = None
        self.okBtn = None
        self.clBtn = None
        self.infoLbl = None
        self.backBtn = None
        self.nextBtn = None
        self.destroy()
