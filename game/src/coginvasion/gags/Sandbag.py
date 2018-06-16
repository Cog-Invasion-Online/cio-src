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
    
    def __init__(self):
        LightDropGag.__init__(self, 
                GagGlobals.Sandbag, GagGlobals.getProp('5', 'sandbag-mod'), 
                GagGlobals.getProp('5', 'sandbag-chan'), 18, GagGlobals.BAG_DROP_SFX, 
                GagGlobals.BAG_MISS_SFX, rotate90 = False)
        self.setImage('phase_3.5/maps/sandbag.png')
        self.colliderRadius = 0.75
