"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file RemoteCameraShyAvatar.py
@author Brian Lach
@date April 28, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Sequence, LerpScaleInterval, Func, SoundInterval

from RemoteAvatar import RemoteAvatar

class RemoteCameraShyAvatar(RemoteAvatar):
    notify = directNotify.newCategory("RemoteCameraShyAvatar")

    def __init__(self, mg, cr, avId):
        RemoteAvatar.__init__(self, mg, cr, avId)
        self.shutter = base.audio3d.loadSfx("phase_4/audio/sfx/Photo_shutter.ogg")
        self.camera = None
        self.pictureTrack = None
        self.cameraFlash = None
        self.retrieveAvatar()

    def retrieveAvatar(self):
        RemoteAvatar.retrieveAvatar(self)
        if self.avatar:
            self.avatar.setForcedTorsoAnim('catchneutral')
            base.audio3d.attachSoundToObject(self.shutter, self.avatar)
            self.attachCamera()

    def attachCamera(self):
        self.camera = loader.loadModel("models/camera.egg.pz")
        self.camera.setScale(0.8)
        self.camera.setH(90)
        self.camera.find('**/o2').setSx(5.0)
        self.camera.setY(-1)
        self.camera.reparentTo(self.avatar.find('**/def_joint_right_hold'))
        self.cameraFlash = loader.loadModel("phase_4/models/minigames/shine.egg")
        self.cameraFlash.reparentTo(self.camera)
        self.cameraFlash.setTwoSided(1)
        self.cameraFlash.setPos(-0.43, 0.28, 0.63)
        self.cameraFlash.setH(180.00)
        self.cameraFlash.setScale(0.0)

    def detachCamera(self):
        if self.camera:
            self.camera.removeNode()
            self.camera = None
        if self.pictureTrack:
            self.pictureTrack.finish()
            self.pictureTrack = None
        if self.cameraFlash:
            self.cameraFlash.removeNode()
            self.cameraFlash = None

    def takePicture(self, ts = 0.0):
        self.pictureTrack = Sequence(
            Func(base.playSfx, self.shutter),
            LerpScaleInterval(
                self.cameraFlash,
                duration = 0.2,
                scale = 25.00,
                startScale = 0.0
            ),
            LerpScaleInterval(
                self.cameraFlash,
                duration = 0.05,
                scale = 0.0,
                startScale = 25.00
            )
        )
        self.pictureTrack.start(ts)

    def doWinDance(self):
        self.avatar.clearForcedTorsoAnim()
        self.avatar.play('hdance')
        sfx = base.loadSfx("phase_5/audio/sfx/AA_heal_happydance.ogg")
        SoundInterval(sfx).start()

    def cleanup(self):
        self.detachCamera()
        del self.shutter
        RemoteAvatar.cleanup(self)
