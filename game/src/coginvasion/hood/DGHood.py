"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DGHood.py
@author Brian Lach
@date July 24, 2015

"""

from panda3d.core import TransparencyAttrib
from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.holiday.HolidayManager import HolidayType

from ToonHood import ToonHood
from playground.DGSafeZoneLoader import DGSafeZoneLoader
from street import DGTownLoader
import ZoneUtil

class DGHood(ToonHood):
    notify = directNotify.newCategory("DGHood")

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.id = ZoneUtil.DaisyGardens
        self.safeZoneLoader = DGSafeZoneLoader
        self.townLoader = DGTownLoader.DGTownLoader
        self.abbr = "DG"
        self.storageDNAFile = "phase_8/dna/storage_DG.pdna"
        self.holidayDNAFile = None
        if base.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS:
            self.holidayDNAFile = "phase_8/dna/winter_storage_DG.pdna"
        self.titleColor = (0.4, 0.67, 0.18, 1.0)
        self.loaderDoneEvent = 'DGHood-loaderDone'

    def load(self):
        ToonHood.load(self)
        self.parentFSM.getStateNamed('DGHood').addChild(self.fsm)

    def unload(self):
        self.parentFSM.getStateNamed('DGHood').removeChild(self.fsm)
        ToonHood.unload(self)
