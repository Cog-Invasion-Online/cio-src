"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file MLHoodAI.py
@author Brian Lach
@date July 24, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

from ToonHoodAI import ToonHoodAI
import ZoneUtil

class MLHoodAI(ToonHoodAI):
    notify = directNotify.newCategory('MLHoodAI')

    def __init__(self, air):
        ToonHoodAI.__init__(self, air, ZoneUtil.MinniesMelodylandId, ZoneUtil.MinniesMelodyland)
        self.startup()

    def startup(self):
        self.dnaFiles = ['phase_6/dna/minnies_melody_land_4100.pdna', 'phase_6/dna/minnies_melody_land_4200.pdna',
            'phase_6/dna/minnies_melody_land_4300.pdna', 'phase_6/dna/minnies_melody_land_sz.pdna']
        ToonHoodAI.startup(self)
