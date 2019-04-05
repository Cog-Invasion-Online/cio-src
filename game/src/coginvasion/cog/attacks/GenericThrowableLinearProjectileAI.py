"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file GenericThrowableLinearProjectileAI.py
@author Maverick Liberty
@date April 5, 2019

Repeating code over and over sucks, I've created this class for all those boring, generic throw attacks Cogs have.
This will make our lives easier and our workspace cleaner.

"""

from src.coginvasion.attack.LinearProjectileAI import LinearProjectileAI
from src.coginvasion.globals import CIGlobals
from src.coginvasion.phys.WorldCollider import WorldCollider

class GenericThrowableLinearProjectileAI(LinearProjectileAI):

    def __init__(self, air):
        LinearProjectileAI.__init__(self, air)
        self.attackID = -1
    
    def doInitCollider(self):
        WorldCollider.__init__(self, "throwableCollider", 1.0, needSelfInArgs = True,
                          useSweep = True, resultInArgs = True, startNow = False,
                          mask = CIGlobals.WorldGroup | CIGlobals.CharacterGroup)
        self.world = self.air.getPhysicsWorld(self.zoneId)
    
    def setData(self, attackID):
        self.attackID = attackID
        
    def getData(self):
        return self.attackID
        
    def d_setData(self, attackID):
        self.sendUpdate('setData', [attackID])
        
    def b_setData(self, attackID):
        self.attackID = attackID
