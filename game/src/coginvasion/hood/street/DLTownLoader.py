"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DLTownLoader.py
@author Brian Lach
@date July 26, 2015

"""

import TownLoader
import DLStreet

class DLTownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = DLStreet.DLStreet
        self.streetSong = 'DL_SZ'
        self.interiorSong = 'DL_SZ_activity'
        self.townStorageDNAFile = 'phase_8/dna/storage_DL_town.pdna'
        self.lampLights = {}

    def unload(self):
        for lampList in self.lampLights.values():
            for lamp in lampList:
                render.clearLight(lamp)
                lamp.removeNode()
        self.lampLights = None

    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        zone4File = str(self.branchZone)
        dnaFile = 'phase_8/dna/donalds_dreamland_' + zone4File + '.pdna'
        self.createHood(dnaFile, 1, False)
        
        if metadata.USE_LIGHTING:
            lamps = self.geom.findAllMatches("**/*light_DNARoot*")
            for lamp in lamps:
                blockNum = self.__extractBlockNumberFromLamp(lamp)
                blockLamps = self.lampLights.get(blockNum, [])

                lightNP = self.hood.makeLampLight(lamp)
                lightNP.wrtReparentTo(lamp)
                
                blockLamps.append(lightNP)
                self.lampLights.update({blockNum : blockLamps})

        self.doFlatten()
        
    def __extractBlockNumberFromLamp(self, lamp):
        node = lamp.getParent()
        blockNum = -1
        
        while blockNum == -1 and not node.getParent() in [render, hidden]:
            if node.getName()[:2] == 'tb':
                # Great, we're looking at the toon block "container"
                colonIndex = node.getName().find(':')
                
                if colonIndex != -1:
                    blockNum = int(node.getName()[2:colonIndex])
                    break
            
            node = node.getParent()

        return blockNum
        