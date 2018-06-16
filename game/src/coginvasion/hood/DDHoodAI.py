"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DDHoodAI.py
@author Brian Lach
@date July 26, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

from ToonHoodAI import ToonHoodAI
from playground import DistributedBoatAI
import ZoneUtil

class DDHoodAI(ToonHoodAI):
    notify = directNotify.newCategory('DDHoodAI')

    def __init__(self, air):
        ToonHoodAI.__init__(self, air, ZoneUtil.DonaldsDockId, ZoneUtil.DonaldsDock)
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
        self.notify.info("Shutting down Donald's Dock")
        if self.boat:
            self.boat.requestDelete()
            self.boat = None
        ToonHoodAI.shutdown(self)
