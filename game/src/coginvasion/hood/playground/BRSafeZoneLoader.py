"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file BRSafeZoneLoader.py
@author Brian Lach
@date July 01, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.holiday.HolidayManager import HolidayType
from src.coginvasion.toon import ParticleLoader
import SafeZoneLoader
import BRPlayground

class BRSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):
    notify = directNotify.newCategory("BRSafeZoneLoader")

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playground = BRPlayground.BRPlayground
        self.safeZoneSong = 'TB_nbrhood'
        self.interiorSong = 'TB_SZ_activity'
        self.dnaFile = 'phase_8/dna/the_burrrgh_sz.pdna'
        self.szStorageDNAFile = 'phase_8/dna/storage_BR_sz.pdna'
        self.szHolidayDNAFile = None
        self.telescope = None
        base.wakeWaterHeight = 1.72918

    def load(self):
        SafeZoneLoader.SafeZoneLoader.load(self)
        hq = self.geom.find('**/*toon_landmark_hqBR*')
        hq.find('**/doorFrameHoleLeft_0').stash()
        hq.find('**/doorFrameHoleRight_0').stash()
        hq.find('**/doorFrameHoleLeft_1').stash()
        hq.find('**/doorFrameHoleRight_1').stash()

        water = self.geom.find("**/ice_water")
        water.setTransparency(False)
        base.waterReflectionMgr.addWaterNode(water, base.wakeWaterHeight)

    def unload(self):
        SafeZoneLoader.SafeZoneLoader.unload(self)

    def enter(self, requestStatus):
        SafeZoneLoader.SafeZoneLoader.enter(self, requestStatus)

    def exit(self):
        SafeZoneLoader.SafeZoneLoader.exit(self)
