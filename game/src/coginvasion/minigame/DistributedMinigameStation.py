"""

  Filename: DistributedMinigameStation.py
  Created by: blach (04Oct14)

"""

from direct.distributed.DistributedObject import DistributedObject
from direct.interval.IntervalGlobal import Sequence, Wait, Func
from direct.directnotify.DirectNotify import DirectNotify
import MinigameStation
from DistributedGroupStation import DistributedGroupStation

class DistributedMinigameStation(DistributedGroupStation, MinigameStation.MinigameStation, DistributedObject):
    notify = DirectNotify().newCategory("DistributedMinigameStation")

    def __init__(self, cr):
        try:
            self.DistributedMinigameStation_initialized
            return
        except:
            self.DistributedMinigameStation_initialized = 1
        MinigameStation.MinigameStation.__init__(self)
        DistributedObject.__init__(self, cr)
        return

    def setStation(self, game):
        self.generateStation(game)

    def headOff(self, zone, laffMeter):
        if self.camIval:
            self.camIval.finish()
            self.camIval = None
        self.deleteStationAbortGui()
        requestStatus = {'zoneId': zone,
                    'hoodId': self.cr.playGame.hood.hoodId,
                    'where': 'minigame',
                    'avId': base.localAvatar.doId,
                    'loader': 'minigame',
                    'shardId': None,
                    'wantLaffMeter': laffMeter}
        self.cr.playGame.getPlace().fsm.request('teleportOut', [requestStatus])
        Sequence(Wait(3.0), Func(self.d_leaving)).start()
