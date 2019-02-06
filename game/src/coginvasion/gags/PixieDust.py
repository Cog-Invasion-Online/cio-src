"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file PixieDust.py
@author Maverick Liberty
@date August 10, 2015

"""

from src.coginvasion.globals import CIGlobals
from src.coginvasion.gags import GagGlobals
from src.coginvasion.gags.ToonUpGag import ToonUpGag
from src.coginvasion.base.CIParticleEffect import CIParticleEffect
from direct.interval.IntervalGlobal import Parallel, Sequence, Func, Wait, ParticleInterval, ActorInterval
from panda3d.core import Point3

class PixieDust(ToonUpGag):
    
    name = GagGlobals.PixieDust
    minHeal = 50
    maxHeal = 70
    efficiency = 85
    hitSfxPath = GagGlobals.PIXIE_DUST_SFX

    def __init__(self):
        ToonUpGag.__init__(self)
        self.setImage('phase_3.5/maps/pixie-dust.png')
        self.radius = 25
        self.timeout = 4.0

    def createParticle(self, particleFile):
        particle = CIParticleEffect()
        particle.loadConfig('phase_5/etc/%s.ptf' % (particleFile))
        particle.hide(CIGlobals.ShadowCameraBitmask)
        return particle

    def doPixieDust(self, target):
        sprayEffect = self.createParticle('pixieSpray')
        dropEffect = self.createParticle('pixieDrop')
        explodeEffect = self.createParticle('pixieExplode')
        poofEffect = self.createParticle('pixiePoof')
        wallEffect = self.createParticle('pixieWall')

        def face90():
            vec = Point3(target.getPos() - self.avatar.getPos())
            vec.setZ(0)
            temp = vec[0]
            vec.setX(-vec[1])
            vec.setY(temp)
            targetPoint = Point3(self.avatar.getPos() + vec)
            self.avatar.headsUp(render, targetPoint)

        def doHeal():
            if self.isLocal():
                self.healAvatar(target, 'conked')
                base.localAvatar.sendUpdate('gagRelease', [self.getID()])

        delay = 2.5
        track = Sequence()
        mtrack = Parallel(self.__getPartTrack(sprayEffect, 1.5, 0.5, [sprayEffect, self.avatar, 0]),
                          self.__getPartTrack(dropEffect, 1.9, 2.0, [dropEffect, target, 0]),
                          self.__getPartTrack(explodeEffect, 2.7, 1.0, [explodeEffect, self.avatar, 0]),
                          self.__getPartTrack(poofEffect, 3.4, 1.0, [poofEffect, target, 0]),
                          self.__getPartTrack(wallEffect, 4.05, 1.2, [wallEffect, self.avatar, 0]),
                          self.getSoundTrack(0, self.avatar, 4.1), Sequence(Func(face90), 
                            ActorInterval(self.avatar, 'sprinkle-dust')),
                          Sequence(Wait(delay), Func(doHeal)))
        track.append(mtrack)
        track.append(Func(self.reset))
        track.start()

    def __getPartTrack(self, particleEffect, startDelay, durationDelay, partExtraArgs):
        pEffect = partExtraArgs[0]
        parent = partExtraArgs[1]
        if len(partExtraArgs) == 3:
            worldRelative = partExtraArgs[2]
        else:
            worldRelative = 1
        return Sequence(Wait(startDelay), ParticleInterval(pEffect, parent, worldRelative, duration=durationDelay, cleanup=True))

    def start(self):
        ToonUpGag.start(self)
        if self.isLocal():
            target = self.getClosestAvatar(self.radius)
            if target:
                self.doPixieDust(target)
                self.avatar.sendUpdate('setTarget', [self.getID(), target.doId])
            else:
                self.reset()

    def setTarget(self, target):
        ToonUpGag.setTarget(self, target)
        self.doPixieDust(target)
