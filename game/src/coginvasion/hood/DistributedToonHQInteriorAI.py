"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedToonHQInteriorAI.py
@author Brian Lach
@date July 29, 2015

"""

import DistributedToonInteriorAI
import DistributedDoorAI
from src.coginvasion.globals import CIGlobals

class DistributedToonHQInteriorAI(DistributedToonInteriorAI.DistributedToonInteriorAI):

    def __init__(self, air, blockZone, doorToZone):
        DistributedToonInteriorAI.DistributedToonInteriorAI.__init__(self, air, blockZone, doorToZone)
        self.door2 = None

    def announceGenerate(self):
        DistributedToonInteriorAI.DistributedToonInteriorAI.announceGenerate(self, doorType = 2)

        # Toontown Central's playground HQ only has one accessible front door.
        if not self.doorToZone == CIGlobals.ToontownCentralId:
            self.door2 = DistributedDoorAI.DistributedDoorAI(self.air, self.block, self.doorToZone, 2, 1)
            self.door2.generateWithRequired(self.zoneId)

    def delete(self):
        if self.door2:
            self.door2.requestDelete()
            self.door2 = None
        DistributedToonInteriorAI.DistributedToonInteriorAI.delete(self)
