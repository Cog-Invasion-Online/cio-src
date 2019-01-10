"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file WholeCreamPie.py
@author Maverick Liberty
@date July 07, 2015

"""

from src.coginvasion.gags.ThrowGag import ThrowGag
from src.coginvasion.gags import GagGlobals

class WholeCreamPie(ThrowGag):
        
    name = GagGlobals.WholeCreamPie
    model = "phase_14/models/props/creampie.bam"
    hitSfxPath = GagGlobals.WHOLE_PIE_SPLAT_SFX
    splatColor = GagGlobals.CREAM_SPLAT_COLOR

    def __init__(self):
        ThrowGag.__init__(self)
        self.setHealth(GagGlobals.CREAM_PIE_HEAL)
        self.setImage('phase_3.5/maps/tart.png')
