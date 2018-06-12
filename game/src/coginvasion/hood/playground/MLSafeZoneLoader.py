"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file MLSafeZoneLoader.py
@author Brian Lach
@date July 24, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

from SafeZoneLoader import SafeZoneLoader
from MLPlayground import MLPlayground
from src.coginvasion.holiday.HolidayManager import HolidayType

class MLSafeZoneLoader(SafeZoneLoader):
    notify = directNotify.newCategory("MLSafeZoneLoader")

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playground = MLPlayground
        self.safeZoneSong = 'MM_nbrhood'
        self.interiorSong = 'MM_SZ_activity'
        self.dnaFile = 'phase_6/dna/minnies_melody_land_sz.pdna'
        self.szStorageDNAFile = 'phase_6/dna/storage_MM_sz.pdna'
        self.szHolidayDNAFile = None
        if base.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS:
            self.szHolidayDNAFile = 'phase_6/dna/winter_storage_MM_sz.pdna'
        self.telescope = None
        base.wakeWaterHeight = -14.5652

    def load(self):
        SafeZoneLoader.load(self)
        hq = self.geom.find('**/*toon_landmark_hqMM*')
        hq.find('**/doorFrameHoleLeft_0').stash()
        hq.find('**/doorFrameHoleRight_0').stash()
        hq.find('**/doorFrameHoleLeft_1').stash()
        hq.find('**/doorFrameHoleRight_1').stash()

        water = self.geom.find("**/MMsz_water")
        water.setTransparency(False)
        base.waterReflectionMgr.addWaterNode(water, base.wakeWaterHeight)
