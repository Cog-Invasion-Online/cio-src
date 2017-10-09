"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedMLTreasureAI.py
@author Brian Lach
@date July 29, 2015

"""

import DistributedTreasureAI

class DistributedMLTreasureAI(DistributedTreasureAI.DistributedTreasureAI):

    def __init__(self, air, planner, x, y, z):
        DistributedTreasureAI.DistributedTreasureAI.__init__(self, air, planner, x, y, z)
