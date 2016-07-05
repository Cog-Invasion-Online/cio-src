# Filename: DGTownLoader.py
# Created by:  blach (26Jul15)

import TownLoader
import DGStreet

from lib.coginvasion.globals import CIGlobals

class DGTownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = DGStreet.DGStreet
        self.musicFile = 'phase_8/audio/bgm/DG_SZ.ogg'
        self.interiorMusicFile = self.musicFile
        self.townStorageDNAFile = 'phase_8/dna/storage_DG_town.pdna'

    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        zone4File = str(self.branchZone)
        dnaFile = 'phase_8/dna/daisys_garden_' + zone4File + '.pdna'
        self.createHood(dnaFile)
