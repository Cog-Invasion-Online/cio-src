"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Sandbag.py
@author Maverick Liberty
@date August 13, 2015

"""

from src.coginvasion.gags.LightDropGag import LightDropGag
from src.coginvasion.gags import GagGlobals

class Sandbag(LightDropGag):
        
    name = GagGlobals.Sandbag
    model = GagGlobals.getProp('5', 'sandbag-mod')
    anim = GagGlobals.getProp('5', 'sandbag-chan')
    hitSfxPath = GagGlobals.BAG_DROP_SFX
    missSfxPath = GagGlobals.BAG_MISS_SFX
    
    def __init__(self):
        LightDropGag.__init__(self)
        self.setImage('phase_3.5/maps/sandbag.png')
        self.colliderRadius = 0.75
