########################################
# Filename: BackpackAI.py
# Created by: DecodedLogic (20Mar16)
########################################
# The server version of the backpack.
from src.coginvasion.gags import GagGlobals

from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

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
    
    # Converts out backpack to a blob for storing.
    # Returns a blob of bytes.
    def toNetString(self):
        dg = PyDatagram()
        for gagId in self.gags.keys():
            supply = self.gags[gagId][0]
            dg.addUint8(gagId)
            dg.addUint8(supply)
        dgi = PyDatagramIterator(dg)
        return dgi.getRemainingBytes()
    
    # Converts a net string blob back to data that we can handle.
    # Returns a dictionary of {gagIds : supply}
    def fromNetString(self, netString):
        dg = PyDatagram(netString)
        dgi = PyDatagramIterator(dg)
        dictionary = {}
        
        while dgi.getRemainingSize() > 0:
            gagId = dgi.getUint8()
            supply = dgi.getUint8()
            dictionary[gagId] = supply
        return dictionary
    
    # Update the network ammo.
    def updateNetAmmo(self):
        self.owner.b_setBackpackAmmo(self.toNetString())
    
    # Cleans up the backpack.
    def cleanup(self):
        self.updateNetAmmo()
        self.gags.clear()
        del self.gags
        self.owner = None
        del self.owner
