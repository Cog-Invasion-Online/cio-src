# Filename: CTDDHood.py
# Created by:  blach (12Dec15)

import CTDDSafeZoneLoader
from lib.coginvasion.hood.DDHood import DDHood
from lib.coginvasion.hood import DDTownLoader

class CTDDHood(DDHood):

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        DDHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.safeZoneLoader = CTDDSafeZoneLoader.CTDDSafeZoneLoader
        self.townLoader = DDTownLoader.DDTownLoader
        self.titleColor = (0.5, 0.5, 0.5, 1.0)
