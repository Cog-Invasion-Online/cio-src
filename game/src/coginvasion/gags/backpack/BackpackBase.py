"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file BackpackBase.py
@author Maverick Liberty
@date November 12, 2017

@desc The base class for backpacks on both the AI and the client.

"""

from src.coginvasion.gags import GagGlobals

from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

MAXIMUM_SUPPLY = 255

class BackpackBase:
    
    def __init__(self, avatar):
        # Must pass the avatar this backpack is associated with.
        self.avatar = avatar
        
        # A dictionary used to store gag data.
        # Data is stored differently depending on the game process.
        # Clients store data like: {gagId: [gag class instance, current supply, max supply]}
        # AIs store data like this: {gagId: [current supply, max supply]}
        # This is because the gag class instance would be redundant to point to on the AI.
        self.gags = {}
        
        # A list of gags immediately available in the avatar's loadout.
        self.loadout = []
    
    # Adds a gag to the backpack if it already isn't in it.
    # When a max supply isn't specified, the default is located and assigned from GagGlobals.
    # The current supply is assigned to the max supply if both the max supply and current supply is 0.
    # Returns true/false depending on if the gag was successfully added to the backpack or not.
    def addGag(self, gagId, curSupply = None, maxSupply = None):
        if not self.hasGag(gagId):
            if maxSupply is None:
                # Sets the max supply if one is not specified.
                maxSupply = GagGlobals.calculateMaxSupply(self.avatar,
                    GagGlobals.gagIds.get(gagId), 
                GagGlobals.getGagData(gagId))
                
            # Sets the current supply to the max supply if current supply isn't
            # specified.
            if curSupply is None:
                curSupply = maxSupply
            
            if game.process == 'server':
                self.gags.update({gagId: [curSupply, maxSupply]})
                return True
            elif hasattr(self, 'gagManager'):
                # This code will only occur on the client.
                gagName = GagGlobals.getGagByID(gagId)
                
                if gagName:
                    # We must create a new gag class instance for the client.
                    gagClass = self.gagManager.getGagByName(gagName)
                    gagClass.setAvatar(self.avatar)
                    self.gags.update({gagId : [gagClass, curSupply, maxSupply]})
                    return True
        return False
        
    def setLoadout(self, gagIds):
        self.loadout = gagIds

    # Sets the max supply of a gag.
    # Returns either true/false depending on if max supply
    # was updated or not.
    def setMaxSupply(self, gagId, maxSupply):
        if self.hasGag(gagId) and 0 <= maxSupply <= MAXIMUM_SUPPLY:
            values = self.gags.get(gagId)
            supply = -1
            
            if game.process == 'server':
                supply = values[0]
                self.gags.update({gagId : [supply, maxSupply]})
            else:
                gagInstance = values[0]
                supply = values[1]
                self.gags.update({gagId : [gagInstance, supply, maxSupply]})
            return True
        return False
    
    # Returns the max supply of a gag in the backpack or
    # -1 if the gag isn't in the backpack.
    def getMaxSupply(self, gagId):
        if self.hasGag(gagId):
            if game.process == 'server':
                return self.gags.get(gagId)[1]
            else:
                return self.gags.get(gagId)[2]
        return -1
    
    # Returns the default max supply of a gag.
    def getDefaultMaxSupply(self, gagId):
        data = GagGlobals.getGagData(gagId)
        
        if 'minMaxSupply' in data.keys():
            return data.get('minMaxSupply')
        else:
            return data.get('maxSupply')

    # Sets the supply of a gag.
    # Returns either true or false depending on if the
    # supply was updated.
    def setSupply(self, gagId, supply):
        if self.hasGag(gagId) and 0 <= supply <= MAXIMUM_SUPPLY:
            values = self.gags.get(gagId)
            maxSupply = -1
            
            # If we're updating the supply of a gag on the AI,
            # we need to do this a little bit differently.
            if game.process == 'server':
                currSupply = values[0]
                if currSupply == supply:
                    # No change in supply.
                    return False
                maxSupply = values[1]
                self.gags.update({gagId : [supply, maxSupply]})
            else:
                currSupply = values[1]
                if currSupply == supply:
                    # No change in supply.
                    return False
                gagInstance = values[0]
                maxSupply = values[2]
                self.gags.update({gagId : [gagInstance, supply, maxSupply]})
            return True
        return False
    
    # Returns the supply of a gag in the backpack by gagId.
    # If gagId is not in the backpack, -1 is returned.
    def getSupply(self, gagId):
        if self.hasGag(gagId):
            if game.process == 'server':
                return self.gags.get(gagId)[0]
            else:
                return self.gags.get(gagId)[1]
        return -1
        
    # Returns true or false depending on if the gag
    # is in the backpack.
    def hasGag(self, gagId):
        return gagId in self.gags.keys()
        
    # Converts out backpack to a blob for storing.
    # Returns a blob of bytes.
    def toNetString(self):
        dg = PyDatagram()
        supplyIndex = 1
        
        # On the server side, the supply of the current gag is first
        # in the list of data assigned to each gagId.
        if game.process == 'server':
            supplyIndex = 0
        
        for gagId in self.gags.keys():
            supply = self.gags[gagId][supplyIndex]
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
        
    def cleanup(self):
        self.gags.clear()
        self.loadout = []
        self.avatar = None
        del self.gags
        del self.loadout
        del self.avatar
        