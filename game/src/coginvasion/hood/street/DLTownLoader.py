"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DLTownLoader.py
@author Brian Lach
@date July 26, 2015

"""

import TownLoader
import DLStreet

from src.coginvasion.globals import CIGlobals

class DLTownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = DLStreet.DLStreet
        self.streetSong = 'DL_SZ'
        self.interiorSong = 'DL_SZ_activity'
        self.townStorageDNAFile = 'phase_8/dna/storage_DL_town.pdna'
        self.lampLights = []

    def unload(self):
        for lamp in self.lampLights:
            render.clearLight(lamp)
            lamp.removeNode()
        self.lampLights = []

    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        zone4File = str(self.branchZone)
        dnaFile = 'phase_8/dna/donalds_dreamland_' + zone4File + '.pdna'
        self.createHood(dnaFile, 1, False)
        
        if game.uselighting:
            for lamp in self.geom.findAllMatches("**/*light_DNARoot*"):
                lightNP = self.hood.makeLampLight(lamp)
                lightNP.wrtReparentTo(lamp)
                self.lampLights.append(lightNP)

        self.doFlatten()