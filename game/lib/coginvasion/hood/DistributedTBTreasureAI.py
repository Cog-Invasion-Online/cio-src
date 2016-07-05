"""

  Filename: DistributedTBTreasureAI.py
  Created by: DecodedLogic (15Jul15)

"""

from lib.coginvasion.hood.DistributedTreasureAI import DistributedTreasureAI

class DistributedTBTreasureAI(DistributedTreasureAI):

    def __init__(self, air, treasurePlanner, x, y, z):
        DistributedTreasureAI.__init__(self, air, treasurePlanner, x, y, z)
