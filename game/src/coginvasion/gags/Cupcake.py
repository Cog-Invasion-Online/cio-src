"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Cupcake.py
@author Brian Lach
@date July 23, 2015

"""

from src.coginvasion.gags.ThrowGag import ThrowGag
from src.coginvasion.gags import GagGlobals

class Cupcake(ThrowGag):
        
    name                = GagGlobals.Cupcake
    model               = "phase_3.5/models/props/tart.bam"
    hitSfxPath          = GagGlobals.TART_SPLAT_SFX
    splatColor          = GagGlobals.TART_SPLAT_COLOR
    scale               = GagGlobals.CUPCAKE_SCALE

    def __init__(self):
        ThrowGag.__init__(self)
        self.setHealth(GagGlobals.CUPCAKE_HEAL)
        self.setImage('phase_3.5/maps/cupcake.png')
