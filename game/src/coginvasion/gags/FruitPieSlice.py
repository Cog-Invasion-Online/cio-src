"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file FruitPieSlice.py
@author Maverick Liberty
@date July 15, 2015

"""

from src.coginvasion.gags.ThrowGag import ThrowGag
from src.coginvasion.gags import GagGlobals

class FruitPieSlice(ThrowGag):

    def __init__(self):
        ThrowGag.__init__(self, GagGlobals.FruitPieSlice, 'phase_5/models/props/fruit-pie-slice.bam',
                          10, GagGlobals.SLICE_SPLAT_SFX, GagGlobals.TART_SPLAT_COLOR)
        self.setHealth(GagGlobals.FRUIT_PIE_SLICE_HEAL)
        self.setImage('phase_3.5/maps/fruit_pie_slice.png')
