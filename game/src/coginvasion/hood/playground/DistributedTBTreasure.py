"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedTBTreasure.py
@author Maverick Liberty
@date July 15, 2015

"""

from DistributedTreasure import DistributedTreasure

class DistributedTBTreasure(DistributedTreasure):

    def __init__(self, cr):
        DistributedTreasure.__init__(self, cr)
        self.modelPath = 'phase_8/models/props/snowflake_treasure.bam'
        self.grabSoundPath = 'phase_4/audio/sfx/SZ_DD_treasure.ogg'
