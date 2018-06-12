"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file BRTownLoader.py
@author Brian Lach
@date July 26, 2015

"""

import TownLoader
import BRStreet

from src.coginvasion.globals import CIGlobals

class BRTownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = BRStreet.BRStreet
        self.streetSong = 'TB_SZ'
        self.interiorSong = 'TB_SZ_activity'
        self.townStorageDNAFile = 'phase_8/dna/storage_BR_town.pdna'

    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        zone4File = str(self.branchZone)
        dnaFile = 'phase_8/dna/the_burrrgh_' + zone4File + '.pdna'
        self.createHood(dnaFile)
