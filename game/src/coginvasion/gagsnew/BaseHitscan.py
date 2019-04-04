"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file BaseHitscan.py
@author CheezedFish
@date March 9, 2019

@desc Base Hitscan class, to be used for all other Hitscans

"""
from BaseGag import BaseGag
from BaseHitscanShared import BaseHitscanShared

from src.coginvasion.gui.Crosshair import CrosshairData
from src.coginvasion.globals import CIGlobals
from src.coginvasion.attack.Attacks import ATTACK_HOLD_NONE, ATTACK_NONE
    
class BaseHitscan(BaseGag, BaseHitscanShared):
    Name = 'BASE HITSCAN: DO NOT USE'
    ID = ATTACK_NONE
    Hold = ATTACK_HOLD_NONE
    
    def __init__(self):
        BaseGag.__init__(self)

        self.crosshair = CrosshairData(crosshairScale = 0.6, crosshairRot = 45)
            
    def addPrimaryPressData(self, dg):
        CIGlobals.putVec3(dg, camera.getPos(render))
        CIGlobals.putVec3(dg, camera.getQuat(render).getForward())
