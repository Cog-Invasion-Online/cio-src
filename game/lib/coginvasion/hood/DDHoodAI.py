# Filename: DDHoodAI.py
# Created by:  blach (26Jul15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from ToonHoodAI import ToonHoodAI
import DistributedBoatAI
from lib.coginvasion.globals import CIGlobals

class DDHoodAI(ToonHoodAI):
    notify = directNotify.newCategory('DDHoodAI')

    def __init__(self, air):
        ToonHoodAI.__init__(self, air, CIGlobals.DonaldsDockId, CIGlobals.DonaldsDock)
        self.boat = None
        self.startup()

    def startup(self):
        self.dnaFiles = ['phase_6/dna/donalds_dock_1100.pdna', 'phase_6/dna/donalds_dock_1200.pdna',
            'phase_6/dna/donalds_dock_1300.pdna', 'phase_6/dna/donalds_dock_sz.pdna']
        ToonHoodAI.startup(self)
        self.notify.info("Making Donald's Dock boat...")
        self.boat = DistributedBoatAI.DistributedBoatAI(self.air)
        self.boat.generateWithRequired(self.zoneId)

    def shutdown(self):
        self.notify.info("Shutting down donald's dock")
        if self.boat:
            self.boat.requestDelete()
            self.boat = None
        ToonHoodAI.shutdown(self)
