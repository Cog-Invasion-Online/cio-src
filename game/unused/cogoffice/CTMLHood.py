# Filename: CTMLHood.py
# Created by:  blach (12Dec15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from lib.coginvasion.hood.MLHood import MLHood
from CTMLSafeZoneLoader import CTMLSafeZoneLoader

class CTMLHood(MLHood):
    notify = directNotify.newCategory("CTMLHood")

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        MLHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.safeZoneLoader = CTMLSafeZoneLoader
        self.skyFilename = "phase_3.5/models/props/BR_sky.bam"
        self.titleColor = (0.5, 0.5, 0.5, 1.0)
