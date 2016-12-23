########################################
# Filename: Lipstick.py
# Created by: DecodedLogic (27Jul15)
########################################

from src.coginvasion.gags.ToonUpGag import ToonUpGag
from src.coginvasion.gags import GagGlobals
from src.coginvasion.globals import CIGlobals
from direct.interval.IntervalGlobal import Sequence, Wait, Func, Parallel, LerpPosInterval, LerpScaleInterval, ActorInterval
from pandac.PandaModules import Point3

class Lipstick(ToonUpGag):

    def __init__(self):
        ToonUpGag.__init__(self, CIGlobals.Lipstick,
                           GagGlobals.getProp(5, 'lipstick'), 25, 30, 75, GagGlobals.SMOOCH_SFX, 1)
        self.setImage('phase_3.5/maps/lipstick.png')
        self.avAnim = 'smooch'
        self.track = None
        self.soundInterval = None
        self.lips = None
        self.radius = 25
        self.timeout = 6.0

    def start(self):
        ToonUpGag.start(self)
        self.setupHandJoints()
        self.build()
        if self.isLocal():
            target = self.getClosestAvatar(self.radius)
            if target:
                self.doLipstick(target)
                self.avatar.sendUpdate('setTarget', [self.getID(), target.doId])
            else:
                self.reset()

    def doLipstick(self, target):
        dScale = 0.5
        tLips = 2.5
        animDuration = base.localAvatar.getDuration(self.avAnim)
        tThrow = 115.0 / base.localAvatar.getFrameRate(self.avAnim)

        def doHeal():
            if self.isLocal():
                self.setHealAmount()
                self.healAvatar(target, 'conked')
                base.localAvatar.sendUpdate('gagRelease', [self.getID()])
            else:
                Func(target.play, 'conked').start()

        self.placeProp(self.handJoint, self.gag, Point3(-0.27, -0.24, -0.95), Point3(-118, -10.6, -25.9))
        stickScaleUp = self.getScaleTrack([self.gag], dScale, GagGlobals.PNT3NEAR0, GagGlobals.PNT3NORMAL)
        stickScaleDn = self.getScaleTrack([self.gag], dScale, GagGlobals.PNT3NORMAL, GagGlobals.PNT3NEAR0)
        stickTrack = Sequence(stickScaleUp, Wait(animDuration - 2.0 * dScale), stickScaleDn)

        lipsTrack = Sequence(
            Wait(tLips),
            Func(self.avatar.pose, self.avAnim, 57),
            Func(self.avatar.update, 0),
            Func(self.placeProp, render, self.lips, self.gag.getPos(render)),
            Func(self.lips.setBillboardPointWorld),
            LerpScaleInterval(self.lips, dScale, Point3(3, 3, 3), startScale=GagGlobals.PNT3NEAR0),
            Wait(tThrow - tLips - dScale),
            LerpPosInterval(self.lips, dScale, Point3(target.getPos()), startPos=self.gag.getPos(render)),
            Sequence(Func(doHeal)),
            Func(self.cleanupLips)
        )
        delay = tThrow + dScale
        mainTrack = Parallel(stickTrack, lipsTrack, self.getSoundTrack(delay, self.avatar, 2),
                             ActorInterval(self.avatar, self.avAnim))
        mainTrack.start()

    def setTarget(self, target):
        ToonUpGag.setTarget(self, target)
        self.doLipstick(target)

    def build(self):
        ToonUpGag.build(self)
        self.buildLips()

    def buildLips(self):
        self.cleanupLips()
        self.lips = GagGlobals.loadProp(5, 'lips')

    def cleanupLips(self):
        if self.lips:
            self.lips.removeNode()
            self.lips = None

    def equip(self):
        ToonUpGag.equip(self)

    def unEquip(self):
        if self.track:
            self.soundInterval.finish()
            self.track.finish()
            self.track = None
        self.reset()
