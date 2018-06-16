"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file TTHoodAI.py
@author Brian Lach
@date December 20, 2014

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

import ToonHoodAI
import ZoneUtil

class TTHoodAI(ToonHoodAI.ToonHoodAI):
    notify = directNotify.newCategory("TTHoodAI")
    notify.setInfo(True)

    def __init__(self, air):
        ToonHoodAI.ToonHoodAI.__init__(self, air, ZoneUtil.ToontownCentralId,
                    ZoneUtil.ToontownCentral)
        self.startup()

    def startup(self):
        self.notify.info("Creating hood %s" % ZoneUtil.ToontownCentral)
        self.dnaFiles = ['phase_5/dna/toontown_central_2100.pdna', 'phase_5/dna/toontown_central_2200.pdna',
            'phase_5/dna/toontown_central_2300.pdna', 'phase_4/dna/new_ttc_sz.pdna']
        ToonHoodAI.ToonHoodAI.startup(self)
        self.notify.info("Finished creating hood %s" % ZoneUtil.ToontownCentral)

    def shutdown(self):
        self.notify.info("Shutting down hood %s" % ZoneUtil.ToontownCentral)
        ToonHoodAI.ToonHoodAI.shutdown(self)
        self.notify.info("Finished shutting down hood %s" % ZoneUtil.ToontownCentral)
