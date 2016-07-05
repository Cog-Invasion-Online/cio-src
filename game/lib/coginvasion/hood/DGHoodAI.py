# Filename: DGHoodAI.py
# Created by:  blach (24Jul15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from ToonHoodAI import ToonHoodAI
from lib.coginvasion.globals import CIGlobals

class DGHoodAI(ToonHoodAI):
    notify = directNotify.newCategory('DGHoodAI')

    def __init__(self, air):
        ToonHoodAI.__init__(self, air, CIGlobals.DaisyGardensId, CIGlobals.DaisyGardens)
        self.startup()

    def startup(self):
        self.dnaFiles = []
        self.dnaFiles = ['phase_8/dna/daisys_garden_5100.pdna', #'phase_8/dna/daisys_garden_5200.dna',
            'phase_8/dna/daisys_garden_5300.pdna', 'phase_8/dna/daisys_garden_sz.pdna']
        ToonHoodAI.startup(self)
