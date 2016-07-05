# Filename: MLHoodAI.py
# Created by:  blach (24Jul15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from ToonHoodAI import ToonHoodAI
from lib.coginvasion.globals import CIGlobals

class MLHoodAI(ToonHoodAI):
    notify = directNotify.newCategory('MLHoodAI')

    def __init__(self, air):
        ToonHoodAI.__init__(self, air, CIGlobals.MinniesMelodylandId, CIGlobals.MinniesMelodyland)
        self.startup()

    def startup(self):
        self.dnaFiles = ['phase_6/dna/minnies_melody_land_4100.pdna', 'phase_6/dna/minnies_melody_land_4200.pdna',
            'phase_6/dna/minnies_melody_land_4300.pdna', 'phase_6/dna/minnies_melody_land_sz.pdna']
        ToonHoodAI.startup(self)
