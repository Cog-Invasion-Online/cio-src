"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file WeddingCake.py
@author Maverick Liberty
@date July 15, 2015

"""

from src.coginvasion.gags.ThrowGag import ThrowGag
from src.coginvasion.gags import GagGlobals
from src.coginvasion.globals import CIGlobals

class WeddingCake(ThrowGag):

    def __init__(self):
        ThrowGag.__init__(self, CIGlobals.WeddingCake, 'phase_5/models/props/wedding_cake.bam',
                          120, GagGlobals.WEDDING_SPLAT_SFX, GagGlobals.CAKE_SPLAT_COLOR)
        self.setHealth(GagGlobals.WEDDING_HEAL)
        self.setImage('phase_3.5/maps/wedding-cake.png')
