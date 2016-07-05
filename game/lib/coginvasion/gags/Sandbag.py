"""

  Filename: Sandbag.py
  Created by: DecodedLogic (13Aug15)

"""

from lib.coginvasion.gags.LightDropGag import LightDropGag
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.gags import GagGlobals

class Sandbag(LightDropGag):
    
    def __init__(self):
        LightDropGag.__init__(self, 
                CIGlobals.Sandbag, GagGlobals.getProp('5', 'sandbag-mod'), 
                GagGlobals.getProp('5', 'sandbag-chan'), 18, GagGlobals.BAG_DROP_SFX, 
                GagGlobals.BAG_MISS_SFX, rotate90 = False, 
        sphereSize = 2)
        self.setImage('phase_3.5/maps/sandbag.png')