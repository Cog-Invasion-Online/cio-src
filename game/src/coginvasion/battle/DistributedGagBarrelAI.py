"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedGagBarrelAI.py
@author Maverick Liberty
@date March 12, 2016

"""

from DistributedRestockBarrelAI import DistributedRestockBarrelAI
from src.coginvasion.gags import GagGlobals

class DistributedGagBarrelAI(DistributedRestockBarrelAI):
    
    def __init__(self, gagId, air, loadoutOnly = False):
        DistributedRestockBarrelAI.__init__(self, air)
        self.gagId = gagId
        self.maxRestock = 20
        self.loadoutOnly = loadoutOnly
        
    def announceGenerate(self):
        DistributedRestockBarrelAI.announceGenerate(self)
        self.sendUpdate('setLabel', [self.gagId + 2])
        
    def delete(self):
        DistributedRestockBarrelAI.delete(self)
        del self.gagId
        del self.maxRestock
        del self.loadoutOnly
        
    def d_setGrab(self, avId):
        self.sendUpdate('setGrab', [avId])
        avatar = self.air.doId2do.get(avId)
        backpack = avatar.backpack
        track = GagGlobals.getTrackOfGag(self.gagId)
        availableGags = []
        restockGags = {}
        
        if not self.loadoutOnly:
            trackGags = GagGlobals.TrackGagNamesByTrackName.get(GagGlobals.TrackNameById.get(GagGlobals.Type2TrackName.get(track)))
            
            # Get the gagids of gags in this gag track.
            for trackGag in trackGags:
                gagId = GagGlobals.getIDByName(trackGag)
                if backpack.hasGag(gagId):
                    availableGags.append(gagId)
            # The strongest gags should be first.
            availableGags.reverse()
        else:
            loadout = backpack.getLoadout()
            for gagId in loadout:
                if GagGlobals.getTrackOfGag(gagId) == track:
                    availableGags.append(gagId)
        
        restockLeft = int(self.maxRestock)
        
        for gagId in availableGags:
            if restockLeft <= 0:
                break
            supply = backpack.getSupply(gagId)
            maxAmount = backpack.getMaxSupply(gagId)
            
            if supply < maxAmount:
                giveAmount = maxAmount - backpack.getSupply(gagId)
                if restockLeft < giveAmount:
                    giveAmount = restockLeft
                restockGags[gagId] = supply + giveAmount
                restockLeft -= giveAmount
                print 'Requesting to give %s %ss.' % (str(restockGags[gagId]), GagGlobals.getGagByID(gagId))
                
        for gagId in restockGags.keys():
            avatar.b_setGagAmmo(gagId, restockGags.get(gagId))
            