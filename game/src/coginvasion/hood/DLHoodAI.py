"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DLHoodAI.py
@author Brian Lach
@date July 24, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

from ToonHoodAI import ToonHoodAI
import ZoneUtil

class DLHoodAI(ToonHoodAI):
    notify = directNotify.newCategory('DLHoodAI')

    def __init__(self, air):
        ToonHoodAI.__init__(self, air, ZoneUtil.DonaldsDreamlandId, ZoneUtil.DonaldsDreamland)
        self.startup()

    def startup(self):
        self.dnaFiles = ['phase_8/dna/donalds_dreamland_9100.pdna', 'phase_8/dna/donalds_dreamland_9200.pdna',
            'phase_8/dna/donalds_dreamland_sz.pdna']
        ToonHoodAI.startup(self)
