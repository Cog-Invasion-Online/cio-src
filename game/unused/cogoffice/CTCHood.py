########################################
# Filename: CTCHood.py
# Created by: blach (01Dec14)
########################################

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.holiday.HolidayManager import HolidayType
from panda3d.core import TransparencyAttrib
from lib.coginvasion.hood import ToonHood
import CTCSafeZoneLoader
from lib.coginvasion.hood import TTTownLoader
from lib.coginvasion.hood import SkyUtil

class CTCHood(ToonHood.ToonHood):

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.id = CIGlobals.CogTropCentral
        self.safeZoneLoader = CTCSafeZoneLoader.CTCSafeZoneLoader
        self.townLoader = TTTownLoader.TTTownLoader
        self.skyUtil = SkyUtil.SkyUtil()
        self.storageDNAFile = "phase_4/dna/storage_TT.pdna"
        self.holidayDNAFile = None
        if base.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS:
            self.holidayDNAFile = "phase_4/dna/winter_storage_TT.pdna"
        self.skyFilename = "phase_3.5/models/props/BR_sky.bam"
        self.spookySkyFile = "phase_3.5/models/props/BR_sky.bam"
        self.titleColor = (0.5, 0.5, 0.5, 1.0)
        self.loaderDoneEvent = 'TTHood-loaderDone'

    def load(self):
        ToonHood.ToonHood.load(self)
        self.parentFSM.getStateNamed('TTHood').addChild(self.fsm)

    def unload(self):
        self.parentFSM.getStateNamed('TTHood').removeChild(self.fsm)
        ToonHood.ToonHood.unload(self)

    def enter(self, requestStatus):
        ToonHood.ToonHood.enter(self, requestStatus)

    def exit(self):
        ToonHood.ToonHood.exit(self)

    def startSuitEffect(self):
        ToonHood.ToonHood.startSuitEffect(self)
        if base.cr.playGame.getPlace():
            if hasattr(base.cr.playGame.getPlace(), 'stopBirds'):
                base.cr.playGame.getPlace().stopBirds()

    def stopSuitEffect(self, newSky = 1):
        if base.cr.playGame.getPlace():
            if hasattr(base.cr.playGame.getPlace(), 'startBirds'):
                base.cr.playGame.getPlace().startBirds()
        ToonHood.ToonHood.stopSuitEffect(self, newSky)

    def startSky(self):
        ToonHood.ToonHood.startSky(self)
        self.sky.setTransparency(TransparencyAttrib.MDual, 1)
        self.skyUtil.startSky(self.sky)

    def stopSky(self):
        ToonHood.ToonHood.stopSky(self)
        self.skyUtil.stopSky()
