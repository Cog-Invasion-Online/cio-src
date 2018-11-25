"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DGSafeZoneLoader.py
@author Brian Lach
@date July 24, 2015

"""

from panda3d.core import TransparencyAttrib, ColorAttrib

from src.coginvasion.globals import CIGlobals
from src.coginvasion.holiday.HolidayManager import HolidayType
import SafeZoneLoader
import DGPlayground

class DGSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playground = DGPlayground.DGPlayground
        self.safeZoneSong = 'DG_nbrhood'
        self.interiorSong = 'DG_SZ'
        self.dnaFile = 'phase_8/dna/daisys_garden_sz.pdna'
        self.szStorageDNAFile = 'phase_8/dna/storage_DG_sz.pdna'
        self.szHolidayDNAFile = None
        if base.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS:
            self.szHolidayDNAFile = 'phase_8/dna/winter_storage_DG_sz.pdna'
        self.telescope = None
        self.birdNoises = [
            'phase_8/audio/sfx/SZ_DG_bird_01.ogg',
            'phase_8/audio/sfx/SZ_DG_bird_02.ogg',
            'phase_8/audio/sfx/SZ_DG_bird_03.ogg',
            'phase_8/audio/sfx/SZ_DG_bird_04.ogg'
        ]
        base.wakeWaterHeight = -1.26438

    def load(self):
        SafeZoneLoader.SafeZoneLoader.load(self)
        hq = self.geom.find('**/*toon_landmark_hqDG*')
        hq.find('**/doorFrameHoleLeft_0').stash()
        hq.find('**/doorFrameHoleRight_0').stash()
        hq.find('**/doorFrameHoleLeft_1').stash()
        hq.find('**/doorFrameHoleRight_1').stash()
        
    def doFlatten(self):
    
        water = self.geom.find("**/water_surface")
        water.removeNode()
        
        dg = self.geom.find("**/daisys_garden_DNARoot")
        dg.flattenStrong()
        
        dgprops = self.geom.attachNewNode("dgprops")
        CIGlobals.moveNodes(self.geom, "*daisys_flowerbox*_DNARoot", dgprops)
        CIGlobals.moveNodes(self.geom, "*prop_daisys_fountain*_DNARoot", dgprops)
        CIGlobals.moveNodes(self.geom, "*prop_daisy_park_table*_DNARoot", dgprops)
        CIGlobals.moveNodes(self.geom, "*prop_DG_flower*_DNARoot", dgprops)
        CIGlobals.removeDNACodes(dgprops)
        dgprops.clearModelNodes()
        dgprops.flattenStrong()
        CIGlobals.moveChildren(dgprops, self.geom)
        
        SafeZoneLoader.SafeZoneLoader.doFlatten(self)
        