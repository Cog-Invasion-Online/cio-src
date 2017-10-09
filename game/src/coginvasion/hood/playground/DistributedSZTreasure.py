"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedSZTreasure.py
@author Brian Lach
@date July 15, 2015

"""

from DistributedTreasure import DistributedTreasure

class DistributedSZTreasure(DistributedTreasure):

    def __init__(self, cr):
        DistributedTreasure.__init__(self, cr)

    def delete(self):
        DistributedTreasure.delete(self)
