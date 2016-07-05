# Filename: CTDGHood.py
# Created by:  blach (12Dec15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from lib.coginvasion.hood.DGHood import DGHood
from CTDGSafeZoneLoader import CTDGSafeZoneLoader

class CTDGHood(DGHood):
    notify = directNotify.newCategory("CTDGHood")

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        DGHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.safeZoneLoader = CTDGSafeZoneLoader
        self.skyFilename = "phase_3.5/models/props/BR_sky.bam"
        self.titleColor = (0.5, 0.5, 0.5, 1.0)
