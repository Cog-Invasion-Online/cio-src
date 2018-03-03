"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file RemoteDodgeballAvatar.py
@author Brian Lach
@date April 30, 2016

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Parallel, Sequence, Func

from RemoteAvatar import RemoteAvatar
from DistributedDodgeballGame import TEAM_COLOR_BY_ID
from src.coginvasion.toon import ToonEffects

class RemoteDodgeballAvatar(RemoteAvatar):
    """A wrapper around a DistributedToon for use in the Dodgeball minigame (client side)"""

    notify = directNotify.newCategory("RemoteDodgeballAvatar")

    def __init__(self, mg, cr, avId):
        RemoteAvatar.__init__(self, mg, cr, avId)
        self.retrieveAvatar()
        
        self.throwSound = base.loadSfx('phase_3.5/audio/sfx/AA_pie_throw_only.ogg')
        base.audio3d.attachSoundToObject(self.throwSound, self.avatar)

        self.iceCube = ToonEffects.generateIceCube(self.avatar)

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
                ToonEffects.getIceCubeThawInterval(self.iceCube),
                ToonEffects.getToonThawInterval(self.avatar)
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
            ToonEffects.getIceCubeFormInterval(self.iceCube),
            ToonEffects.getToonFreezeInterval(self.avatar)
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
        self.throwSound = None
        self.isFrozen = None
        RemoteAvatar.cleanup(self)
