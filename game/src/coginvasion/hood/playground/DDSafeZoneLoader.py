"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DDSafeZoneLoader.py
@author Brian Lach
@date July 26, 2015

"""

from src.coginvasion.holiday.HolidayManager import HolidayType
import SafeZoneLoader
import DDPlayground

class DDSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playground = DDPlayground.DDPlayground
        self.safeZoneSong = 'DD_nbrhood'
        self.interiorSong = 'DD_SZ_activity'
        self.dnaFile = 'phase_6/dna/donalds_dock_sz.pdna'
        self.szStorageDNAFile = 'phase_6/dna/storage_DD_sz.pdna'
        self.szHolidayDNAFile = None
        if base.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS:
            self.szHolidayDNAFile = 'phase_6/dna/winter_storage_DD_sz.pdna'
        self.telescope = None
        self.birdNoise = 'phase_6/audio/sfx/SZ_DD_Seagull.ogg'

        self.wRefl = None

        base.wakeWaterHeight = 1.64415

    def load(self):
        SafeZoneLoader.SafeZoneLoader.load(self)
        hq = self.geom.find('**/*toon_landmark_hqDD*')
        hq.find('**/doorFrameHoleLeft_0').stash()
        hq.find('**/doorFrameHoleRight_0').stash()
        hq.find('**/doorFrameHoleLeft_1').stash()
        hq.find('**/doorFrameHoleRight_1').stash()

        water = self.geom.find("**/top_surface")
        water.setTwoSided(True)
        #water.setTransparency(True)
        #water.setAlphaScale(0.9)
        self.geom.find("**/bottom_surface").stash()
        base.waterReflectionMgr.addWaterNode(water, base.wakeWaterHeight)

    def enter(self, requestStatus):
        SafeZoneLoader.SafeZoneLoader.enter(self, requestStatus)
        #self.hood.setWhiteFog()

    def exit(self):
        #self.hood.setNoFog()
        SafeZoneLoader.SafeZoneLoader.exit(self)
