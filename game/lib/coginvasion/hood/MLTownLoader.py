# Filename: MLTownLoader.py
# Created by:  blach (26Jul15)

import TownLoader
import MLStreet

from lib.coginvasion.globals import CIGlobals

class MLTownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = MLStreet.MLStreet
        self.musicFile = 'phase_6/audio/bgm/MM_SZ.ogg'
        self.interiorMusicFile = 'phase_6/audio/bgm/MM_SZ_activity.ogg'
        self.townStorageDNAFile = 'phase_6/dna/storage_MM_town.pdna'

    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        zone4File = str(self.branchZone)
        dnaFile = 'phase_6/dna/minnies_melody_land_' + zone4File + '.pdna'
        self.createHood(dnaFile)

    def unload(self):
        TownLoader.TownLoader.unload(self)
