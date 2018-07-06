"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DLSafeZoneLoader.py
@author Brian Lach
@date July 24, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

from SafeZoneLoader import SafeZoneLoader
from DLPlayground import DLPlayground
from src.coginvasion.holiday.HolidayManager import HolidayType

from src.coginvasion.globals import CIGlobals

class DLSafeZoneLoader(SafeZoneLoader):
    notify = directNotify.newCategory("DLSafeZoneLoader")

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playground = DLPlayground
        self.safeZoneSong = 'DL_nbrhood'
        self.interiorSong = 'DL_SZ_activity'
        self.dnaFile = 'phase_8/dna/donalds_dreamland_sz.pdna'
        self.szStorageDNAFile = 'phase_8/dna/storage_DL_sz.pdna'
        self.szHolidayDNAFile = None
        if base.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS:
            self.szHolidayDNAFile = 'phase_8/dna/winter_storage_DL_sz.pdna'
        self.telescope = None
        base.wakeWaterHeight = -17.0385

        self.lampLights = []

    def unload(self):
        for lamp in self.lampLights:
            render.clearLight(lamp)
            lamp.removeNode()
        self.lampLights = None
        SafeZoneLoader.unload(self)

    def load(self):
        SafeZoneLoader.load(self, False)
        
        if game.uselighting:
            for lamp in self.geom.findAllMatches("**/*light_DNARoot*"):
                self.lampLights.append(self.hood.makeLampLight(lamp))

        self.doFlatten()

        hq = self.geom.find('**/*toon_landmark_hqDL*')
        hq.find('**/doorFrameHoleLeft_0').stash()
        hq.find('**/doorFrameHoleRight_0').stash()
        hq.find('**/doorFrameHoleLeft_1').stash()
        hq.find('**/doorFrameHoleRight_1').stash()

        water = self.geom.find("**/DLpd_water")
        water.removeNode()