# Filename: DLHood.py
# Created by:  blach (24Jul15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from ToonHood import ToonHood
from playground.DLSafeZoneLoader import DLSafeZoneLoader
from street.DLTownLoader import DLTownLoader
from src.coginvasion.globals import CIGlobals
from src.coginvasion.holiday.HolidayManager import HolidayType

class DLHood(ToonHood):
    notify = directNotify.newCategory("DLHood")

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.id = CIGlobals.DonaldsDreamland
        self.safeZoneLoader = DLSafeZoneLoader
        self.townLoader = DLTownLoader
        self.abbr = "DL"
        self.storageDNAFile = "phase_8/dna/storage_DL.pdna"
        self.holidayDNAFile = None
        if base.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS:
            self.holidayDNAFile = "phase_8/dna/winter_storage_DL.pdna"
        self.skyFilename = "phase_8/models/props/DL_sky.bam"
        self.spookySkyFile = "phase_3.5/models/props/BR_sky.bam"
        self.titleColor = (0.443, 0.21, 1.0, 1.0)
        self.loaderDoneEvent = 'DLHood-loaderDone'

    def load(self):
        ToonHood.load(self)
        self.parentFSM.getStateNamed('DLHood').addChild(self.fsm)

    def unload(self):
        self.parentFSM.getStateNamed('DLHood').removeChild(self.fsm)
        ToonHood.unload(self)
