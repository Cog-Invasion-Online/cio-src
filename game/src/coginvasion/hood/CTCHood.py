"""

  Filename: CTCHood.py
  Created by: blach (01Dec14)

"""

from src.coginvasion.globals import CIGlobals
from src.coginvasion.holiday.HolidayManager import HolidayType
from pandac.PandaModules import TransparencyAttrib

from playground import CTCSafeZoneLoader
from street import TTTownLoader

import ToonHood

class CTCHood(ToonHood.ToonHood):

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.id = CIGlobals.BattleTTC
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
