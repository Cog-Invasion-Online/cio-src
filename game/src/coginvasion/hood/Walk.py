"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Walk.py
@author Brian Lach
@date December 15, 2014

"""

from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.StateData import StateData
from direct.fsm.State import State
from direct.directnotify.DirectNotifyGlobal import directNotify

class Walk(StateData):
    notify = directNotify.newCategory("Walk")

    def __init__(self, doneEvent):
        StateData.__init__(self, doneEvent)
        self.fsm = ClassicFSM('Walk', [
            State('off', self.enterOff, self.exitOff, ['walking', 'deadWalking']),
            State('walking', self.enterWalking, self.exitWalking),
            State('deadWalking', self.enterDeadWalking, self.exitDeadWalking)],
            'off', 'off')
        self.fsm.enterInitialState()

    def unload(self):
        del self.fsm

    def enter(self, wantMouse = 0):
        base.localAvatar.startPlay(wantMouse = wantMouse)

    def exit(self):
        if base.localAvatarReachable():
            base.localAvatar.lastState = None
            self.fsm.request('off')
            base.localAvatar.stopPlay()
        

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterWalking(self):
        if base.localAvatar.getHealth() > 0:
            base.localAvatar.startTrackAnimToSpeed()
            #base.localAvatar.setWalkSpeedNormal()
        else:
            self.fsm.request('deadWalking')

    def exitWalking(self):
        base.localAvatar.stopTrackAnimToSpeed()

    def enterDeadWalking(self):
        base.localAvatar.startTrackAnimToSpeed()
        base.localAvatar.setWalkSpeedSlow()
        base.taskMgr.add(self.__watchForPositiveHP, base.localAvatar.uniqueName('watchforPositiveHP'))

    def __watchForPositiveHP(self, task):
        if base.localAvatar.getHealth() > 0:
            self.fsm.request('walking')
            return task.done
        return task.cont

    def exitDeadWalking(self):
        base.taskMgr.remove(base.localAvatar.uniqueName('watchforPositiveHP'))
        base.localAvatar.stopTrackAnimToSpeed()
