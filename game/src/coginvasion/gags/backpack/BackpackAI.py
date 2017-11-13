"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file BackpackAI.py
@author Maverick Liberty
@date March 20, 2016

@desc The AI version of the backpack.

"""

from src.coginvasion.gags.backpack.BackpackBase import BackpackBase

class BackpackAI(BackpackBase):
    
    def __init__(self, avatar):
        BackpackBase.__init__(self, avatar)
    
    # Sets the supply of a gag in the backpack.
    # Returns true or false if the supply was set.
    def setSupply(self, gagId, supply):
        updatedSupply = BackpackBase.setSupply(self, gagId, supply)
        if updatedSupply:
            self.updateNetAmmo()
        return updatedSupply
    
    # Update the network ammo.
    def updateNetAmmo(self):
        self.avatar.b_setBackpackAmmo(self.toNetString())
    
    # Cleans up the backpack.
    def cleanup(self):
        self.updateNetAmmo()
        BackpackBase.cleanup(self)
