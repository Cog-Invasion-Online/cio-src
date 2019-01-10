"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file WeddingCake.py
@author Maverick Liberty
@date July 15, 2015

"""

from src.coginvasion.gags.ThrowGag import ThrowGag
from src.coginvasion.gags import GagGlobals

class WeddingCake(ThrowGag):
        
    name = GagGlobals.WeddingCake
    model = 'phase_5/models/props/wedding_cake.bam'
    hitSfxPath = GagGlobals.WEDDING_SPLAT_SFX
    splatColor = GagGlobals.CAKE_SPLAT_COLOR

    def __init__(self):
        ThrowGag.__init__(self)
        self.setHealth(GagGlobals.WEDDING_HEAL)
        self.setImage('phase_3.5/maps/wedding-cake.png')
