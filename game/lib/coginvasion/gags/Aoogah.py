########################################
# Filename: Aoogah.py
# Created by: DecodedLogic (08Aug15)
########################################

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.gags import GagGlobals
from lib.coginvasion.gags.SoundGag import SoundGag
from direct.interval.IntervalGlobal import Parallel, Sequence, Func, Wait, SoundInterval, ActorInterval
from panda3d.core import Vec3

class Aoogah(SoundGag):

    def __init__(self):
        SoundGag.__init__(self, CIGlobals.Aoogah, 'phase_5/models/props/aoogah.bam',
                          16, GagGlobals.AOOGAH_APPEAR_SFX, GagGlobals.AOOGAH_SFX, soundRange = 30, hitSfx = None)
        self.setImage('phase_3.5/maps/aoogah.png')
        self.setRechargeTime(5.5)

    def start(self):
        SoundGag.start(self)
        delayTime = 2.45
        delayUntilAppearSound = 1.0
        INSTRUMENT_SCALE_MODIFIER = 0.5
        tracks = Parallel()
        instrMin = Vec3(0.001, 0.001, 0.001)
        instrMax = Vec3(0.5, 0.5, 0.5)
        instrMax *= INSTRUMENT_SCALE_MODIFIER
        instrStretch = Vec3(1.1, 0.9, 0.4)
        instrStretch *= INSTRUMENT_SCALE_MODIFIER

        def setInstrumentStats():
            self.gag.setPos(-1.0, -1.5, 0.2)
            self.gag.setHpr(145, 0, 85)
            self.gag.setScale(instrMin)

        megaphoneSh = Sequence(Func(self.placeProp, self.handJoint, self.megaphone), Func(self.placeProp, self.handJoint, self.gag), Func(setInstrumentStats))
        grow = self.getScaleIntervals(self.gag, duration=0.2, startScale=instrMin, endScale=instrMax)
        instrumentAppear = Parallel(grow)
        stretchInstr = self.getScaleBlendIntervals(self.gag, duration=0.2, startScale=instrMax, endScale=instrStretch, blendType='easeOut')
        backInstr = self.getScaleBlendIntervals(self.gag, duration=0.2, startScale=instrStretch, endScale=instrMax, blendType='easeInOut')
        attackTrack = Sequence(stretchInstr, Wait(1), backInstr)
        megaphoneTrack = Sequence(megaphoneSh, Wait(delayUntilAppearSound), SoundInterval(self.appearSfx, node=self.avatar), Wait(delayTime + 1.0), instrumentAppear)
        tracks.append(megaphoneTrack)
        tracks.append(ActorInterval(self.avatar, 'sound'))
        instrumentshrink = self.getScaleIntervals(self.gag, duration=0.1, startScale=instrMax, endScale=instrMin)
        soundTrack = Sequence(Wait(delayTime), Parallel(attackTrack, SoundInterval(self.soundSfx, node=self.avatar), Sequence(Wait(1.5), instrumentshrink), Func(self.damageCogsNearby), Wait(0.4), Func(self.finish)))
        tracks.append(soundTrack)
        tracks.start()
        self.tracks = tracks
