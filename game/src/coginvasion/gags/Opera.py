"""

  Filename: Opera.py
  Created by: DecodedLogic (09Aug15)

"""

from src.coginvasion.globals import CIGlobals
from src.coginvasion.gags import GagGlobals
from src.coginvasion.gags.SoundGag import SoundGag
from direct.interval.IntervalGlobal import Parallel, Sequence, Func, Wait, SoundInterval, ParticleInterval, ActorInterval
from pandac.PandaModules import Vec3, Point3
from direct.particles.ParticleEffect import ParticleEffect

class Opera(SoundGag):

    def __init__(self):
        SoundGag.__init__(self, CIGlobals.Opera, 'phase_5/models/props/singing.bam', 90, appearSfx = GagGlobals.FOG_APPEAR_SFX,
                          soundSfx = GagGlobals.OPERA_SFX, soundRange = 50, hitSfx = GagGlobals.OPERA_HIT_SFX)
        self.setImage('phase_3.5/maps/opera.png')

    def __createToonInterval(self, delay):
        track = Sequence(Wait(delay))
        sprayEffect = ParticleEffect()
        sprayEffect.loadConfig('phase_5/etc/soundWave.ptf')
        sprayEffect.setDepthWrite(0)
        sprayEffect.setDepthTest(0)
        sprayEffect.setTwoSided(1)
        I1 = 2.8
        track.append(ActorInterval(self.avatar, 'sound', playRate = 1.0, startTime = 0.0, endTime = I1))
        track.append(Func(self.setPosFromOther, sprayEffect, self.gag, Point3(0, 1.6, -0.18)))
        track.append(self.__getPartTrack(sprayEffect, 0.0, 6.0, [sprayEffect, self.avatar, 0], softStop=-3.5))
        track.append(ActorInterval(self.avatar, 'sound', playRate = 1.0, startTime = I1))
        return track

    def __getPartTrack(self, particleEffect, startDelay, durationDelay, partExtraArgs, softStop = 0):
        pEffect = partExtraArgs[0]
        parent = partExtraArgs[1]
        if len(partExtraArgs) == 3:
            worldRelative = partExtraArgs[2]
        else:
            worldRelative = 1
        return Sequence(Wait(startDelay), ParticleInterval(pEffect, parent, worldRelative, duration=durationDelay, cleanup=True, softStopT=softStop))

    def start(self):
        SoundGag.start(self)
        tracks = Parallel()
        delay = 2.45
        INSTRUMENT_SCALE_MODIFIER = 0.5
        instrMin = Vec3(0.001, 0.001, 0.001)
        instrMax1 = Vec3(1.7, 1.7, 1.7)
        instrMax1 *= INSTRUMENT_SCALE_MODIFIER
        instrMax2 = Vec3(2.2, 2.2, 2.2)
        instrMax2 *= INSTRUMENT_SCALE_MODIFIER
        instrStretch = Vec3(0.4, 0.4, 0.4)
        instrStretch *= INSTRUMENT_SCALE_MODIFIER
        head = self.gag.find('**/opera_singer')
        head.setPos(0, 0, 0)

        def setInstrumentStats():
            newPos = Vec3(-0.8, -0.9, 0.2)
            newPos *= 1.3
            self.gag.setPos(newPos[0], newPos[1], newPos[2])
            self.gag.setHpr(145, 0, 90)
            self.gag.setScale(instrMin)

        megaphoneShow = Sequence(Func(self.placeProp, self.handJoint, self.megaphone), Func(self.placeProp, self.handJoint, self.gag), Func(setInstrumentStats))
        grow1 = self.getScaleBlendIntervals(self.gag, duration=1, startScale=instrMin, endScale=instrMax1, blendType='easeOut')
        grow2 = self.getScaleBlendIntervals(self.gag, duration=1.1, startScale=instrMax1, endScale=instrMax2, blendType='easeIn')
        shrink2 = self.getScaleIntervals(self.gag, duration=0.1, startScale=instrMax2, endScale=instrMin)
        instrumentAppear = Parallel(Sequence(grow1, grow2, Wait(6.0), shrink2, Wait(0.4), Func(self.finish)), SoundInterval(self.appearSfx, node=self.avatar))
        delayTime = delay
        megaphoneTrack = Sequence(megaphoneShow, Wait(delayTime + 1.0), instrumentAppear)
        tracks.append(megaphoneTrack)
        toonTrack = self.__createToonInterval(0)
        tracks.append(toonTrack)
        soundTrack = Sequence(Wait(delayTime), Parallel(SoundInterval(self.soundSfx, node=self.avatar), Func(self.damageCogsNearby)))
        tracks.append(soundTrack)
        tracks.start()
        self.tracks = tracks
