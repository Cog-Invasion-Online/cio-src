# Filename: RemoteDodgeballAvatar.py
# Created by:  blach (30Apr16)

from panda3d.core import VBase4

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Parallel, SoundInterval, LerpColorScaleInterval, Sequence, Func

from RemoteAvatar import RemoteAvatar
from DistributedDodgeballGame import TEAM_COLOR_BY_ID

class RemoteDodgeballAvatar(RemoteAvatar):
    """A wrapper around a DistributedToon for use in the Dodgeball minigame (client side)"""

    notify = directNotify.newCategory("RemoteDodgeballAvatar")

    def __init__(self, mg, cr, avId):
        RemoteAvatar.__init__(self, mg, cr, avId)
        self.retrieveAvatar()
        
        self.throwSound = base.loadSfx('phase_3.5/audio/sfx/AA_pie_throw_only.ogg')
        base.audio3d.attachSoundToObject(self.throwSound, self.avatar)

        self.iceCube = loader.loadModel('phase_8/models/props/icecube.bam')
        for node in self.iceCube.findAllMatches('**/billboard*'):
            node.removeNode()
        for node in self.iceCube.findAllMatches('**/drop_shadow*'):
            node.removeNode()
        for node in self.iceCube.findAllMatches('**/prop_mailboxcollisions*'):
            node.removeNode()
        self.iceCube.reparentTo(self.avatar)
        self.iceCube.setScale(1.2, 1.0, self.avatar.getHeight() / 1.7)
        self.iceCube.setTransparency(1)
        self.iceCube.setColorScale(0.76, 0.76, 1.0, 0.0)

        self.iceCubeForm = base.loadSfx('phase_4/audio/sfx/ice_cube_form.ogg')
        base.audio3d.attachSoundToObject(self.iceCubeForm, self.iceCube)
        self.iceCubeBreak = base.loadSfx('phase_4/audio/sfx/ice_cube_break.ogg')
        base.audio3d.attachSoundToObject(self.iceCubeBreak, self.iceCube)

        self.freezeUpTrack = None
        self.freezeDnTrack = None

        self.isFrozen = False

    def clearFreezeTracks(self):
        if self.freezeUpTrack:
            self.freezeUpTrack.pause()
            self.freezeUpTrack = None
        if self.freezeDnTrack:
            self.freezeDnTrack.pause()
            self.freezeDnTrack = None

    def unFreeze(self):
        if not self.isFrozen:
            return 0

        self.clearFreezeTracks()

        # Start avatar movement animations
        self.avatar.animFSM.request('Happy')

        self.iceCube.wrtReparentTo(render)

        self.freezeDnTrack = Sequence(
            Parallel(
                SoundInterval(self.iceCubeBreak, node = self.iceCube),
                LerpColorScaleInterval(
                    self.iceCube,
                    duration = 0.5,
        			colorScale = VBase4(0.76, 0.76, 1.0, 0.0),
        			startColorScale = self.iceCube.getColorScale(),
        			blendType = 'easeInOut'
                ),
                LerpColorScaleInterval(
                    self.avatar.getGeomNode(),
                    duration = 0.5,
                    colorScale = VBase4(1.0, 1.0, 1.0, 1.0),
    				startColorScale = base.localAvatar.getGeomNode().getColorScale(),
    				blendType = 'easeOut'
                )
            ),
            Func(self.iceCube.reparentTo, self.avatar),
            Func(self.iceCube.setPosHpr, 0, 0, 0, 0, 0, 0)
        )
        self.freezeDnTrack.start()

        self.isFrozen = False
        return 1

    def freeze(self):
        if self.isFrozen:
            return 0

        self.clearFreezeTracks()

        # Stop avatar movement animations
        self.avatar.animFSM.request('off')
        self.avatar.stop()

        self.freezeUpTrack = Parallel(
            SoundInterval(self.iceCubeForm, node = self.iceCube),
            LerpColorScaleInterval(
                self.iceCube,
                duration = 0.5,
    			colorScale = VBase4(0.76, 0.76, 1.0, 1.0),
    			startColorScale = self.iceCube.getColorScale(),
    			blendType = 'easeInOut'
            ),
            LerpColorScaleInterval(
                self.avatar.getGeomNode(),
                duration = 0.5,
                colorScale = VBase4(0.5, 0.5, 1.0, 1.0),
				startColorScale = base.localAvatar.getGeomNode().getColorScale(),
				blendType = 'easeOut'
            )
        )
        self.freezeUpTrack.start()

        self.isFrozen = True
        return 1

    def setTeam(self, team):
        RemoteAvatar.setTeam(self, team)
        self.teamText.node().setText("")
        self.teamText.node().setTextColor(TEAM_COLOR_BY_ID[team])

    def cleanup(self):
        self.clearFreezeTracks()
        if self.iceCube:
            self.iceCube.removeNode()
            self.iceCube = None
        self.iceCubeForm = None
        self.throwSound = None
        self.iceCubeBreak = None
        self.isFrozen = None
        RemoteAvatar.cleanup(self)
