"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Aoogah.py
@author Maverick Liberty
@date August 08, 2015

"""

from src.coginvasion.gags import GagGlobals
from src.coginvasion.gags.SoundGag import SoundGag
from direct.interval.IntervalGlobal import Parallel, Sequence, Func, Wait, SoundInterval, ActorInterval
from panda3d.core import Vec3

class Aoogah(SoundGag):
    
    name = GagGlobals.Aoogah
    model = 'phase_5/models/props/aoogah.bam'
    appearSfxPath = GagGlobals.AOOGAH_APPEAR_SFX
    soundSfxPath = GagGlobals.AOOGAH_SFX
    soundRange = 30

    def __init__(self):
        SoundGag.__init__(self)
        self.setImage('phase_3.5/maps/aoogah.png')
        #self.setRechargeTime(5.5)

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
            
        track = Sequence(
            Parallel(
                # Let's show the megaphone and the gag.
                Sequence(
                    Sequence(
                        Func(self.placeProp, self.handJoint, self.megaphone),
                        Func(self.placeProp, self.handJoint, self.gag),
                        Func(setInstrumentStats)
                    ),
                    Wait(delayUntilAppearSound),
                    SoundInterval(self.appearSfx, node=self.avatar),
                    Wait(delayTime + 1.0),
                    self.getScaleIntervals(
                        self.gag, 
                        duration=0.2, 
                        startScale=instrMin, 
                    endScale=instrMax)
                ),
                Parallel(
                    Func(self.avatar.setForcedTorsoAnim, 'sound'),
                    self.getAnimationTrack('sound')
                ),
                Sequence(
                    Wait(delayTime),
                    Parallel(
                        Sequence(
                            self.getScaleBlendIntervals(self.gag, 
                                duration=0.2, 
                                startScale=instrMax, 
                                endScale=instrStretch, 
                            blendType='easeOut'),
                            Wait(1.0),
                            self.getScaleBlendIntervals(self.gag,
                                duration=0.2,
                                startScale=instrStretch,
                                endScale=instrMax,
                            blendType='easeInOut'),
                            SoundInterval(self.soundSfx, node=self.avatar),
                            Sequence(
                                Wait(1.5),
                                self.getScaleIntervals(self.gag,
                                    duration=0.1,
                                    startScale=instrMax,
                                endScale=instrMin)
                            ),
                            Func(self.damageCogsNearby),
                            Wait(0.4),
                        )
                    )
                )
            ), Func(self.finish)
        )
        

        megaphoneSh = Sequence(
            Func(self.placeProp, self.handJoint, self.megaphone), 
            Func(self.placeProp, self.handJoint, self.gag), 
        Func(setInstrumentStats))
        instrumentAppear = Parallel(self.getScaleIntervals(self.gag, duration=0.2, startScale=instrMin, endScale=instrMax))
        stretchInstr = self.getScaleBlendIntervals(self.gag, 
            duration=0.2, 
            startScale=instrMax, 
            endScale=instrStretch,
        blendType='easeOut')
        backInstr = self.getScaleBlendIntervals(self.gag, 
            duration=0.2, 
            startScale=instrStretch, 
            endScale=instrMax, 
        blendType='easeInOut')
        attackTrack = Sequence(stretchInstr, Wait(1.0), backInstr)
        megaphoneTrack = Sequence(megaphoneSh, 
            Wait(delayUntilAppearSound), 
            SoundInterval(self.appearSfx, node=self.avatar), 
            Wait(delayTime + 1.0), 
        instrumentAppear)
        tracks.append(megaphoneTrack)
        tracks.append(self.getSingularAnimTrack('sound'))
        instrumentshrink = self.getScaleIntervals(self.gag, 
            duration=0.1, 
            startScale=instrMax, 
        endScale=instrMin)
        soundTrack = Sequence(Wait(delayTime), 
            Parallel(attackTrack, 
                SoundInterval(self.soundSfx, node=self.avatar), 
                Sequence(Wait(1.5), 
                    instrumentshrink), 
                Func(self.damageCogsNearby), 
                Wait(0.4), 
            Func(self.finish))
        )
        tracks.append(soundTrack)
        self.setAnimTrack(tracks)
        tracks.start()
