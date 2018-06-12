"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DGTownLoader.py
@author Brian Lach
@date July 26, 2015

"""

import TownLoader
import DGStreet

from src.coginvasion.globals import CIGlobals

class DGTownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = DGStreet.DGStreet
        self.streetSong = 'DG_SZ'
        self.interiorSong = self.streetSong
        self.townStorageDNAFile = 'phase_8/dna/storage_DG_town.pdna'

    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        zone4File = str(self.branchZone)
        dnaFile = 'phase_8/dna/daisys_garden_' + zone4File + '.pdna'
        self.createHood(dnaFile)
