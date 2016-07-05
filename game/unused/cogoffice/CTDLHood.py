# Filename: CTDLHood.py
# Created by:  blach (12Dec15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from lib.coginvasion.hood.DLHood import DLHood
from CTDLSafeZoneLoader import CTDLSafeZoneLoader

class CTDLHood(DLHood):
    notify = directNotify.newCategory("CTDLHood")

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        DLHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.safeZoneLoader = CTDLSafeZoneLoader
        self.skyFilename = "phase_3.5/models/props/BR_sky.bam"
        self.titleColor = (0.5, 0.5, 0.5, 1.0)
