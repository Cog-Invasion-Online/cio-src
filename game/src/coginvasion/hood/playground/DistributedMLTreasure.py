"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedMLTreasure.py
@author Brian Lach
@date July 29, 2015

"""

import DistributedTreasure

class DistributedMLTreasure(DistributedTreasure.DistributedTreasure):

    def __init__(self, cr):
        DistributedTreasure.DistributedTreasure.__init__(self, cr)
        self.modelPath = 'phase_6/models/props/music_treasure.bam'
        self.grabSoundPath = 'phase_4/audio/sfx/SZ_DD_treasure.ogg'
