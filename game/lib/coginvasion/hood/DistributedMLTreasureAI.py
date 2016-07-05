# Filename: DistributedMLTreasureAI.py
# Created by: blach (29Jul15)

import DistributedTreasureAI

class DistributedMLTreasureAI(DistributedTreasureAI.DistributedTreasureAI):

    def __init__(self, air, planner, x, y, z):
        DistributedTreasureAI.DistributedTreasureAI.__init__(self, air, planner, x, y, z)
