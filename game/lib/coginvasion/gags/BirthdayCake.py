########################################
# Filename: BirthdayCake.py
# Created by: DecodedLogic (07Jul15)
########################################

from lib.coginvasion.gags.ThrowGag import ThrowGag
from lib.coginvasion.gags import GagGlobals
from lib.coginvasion.globals import CIGlobals

class BirthdayCake(ThrowGag):

    def __init__(self):
        ThrowGag.__init__(self, CIGlobals.BirthdayCake, "phase_5/models/props/birthday-cake-mod.bam", 75, GagGlobals.WHOLE_PIE_SPLAT_SFX, GagGlobals.CAKE_SPLAT_COLOR, anim = "phase_5/models/props/birthday-cake-chan.bam")
        self.setHealth(GagGlobals.BDCAKE_HEAL)
        self.setImage('phase_3.5/maps/cake.png')
