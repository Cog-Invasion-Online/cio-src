"""

  Filename: DistributedTTCTreasure.py
  Created by: DecodedLogic (15Jul15)

"""

from lib.coginvasion.hood.DistributedTreasure import DistributedTreasure
from lib.coginvasion.holiday.HolidayManager import HolidayType

class DistributedTTCTreasure(DistributedTreasure):
    __module__ = __name__

    def __init__(self, cr):
        DistributedTreasure.__init__(self, cr)
        self.modelPath = 'phase_4/models/props/icecream.bam'
        self.grabSoundPath = 'phase_4/audio/sfx/SZ_DD_treasure.ogg'
        
        if self.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS:
            self.modelPath = 'phase_6/models/karting/qbox.bam'