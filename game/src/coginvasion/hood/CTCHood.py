"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file CTCHood.py
@author Brian Lach
@date December 01, 2014

"""

from src.coginvasion.holiday.HolidayManager import HolidayType
from panda3d.core import TransparencyAttrib

from playground import CTCSafeZoneLoader
from street import TTTownLoader

import ToonHood
import ZoneUtil

class CTCHood(ToonHood.ToonHood):

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.id = ZoneUtil.BattleTTC
        self.safeZoneLoader = CTCSafeZoneLoader.CTCSafeZoneLoader
        self.townLoader = TTTownLoader.TTTownLoader
        self.storageDNAFile = "phase_4/dna/storage_TT.pdna"
        self.holidayDNAFile = None
        if base.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS:
            self.holidayDNAFile = "phase_4/dna/winter_storage_TT.pdna"
        self.titleColor = (1.0, 0.5, 0.4, 1.0)
        self.loaderDoneEvent = 'CTCHood-loaderDone'

    def load(self):
        ToonHood.ToonHood.load(self)
        self.parentFSM.getStateNamed('CTCHood').addChild(self.fsm)

    def unload(self):
        self.parentFSM.getStateNamed('CTCHood').removeChild(self.fsm)
        ToonHood.ToonHood.unload(self)

    def enter(self, requestStatus):
        ToonHood.ToonHood.enter(self, requestStatus)

    def exit(self):
        ToonHood.ToonHood.exit(self)
