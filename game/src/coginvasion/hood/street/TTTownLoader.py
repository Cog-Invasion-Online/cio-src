"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file TTTownLoader.py
@author Brian Lach
@date July 25, 2015

"""

from panda3d.core import TextureStage
from panda3d.bsp import BSPMaterialAttrib

import TownLoader
import TTStreet

class TTTownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = TTStreet.TTStreet
        self.streetSong = 'TC_SZ'
        self.interiorSong = 'TC_SZ_activity'
        self.townStorageDNAFile = 'phase_5/dna/storage_TT_town.pdna'
        
    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        zone4File = str(self.branchZone)
        dnaFile = 'phase_5/dna/toontown_central_' + zone4File + '.pdna'
        self.createHood(dnaFile)
