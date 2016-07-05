"""

  Filename: WholeFruitPie.py
  Created by: DecodedLogic (15Jul15)

"""

from lib.coginvasion.gags.ThrowGag import ThrowGag
from lib.coginvasion.gags import GagGlobals
from lib.coginvasion.globals import CIGlobals

class WholeFruitPie(ThrowGag):

    def __init__(self):
        ThrowGag.__init__(self, CIGlobals.WholeFruitPie, "phase_3.5/models/props/tart.bam", 28, 
            GagGlobals.WHOLE_PIE_SPLAT_SFX, GagGlobals.TART_SPLAT_COLOR, scale=0.75)
        self.setHealth(GagGlobals.FRUIT_PIE_HEAL)
        self.setImage('phase_3.5/maps/fruit-pie.png')
