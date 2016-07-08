# Filename: TTTownLoader.py
# Created by:  blach (25Jul15)

import TownLoader
import TTStreet

from lib.coginvasion.globals import CIGlobals

class TTTownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = TTStreet.TTStreet
        self.musicFile = 'phase_3.5/audio/bgm/TC_SZ.mid'
        self.interiorMusicFile = 'phase_3.5/audio/bgm/TC_SZ_activity.mid'
        self.townStorageDNAFile = 'phase_5/dna/storage_TT_town.pdna'

    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        zone4File = str(self.branchZone)
        dnaFile = 'phase_5/dna/toontown_central_' + zone4File + '.pdna'
        self.createHood(dnaFile)

    def unload(self):
        TownLoader.TownLoader.unload(self)
