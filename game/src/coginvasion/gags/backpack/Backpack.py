########################################
# Filename: Backpack.py
# Created by: DecodedLogic (20Mar16)
########################################
# The client version of the backpack.

from src.coginvasion.gags.GagManager import GagManager
from src.coginvasion.gags.GagState import GagState
from src.coginvasion.gags import GagGlobals
import types

class Backpack:

    def __init__(self, avatar):
        # Dictionary that stores the gags in the backpack.
        # Setup like this:
        # gagId : [gag instance, current ammo, max ammo]
        self.gags = {}

        # The gags in-use by the player.
        self.loadout = []

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

        # The owner of this backpack, who we will be playing gags on.
        self.avatar = avatar

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

    # Adds a gag to the backpack. This shouldn't be called
    # just by the client, the AI should recommend it.
    def addGag(self, gagId, curSupply = 0, maxSupply = 0):
        if not gagId in self.gags.keys():
            gagName = GagGlobals.getGagByID(gagId)
            if not gagName is None:
                gag = self.gagManager.getGagByName(gagName)
                gag.setAvatar(self.avatar)
                self.gags.update({gagId : [gag, curSupply, maxSupply]})

    # Sets the loadout of the backpack.
    # Must receive a list of up to 4 gag ids or
    # an empty list.
    def setLoadout(self, gagIds):
        self.loadout = gagIds

        if self.avatar.doId == base.localAvatar.doId:
            # Let's reset the loadout to show the new one.
            playGame = base.cr.playGame
            if playGame and playGame.getPlace() and playGame.getPlace().fsm.getCurrentState().getName() == 'walk':
                base.localAvatar.disableGags()
                base.localAvatar.enableGags(1)

    # Adds a gag to the loadout.
    def addLoadoutGag(self, gagId):
        if len(self.loadout) < 4 and self.hasGag(gagId) and not gagId in self.loadout:
            self.loadout.append(gagId)
            if self.loadoutGUI:
                self.loadoutGUI.updateLoadout()

    # Removes a gag from the loadout.
    def removeLoadoutGag(self, gagId):
        if len(self.loadout) > 0 and gagId in self.loadout:
            self.loadout.remove(gagId)
            if self.loadoutGUI:
                self.loadoutGUI.updateLoadout()

    # Returns the current loadout of the backpack.
    def getLoadout(self):
        return self.loadout

    def getLoadoutInIds(self):
        ids = []
        for gag in self.loadout:
            ids.append(gag.getID())
        return ids

    # Sets the max supply of a gag.
    # Returns either true or false depending on if the
    # max supply was updated.
    def setMaxSupply(self, gagId, maxSupply):
        if self.hasGag(gagId) and 0 <= maxSupply <= 255:
            values = self.gags.get(gagId)
            gag = values[0]
            supply = values[1]
            self.gags.update({gagId : [gag, supply, maxSupply]})
            if self.loadoutGUI:
                self.loadoutGUI.update()
            return True
        return False

    # Returns the max supply of a gag in the backpack or
    # -1 if the gag isn't in the backpack.
    def getMaxSupply(self, arg = -1):
        if type(arg) == types.IntType and self.hasGag(arg):
            return self.gags.get(arg)[2]
        elif arg != -1:
            for values in self.gags.values():
                if values[0].getName() == arg:
                    return values[2]
        elif arg == -1:
            if self.currentGag > -1:
                return self.gags.get(self.currentGag)[2]
        return -1

    # Sets the supply of a gag.
    # Returns either true or false depending on if the
    # supply was updated.
    def setSupply(self, gagId, supply):
        if self.hasGag(gagId) and 0 <= supply <= 255:
            values = self.gags.get(gagId)
            gag = values[0]
            maxSupply = values[2]
            self.gags.update({gagId : [gag, supply, maxSupply]})
            if self.loadoutGUI:
                self.loadoutGUI.update()
            return True
        return False

    # Returns the supply of a gag in the backpack or
    # -1 if the gag isn't in the backpack.
    def getSupply(self, arg = -1):
        if type(arg) == types.IntType and self.hasGag(arg):
            return self.gags.get(arg)[1]
        elif arg != -1:
            for values in self.gags.values():
                if values[0].getName() == arg:
                    return values[1]
        elif arg == -1:
            if self.currentGag > -1:
                return self.gags.get(self.currentGag)[1]
        return -1

    # Returns a true/false flag if the gag is in the backpack.
    def hasGag(self, gagId):
        return gagId in self.gags.keys()

    # Returns the gag's class by gag id.
    def getGagByID(self, gagId):
        if self.hasGag(gagId):
            return self.gags.get(gagId)[0]
        return None

    # Returns the gag by index.
    def getGagByIndex(self, index):
        return self.gags.get(self.gags.keys()[index])[0]

    # Returns the gags in the backpack.
    def getGags(self):
        return self.gags

    # Cleans up all the variables that are no longer needed.
    def cleanup(self):
        for _, data in self.gags.iteritems():
            gag = data[0]
            gag.delete()
        del self.gags
        del self.loadout
        del self.currentGag
        del self.activeGag
        del self.loadoutGUI
        del self.gagManager
        del self.avatar
