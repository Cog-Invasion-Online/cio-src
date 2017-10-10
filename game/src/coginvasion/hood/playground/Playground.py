"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Playground.py
@author Brian Lach
@date December 14, 2014

"""

from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.directnotify.DirectNotifyGlobal import directNotify
from panda3d.core import Fog

from src.coginvasion.globals import CIGlobals
from src.coginvasion.hood import Place

class Playground(Place.Place):
    notify = directNotify.newCategory("Playground")

    def __init__(self, loader, parentFSM, doneEvent):
        Place.Place.__init__(self, loader, doneEvent)
        self.fsm = ClassicFSM('Playground', [
                State('start', self.enterStart, self.exitStart,
                    ['walk', 'teleportIn', 'tunnelOut', 'doorOut', 'trolleyOut']),
                State('teleportIn', self.enterTeleportIn, self.exitTeleportIn,
                    ['walk', 'acknowledgeDeath']),
                State('walk', self.enterWalk, self.exitWalk,
                    ['teleportOut', 'stop', 'shtickerBook', 'died', 'tunnelIn']),
                State('teleportOut', self.enterTeleportOut, self.exitTeleportOut,
                    ['teleportIn', 'stop']),
                State('stop', self.enterStop, self.exitStop,
                    ['walk', 'died', 'station', 'teleportOut', 'doorIn']),
                State('shtickerBook', self.enterShtickerBook, self.exitShtickerBook,
                    ['teleportOut', 'walk']),
                State('tunnelOut', self.enterTunnelOut, self.exitTeleportOut, ['walk']),
                State('final', self.enterFinal, self.exitFinal,
                    ['start']),
                State('died', self.enterDied, self.exitDied, ['final']),
                State('station', self.enterStation, self.exitStation, ['teleportOut', 'walk']),
                State('doorIn', self.enterDoorIn, self.exitDoorIn, ['stop']),
                State('doorOut', self.enterDoorOut, self.exitDoorOut, ['walk']),
                State('tunnelIn', self.enterTunnelIn, self.exitTunnelIn, ['stop']),
                State('acknowledgeDeath', self.enterAcknowledgeDeath, self.exitAcknowledgeDeath, ['walk']),
                State('trolleyOut', self.enterTrolleyOut, self.exitTrolleyOut, ['walk' ,'stop'])],
                'start', 'final')
        self.parentFSM = parentFSM
        return

    def enter(self, requestStatus):
        self.fsm.enterInitialState()
        self.loader.hood.enableOutdoorLighting()
        messenger.send('enterPlayground')
        if self.loader.music:
            if self.__class__.__name__ == 'CTPlayground':
                volume = 2.0
            else:
                volume = 0.8
            base.playMusic(self.loader.music, looping = 1, volume = volume)
        self.loader.geom.reparentTo(render)
        #self.loader.hood.startSky()
        
        self.zoneId = requestStatus['zoneId']
        if base.cr.playGame.suitManager:
            base.cr.playGame.suitManager.d_requestSuitInfo()
        how = requestStatus['how']
        self.fsm.request(how, [requestStatus])
        Place.Place.enter(self)

    def exit(self):
        self.ignoreAll()
        messenger.send('exitPlayground')
        
        self.loader.geom.reparentTo(hidden)
        #self.loader.hood.stopSky()
        if self.loader.music:
            # Workaround to try to fix the persistent humming from the DDL safezone music.
            if self.loader.music == 'phase_8/audio/bgm/DL_nbrhood.mid':
                base.playMusic(self.loader.music, looping = 0, volume = 0)
            else:
                self.loader.music.stop()
        if self.loader.bossBattleMusic:
            self.loader.bossBattleMusic.stop()
        if self.loader.battleMusic:
            self.loader.battleMusic.stop()
        if self.loader.invasionMusic:
            self.loader.invasionMusic.stop()
        if self.loader.tournamentMusic:
            self.loader.tournamentMusic.stop()

        self.loader.hood.disableOutdoorLighting()
        
        Place.Place.exit(self)

    def load(self):
        Place.Place.load(self)
        self.parentFSM.getStateNamed('playground').addChild(self.fsm)

    def unload(self):
        self.parentFSM.getStateNamed('playground').removeChild(self.fsm)
        del self.parentFSM
        del self.fsm
        self.ignoreAll()
        Place.Place.unload(self)
        return

    def enterStation(self):
        pass

    def exitStation(self):
        pass

    def enterWalk(self, teleportIn = 0):
        Place.Place.enterWalk(self, teleportIn)
        if base.localAvatar.zoneId != CIGlobals.RecoverAreaId:
            base.localAvatar.startMonitoringHP()

    def exitWalk(self):
        if base.localAvatar.zoneId != CIGlobals.RecoverAreaId:
            base.localAvatar.stopMonitoringHP()
        Place.Place.exitWalk(self)

    def enterTeleportIn(self, requestStatus):
        if base.localAvatar.getHealth() < 1:
            requestStatus['nextState'] = 'acknowledgeDeath'
        else:
            requestStatus['nextState'] = 'walk'
        x, y, z, h, p, r = base.cr.hoodMgr.getPlaygroundCenterFromId(self.loader.hood.id)
        base.localAvatar.detachNode()
        base.localAvatar.setPosHpr(render, x, y, z, h, p, r)
        Place.Place.enterTeleportIn(self, requestStatus)
        return
