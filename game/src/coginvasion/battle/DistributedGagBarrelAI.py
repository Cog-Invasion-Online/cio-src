"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedGagBarrelAI.py
@author Maverick Liberty
@date March 12, 2016

"""

from DistributedRestockBarrelAI import DistributedRestockBarrelAI
from src.coginvasion.gags import GagGlobals, GagType

import random

class DistributedGagBarrelAI(DistributedRestockBarrelAI):
    
    def __init__(self, air, dispatch):
        DistributedRestockBarrelAI.__init__(self, air, dispatch)
        self.track = -1
        self.gagId = -1
        self.maxRestock = 20
        
    def loadEntityValues(self):
        self.track = self.getEntityValueInt("track")
        if self.track == -1:
            # random track
            self.track = random.choice(GagGlobals.TrackIdByName.values())

        trackName = GagGlobals.getTrackName(self.track)
            
        self.gagId = self.getEntityValueInt("gag")
        if self.gagId != -1:
            self.gagId = GagGlobals.gagIdByName[GagGlobals.TrackGagNamesByTrackName[trackName][self.gagId]]
        
    def announceGenerate(self):
        DistributedRestockBarrelAI.announceGenerate(self)
        self.sendUpdate('setLabel', [self.gagId + 2])
        
    def delete(self):
        DistributedRestockBarrelAI.delete(self)
        del self.gagId
        del self.maxRestock
        del self.track
        
    def d_setGrab(self, avId):
        DistributedRestockBarrelAI.d_setGrab(self, avId)
        avatar = self.air.doId2do.get(avId)
        backpack = avatar.backpack
        trackName = GagGlobals.getTrackName(self.track)
        availableGags = []
        restockGags = {}
        
        trackGags = GagGlobals.TrackGagNamesByTrackName.get(trackName)
        if self.gagId == -1:
            # Gets the gag ids of gags in this gag track.
            for trackGag in trackGags:
                gagId = GagGlobals.getIDByName(trackGag)
                if backpack.hasGag(gagId):
                    availableGags.append(gagId)
            # The strongest gags should be first.
            availableGags.reverse()
        else:
            # this barrel restocks a specific gag
            if backpack.hasGag(self.gagId):
                availableGags.append(self.gagId)
        
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
                self.notify.info('Requesting to give %s %ss.' % (str(giveAmount), GagGlobals.getGagByID(gagId)))
                
        for gagId in restockGags.keys():
            avatar.b_setGagAmmo(gagId, restockGags.get(gagId))
            