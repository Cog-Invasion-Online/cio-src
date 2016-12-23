########################################
# Filename: Anvil.py
# Created by: DecodedLogic (13Aug15)
########################################

from src.coginvasion.gags.LightDropGag import LightDropGag
from src.coginvasion.globals import CIGlobals
from src.coginvasion.gags import GagGlobals

class Anvil(LightDropGag):
    
    def __init__(self):
        LightDropGag.__init__(self, 
                CIGlobals.Anvil, GagGlobals.getProp('4', 'anvil-mod'), 
                GagGlobals.getProp('4', 'anvil-chan'), 30, GagGlobals.ANVIL_DROP_SFX, 
                GagGlobals.ANVIL_MISS_SFX, rotate90 = True, 
        sphereSize = 2)
        self.setImage('phase_3.5/maps/anvil.png')