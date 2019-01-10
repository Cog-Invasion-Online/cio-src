"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Anvil.py
@author Maverick Liberty
@date August 13, 2015

"""

from src.coginvasion.gags.LightDropGag import LightDropGag
from src.coginvasion.gags import GagGlobals

class Anvil(LightDropGag):
        
    name = GagGlobals.Anvil
    model = GagGlobals.getProp('4', 'anvil-mod')
    anim = GagGlobals.getProp('4', 'anvil-chan')
    hitSfxPath = GagGlobals.ANVIL_DROP_SFX
    missSfxPath = GagGlobals.ANVIL_MISS_SFX
    rotate90 = True
    
    def __init__(self):
        LightDropGag.__init__(self)
        self.setImage('phase_3.5/maps/anvil.png')
        self.colliderRadius = 0.75
