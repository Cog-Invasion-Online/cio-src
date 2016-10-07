# Filename: DGHood.py
# Created by:  blach (24Jul15)

from pandac.PandaModules import TransparencyAttrib
from direct.directnotify.DirectNotifyGlobal import directNotify

from ToonHood import ToonHood
import SkyUtil
from DGSafeZoneLoader import DGSafeZoneLoader
import DGTownLoader
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.holiday.HolidayManager import HolidayType

class DGHood(ToonHood):
    notify = directNotify.newCategory("DGHood")

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.id = CIGlobals.DaisyGardens
        self.safeZoneLoader = DGSafeZoneLoader
        self.townLoader = DGTownLoader.DGTownLoader
        self.skyUtil = SkyUtil.SkyUtil()
        self.abbr = "DG"
        self.storageDNAFile = "phase_8/dna/storage_DG.pdna"
        self.holidayDNAFile = None
        if base.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS:
            self.holidayDNAFile = "phase_8/dna/winter_storage_DG.pdna"
        self.skyFilename = "phase_3.5/models/props/TT_sky.bam"
        self.spookySkyFile = "phase_3.5/models/props/BR_sky.bam"
        self.titleColor = (0.4, 0.67, 0.18, 1.0)
        self.loaderDoneEvent = 'DGHood-loaderDone'

    def load(self):
        ToonHood.load(self)
        self.parentFSM.getStateNamed('DGHood').addChild(self.fsm)

    def unload(self):
        self.parentFSM.getStateNamed('DGHood').removeChild(self.fsm)
        ToonHood.unload(self)

    def startSuitEffect(self):
        ToonHood.startSuitEffect(self)
        if base.cr.playGame.getPlace():
            base.cr.playGame.getPlace().stopBirds()

    def stopSuitEffect(self, newSky = 1):
        if base.cr.playGame.getPlace():
            base.cr.playGame.getPlace().startBirds()
        ToonHood.stopSuitEffect(self, newSky)

    def startSky(self):
        ToonHood.startSky(self)
        self.sky.setTransparency(TransparencyAttrib.MDual, 1)
        self.skyUtil.startSky(self.sky)

    def stopSky(self):
        ToonHood.stopSky(self)
        self.skyUtil.stopSky()
