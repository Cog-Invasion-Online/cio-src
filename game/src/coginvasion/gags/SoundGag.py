"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file SoundGag.py
@author Maverick Liberty
@date August 07, 2015

"""

from src.coginvasion.globals import CIGlobals
from src.coginvasion.gags.Gag import Gag
from src.coginvasion.gags.GagType import GagType
from src.coginvasion.gags.GagState import GagState
from src.coginvasion.gags import GagGlobals
from src.coginvasion.base.CIParticleEffect import CIParticleEffect
from direct.interval.IntervalGlobal import Sequence, Wait, Func, SoundInterval
from panda3d.core import Point3
import random

class SoundGag(Gag):

    def __init__(self, name, model, damage, appearSfx, soundSfx, soundRange = 18, hitSfx = None):
        Gag.__init__(self, name, model, GagType.SOUND, hitSfx, anim = None, scale = 1)
        self.appearSfx = None
        self.soundSfx = None
        self.soundRange = soundRange
        self.megaphonePath = 'phase_5/models/props/megaphone.bam'
        self.megaphone = None
        self.tracks = None
        self.timeout = 5.0

        if game.process == 'client':
            self.appearSfx = base.audio3d.loadSfx(appearSfx)
            self.soundSfx = base.audio3d.loadSfx(soundSfx)

    def start(self):
        Gag.start(self)
        if self.isLocal():
            self.startTimeout()
        if self.tracks:
            self.tracks.pause()
            self.tracks = None
        self.build()
        base.audio3d.attachSoundToObject(self.soundSfx, self.avatar)
        base.audio3d.attachSoundToObject(self.appearSfx, self.avatar)
        if self.isLocal():
            base.localAvatar.sendUpdate('usedGag', [self.id])

    def finish(self):
        self.reset()
        self.tracks = None
        Sequence(Wait(1.5), Func(self.cleanupGag)).start()

    def unEquip(self):
        Gag.unEquip(self)
        self.finish()

    def damageCogsNearby(self, radius = None):
        if self.avatar.doId != base.localAvatar.doId:
            return
        if not radius:
            radius = self.soundRange
        suits = []
        for obj in base.avatars:
            if CIGlobals.isAvatar(obj):
                if obj.getDistance(self.avatar) <= radius:
                    if self.avatar.doId == base.localAvatar.doId:
                        suits.append(obj)
        def shouldContinue(suit, track):
            if suit.isDead():
                track.finish()
        for suit in suits:
            if self.name != GagGlobals.Opera:
                suit.handleHitByToon(self.avatar, self.getID(), obj.getDistance(self.avatar))
            else:
                breakEffect = CIParticleEffect()
                breakEffect.loadConfig('phase_5/etc/soundBreak.ptf')
                breakEffect.setDepthWrite(0)
                breakEffect.setDepthTest(0)
                breakEffect.setTwoSided(1)
                suitTrack = Sequence()
                if suit.isDead():
                    return
                suitTrack.append(Wait(2.5))
                delayTime = random.random()
                suitTrack.append(Wait(delayTime + 2.0))
                suitTrack.append(Func(shouldContinue, suit, suitTrack))
                suitTrack.append(Func(self.setPosFromOther, breakEffect, suit, Point3(0, 0, 0)))
                suitTrack.append(SoundInterval(self.hitSfx, node=suit))
                suitTrack.append(Func(suit.handleHitByToon, self.avatar, self.getID(), obj.getDistance(self.avatar)))
                suitTrack.start()
        suits = None

    def setPosFromOther(self, dest, source, offset = Point3(0, 0, 0)):
        if not source:
            return
        pos = render.getRelativePoint(source, offset)
        dest.setPos(pos)
        dest.reparentTo(render)

    def build(self):
        Gag.build(self)
        self.megaphone = loader.loadModel(self.megaphonePath)

    def cleanupGag(self):
        if self.state == GagState.LOADED or self.state == GagState.RECHARGING:
            Gag.cleanupGag(self)
            if CIGlobals.isNodePathOk(self.megaphone):
                if CIGlobals.isNodePathOk(self.avatar):
                    copies = self.avatar.findAllMatches('**/%s' % self.megaphone.getName())
                    for copy in copies:
                        copy.removeNode()
            self.megaphone = None
