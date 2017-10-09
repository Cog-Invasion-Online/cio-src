"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedTBTreasureAI.py
@author Maverick Liberty
@date July 15, 2015

"""

from DistributedTreasureAI import DistributedTreasureAI

class DistributedTBTreasureAI(DistributedTreasureAI):

    def __init__(self, air, treasurePlanner, x, y, z):
        DistributedTreasureAI.__init__(self, air, treasurePlanner, x, y, z)
