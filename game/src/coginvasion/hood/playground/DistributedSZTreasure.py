"""

  Filename: DistributedSZTreasure.py
  Created by: DecodedLogic (15Jul15)

"""

from DistributedTreasure import DistributedTreasure

class DistributedSZTreasure(DistributedTreasure):

    def __init__(self, cr):
        DistributedTreasure.__init__(self, cr)

    def delete(self):
        DistributedTreasure.delete(self)
