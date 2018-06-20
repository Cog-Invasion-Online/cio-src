"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file LocationGag.py
@author Maverick Liberty
@date July 24, 2015

"""

from LocationSeeker import LocationSeeker
from direct.interval.IntervalGlobal import Sequence, Func, Parallel, SoundInterval, Wait, ActorInterval
from direct.gui.DirectGui import OnscreenText
from panda3d.core import Point3
from src.coginvasion.globals import CIGlobals

class LocationGag:

    def __init__(self, minDistance, maxDistance, shadowScale = 1):
        self.buttonSoundPath = 'phase_5/audio/sfx/AA_drop_trigger_box.ogg'
        self.button = None
        self.buttonSfx = loader.loadSfx(self.buttonSoundPath)
        self.buttonAnim = 'push-button'
        self.chooseLocFrame = 34
        self.hitStartFrame = 45
        self.completeFrame = 77
        self.dropLoc = None
        self.minDistance = minDistance
        self.maxDistance = maxDistance
        self.locationSeeker = None
        self.buttonHold = 0.15
        self.actorTrack = None
        self.soundTrack = None
        self.isCircle = False
        self.shadowScale = 1
        self.helpInfo = None

    def setShadowData(self, isCircle, shadowScale):
        self.isCircle = isCircle
        self.shadowScale = shadowScale

    def getShadowScale(self):
        return self.shadowScale

    def equip(self):
        self.cleanupLocationSeeker()
        self.buildButton()
        self.button.reparentTo(self.avatar.find('**/def_joint_left_hold'))

        if self.isLocal():
            fpsCam = base.localAvatar.getFPSCam()
            vm = fpsCam.viewModel
            fpsCam.setVMGag(self.button, pos = (-0.04, 0.05, -0.01),
                            hpr = (328.39, 268.95, 359.48), scale = 0.559,
                            hand = 1)
            fpsCam.setVMAnimTrack(Sequence(ActorInterval(vm, 'button_draw'), Func(vm.loop, 'button_idle')))

            self.locationSeeker = LocationSeeker(self.avatar, self, self.minDistance, self.maxDistance)
            self.locationSeeker.setShadowType(self.isCircle, self.shadowScale)
            self.avatar.acceptOnce(self.locationSeeker.getLocationSelectedName(), base.localAvatar.releaseGag)

            self.helpInfo = OnscreenText(text = 'Move the shadow with your mouse\nClick to release',
                pos = (0, -0.75), font = CIGlobals.getToonFont(), fg = (1, 1, 1, 1),
                shadow = (0, 0, 0, 1))
            self.helpInfo.hide() # yeet

        self.doDrawAndHold(self.buttonAnim, 0, self.chooseLocFrame, bobStart = self.chooseLocFrame,
                           bobEnd = self.chooseLocFrame,
                           holdCallback = self.locationSeeker.startSeeking if self.isLocal() else None)

    def release(self):
        if self.avatar:
            self.buildTracks()
            if self.isLocal():
                self.getFPSCam().setVMAnimTrack(Sequence(ActorInterval(self.getViewModel(), 'button_press'),
                                                         Func(self.getViewModel().loop, 'button_idle')))

    def complete(self):
        if self.button:
            numFrames = base.localAvatar.getNumFrames(self.buttonAnim)
            ActorInterval(self.avatar, self.buttonAnim, startFrame = self.completeFrame, endFrame = numFrames,
                          playRate = self.playRate).start()

        self.cleanupButton()

    def buildTracks(self, mode=0):
        if not self.avatar:
            return
        self.cleanupTracks()
        if mode == 0:
            self.actorTrack = Sequence(ActorInterval(self.avatar, self.buttonAnim, startFrame = self.hitStartFrame,
                               endFrame = self.completeFrame, playRate = self.playRate))
            self.soundTrack = Sequence(Wait(self.buttonHold), SoundInterval(self.buttonSfx, node = self.avatar))

    def cleanupTracks(self):
        if self.actorTrack:
            self.actorTrack.pause()
            self.actorTrack = None
        if self.soundTrack:
            self.soundTrack.pause()
            self.soundTrack = None

    def getActorTrack(self):
        return self.actorTrack

    def getSoundTrack(self):
        return self.soundTrack

    def setDropLoc(self, x, y, z):
        self.dropLoc = Point3(x, y, z)

    def buildButton(self):
        self.cleanupButton()
        self.button = loader.loadModel('phase_3.5/models/props/button.bam')

    def setLocation(self, value):
        self.dropLoc = value

    def getLocation(self):
        return self.dropLoc

    def getLocationSeeker(self):
        return self.locationSeeker

    def cleanupButton(self):
        if self.button:
            self.button.removeNode()
            self.button = None

    def cleanupLocationSeeker(self):
        if self.locationSeeker:
            self.dropLoc = self.locationSeeker.getLocation()
            self.locationSeeker.cleanup()
            self.locationSeeker = None
        if self.helpInfo:
            self.helpInfo.destroy()

    def cleanup(self):
        self.cleanupButton()
        self.cleanupLocationSeeker()
        self.cleanupTracks()
        self.dropLoc = None
        self.buttonSfx.stop()
        self.buttonSoundPath = None
        self.buttonAnim = None
