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

from src.coginvasion.hood import ZoneUtil, Place

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

        base.playMusic(self.loader.safeZoneSong)

        self.loader.geom.reparentTo(render)
        base.enablePhysicsNodes(self.loader.geom)
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
        base.disablePhysicsNodes(self.loader.geom)
        
        base.stopMusic()

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
        if base.localAvatar.zoneId != ZoneUtil.RecoverAreaId:
            base.localAvatar.startMonitoringHP()

    def exitWalk(self):
        if base.localAvatar.zoneId != ZoneUtil.RecoverAreaId:
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
