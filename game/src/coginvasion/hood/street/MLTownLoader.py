"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file MLTownLoader.py
@author Brian Lach
@date July 26, 2015

"""

import TownLoader
import MLStreet

from src.coginvasion.globals import CIGlobals

class MLTownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = MLStreet.MLStreet
        self.musicFile = 'phase_6/audio/bgm/MM_SZ.mid'
        self.interiorMusicFile = 'phase_6/audio/bgm/MM_SZ_activity.mid'
        self.townStorageDNAFile = 'phase_6/dna/storage_MM_town.pdna'

    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        zone4File = str(self.branchZone)
        dnaFile = 'phase_6/dna/minnies_melody_land_' + zone4File + '.pdna'
        self.createHood(dnaFile)

    def unload(self):
        TownLoader.TownLoader.unload(self)
