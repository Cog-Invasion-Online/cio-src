"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Backpack.py
@author Maverick Liberty
@date March 20, 2016

@desc The client version of the backpack.

"""

from src.coginvasion.gags.backpack.BackpackBase import BackpackBase
from src.coginvasion.gags.GagManager import GagManager
from src.coginvasion.gags.GagState import GagState

from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

class Backpack(BackpackBase):

    def __init__(self, avatar):
        BackpackBase.__init__(self, avatar)

        # The gag that's is active.
        # This returns either -1 or the gag id of the active gag.
        self.activeGag = -1

        # The gag that's currently in use by the avatar.
        # This returns either -1 or the gag id of the current gag.
        self.currentGag = -1

        # The GUI that shows the avatar's current loadout.
        # This is used for calling update() when we changed
        # the ammo of a gag.
        self.loadoutGUI = None

        # This is just used to create gag instances when
        # necessary.
        self.gagManager = GagManager()

    # Sets the current gag that's being used.
    # Requires a gag id or -1 to remove a current gag.
    def setCurrentGag(self, gagId = -1):
        if not self.currentGag == -1 and self.hasGag(self.currentGag):
            # Unequip the gag as we're switching to another one.
            self.gags.get(self.currentGag)[0].unEquip()
            self.currentGag = -1

        if not gagId == -1 and self.hasGag(gagId):
            # Set the current gag.
            self.currentGag = gagId
            self.gags.get(self.currentGag)[0].equip()

        if self.loadoutGUI:
            self.loadoutGUI.update()

    # Returns the current gag.
    def getCurrentGag(self):
        return self.getGagByID(self.currentGag)

    # Sets the gag that is now activated.
    # Requires a gag id or -1 to remove an active gag.
    def setActiveGag(self, gagId):
        # Clear the active gag if it's not active.
        if not self.activeGag == -1:
            state = self.gags.get(self.activeGag)[0].getState()
            if state in [GagState.LOADED, GagState.RECHARGING]:
                self.activeGag = -1

        # Finally, set the active gag if one isn't set and
        # the gag is in the backpack.
        if self.activeGag == -1 and self.hasGag(gagId):
            self.activeGag = gagId

    # Returns the active gag.
    def getActiveGag(self):
        return self.getGagByID(self.activeGag)

    # Adds a gag to the loadout.
    def addLoadoutGag(self, gagId):
        if len(self.loadout) < 4 and self.hasGag(gagId) and not gagId in self.loadout:
            self.loadout.append(gagId)

    # Removes a gag from the loadout.
    def removeLoadoutGag(self, gagId):
        if len(self.loadout) > 0 and gagId in self.loadout:
            self.loadout.remove(gagId)

    # Sets the max supply of a gag.
    # Returns either true or false depending on if the
    # max supply was updated.
    def setMaxSupply(self, gagId, maxSupply):
        updatedMaxSupply = BackpackBase.setMaxSupply(self, gagId, maxSupply)
        if updatedMaxSupply and self.loadoutGUI:
            self.loadoutGUI.update()
        return updatedMaxSupply

    # When a gagId is specified, returns the max supply of a gag in the backpack or -1.
    # When a gagId isn't specified, simply returns the max supply of the current gag.
    def getMaxSupply(self, gagId = -1):
        if gagId == -1 and self.currentGag > -1:
            return BackpackBase.getMaxSupply(self, self.currentGag)
        return BackpackBase.getMaxSupply(self, gagId)

    # Sets the supply of a gag.
    # Returns either true or false depending on if the
    # supply was updated.
    def setSupply(self, gagId, supply):
        updatedSupply = BackpackBase.setSupply(self, gagId, supply)
        if updatedSupply and self.loadoutGUI:
            self.loadoutGUI.update()
        return updatedSupply

    # When a gagId is specified, returns the supply of a gag in the backpack or -1.
    # When a gagId isn't specified, simply returns the supply of the current gag.
    def getSupply(self, gagId = -1):
        if gagId == -1 and self.currentGag > -1:
            return BackpackBase.getSupply(self, self.currentGag)
        return BackpackBase.getSupply(self, gagId)

    # Returns the gag's class by gag id.
    def getGagByID(self, gagId):
        if self.hasGag(gagId):
            return self.gags.get(gagId)[0]
        return None

    # Returns the gag by index.
    def getGagByIndex(self, index):
        return self.gags.get(self.gags.keys()[index])[0]
    
    # Converts a net string blob back to useable data and then
    # updates supplies.
    def updateSuppliesFromNetString(self, netString):
        dg = PyDatagram(netString)
        dgi = PyDatagramIterator(dg)

        addedGag = False
        
        while dgi.getRemainingSize() > 0:
            gagId = dgi.getUint8()
            supply = dgi.getUint8()
            
            if self.hasGag(gagId):
                self.setSupply(gagId, supply)
            else:
                addedGag = True
                self.addGag(gagId, supply)

        if addedGag and self.avatar == base.localAvatar:
            if base.localAvatar.invGui:
                base.localAvatar.reloadInvGui()

    # Cleans up all the variables that are no longer needed.
    def cleanup(self):
        for _, data in self.gags.iteritems():
            gag = data[0]
            gag.delete()
        del self.currentGag
        del self.activeGag
        del self.loadoutGUI
        del self.gagManager
        BackpackBase.cleanup(self)
