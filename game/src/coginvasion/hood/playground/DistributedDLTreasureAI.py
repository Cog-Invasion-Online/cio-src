"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedDLTreasureAI.py
@author Brian Lach
@date July 29, 2015

"""

import DistributedTreasureAI

class DistributedDLTreasureAI(DistributedTreasureAI.DistributedTreasureAI):

    def __init__(self, air, treasurePlanner, x, y, z):
        DistributedTreasureAI.DistributedTreasureAI.__init__(self, air, treasurePlanner, x, y, z)
