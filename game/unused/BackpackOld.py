########################################
# Filename: Backpack.py
# Created by: DecodedLogic (07Jul15)
########################################

from lib.coginvasion.gags.GagManager import GagManager
from lib.coginvasion.gags.GagState import GagState
from lib.coginvasion.globals import CIGlobals
from abc import ABCMeta
import random, types

class Backpack:
    amounts = {CIGlobals.WholeCreamPie : 7,
        CIGlobals.WholeFruitPie : 10,
        CIGlobals.BirthdayCake : 3,
        CIGlobals.WeddingCake : 3,
        CIGlobals.JugglingBalls : 3,
        CIGlobals.BambooCane : 4,
        CIGlobals.GrandPiano : 3,
        CIGlobals.Safe : 7,
        CIGlobals.TNT : 3,
        CIGlobals.SeltzerBottle : 10,
        CIGlobals.FruitPieSlice : 10,
        CIGlobals.CreamPieSlice : 10,
        CIGlobals.Megaphone : 7,
        CIGlobals.Cupcake: 15,
        CIGlobals.SquirtFlower : 15,
        CIGlobals.TrapDoor : 7,
        CIGlobals.Quicksand : 7,
        CIGlobals.BananaPeel : 10,
        CIGlobals.Lipstick : 5,
        CIGlobals.Aoogah : 7,
        CIGlobals.ElephantHorn : 5,
        CIGlobals.Foghorn : 3,
        CIGlobals.Opera : 1,
        CIGlobals.BikeHorn : 15,
        CIGlobals.Whistle : 10,
        CIGlobals.Bugle : 10,
        CIGlobals.PixieDust : 5,
        CIGlobals.Anvil : 8,
        CIGlobals.FlowerPot : 12,
        CIGlobals.Sandbag : 10,
        CIGlobals.Geyser : 1,
        CIGlobals.BigWeight : 7,
        CIGlobals.StormCloud : 3,
        CIGlobals.WaterGlass : 10,
        CIGlobals.WaterGun : 7,
        CIGlobals.FireHose : 5}

    def __init__(self):
        __metaclass__ = ABCMeta
        self.gags = {}
        self.gagIds = {}
        self.avatar = None
        self.index = 3
        self.currentGag = None
        self.activeGag = None
        self.gagMgr = GagManager()
        self.gagGUI = None
        self.loadout = []

    def setup(self, avatar):
        self.avatar = avatar

    def setGagGUI(self, gui):
        self.gagGUI = gui

        if not len(self.loadout):
            availableGags = self.gags.keys()
            for _ in xrange(4):
                gag = random.choice(availableGags)
                availableGags.remove(gag)
                self.addLoadoutGag(gag)
        else:
            self.gagGUI.updateLoadout()

    def getGagGUI(self):
        return self.gagGUI

    def setGags(self, gags):
        self.gags = gags

    def addGag(self, gag, supply):
        gag.setAvatar(self.avatar)
        self.gags[gag] = [supply, self.amounts.get(gag.getName())]
        self.gagIds[gag.getID()] = gag
        for key in self.gags.keys():
            if key == None:
                del self.gags[key]

    def getGags(self):
        return self.gags

    def getGagByIndex(self, index):
        return self.gags.keys()[index]

    def getIndexFromName(self, name):
        names = self.gags.keys()
        for gName in names:
            if gName == name:
                return self.gags.keys().index(gName)

    def setLoadout(self, loadoutList):
        self.loadout = loadoutList
        if hasattr(base, 'cr'):
            if base.cr.playGame.world and base.cr.playGame.world.getPlace() and base.cr.playGame.world.getPlace().fsm.getCurrentState().getName() == 'walk':
                base.localAvatar.disablePies()
                base.localAvatar.enablePies(1)

    def addLoadoutGag(self, gag):
        if gag not in self.loadout:
            if len(self.loadout) < 4:
                self.loadout.append(gag)
                self.gagGUI.updateLoadout()

    def removeLoadoutGag(self, gag):
        if type(gag) == types.IntType:
            gag = self.getGagByIndex(gag)
        self.loadout.remove(gag)
        self.gagGUI.updateLoadout()

    def getLoadout(self):
        return self.loadout

    def setCurrentGag(self, arg):
        if arg == None:
            if self.currentGag:
                self.currentGag.unEquip()
                self.currentGag = None
            self.index = -1
            return

        for gag in self.gags.keys():
            if gag:
                if gag.getName() == arg:
                    if not gag.getAvatar():
                        gag.setAvatar(self.avatar)
                    self.index = self.gags.keys().index(gag)
                    break
        if self.currentGag:
            if not self.currentGag.getAvatar():
                self.currentGag.setAvatar(self.avatar)
            self.currentGag.unEquip()
        self.currentGag = self.gags.keys()[self.index]

    def getCurrentGag(self):
        return self.currentGag

    def setActiveGag(self, arg):
        if arg != None:
            for gag in self.gags.keys():
                if gag:
                    if gag.getName() == arg:
                        if not self.activeGag:
                            self.activeGag = gag
                        else:
                            if self.activeGag.getState() == GagState.LOADED:
                                self.activeGag = gag
                        break
        else:
            if self.activeGag:
                if self.activeGag.getState() == GagState.LOADED:
                    self.activeGag = arg

    def getActiveGag(self):
        return self.activeGag

    def setMaxSupply(self, nMaxSupply, arg = None):
        if type(arg) == types.IntType or arg == None:
            if self.index and self.gags:
                if arg == None:
                    arg = self.index
                self.amounts.values()[arg] = nMaxSupply
        elif isinstance(arg, str):
            self.amounts.update({arg : nMaxSupply})

    def getMaxSupply(self, arg = None):
        if type(arg) == types.IntType or arg == None:
            if not self.index is None and not self.gags is None:
                if arg == None:
                    return self.amounts.values()[self.index]
                return self.gags.values()[self.gags.keys().index(self.getGagByID(arg))][1]
        elif isinstance(arg, str):
            return self.amounts.get(arg)
        if arg: return 0

    def isInBackpack(self, name):
        if len(self.gags) == 0:
            return False
        else:
            for gag in self.gags.keys():
                if not gag:
                    del self.gags[gag]
                else:
                    if gag.getName() == name:
                        return True
            return False

    def resetGags(self):
        self.gags = {}
        self.gagIds = {}
        self.currentGag = None
        self.activeGag = None

    def setSupply(self, nSupply, arg = None):
        curMaxSupply = None
        index = None
        if arg == None and self.index:
            curMaxSupply = self.gags.values()[self.index][1]
            index = self.gags.keys()[self.index]
        if type(arg) == types.IntType:
            if not self.index is None and not self.gags is None:
                for gag, values in self.gags.iteritems():
                    if gag.getID() == arg:
                        curMaxSupply = values[1]
                        index = gag
        elif isinstance(arg, str):
            if self.isInBackpack(arg):
                for gag, ammoTbl in self.gags.iteritems():
                    if gag.getName() == arg:
                        ammoTbl[0] = nSupply
                        curMaxSupply = ammoTbl[1]
                        index = gag
                        break
            else:
                gag = self.gagMgr.getGagByName(arg)
                self.addGag(gag, nSupply)
        if index != None:
            self.gags.update({index : [nSupply, curMaxSupply]})
        if game.process == 'client' and self.gagGUI:
            self.gagGUI.update()

    def getSupply(self, arg = None):
        curSupply = 0
        if arg == None:
            curSupply = self.gags.values()[self.index][0]
        if type(arg) == types.IntType:
            if not self.index is None and not self.gags is None:
                curSupply = self.gags.values()[self.gags.keys().index(self.getGagByID(arg))][0]
            if curSupply == None: return 0
        elif isinstance(arg, str):
            if len(self.gags) > 0:
                for gag, ammoTbl in self.gags.iteritems():
                    if gag:
                        if gag.getName() == arg:
                            curSupply = ammoTbl[0]
                            break
        return curSupply

    def getGagByID(self, gagID):
        if not self.gags: return
        if gagID in self.gagIds.keys():
            return self.gagIds.get(gagID)
        else:
            return None

    def getIndex(self):
        return self.index

    def cleanup(self):
        self.gags = None
        self.avatar = None
        self.index = None
        self.currentGag = None
        self.activeGag = None
        self.gagMgr = None
        self.gagGUI = None
