"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file BikeHorn.py
@author Maverick Liberty
@date August 10, 2015

"""

from src.coginvasion.gags import GagGlobals
from src.coginvasion.gags.SoundGag import SoundGag
from direct.interval.IntervalGlobal import Parallel, Sequence, Func, Wait, SoundInterval, ActorInterval
from panda3d.core import Vec3

class BikeHorn(SoundGag):

    def __init__(self):
        SoundGag.__init__(self, GagGlobals.BikeHorn, 'phase_5/models/props/bikehorn.bam', 5,
                          GagGlobals.BIKE_HORN_APPEAR_SFX, GagGlobals.BIKE_HORN_SFX, hitSfx = None)
        self.setImage('phase_3.5/maps/bike-horn.png')
        self.setRechargeTime(2.5)

    def start(self):
        SoundGag.start(self)
        INSTRUMENT_SCALE_MODIFIER = 0.5
        delayTime = 2.45
        delayUntilAppearSound = 1.0
        tracks = Parallel()
        instrMin = Vec3(0.001, 0.001, 0.001)
        instrMax = Vec3(0.65, 0.65, 0.65)
        instrMax *= INSTRUMENT_SCALE_MODIFIER
        instrStretch = Vec3(0.6, 1.1, 0.6)
        instrStretch *= INSTRUMENT_SCALE_MODIFIER

        def setInstrumentStats():
            self.gag.setPos(-1.1, -1.4, 0.1)
            self.gag.setHpr(145, 0, 0)
            self.gag.setScale(instrMin)

        megaphoneShow = Sequence(Func(self.placeProp, self.handJoint, self.megaphone), Func(self.placeProp, self.handJoint, self.gag), Func(setInstrumentStats))
        grow = self.getScaleIntervals(self.gag, duration=0.2, startScale=instrMin, endScale=instrMax)
        instrumentAppear = grow
        stretchInstr = self.getScaleBlendIntervals(self.gag, duration=0.2, startScale=instrMax, endScale=instrStretch, blendType='easeOut')
        backInstr = self.getScaleBlendIntervals(self.gag, duration=0.2, startScale=instrStretch, endScale=instrMax, blendType='easeIn')
        stretchMega = self.getScaleBlendIntervals(self.megaphone, duration=0.2, startScale=self.megaphone.getScale(), endScale=0.9, blendType='easeOut')
        backMega = self.getScaleBlendIntervals(self.megaphone, duration=0.2, startScale=0.9, endScale=self.megaphone.getScale(), blendType='easeIn')
        attackTrack = Parallel(Sequence(stretchInstr, backInstr), Sequence(stretchMega, backMega))
        megaphoneTrack = Sequence(megaphoneShow, Wait(delayUntilAppearSound), SoundInterval(self.appearSfx, node=self.avatar), instrumentAppear)
        tracks.append(megaphoneTrack)
        tracks.append(self.getSingularAnimTrack('sound'))
        instrumentshrink = self.getScaleIntervals(self.gag, duration=0.1, startScale=instrMax, endScale=instrMin)
        soundTrack = Sequence(Wait(delayTime), Parallel(attackTrack, SoundInterval(self.soundSfx, node=self.avatar), Wait(0.2), instrumentshrink, Func(self.damageCogsNearby), Wait(0.4), Func(self.finish)))
        tracks.append(soundTrack)
        tracks.start()
        self.tracks = tracks
