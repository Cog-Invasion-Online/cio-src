"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DGHoodAI.py
@author Brian Lach
@date July 24, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

from ToonHoodAI import ToonHoodAI
import ZoneUtil

class DGHoodAI(ToonHoodAI):
    notify = directNotify.newCategory('DGHoodAI')

    def __init__(self, air):
        ToonHoodAI.__init__(self, air, ZoneUtil.DaisyGardensId, ZoneUtil.DaisyGardens)
        self.startup()

    def startup(self):
        self.dnaFiles = ['phase_8/dna/daisys_garden_5100.pdna', 'phase_8/dna/daisys_garden_5200.pdna',
            'phase_8/dna/daisys_garden_5300.pdna', 'phase_8/dna/daisys_garden_sz.pdna']
        ToonHoodAI.startup(self)
