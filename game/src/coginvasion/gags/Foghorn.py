"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Foghorn.py
@author Maverick Liberty
@date August 07, 2015

"""

from src.coginvasion.globals import CIGlobals
from src.coginvasion.gags.SoundGag import SoundGag
from src.coginvasion.gags import GagGlobals
from direct.interval.IntervalGlobal import Parallel, Sequence, Func, Wait, SoundInterval, LerpHprInterval, ActorInterval
from panda3d.core import Vec3

class Foghorn(SoundGag):

    def __init__(self):
        SoundGag.__init__(self, CIGlobals.Foghorn, 'phase_5/models/props/fog_horn.bam', 50, GagGlobals.FOG_APPEAR_SFX,
                          GagGlobals.FOG_SFX, soundRange = 40, hitSfx = None)
        self.setImage('phase_3.5/maps/fog-horn.png')
        self.setRechargeTime(14.5)

    def start(self):
        SoundGag.start(self)
        tracks = Parallel()
        delayTime = 2.45
        delayUntilAppearSound = 1.0
        INSTRUMENT_SCALE_MODIFIER = 0.5
        instrMin = Vec3(0.001, 0.001, 0.001)
        instrMax1 = Vec3(0.1, 0.1, 0.1)
        instrMax1 *= INSTRUMENT_SCALE_MODIFIER
        instrMax2 = Vec3(0.3, 0.3, 0.3)
        instrMax2 *= INSTRUMENT_SCALE_MODIFIER
        instrStretch = Vec3(0.4, 0.4, 0.4)
        instrStretch *= INSTRUMENT_SCALE_MODIFIER
        def setInstrumentStats():
            self.gag.setPos(-0.8, -0.9, 0.2)
            self.gag.setHpr(145, 0, 0)
            self.gag.setScale(instrMin)
        megaphoneSh = Sequence(Func(self.placeProp, self.handJoint, self.megaphone), Func(self.placeProp, self.handJoint, self.gag), Func(setInstrumentStats))
        grow = self.getScaleIntervals(self.gag, duration=1, startScale=instrMin, endScale=instrMax1)
        instrumentAppear = Parallel(grow)
        stretchInstr = self.getScaleBlendIntervals(self.gag, duration=0.3, startScale=instrMax2, endScale=instrStretch, blendType='easeOut')
        backInstr = self.getScaleBlendIntervals(self.gag, duration=1.0, startScale=instrStretch, endScale=instrMin, blendType='easeIn')
        spinInstr = LerpHprInterval(self.gag, duration=1.5, startHpr=Vec3(145, 0, 0), hpr=Vec3(145, 0, 90), blendType='easeInOut')
        attackTrack = Parallel(Sequence(Wait(0.2), spinInstr), Sequence(stretchInstr, Wait(0.5), backInstr))
        megaphoneTrack = Sequence(megaphoneSh, Wait(delayUntilAppearSound), SoundInterval(self.appearSfx, node=self.avatar), Wait(delayTime + 1.0), instrumentAppear)
        tracks.append(megaphoneTrack)
        tracks.append(ActorInterval(self.avatar, 'sound'))
        soundTrack = Sequence(Wait(delayTime), Parallel(attackTrack, SoundInterval(self.soundSfx, node=self.avatar), Func(self.damageCogsNearby), Wait(0.4), Func(self.finish)))
        tracks.append(soundTrack)
        tracks.start()
        self.tracks = tracks
