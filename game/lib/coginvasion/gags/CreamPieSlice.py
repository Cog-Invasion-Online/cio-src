########################################
# Filename: CreamPieSlice.py
# Created by: DecodedLogic (07Jul15)
########################################

from lib.coginvasion.gags.ThrowGag import ThrowGag
from lib.coginvasion.gags import GagGlobals
from lib.coginvasion.globals import CIGlobals

class CreamPieSlice(ThrowGag):

    def __init__(self):
        ThrowGag.__init__(self, CIGlobals.CreamPieSlice, "phase_5/models/props/cream-pie-slice.bam", 17, GagGlobals.SLICE_SPLAT_SFX, GagGlobals.CREAM_SPLAT_COLOR)
        self.setHealth(GagGlobals.CREAM_PIE_SLICE_HEAL)
        self.setImage('phase_3.5/maps/cream_pie_slice.png')
