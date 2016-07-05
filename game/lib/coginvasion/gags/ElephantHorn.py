########################################
# Filename: ElephantHorn.py
# Created by: DecodedLogic (08Aug15)
########################################

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.gags import GagGlobals
from lib.coginvasion.gags.SoundGag import SoundGag
from direct.interval.IntervalGlobal import Parallel, Sequence, Func, Wait, SoundInterval, ActorInterval
from panda3d.core import Vec3

class ElephantHorn(SoundGag):

    def __init__(self):
        SoundGag.__init__(self, CIGlobals.ElephantHorn, 'phase_5/models/props/elephant.bam', 21,
                          GagGlobals.ELEPHANT_APPEAR_SFX, GagGlobals.ELEPHANT_SFX, soundRange = 35, hitSfx = None)
        self.setImage('phase_3.5/maps/elephant-horn.png')
        self.setRechargeTime(6.5)

    def start(self):
        SoundGag.start(self)
        tracks = Parallel()
        INSTRUMENT_SCALE_MODIFIER = 0.5
        instrMin = Vec3(0.001, 0.001, 0.001)
        instrMax1 = Vec3(0.3, 0.4, 0.2)
        instrMax1 *= INSTRUMENT_SCALE_MODIFIER
        instrMax2 = Vec3(0.3, 0.3, 0.3)
        instrMax2 *= INSTRUMENT_SCALE_MODIFIER
        instrStretch1 = Vec3(0.3, 0.5, 0.25)
        instrStretch1 *= INSTRUMENT_SCALE_MODIFIER
        instrStretch2 = Vec3(0.3, 0.7, 0.3)
        instrStretch2 *= INSTRUMENT_SCALE_MODIFIER

        def setInstrumentStats():
            self.gag.setPos(-0.6, -0.9, 0.15)
            self.gag.setHpr(145, 0, 85)
            self.gag.setScale(instrMin)

        megaphoneShow = Sequence(Func(self.placeProp, self.handJoint, self.megaphone), Func(self.placeProp, self.handJoint, self.gag), Func(setInstrumentStats))
        grow1 = self.getScaleIntervals(self.gag, duration=0.3, startScale=instrMin, endScale=instrMax1)
        grow2 = self.getScaleIntervals(self.gag, duration=0.3, startScale=instrMax1, endScale=instrMax2)
        instrumentAppear = Parallel(Sequence(grow1, grow2))
        stretchInstr1 = self.getScaleBlendIntervals(self.gag, duration=0.1, startScale=instrMax2, endScale=instrStretch1, blendType='easeOut')
        stretchInstr2 = self.getScaleBlendIntervals(self.gag, duration=0.1, startScale=instrStretch1, endScale=instrStretch2, blendType='easeOut')
        stretchInstr = Sequence(stretchInstr1, stretchInstr2)
        backInstr = self.getScaleBlendIntervals(self.gag, duration=0.1, startScale=instrStretch2, endScale=instrMax2, blendType='easeOut')
        attackTrack = Sequence(stretchInstr, Wait(1), backInstr)
        delayTime = 2.45
        delayUntilAppearSound = 1.0
        megaphoneTrack = Sequence(megaphoneShow, Wait(delayUntilAppearSound), SoundInterval(self.appearSfx, node=self.avatar), Wait(delayTime + 1.0), instrumentAppear)
        tracks.append(megaphoneTrack)
        tracks.append(ActorInterval(self.avatar, 'sound'))
        instrumentshrink = self.getScaleIntervals(self.gag, duration=0.1, startScale=instrMax2, endScale=instrMin)
        soundTrack = Sequence(Wait(delayTime), Parallel(attackTrack, SoundInterval(self.soundSfx, node=self.avatar), Sequence(Wait(1.5), instrumentshrink), Func(self.damageCogsNearby), Wait(0.4), Func(self.finish)))
        tracks.append(soundTrack)
        tracks.start()
        self.tracks = tracks
