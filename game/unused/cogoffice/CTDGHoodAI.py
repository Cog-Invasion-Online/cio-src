# Filename: CTDGHoodAI.py
# Created by:  blach (12Dec15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from CTHoodAI import CTHoodAI
from lib.coginvasion.globals import CIGlobals

class CTDGHoodAI(CTHoodAI):
    notify = directNotify.newCategory('DGHoodAI')

    def __init__(self, air):
        self.dnaFiles = ['phase_8/dna/daisys_garden_5100.pdna', #'phase_8/dna/daisys_garden_5200.dna',
            'phase_8/dna/daisys_garden_5300.pdna']
        CTHoodAI.__init__(self, air, CIGlobals.World2Hood2ZoneId[CIGlobals.CogTropolis][CIGlobals.DaisyGardens], CIGlobals.DaisyGardens)
