# Filename: MLHood.py
# Created by:  blach (24Jul15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from ToonHood import ToonHood
from MLSafeZoneLoader import MLSafeZoneLoader
from MLTownLoader import MLTownLoader
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.holiday.HolidayManager import HolidayType

class MLHood(ToonHood):
    notify = directNotify.newCategory("MLHood")

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.id = CIGlobals.MinniesMelodyland
        self.safeZoneLoader = MLSafeZoneLoader
        self.townLoader = MLTownLoader
        self.storageDNAFile = "phase_6/dna/storage_MM.pdna"
        self.holidayDNAFile = None
        if base.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS:
            self.holidayDNAFile = "phase_6/dna/winter_storage_MM.pdna"
        self.skyFilename = "phase_6/models/props/MM_sky.bam"
        self.spookySkyFile = "phase_3.5/models/props/BR_sky.bam"
        self.titleColor = (0.945, 0.54, 1.0, 1.0)
        self.loaderDoneEvent = 'MLHood-loaderDone'

    def load(self):
        ToonHood.load(self)
        self.parentFSM.getStateNamed('MLHood').addChild(self.fsm)

    def unload(self):
        self.parentFSM.getStateNamed('MLHood').removeChild(self.fsm)
        ToonHood.unload(self)
