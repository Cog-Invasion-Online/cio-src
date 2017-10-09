"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file TTHood.py
@author Brian Lach
@date October 25, 2015

"""

from src.coginvasion.globals import CIGlobals
from src.coginvasion.holiday.HolidayManager import HolidayType
from playground import TTSafeZoneLoader
from street import TTTownLoader
import ToonHood
from panda3d.core import TransparencyAttrib

class TTHood(ToonHood.ToonHood):

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.id = CIGlobals.ToontownCentral
        self.safeZoneLoader = TTSafeZoneLoader.TTSafeZoneLoader
        self.townLoader = TTTownLoader.TTTownLoader
        self.abbr = "TT"
        self.storageDNAFile = "phase_4/dna/storage_TT.pdna"
        self.holidayDNAFile = None
        if base.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS:
            self.holidayDNAFile = "phase_4/dna/winter_storage_TT.pdna"
        self.titleColor = (1.0, 0.5, 0.4, 1.0)
        self.loaderDoneEvent = 'TTHood-loaderDone'

    def load(self):
        ToonHood.ToonHood.load(self)
        self.parentFSM.getStateNamed('TTHood').addChild(self.fsm)

    def unload(self):
        self.parentFSM.getStateNamed('TTHood').removeChild(self.fsm)
        ToonHood.ToonHood.unload(self)
