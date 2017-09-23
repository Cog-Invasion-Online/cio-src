# Filename: DDHood.py
# Created by:  blach (26Jul15)

from pandac.PandaModules import VBase4
from src.coginvasion.globals import CIGlobals
from src.coginvasion.holiday.HolidayManager import HolidayType

from street import DDTownLoader
from playground import DDSafeZoneLoader

from ToonHood import ToonHood

class DDHood(ToonHood):

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.id = CIGlobals.DonaldsDock
        self.safeZoneLoader = DDSafeZoneLoader.DDSafeZoneLoader
        self.townLoader = DDTownLoader.DDTownLoader
        self.abbr = "DD"
        self.storageDNAFile = "phase_6/dna/storage_DD.pdna"
        self.holidayDNAFile = None
        if base.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS:
            self.holidayDNAFile = "phase_6/dna/winter_storage_DD.pdna"
        self.skyFilename = "phase_3.5/models/props/BR_sky.bam"
        self.spookySkyFile = "phase_3.5/models/props/BR_sky.bam"
        self.titleColor = (0.80000000000000004, 0.59999999999999998, 0.5, 1.0)
        self.loaderDoneEvent = 'DDHood-loaderDone'
        self.fog = VBase4(0.80000000000000004, 0.80000000000000004, 0.80000000000000004, 1)
        self.fogDensity = 0.0035

    def load(self):
        ToonHood.load(self)
        self.parentFSM.getStateNamed('DDHood').addChild(self.fsm)

    def unload(self):
        self.parentFSM.getStateNamed('DDHood').removeChild(self.fsm)
        ToonHood.unload(self)
