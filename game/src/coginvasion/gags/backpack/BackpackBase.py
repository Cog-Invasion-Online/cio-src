"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file BackpackBase.py
@author Maverick Liberty
@date November 12, 2017

@desc The base class for backpacks on both the AI and the client.

"""

from src.coginvasion.gags import GagGlobals
from src.coginvasion.attack import Attacks

from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator

MAXIMUM_SUPPLY = 255

class BackpackBase:
    """
    Shared base class between AI and Client for a backpack.
    A backpack is a collection of Toon/Player attacks, suited for storing on a database.

    In the new universal attacks system, the backpack does not store the attacks directly,
    but reads and manipulates the `attacks` dictionary on an avatar. It kinds of acts
    as a wrapper layer around the attacks system to maintain compatibility with the old system code.
    """
    
    def __init__(self, avatar):
        # Must pass the avatar this backpack is associated with.
        self.avatar = avatar

        # A list of gags immediately available in the avatar's loadout.
        self.loadout = []
    
    # Adds a gag to the backpack if it already isn't in it.
    # When a max supply isn't specified, the default is located and assigned from GagGlobals.
    # The current supply is assigned to the max supply if both the max supply and current supply is 0.
    # Returns true/false depending on if the gag was successfully added to the backpack or not.
    #
    # TODO: work with new system
    def addGag(self, gagId, curSupply = None, maxSupply = None):
        if isinstance(gagId, str):
            gagId = GagGlobals.getIDByName(gagId)
        # Make sure the gag is actually a registered attack and we
        # don't already have it in our backpack
        if not self.hasGag(gagId) and gagId in base.attackMgr.AttackClasses.keys():
            if maxSupply is None:
                # Sets the max supply if one is not specified.
                maxSupply = GagGlobals.calculateMaxSupply(self.avatar,
                    GagGlobals.getGagByID(gagId),
                GagGlobals.getGagData(gagId))
                
            # Sets the current supply to the max supply if current supply isn't
            # specified.
            if curSupply is None:
                curSupply = maxSupply

            gagData = GagGlobals.getGagData(gagId)

            attackCls = base.attackMgr.getAttackClassByID(gagId)
            if attackCls:
                attack = attackCls()
                attack.setAvatar(self.avatar)
                attack.setMaxAmmo(maxSupply)
                attack.setAmmo(curSupply)
                attack.baseDamage = GagGlobals.calcBaseDamage(self.avatar, GagGlobals.getGagByID(gagId), gagData)
                attack.damageMaxDistance = float(gagData.get('distance', 10))
                attack.load()
                self.avatar.attacks[gagId] = attack
                return True

        return False
        
    def setLoadout(self, gagIds):
        self.loadout = gagIds

    # Sets the max supply of a gag.
    # Returns either true/false depending on if max supply
    # was updated or not.
    def setMaxSupply(self, gagId, maxSupply):
        if isinstance(gagId, str):
            gagId = GagGlobals.getIDByName(gagId)
        if self.hasGag(gagId) and 0 <= maxSupply <= MAXIMUM_SUPPLY:
            attack = self.avatar.attacks.get(gagId)
            attack.setMaxAmmo(maxSupply)
            return True

        return False
    
    # Returns the max supply of a gag in the backpack or
    # -1 if the gag isn't in the backpack.
    def getMaxSupply(self, gagId):
        if isinstance(gagId, str):
            gagId = GagGlobals.getIDByName(gagId)
        if self.hasGag(gagId):
            return self.avatar.attacks[gagId].getMaxAmmo()
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
        if isinstance(gagId, str):
            gagId = GagGlobals.getIDByName(gagId)
        if self.hasGag(gagId) and 0 <= supply <= MAXIMUM_SUPPLY:
            attack = self.avatar.attacks.get(gagId)

            currSupply = attack.getAmmo()
            if supply == currSupply:
                # No change in supply.
                return False

            attack.setAmmo(supply)
            return True

        return False
    
    # Returns the supply of a gag in the backpack by gagId.
    # If gagId is not in the backpack, -1 is returned.
    def getSupply(self, gagId):
        if isinstance(gagId, str):
            gagId = GagGlobals.getIDByName(gagId)
        if self.hasGag(gagId):
            return self.avatar.attacks[gagId].getAmmo()
        return -1
        
    # Returns true or false depending on if the gag
    # is in the backpack.
    def hasGag(self, gagId):
        if isinstance(gagId, str):
            gagId = GagGlobals.getIDByName(gagId)
        return gagId in self.avatar.attacks.keys()
        
    # Converts out backpack to a blob for storing.
    # Returns a blob of bytes.
    def toNetString(self):
        dg = PyDatagram()
        
        for gagId in self.avatar.attacks.keys():
            supply = self.avatar.attacks[gagId].getAmmo()
            
            if supply < 0:
                print "Gag ID {0} is about to cause a cause with supply: {1}".format(str(gagId), str(supply))
                supply = 0
            
            dg.addUint8(gagId)
            dg.addUint8(supply)

        return dg.getMessage()
    
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
        del self.loadout
        del self.avatar
        