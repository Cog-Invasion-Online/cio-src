"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file TTTownLoader.py
@author Brian Lach
@date July 25, 2015

"""

from panda3d.core import TextureStage

import TownLoader
import TTStreet

from src.coginvasion.globals import CIGlobals

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

        #streetNormal = TextureStage('TTStreetNormal')
        #streetNormal.setMode(TextureStage.MNormal)
        #normalTex = loader.loadTexture("phase_3.5/maps/cobblestone_normal.jpg")
        #for street in self.geom.findAllMatches("**/*street_*_street*"):
        #    print "Applying normal texture to", street.getName()
        #    street.setTexture(streetNormal, normalTex)

    def unload(self):
        TownLoader.TownLoader.unload(self)
