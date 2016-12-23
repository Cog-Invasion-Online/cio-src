# Filename: DistributedToonHQInteriorAI.py
# Created by:  blach (29Jul15)

import DistributedToonInteriorAI
import DistributedDoorAI

class DistributedToonHQInteriorAI(DistributedToonInteriorAI.DistributedToonInteriorAI):

    def __init__(self, air, blockZone, doorToZone):
        DistributedToonInteriorAI.DistributedToonInteriorAI.__init__(self, air, blockZone, doorToZone)
        self.door2 = None

    def announceGenerate(self):
        DistributedToonInteriorAI.DistributedToonInteriorAI.announceGenerate(self, doorType = 2)
        self.door2 = DistributedDoorAI.DistributedDoorAI(self.air, self.block, self.doorToZone, 2, 1)
        self.door2.generateWithRequired(self.zoneId)

    def delete(self):
        if self.door2:
            self.door2.requestDelete()
            self.door2 = None
        DistributedToonInteriorAI.DistributedToonInteriorAI.delete(self)
