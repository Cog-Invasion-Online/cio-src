########################################
# Filename: BackpackAI.py
# Created by: DecodedLogic (20Mar16)
########################################
# The server version of the backpack.
from src.coginvasion.gags import GagGlobals

class BackpackAI:
    
    def __init__(self, owner):
        # A dictionary used to store the current supply and
        # max supply of gags. It is setup like this:
        # gagId : [current supply, max supply]
        self.gags = {}
        
        # The list of the current loadout
        self.loadout = []
        
        # The owner of this backpack, used to send updates.
        self.owner = owner
        
    # Adds a gag to the backpack.
    # If you don't set a current supply or max supply,
    # it will look up the defaults and use those.
    def addGag(self, gagId, curSupply = 0, maxSupply = 0):
        if not self.hasGag(gagId):
            if maxSupply == 0:
                maxSupply = GagGlobals.getGagData(gagId).get('maxSupply')
                curSupply = maxSupply
            self.gags.update({gagId : [curSupply, maxSupply]})
            
    # Sets the maximum supply of a gag in the backpack.
    # Returns true or false if the maximum supply was set.
    def setMaxSupply(self, gagId, maxSupply):
        if self.hasGag(gagId) and 0 <= maxSupply <= 255:
            values = self.gags.get(gagId)
            supply = values[0]
            self.gags.update({gagId : [supply, maxSupply]})
            return True
        return False
    
    # Returns the max supply of a gag in the backpack or
    # -1 if the gag isn't in the backpack.
    def getMaxSupply(self, gagId):
        if self.hasGag(gagId):
            return self.gags.get(gagId)[1]
        return -1
    
    # Sets the supply of a gag in the backpack.
    # Returns true or false if the supply was set.
    def setSupply(self, gagId, supply):
        if self.hasGag(gagId) and 0 <= supply <= 255:
            values = self.gags.get(gagId)
            maxSupply = values[1]
            self.gags.update({gagId : [supply, maxSupply]})
            self.updateNetAmmo()
            return True
        return False
    
    # Returns the supply of a gag in the backpack or
    # -1 if the gag isn't in the backpack.
    def getSupply(self, gagId):
        if self.hasGag(gagId):
            return self.gags.get(gagId)[0]
        return -1
    
    # Returns true or false depending on if the gag
    # is in the backpack.
    def hasGag(self, gagId):
        return gagId in self.gags.keys()
    
    # Returns the gags dictionary.
    def getGags(self):
        return self.gags
    
    # Sets the current loadout.
    def setLoadout(self, gagIds):
        self.loadout = gagIds
    
    # Returns the current loadout.
    def getLoadout(self):
        return self.loadout
    
    # Update the network ammo.
    def updateNetAmmo(self):
        gagIds = self.gags.keys()
        ammo = []
        for i in xrange(len(gagIds)):
            gagId = gagIds[i]
            ammo.append(self.gags.get(gagId)[0])
        self.owner.b_setBackpackAmmo(gagIds, ammo)
    
    # Cleans up the backpack.
    def cleanup(self):
        self.updateNetAmmo()
        self.gags.clear()
        del self.gags
        self.owner = None
        del self.owner
