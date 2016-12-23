# Filename: DistributedDLTreasureAI.py
# Created by:  blach (29Jul15)

import DistributedTreasureAI

class DistributedDLTreasureAI(DistributedTreasureAI.DistributedTreasureAI):

    def __init__(self, air, treasurePlanner, x, y, z):
        DistributedTreasureAI.DistributedTreasureAI.__init__(self, air, treasurePlanner, x, y, z)
