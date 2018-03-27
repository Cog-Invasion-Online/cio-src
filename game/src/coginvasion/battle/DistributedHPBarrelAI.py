"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedHPBarrelAI.py
@author Maverick Liberty
@date March 27, 2018

It seriously took me 2 years to add in toon-up barrels. SMH

"""

from DistributedRestockBarrelAI import DistributedRestockBarrelAI
from src.coginvasion.hood.playground import TreasureGlobals

class DistributedHPBarrelAI(DistributedRestockBarrelAI):
    
    def __init__(self, hoodId, air):
        DistributedRestockBarrelAI.__init__(self, air)
        self.hoodId = hoodId
        
    def announceGenerate(self):
        DistributedRestockBarrelAI.announceGenerate(self)
        self.sendUpdate('setLabel', [self.hoodId])
        
    def delete(self):
        DistributedRestockBarrelAI.delete(self)
        del self.hoodId
    
    def d_setGrab(self, avId):
        DistributedRestockBarrelAI.d_setGrab(self, avId)
        avatar = self.air.doId2do.get(avId, None)
        treasureData = TreasureGlobals.treasureSpawns.get(self.hoodId, None)
        
        if not avatar is None:
            healAmt = 3
            
            if not treasureData is None:
                # Buildings can be difficult, let's multiply the heal amount by 2.
                healAmt = (treasureData[1] * 2)
                
            if (avatar.health + healAmt > avatar.maxHealth):
                healAmt = avatar.maxHealth - avatar.health
            
            avatar.toonUp(healAmt, announce = 1, sound = 1)
