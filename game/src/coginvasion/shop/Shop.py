"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Shop.py
@author Maverick Liberty
@date July 13, 2015

@desc Base class for all shops.

"""

from direct.fsm.StateData import StateData
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectButton, OnscreenImage, DGG
from direct.interval.IntervalGlobal import Sequence, Wait, Func
from direct.task.Task import Task

from src.coginvasion.globals import CIGlobals
from src.coginvasion.shop.ItemType import ItemType
from src.coginvasion.cog import CogBattleGlobals
from src.coginvasion.gags import GagGlobals

from panda3d.core import Vec4, TransparencyAttrib

from collections import OrderedDict

GRAYED_OUT_COLOR = Vec4(0.25, 0.25, 0.25, 1)
NORMAL_COLOR = Vec4(1, 1, 1, 1)

class Shop(StateData):
    notify = directNotify.newCategory('Shop')

    def __init__(self, distShop, doneEvent, wantTurretCount = 0, wantFullShop = False):
        StateData.__init__(self, doneEvent)
        self.distShop = distShop
        self.origHealth = None
        self.avMoney = 0
        self.healCooldownDoneSoundPath = 'phase_3.5/audio/sfx/tt_s_gui_sbk_cdrSuccess.ogg'
        self.healCooldownDoneSfx = None
        self.requestedHp = None
        self.pages = 1
        self.window = None
        self.upgradesPurchased = False
        self.originalSupply = {}
        self.wantTurretCount = wantTurretCount
        self.wantFullShop = wantFullShop

        # This handles heal cooldowns.
        self.healCooldowns = {}
        self.newHealCooldowns = {}

    def confirmPurchase(self):
        if self.requestedHp != None:
            self.distShop.d_requestHealth(self.requestedHp)
        messenger.send(self.doneEvent)

    def cancelPurchase(self):
        messenger.send(self.doneEvent)
        base.localAvatar.setMoney(self.avMoney)
        base.localAvatar.setHealth(self.origHealth)

        for healCooldown in self.newHealCooldowns.keys():
            if self.healCooldowns.get(healCooldown):
                del self.healCooldowns[healCooldown]

    def __purchaseUpgradeItem(self, values):
        upgradeID = values.get('upgradeID')
        upgrades = 0
        maxUpgrades = values.get('maxUpgrades')
        avID = base.localAvatar.getPUInventory()[1]
        hasTurret = False
        turretCount = 0

        battle = base.localAvatar.getBattleZone()
        if battle and battle.getTurretManager():
            turret = battle.getTurretManager().getTurret()
            turretCount = battle.getTurretCount()
            if turret:
                hasTurret = True
                if turret.getGagID() == upgradeID:
                    upgrades = 1

        if avID == upgradeID:
            dataSupply = base.localAvatar.getPUInventory()[0]
            if dataSupply > 0:
                upgrades = dataSupply

        if upgrades < maxUpgrades and not hasTurret and turretCount < CogBattleGlobals.MAX_TURRETS:
            if upgrades < 0:
                upgrades = 1
            else:
                upgrades += 1
            self.upgradesPurchased = True
            base.localAvatar.getBattleZone().getTurretManager().setGag(upgradeID)
            base.localAvatar.setMoney(base.localAvatar.getMoney() - values.get('price'))
            base.localAvatar.setPUInventory([upgrades, upgradeID])
        elif turretCount >= CogBattleGlobals.MAX_TURRETS:
            self.window.showInfo("The maximum amount of turrets has been reached.", 1, 2)

    def __purchaseGagItem(self, gag, values):
        gagID = GagGlobals.getIDByName(gag)
        supply = self.backpack.getSupply(gagID)
        maxSupply = self.backpack.getMaxSupply(gagID)
        vowels = ['a', 'e', 'i', 'o', 'u']
        if supply < maxSupply:
            if not hasattr(self.originalSupply, 'keys'):
                self.originalSupply = {gagID : supply}
            else:
                self.originalSupply.update({gagID : supply})
            base.localAvatar.setMoney(base.localAvatar.getMoney() - values.get('price'))
            
            # Let's check the first letter of the name for a vowel.
            infoPrefix = 'Purchased a %s'
            if gag[0].lower() in vowels:
                infoPrefix = 'Purchased an %s'
            
            self.window.showInfo('%s' % ((infoPrefix % (gag))), duration = 3)
            base.localAvatar.updateAttackAmmo(gagID, supply + 1)

    def __purchaseHealItem(self, item, values):
        health = base.localAvatar.getHealth()
        maxHealth = base.localAvatar.getMaxHealth()
        healAmt = values.get('heal')
        if health < maxHealth and not self.hasCooldown(item):
            if health + healAmt > maxHealth:
                healAmt = maxHealth - health
            self.requestedHp = healAmt
            base.localAvatar.setHealth(health + healAmt)
            healDict = {item : [0, values.get('healCooldown')]}
            self.healCooldowns.update(healDict)
            self.newHealCooldowns.update(healDict)
            base.taskMgr.doMethodLater(1, self.__doHealCooldown, item, extraArgs = [item], appendTask = True)
            base.localAvatar.setMoney(base.localAvatar.getMoney() - values.get('price'))

    def __doHealCooldown(self, item, task):
        cooldownData = self.getCooldown(item)
        if cooldownData:
            cooldownTime = cooldownData[0]
            maxCooldownTime = cooldownData[1]
            cooldownTime += 1
            self.healCooldowns[item] = [cooldownTime, maxCooldownTime]
            if cooldownTime == maxCooldownTime:
                if item in self.healCooldowns:
                    del self.healCooldowns[item]
                if self.window:
                    self.healCooldownDoneSfx.play()
                self.update()
                return Task.done
            return Task.again
        return Task.done

    def updateTurrets(self, amount):
        if self.window:
            self.window.setTurrets(amount)

    def getCooldown(self, item):
        if self.hasCooldown(item):
            return self.healCooldowns.get(item)

    def hasCooldown(self, item):
        return item in self.healCooldowns.keys()

    def purchaseItem(self, item):
        items = self.items
        itemType = None
        values = None
        for iItem, iValues in items.iteritems():
            if iItem == item:
                values = iValues
                itemType = values.get('type')
                break
        price = values.get('price')
        if self.isAffordable(price):
            if itemType == ItemType.GAG:
                self.__purchaseGagItem(item, values)
            elif itemType == ItemType.UPGRADE:
                self.__purchaseUpgradeItem(values)
            elif itemType == ItemType.HEAL:
                self.__purchaseHealItem(item, values)
        self.update()

    def update(self):
        if self.window:
            self.window.updatePage()
            if base.localAvatar.getMoney() == 0: self.handleNoMoney()

    def handleNoMoney(self, duration = -1):
        self.window.showInfo('You need more jellybeans!', negative = 1, duration = duration)

    def isAffordable(self, price, silent = 0):
        if base.localAvatar.getMoney() - price >= 0:
            return True
        else:
            if not silent:
                Shop.handleNoMoney(self, duration = 2)
            return False

    def setup(self):
        pass

    def enter(self):
        StateData.enter(self)
        self.avMoney = base.localAvatar.getMoney()
        self.origHealth = base.localAvatar.getHealth()
        self.window = ShopWindow(self, image = 'phase_4/maps/FrameBlankA.jpg', wantTurretCount = self.wantTurretCount)
        self.window.setup()
        self.window.setOKCommand(self.confirmPurchase)
        self.window.setCancelCommand(self.cancelPurchase)
        self.window.initializeShop(self.distShop.getItems())
        self.window.updatePage()

        # Load the rejection sfx.
        self.healCooldownDoneSfx = base.loadSfx(self.healCooldownDoneSoundPath)

    def exit(self):
        StateData.exit(self)
        if self.window:
            self.upgradesPurchased = False
            self.window.delete()
            self.requestedHp = None
            self.healCooldownDoneSfx = None
            self.originalSupply = {}

    def destroy(self):
        self.exit()
        for cooldown in self.healCooldowns.keys():
            base.taskMgr.remove(cooldown)
            if cooldown in self.healCooldowns:
                del self.healCooldowns[cooldown]
            del self.gagsPurchased

class Page(DirectFrame):

    def __init__(self, shop, window):
        DirectFrame.__init__(self, parent = window, sortOrder = 1)
        self.shop = shop

    def destroy(self):
        DirectFrame.destroy(self)

class ItemButton(DirectButton):
    
    def __init__(self, page, pos):
        DirectButton.__init__(self, parent = page, relief = None, command = self.handleClick, pos = pos)
        self.window = page
        self.item = None
        self.values = None
        self.label = DirectLabel(text = '', relief = None, parent = self, 
            text_scale = 0.05)
        self.label.initialiseoptions(DirectLabel)
        self.label.hide()
        self.hide()
    
    def setItem(self, item, values):
        if values:
            image = values.get('image')
            price = values.get('price')
            text = ''
            
            self.item = item
            self.values = values
            self['geom'] = image
            
            if values.get('type') == ItemType.GAG:
                gagId = GagGlobals.getIDByName(item)
                supply = base.localAvatar.getBackpack().getSupply(gagId)
                maxSupply = base.localAvatar.getBackpack().getMaxSupply(gagId)
                self.setScale(1.3)
                self.label['text_scale'] = 0.05
                self.label.setPos(0, 0, -0.11)
                self.setTransparency(TransparencyAttrib.MNone)
            elif values.get('type') == ItemType.UPGRADE:
                upgradeID = values.get('upgradeID')
                avID = base.localAvatar.getPUInventory()[1]
                supply = 0
                maxSupply = values.get('maxUpgrades')
        
                battle = base.localAvatar.getBattleZone()
                if battle and battle.getTurretManager():
                    turret = battle.getTurretManager().getTurret()
                    if turret and turret.getGagID() == upgradeID:
                        supply = 1
        
                if avID == upgradeID:
                    dataSupply = base.localAvatar.getPUInventory()[0]
                    if dataSupply > 0:
                        supply = dataSupply
    
                self.setScale(0.15)
                self.label['text_scale'] = 0.3
                self.label.setPos(0, 0, -1.2)
                self.setTransparency(TransparencyAttrib.MNone)
            elif values.get('type') == ItemType.HEAL:
                text = '%s\n%s JBS' % (item, price) if 'showTitle' in values else item
                self.setTransparency(TransparencyAttrib.MAlpha)
                self.setScale(0.105)
                self.label['text_scale'] = 0.55
                self.label.setPos(0, 0, -1.6)
            text = text if text else '%s/%s\n%s JBS' % (str(supply), str(maxSupply), str(price))
            self.label['text'] = text
                
            self.label.initialiseoptions(DirectLabel)
            self.initialiseoptions(ItemButton)
            
            self.label.show()
            self.show()
        
    def update(self):
        money = base.localAvatar.getMoney()
        if self.values:
            itemType = self.values.get('type')
            price = self.values.get('price')
            self.setColorScale(NORMAL_COLOR)
            if price > money:
                self.setColorScale(GRAYED_OUT_COLOR)
            if itemType == ItemType.GAG:
                backpack = base.localAvatar.getBackpack()
                gagId = GagGlobals.getIDByName(self.item)
                supply = backpack.getSupply(gagId)
                maxSupply = backpack.getMaxSupply(gagId)
                inBackpack = backpack.hasGag(gagId)
                if not inBackpack or inBackpack and supply >= maxSupply:
                    self.setColorScale(GRAYED_OUT_COLOR)
                self.label['text'] = '%s/%s\n%s JBS' % (str(supply), str(maxSupply), str(price))
            elif itemType == ItemType.UPGRADE:
                maxSupply = self.values.get('maxUpgrades')
                upgradeID = self.values.get('upgradeID')
                avID = base.localAvatar.getPUInventory()[1]
                supply = 0
                turretCount = 0
                hasTurret = False
    
                battle = base.localAvatar.getBattleZone()
                if battle and battle.getTurretManager():
                    turretCount = battle.getTurretCount()
                    turret = battle.getTurretManager().getTurret()
                    if turret:
                        hasTurret = True
                        if turret.getGagID() == upgradeID:
                            supply = 1
    
                if avID == upgradeID:
                    dataSupply = base.localAvatar.getPUInventory()[0]
                    if dataSupply > 0:
                        supply = dataSupply
    
                if supply > 0 or base.localAvatar.getPUInventory()[0] > 0 or hasTurret or turretCount == CogBattleGlobals.MAX_TURRETS:
                    self.setColorScale(GRAYED_OUT_COLOR)
    
                self.label['text'] = '%s\n%s/%s\n%s JBS' % (self.item, str(supply), str(maxSupply), str(price))
            elif itemType == ItemType.HEAL:
                if base.localAvatar.getHealth() == base.localAvatar.getMaxHealth() or self.shop.hasCooldown(self.item):
                    self.setColorScale(GRAYED_OUT_COLOR)
        
    def handleClick(self):
        if self.item:
            self.window.shop.purchaseItem(self.item)
            
    def destroy(self):
        DirectFrame.destroy(self)

class ShopWindow(DirectFrame):

    def __init__(self, shop, image, wantTurretCount):
        DirectFrame.__init__(self, sortOrder = 1)
        self.shop = shop
        self.wantTurretCount = wantTurretCount
        self.bgImage = image
        self.title = None
        self.okBtn = None
        self.clBtn = None
        self.infoLbl = None
        self.turretLabel = None
        self.turretImg = None
        self.isSetup = False
        self.turretCount = 0
        
        # New variables for optimized shop.
        self.firstItemIndex = -1
        self.btnPositions = [(-0.45, 0, 0), (-0.15, 0, 0), (0.15, 0, 0), (0.45, 0, 0)]
        self.page = Page(self.shop, self)
        self.itemButtons = []
        self.itemButtons.append(ItemButton(self.page, self.btnPositions[0]))
        self.itemButtons.append(ItemButton(self.page, self.btnPositions[1]))
        self.itemButtons.append(ItemButton(self.page, self.btnPositions[2]))
        self.itemButtons.append(ItemButton(self.page, self.btnPositions[3]))
        self.newItems = None

    def setup(self, title = 'CHOOSE WHAT YOU WANT TO BUY'):
        font = CIGlobals.getMickeyFont()
        txtFg = (0, 0, 0, 1)
        txtScale = 0.05
        txtPos = (0, -0.1)
        buttons = loader.loadModel('phase_3.5/models/gui/QT_buttons.bam')
        self.window = OnscreenImage(image = self.bgImage, scale = (0.9, 1, 0.7), parent = self)
        self.title = DirectLabel(text = title, relief = None, pos = (0, 0, 0.5), text_wordwrap = 10, text_font = font,
                                 text_fg = (1, 1, 0, 1), scale = 0.1, parent = self)

        # Let's update the turret count.
        self.updateTurretCount()

        self.infoLbl = DirectLabel(text = 'Welcome!', relief = None, text_scale = 0.075, text_fg = txtFg, text_shadow = (0, 0, 0, 0),
                                   pos = (0, 0, 0.215))
        self.okBtn = DirectButton(geom = CIGlobals.getOkayBtnGeom(), relief = None, text = 'OK', text_fg = txtFg,
                                  text_scale = txtScale, text_pos = txtPos, pos = (-0.1, 0, -0.5), parent = self)
        self.clBtn = DirectButton(geom = CIGlobals.getCancelBtnGeom(), relief = None, text = 'Cancel', text_fg = txtFg,
                                  text_scale = txtScale, text_pos = txtPos, pos = (0.1, 0, -0.5), parent = self)
        buttonGeom = (buttons.find('**/QT_back'), buttons.find('**/QT_back'), buttons.find('**/QT_back'), buttons.find('**/QT_back'))
        self.backBtn = DirectButton(geom = buttonGeom, relief = None, scale = 0.05, pos = (-0.3, 0, -0.25), parent = self, command = self.changePage, extraArgs = [0])
        self.nextBtn = DirectButton(geom = buttonGeom, relief = None, scale = 0.05, pos = (0.3, 0, -0.25), hpr = (0, 0, 180), command = self.changePage, extraArgs = [1], parent = self)
        self.hideInfo()

    def setTurrets(self, amount):
        if self.shop.upgradesPurchased:
            amount += 1
        self.turretCount = amount
        self.updatePage()

    def updateTurretCount(self):
        if self.turretLabel:
            self.turretLabel.destroy()

        if self.wantTurretCount:
            maxTurrets = CogBattleGlobals.MAX_TURRETS

            if not self.turretImg:
                self.turretImg = OnscreenImage(image = "phase_3.5/maps/cannon-icon.png",
                    scale = (0.05, 1, 0.05),
                    pos = (-0.22, 0, 0.275)
                )
                self.turretImg.setTransparency(TransparencyAttrib.MAlpha)

            self.turretLabel = DirectLabel(text = 'Turrets: %s/%s' % (str(self.turretCount), str(maxTurrets)),
                relief = None,
                text_scale = 0.07,
                text_fg = (0, 0, 0, 1),
                text_shadow = (0, 0, 0, 0),
                pos = (0, 0, 0.265)
            )

    def changePage(self, direction):
        var = (self.firstItemIndex - 4)
        if direction == 1:
            var = (self.firstItemIndex + 4)

        self.setBackBtn(True)
        self.setNextBtn(True)
        if (var - 4) < 0:
            self.setBackBtn(False)
        elif (var + 4) >= len(self.newItems):
            self.setNextBtn(False)
            
        self.firstItemIndex = var
        self.setupItems(begin = self.firstItemIndex)
    
    def initializeShop(self, items):
        newItems = dict(items)
        loadout = base.localAvatar.backpack.loadout
        
        # Let's show the loadout gags first in a full shop.
        if self.shop.wantFullShop:
            crcGags = OrderedDict(newItems)
            for item, values in newItems.items():
                if values and values.get('type') == ItemType.GAG:
                    gagId = GagGlobals.getIDByName(item)
                    hasGag = base.localAvatar.getBackpack().hasGag(gagId)
                    if gagId not in loadout or not hasGag:
                        del crcGags[item]
                        if not hasGag:
                            del newItems[item]
                    else:
                        del newItems[item]
            # Let's add back the other gags.
            crcGags.update(newItems)
            newItems = crcGags
        else:
            for item, values in newItems.items():
                if values and values.get('type') == ItemType.GAG:
                    gagId = base.localAvatar.getBackpack().hasGag(gagId)
                    if gagId not in loadout or not base.localAvatar.getBackpack().hasGag(gagId):
                        del newItems[item]
        
        self.newItems = newItems
        self.firstItemIndex = 0
        self.setupItems()
        
        if len(newItems.keys()) <= 4:
            self.backBtn.hide()
            self.nextBtn.hide()
        self.setBackBtn(False)
        self.isSetup = True
        
    def setupItems(self, begin = 0):
        for button in self.itemButtons:
            button.hide()
            button.label.hide()
        for i in xrange(4):
            item = self.newItems.keys()[begin + i] if (begin + i) < len(self.newItems.keys()) else None
            values = self.newItems.get(item) if item else None
            if item:
                button = self.itemButtons[i]
                button.setItem(item, values)
                button.update()
        
    def updatePage(self):
        battle = base.localAvatar.getBattleZone()

        if battle and self.wantTurretCount:
            self.shop.distShop.sendUpdate('requestTurretCount', [])
            self.updateTurretCount()
        
        for button in self.itemButtons: button.update()

    def setBackBtn(self, enabled):
        if self.backBtn:
            if enabled == False:
                self.backBtn.setColorScale(GRAYED_OUT_COLOR)
                self.backBtn['state'] = DGG.DISABLED
            else:
                self.backBtn.setColorScale(NORMAL_COLOR)
                self.backBtn['state'] = DGG.NORMAL

    def setNextBtn(self, enabled):
        if self.nextBtn:
            if enabled == False:
                self.nextBtn.setColorScale(GRAYED_OUT_COLOR)
                self.nextBtn['state'] = DGG.DISABLED
            else:
                self.nextBtn.setColorScale(NORMAL_COLOR)
                self.nextBtn['state'] = DGG.NORMAL

    def setOKCommand(self, command):
        if self.okBtn: self.okBtn['command'] = command

    def setCancelCommand(self, command):
        if self.clBtn: self.clBtn['command'] = command

    def showInfo(self, text, negative = 0, duration = -1):
        self.infoLbl.show()
        if negative:
            self.infoLbl['text_fg'] = (0.9, 0, 0, 1)
            self.infoLbl['text_shadow'] = (0, 0, 0, 1)
        else:
            self.infoLbl['text_fg'] = (0, 0, 0, 1)
            self.infoLbl['text_shadow'] = (0, 0, 0, 0)
        self.infoLbl['text'] = text
        if duration > -1: Sequence(Wait(duration), Func(self.hideInfo)).start()

    def hideInfo(self):
        if self.infoLbl: self.infoLbl.hide()

    def delete(self):
        elements = [self.title, self.okBtn, self.clBtn, self.infoLbl, self.backBtn, self.nextBtn, self.turretLabel, self.turretImg, self.page]
        for element in elements:
            if element:
                element.destroy()
        del elements
        del self.page
        for button in self.itemButtons:
            button.destroy()
        self.itemButtons = None
        del self.itemButtons
        self.title = None
        self.okBtn = None
        self.clBtn = None
        self.infoLbl = None
        self.backBtn = None
        self.nextBtn = None
        self.bgImage = None
        self.turretLabel = None
        self.turretCount = None
        if self.window:
            self.window.destroy()
            self.window = None
        self.destroy()
