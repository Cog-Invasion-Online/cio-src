"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file FlowerPot.py
@author Maverick Liberty
@date August 13, 2015

"""

from panda3d.core import Point3

from src.coginvasion.gags.LightDropGag import LightDropGag
from src.coginvasion.gags import GagGlobals

class FlowerPot(LightDropGag):
        
    name = GagGlobals.FlowerPot
    model = GagGlobals.getProp('5', 'flowerpot-mod')
    anim = GagGlobals.getProp('5', 'flowerpot-chan')
    hitSfxPath = GagGlobals.POT_DROP_SFX
    missSfxPath = GagGlobals.POT_MISS_SFX
    
    def __init__(self):
        LightDropGag.__init__(self)
        self.setImage('phase_3.5/maps/flowerpot.png')
        self.colliderRadius = 0.75
        self.colliderOfs = Point3(0, 0, -3.5)

    def startDrop(self, entity):
        if self.dropLoc:
            self.dropLoc.setZ(self.dropLoc.getZ() + 3.5)
        LightDropGag.startDrop(self, entity)
