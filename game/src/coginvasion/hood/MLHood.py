# Filename: MLHood.py
# Created by:  blach (24Jul15)

from panda3d.core import VBase4, Vec3

from direct.directnotify.DirectNotifyGlobal import directNotify

from ToonHood import ToonHood
from playground.MLSafeZoneLoader import MLSafeZoneLoader
from street.MLTownLoader import MLTownLoader
from src.coginvasion.globals import CIGlobals
from src.coginvasion.holiday.HolidayManager import HolidayType

class MLHood(ToonHood):
    notify = directNotify.newCategory("MLHood")

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.id = CIGlobals.MinniesMelodyland
        self.safeZoneLoader = MLSafeZoneLoader
        self.townLoader = MLTownLoader
        self.abbr = "MM"
        self.storageDNAFile = "phase_6/dna/storage_MM.pdna"
        self.holidayDNAFile = None
        if base.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS:
            self.holidayDNAFile = "phase_6/dna/winter_storage_MM.pdna"
        self.skyFilename = "phase_6/models/props/MM_sky.bam"
        self.spookySkyFile = "phase_3.5/models/props/BR_sky.bam"
        self.titleColor = (0.945, 0.54, 1.0, 1.0)
        self.loaderDoneEvent = 'MLHood-loaderDone'

        self.ambient = VBase4(110 / 255.0, 180 / 255.0, 204 / 255.0, 1.0)
        self.sun = VBase4(255 / 255.0, 109 / 255.0, 86 / 255.0, 1.0)
        self.sunPos = Vec3(-750, 100, 500)

    def load(self):
        ToonHood.load(self)
        self.parentFSM.getStateNamed('MLHood').addChild(self.fsm)

    def unload(self):
        self.parentFSM.getStateNamed('MLHood').removeChild(self.fsm)
        ToonHood.unload(self)
