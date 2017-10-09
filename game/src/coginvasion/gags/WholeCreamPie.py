"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file WholeCreamPie.py
@author Maverick Liberty
@date July 07, 2015

"""

from src.coginvasion.gags.ThrowGag import ThrowGag
from src.coginvasion.gags import GagGlobals
from src.coginvasion.globals import CIGlobals

class WholeCreamPie(ThrowGag):

    def __init__(self):
        ThrowGag.__init__(self, CIGlobals.WholeCreamPie, "phase_3.5/models/props/tart.bam", 36, GagGlobals.WHOLE_PIE_SPLAT_SFX, GagGlobals.CREAM_SPLAT_COLOR)
        self.setHealth(GagGlobals.CREAM_PIE_HEAL)
        self.setImage('phase_3.5/maps/tart.png')
