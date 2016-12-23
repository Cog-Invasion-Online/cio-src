"""

  Filename: Playground.py
  Created by: blach (14Dec14)

"""

from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.directnotify.DirectNotifyGlobal import directNotify
from pandac.PandaModules import Fog

from src.coginvasion.globals import CIGlobals
from src.coginvasion.holiday.HolidayManager import HolidayType
from src.coginvasion.toon import ParticleLoader
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
        Place.Place.enter(self)
        self.fsm.enterInitialState()
        messenger.send('enterPlayground')
        if self.loader.music:
            if self.__class__.__name__ == 'CTPlayground':
                volume = 2.0
            else:
                volume = 0.8
            base.playMusic(self.loader.music, looping = 1, volume = volume)
        self.loader.geom.reparentTo(render)
        self.loader.hood.startSky()
        self.zoneId = requestStatus['zoneId']
        if base.cr.playGame.suitManager:
            base.cr.playGame.suitManager.d_requestSuitInfo()
        how = requestStatus['how']
        self.fsm.request(how, [requestStatus])

    def exit(self):
        self.ignoreAll()
        messenger.send('exitPlayground')
        self.loader.geom.reparentTo(hidden)
        self.loader.hood.stopSky()
        if self.loader.music:
            self.loader.music.stop()
        if self.loader.bossBattleMusic:
            self.loader.bossBattleMusic.stop()
        if self.loader.battleMusic:
            self.loader.battleMusic.stop()
        if self.loader.invasionMusic:
            self.loader.invasionMusic.stop()
        if self.loader.tournamentMusic:
            self.loader.tournamentMusic.stop()
        Place.Place.exit(self)

    def load(self):
        Place.Place.load(self)
        self.parentFSM.getStateNamed('playground').addChild(self.fsm)

        if base.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS:
            self.particles = ParticleLoader.loadParticleEffect('phase_8/etc/snowdisk.ptf')
            self.particles.setPos(0, 0, 5)
            self.particlesRender = self.loader.geom.attachNewNode('snowRender')
            self.particlesRender.setDepthWrite(0)
            self.particlesRender.setBin('fixed', 1)
            self.particles.start(parent = camera, renderParent = self.particlesRender)
            self.fog = Fog('snowFog')
            self.fog.setColor(0.486, 0.784, 1)
            self.fog.setExpDensity(0.003)
            base.render.setFog(self.fog)

    def unload(self):
        self.parentFSM.getStateNamed('playground').removeChild(self.fsm)
        del self.parentFSM
        del self.fsm
        if hasattr(self, 'particles'):
            self.particles.cleanup()
            self.particlesRender.removeNode()
            del self.particlesRender
            base.render.clearFog()
            self.fog = None
            del self.particles
        self.ignoreAll()
        Place.Place.unload(self)
        return

    def enterStation(self):
        base.localAvatar.startPosHprBroadcast()
        base.localAvatar.d_broadcastPositionNow()

    def exitStation(self):
        base.localAvatar.stopPosHprBroadcast()

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
