"""

  Filename: JugglingBalls.py
  Created by: DecodedLogic (18Jul15)

"""

from lib.coginvasion.gags.ToonUpGag import ToonUpGag
from lib.coginvasion.gags import GagGlobals
from lib.coginvasion.globals import CIGlobals
from direct.interval.IntervalGlobal import Sequence, Func, Parallel, ActorInterval

class JugglingBalls(ToonUpGag):

    def __init__(self):
        ToonUpGag.__init__(self, CIGlobals.JugglingBalls,
                           'phase_5/models/props/cubes-mod.bam', 90, 120, 100, GagGlobals.JUGGLE_SFX, 1, anim = 'phase_5/models/props/cubes-chan.bam')
        self.setImage('phase_3.5/maps/juggling-cubes.png')
        self.track = None
        self.soundInterval = None
        self.timeout = 8.0

    def start(self):
        super(JugglingBalls, self).start()
        self.setupHips()
        self.build()
        self.placeProp(self.hips, self.gag)
        self.soundInterval = self.getSoundTrack(0.7, self.gag, 7.7)
        propInterval = Sequence()
        propInterval.append(ActorInterval(self.gag, 'chan'))
        if self.avatar == base.localAvatar:
            propInterval.append(Func(self.setHealAmount))
            propInterval.append(Func(self.healNearbyAvatars, 25))
        propInterval.append(Func(self.cleanupGag))
        propInterval.append(Func(self.reset))
        self.track = Parallel(ActorInterval(self.avatar, 'juggle'), propInterval, Func(self.soundInterval.start))
        self.track.start()

    def equip(self):
        # self.gag returns the juggling balls.
        super(JugglingBalls, self).equip()

    def unEquip(self):
        if self.track:
            self.soundInterval.finish()
            self.track.finish()
            self.track = None
        self.reset()
