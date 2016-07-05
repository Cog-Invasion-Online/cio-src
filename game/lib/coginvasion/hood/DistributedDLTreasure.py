# Filename: DistributedDLTreasure.py
# Created by:  blach (29Jul15)

import DistributedTreasure

class DistributedDLTreasure(DistributedTreasure.DistributedTreasure):

    def __init__(self, cr):
        DistributedTreasure.DistributedTreasure.__init__(self, cr)
        self.modelPath = 'phase_8/models/props/zzz_treasure.bam'
        self.grabSoundPath = 'phase_4/audio/sfx/SZ_DD_treasure.ogg'
