"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file CreamPieSlice.py
@author Maverick Liberty
@date July 07, 2015

"""

from src.coginvasion.gags.ThrowGag import ThrowGag
from src.coginvasion.gags import GagGlobals
from src.coginvasion.globals import CIGlobals

class CreamPieSlice(ThrowGag):

    def __init__(self):
        ThrowGag.__init__(self, CIGlobals.CreamPieSlice, "phase_5/models/props/cream-pie-slice.bam", 17, GagGlobals.SLICE_SPLAT_SFX, GagGlobals.CREAM_SPLAT_COLOR)
        self.setHealth(GagGlobals.CREAM_PIE_SLICE_HEAL)
        self.setImage('phase_3.5/maps/cream_pie_slice.png')
