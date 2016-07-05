# Filename: CTHood.py
# Created by:  blach (14Aug15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from lib.coginvasion.hood import ToonHood
from lib.coginvasion.globals import CIGlobals
import CTSafeZoneLoader

class CTHood(ToonHood.ToonHood):
    notify = directNotify.newCategory("CTHood")

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.id = CIGlobals.CogTropolis
        self.safeZoneLoader = CTSafeZoneLoader.CTSafeZoneLoader
        self.storageDNAFile = None
        self.holidayDNAFile = None
        self.skyFilename = "phase_9/models/cogHQ/cog_sky.bam"
        self.spookySkyFile = "phase_9/models/cogHQ/cog_sky.bam"
        self.titleColor = (0.5, 0.5, 0.5, 1.0)
        self.loaderDoneEvent = 'CTHood-loaderDone'

    def load(self):
        ToonHood.ToonHood.load(self)
        self.parentFSM.getStateNamed('CTHood').addChild(self.fsm)

    def unload(self):
        self.parentFSM.getStateNamed('CTHood').removeChild(self.fsm)
        ToonHood.ToonHood.unload(self)
