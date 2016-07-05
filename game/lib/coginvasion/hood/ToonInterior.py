# Filename: ToonInterior.py
# Created by:  blach (27Jul15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.State import State
from direct.fsm.ClassicFSM import ClassicFSM

import Place

class ToonInterior(Place.Place):
    notify = directNotify.newCategory("ToonInterior")

    def __init__(self, hood, parentFSM, doneEvent):
        self.parentFSM = parentFSM
        Place.Place.__init__(self, hood, doneEvent)
        self.fsm = ClassicFSM('ToonInterior', [State('start', self.enterStart, self.exitStart, ['doorOut', 'teleportIn']),
            State('walk', self.enterWalk, self.exitWalk, ['stop', 'doorIn', 'shtickerBook', 'teleportOut']),
            State('shtickerBook', self.enterShtickerBook, self.exitShtickerBook, ['teleportOut', 'walk']),
            State('teleportOut', self.enterTeleportOut, self.exitTeleportOut, ['teleportIn', 'stop']),
            State('teleportIn', self.enterTeleportIn, self.exitTeleportIn, ['walk', 'stop']),
            State('tunnelOut', self.enterTunnelOut, self.exitTunnelOut, ['walk']),
            State('tunnelIn', self.enterTunnelIn, self.exitTunnelIn, ['stop']),
            State('stop', self.enterStop, self.exitStop, ['walk', 'died', 'teleportOut', 'doorIn']),
            State('doorIn', self.enterDoorIn, self.exitDoorIn, ['stop']),
            State('doorOut', self.enterDoorOut, self.exitDoorOut, ['walk']),
            State('final', self.enterFinal, self.exitFinal, ['final'])],
            'start', 'final')

    def enter(self, requestStatus):
        Place.Place.enter(self)
        self.fsm.enterInitialState()
        base.playMusic(self.loader.interiorMusic, volume = 0.8, looping = 1)
        self.fsm.request(requestStatus['how'], [requestStatus])
        return

    def exit(self):
        self.loader.interiorMusic.stop()
        Place.Place.exit(self)

    def load(self):
        Place.Place.load(self)
        self.parentFSM.getStateNamed('toonInterior').addChild(self.fsm)

    def unload(self):
        self.parentFSM.getStateNamed('toonInterior').removeChild(self.fsm)
        del self.fsm
        del self.parentFSM
        self.ignoreAll()
        Place.Place.unload(self)
        return
