"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedHPBarrelAI.py
@author Maverick Liberty
@date March 27, 2018

It seriously took me 2 years to add in toon-up barrels. SMH

"""

from src.coginvasion.hood import ZoneUtil

from src.coginvasion.globals import CIGlobals
from DistributedRestockBarrelAI import DistributedRestockBarrelAI
from src.coginvasion.hood.playground import TreasureGlobals

class DistributedHPBarrelAI(DistributedRestockBarrelAI):
    
    def __init__(self, air, dispatch):
        DistributedRestockBarrelAI.__init__(self, air, dispatch)
        
        if hasattr(self.dispatch, 'hood'):
            self.hoodId = ZoneUtil.Hood2ZoneId.get(self.dispatch.hood)
        else:
            self.hoodId = ZoneUtil.ToontownCentralId
            
        self.hp = 10
        
    def loadEntityValues(self):
        self.hp = self.getEntityValueInt("healamt")
        
    def announceGenerate(self):
        DistributedRestockBarrelAI.announceGenerate(self)
        self.sendUpdate('setLabel', [self.hoodId])
        
    def delete(self):
        DistributedRestockBarrelAI.delete(self)
        del self.hoodId
        del self.hp
    
    def d_setGrab(self, avId):
        DistributedRestockBarrelAI.d_setGrab(self, avId)
        avatar = self.air.doId2do.get(avId, None)
        
        if avatar is not None:
            healAmt = self.hp
            
            if healAmt == -1:
                # no specific heal amount, use the neighborhood amount
                treasureData = TreasureGlobals.treasureSpawns.get(self.hoodId, None)
                if treasureData is not None:
                    # Buildings can be difficult, let's multiply the heal amount by 2.
                    healAmt = (treasureData[1] * 2)
                    
            if (avatar.health + healAmt > avatar.maxHealth):
                healAmt = avatar.maxHealth - avatar.health
            
            if healAmt > 0:
                # Let's toon up the avatar that wants to grab health and announce it.
                avatar.toonUp(healAmt, announce = 1, sound = 0)
