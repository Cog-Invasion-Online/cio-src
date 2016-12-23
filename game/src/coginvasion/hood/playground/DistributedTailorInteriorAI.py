# Filename: DistributedTailorInteriorAI.py
# Created by:  DecodedLogic (11Aug15)

from src.coginvasion.hood import DistributedToonInteriorAI

class DistributedTailorInteriorAI(DistributedToonInteriorAI.DistributedToonInteriorAI):

    def __init__(self, air, blockZone, doorToZone):
        DistributedToonInteriorAI.DistributedToonInteriorAI.__init__(self, air, blockZone, doorToZone)

    def announceGenerate(self):
        DistributedToonInteriorAI.DistributedToonInteriorAI.announceGenerate(self, doorType = 0)

    def delete(self):
        DistributedToonInteriorAI.DistributedToonInteriorAI.delete(self)