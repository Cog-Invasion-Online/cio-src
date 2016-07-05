# Filename: DLHoodAI.py
# Created by:  blach (24Jul15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from ToonHoodAI import ToonHoodAI
from lib.coginvasion.globals import CIGlobals

class DLHoodAI(ToonHoodAI):
    notify = directNotify.newCategory('DLHoodAI')

    def __init__(self, air):
        ToonHoodAI.__init__(self, air, CIGlobals.DonaldsDreamlandId, CIGlobals.DonaldsDreamland)
        self.startup()

    def startup(self):
        self.dnaFiles = ['phase_8/dna/donalds_dreamland_9100.pdna', 'phase_8/dna/donalds_dreamland_9200.pdna',
            'phase_8/dna/donalds_dreamland_sz.pdna']
        ToonHoodAI.startup(self)
