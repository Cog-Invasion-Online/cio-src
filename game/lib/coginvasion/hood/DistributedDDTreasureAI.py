# Filename: DistributedDDTreasureAI.py
# Created by:  blach (29Jul15)

import DistributedTreasureAI

class DistributedDDTreasureAI(DistributedTreasureAI.DistributedTreasureAI):

    def __init__(self, air, planner, x, y, z):
        DistributedTreasureAI.DistributedTreasureAI.__init__(self, air, planner, x, y, z)
