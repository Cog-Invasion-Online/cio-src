"""

  Filename: DistributedTTCTreasure.py
  Created by: DecodedLogic (15Jul15)

"""

from DistributedTreasure import DistributedTreasure
from src.coginvasion.holiday.HolidayManager import HolidayType

class DistributedTTCTreasure(DistributedTreasure):
    __module__ = __name__

    def __init__(self, cr):
        DistributedTreasure.__init__(self, cr)
        self.modelPath = 'phase_4/models/props/icecream.bam'
        self.grabSoundPath = 'phase_4/audio/sfx/SZ_DD_treasure.ogg'