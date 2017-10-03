# Filename: DGHood.py
# Created by:  blach (24Jul15)

from pandac.PandaModules import TransparencyAttrib
from direct.directnotify.DirectNotifyGlobal import directNotify

from ToonHood import ToonHood
from playground.DGSafeZoneLoader import DGSafeZoneLoader
from street import DGTownLoader
from src.coginvasion.globals import CIGlobals
from src.coginvasion.holiday.HolidayManager import HolidayType

class DGHood(ToonHood):
    notify = directNotify.newCategory("DGHood")

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.id = CIGlobals.DaisyGardens
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
