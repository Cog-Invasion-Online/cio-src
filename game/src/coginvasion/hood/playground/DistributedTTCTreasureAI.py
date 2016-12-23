"""

  Filename: DistributedTTCTreasureAI.py
  Created by: DecodedLogic (15Jul15)

"""

from DistributedTreasureAI import DistributedTreasureAI

class DistributedTTCTreasureAI(DistributedTreasureAI):

    def __init__(self, air, treasurePlanner, x, y, z):
        DistributedTreasureAI.__init__(self, air, treasurePlanner, x, y, z)
