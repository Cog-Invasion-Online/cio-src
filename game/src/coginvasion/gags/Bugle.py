########################################
# Filename: Bugle.py
# Created by: DecodedLogic (10Aug15)
########################################

from src.coginvasion.globals import CIGlobals
from src.coginvasion.gags import GagGlobals
from src.coginvasion.gags.SoundGag import SoundGag
from direct.interval.IntervalGlobal import Parallel, Sequence, Func, Wait, SoundInterval, ActorInterval
from pandac.PandaModules import Vec3

class Bugle(SoundGag):

    def __init__(self):
        SoundGag.__init__(self, CIGlobals.Bugle, 'phase_5/models/props/bugle.bam', 11,
                          GagGlobals.BUGLE_APPEAR_SFX, GagGlobals.BUGLE_SFX, soundRange = 25, hitSfx = None)
        self.setImage('phase_3.5/maps/bugle.png')
        self.setRechargeTime(4.5)

    def start(self):
        SoundGag.start(self)
        INSTRUMENT_SCALE_MODIFIER = 0.5
        tracks = Parallel()
        instrMin = Vec3(0.001, 0.001, 0.001)
        instrMax = Vec3(0.4, 0.4, 0.4)
        instrMax *= INSTRUMENT_SCALE_MODIFIER
        instrStretch = Vec3(0.5, 0.5, 0.5)
        instrStretch *= INSTRUMENT_SCALE_MODIFIER

        def setInstrumentStats():
            self.gag.setPos(-1.3, -1.4, 0.1)
            self.gag.setHpr(145, 0, 85)
            self.gag.setScale(instrMin)

        def longshake(models, num):
            inShake = self.getScaleBlendIntervals(models, duration=0.2, startScale=instrMax, endScale=instrStretch, blendType='easeInOut')
            outShake = self.getScaleBlendIntervals(models, duration=0.2, startScale=instrStretch, endScale=instrMax, blendType='easeInOut')
            i = 1
            seq = Sequence()
            while i < num:
                if i % 2 == 0:
                    seq.append(inShake)
                else:
                    seq.append(outShake)
                i += 1

            seq.start()
        megaphoneShow = Sequence(Func(self.placeProp, self.handJoint, self.megaphone), Func(self.placeProp, self.handJoint, self.gag), Func(setInstrumentStats))
        grow = self.getScaleBlendIntervals(self.gag, duration=1, startScale=instrMin, endScale=instrMax, blendType='easeInOut')
        instrumentshrink = self.getScaleIntervals(self.gag, duration=0.1, startScale=instrMax, endScale=instrMin)
        instrumentAppear = Sequence(grow, Wait(0), Func(longshake, self.gag, 5))
        megaphoneTrack = Parallel(Sequence(Wait(1.7), SoundInterval(self.soundSfx, node=self.avatar)), Sequence(megaphoneShow, Wait(1.7), instrumentAppear, Wait(1),
                                           Func(self.damageCogsNearby), instrumentshrink, Wait(0.4), Func(self.finish)))
        tracks.append(megaphoneTrack)
        tracks.append(ActorInterval(self.avatar, 'sound'))
        tracks.start()
        self.tracks = tracks
