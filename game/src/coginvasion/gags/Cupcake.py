# Filename: Cupcake.py
# Created by:  blach (23Jul15)

from src.coginvasion.gags.ThrowGag import ThrowGag
from src.coginvasion.gags import GagGlobals
from src.coginvasion.globals import CIGlobals

class Cupcake(ThrowGag):

    def __init__(self):
        ThrowGag.__init__(self, CIGlobals.Cupcake, "phase_3.5/models/props/tart.bam", 6, GagGlobals.TART_SPLAT_SFX, GagGlobals.TART_SPLAT_COLOR, scale = GagGlobals.CUPCAKE_SCALE)
        self.setHealth(GagGlobals.CUPCAKE_HEAL)
        self.setImage('phase_3.5/maps/cupcake.png')
