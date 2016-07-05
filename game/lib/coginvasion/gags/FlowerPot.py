########################################
# Filename: FlowerPot.py
# Created by: DecodedLogic (13Aug15)
########################################

from lib.coginvasion.gags.LightDropGag import LightDropGag
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.gags import GagGlobals

class FlowerPot(LightDropGag):
    
    def __init__(self):
        LightDropGag.__init__(self, 
                CIGlobals.FlowerPot, GagGlobals.getProp('5', 'flowerpot-mod'), 
                GagGlobals.getProp('5', 'flowerpot-chan'), 10, GagGlobals.POT_DROP_SFX, 
                GagGlobals.POT_MISS_SFX, rotate90 = False, 
        sphereSize = 2, sphereZ = -3.5)
        self.setImage('phase_3.5/maps/flowerpot.png')