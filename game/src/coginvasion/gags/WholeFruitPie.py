"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file WholeFruitPie.py
@author Maverick Liberty
@date July 15, 2015

"""

from src.coginvasion.gags.ThrowGag import ThrowGag
from src.coginvasion.gags import GagGlobals

class WholeFruitPie(ThrowGag):
    
    name = GagGlobals.WholeFruitPie
    model = "phase_3.5/models/props/tart.bam"
    hitSfxPath = GagGlobals.WHOLE_PIE_SPLAT_SFX
    splatColor = GagGlobals.TART_SPLAT_COLOR
    scale = 0.75

    def __init__(self):
        ThrowGag.__init__(self)
        self.setHealth(GagGlobals.FRUIT_PIE_HEAL)
        self.setImage('phase_3.5/maps/fruit-pie.png')
