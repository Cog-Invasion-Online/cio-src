"""

  Filename: Walk.py
  Created by: blach (15Dec14)

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

    def load(self):
        pass

    def unload(self):
        del self.fsm

    def enter(self):
        base.localAvatar.startPosHprBroadcast()
        base.localAvatar.d_broadcastPositionNow()
        base.localAvatar.startBlink()
        base.localAvatar.attachCamera()
        base.localAvatar.startSmartCamera()
        base.localAvatar.collisionsOn()
        if not base.localAvatar.walkControls.getCollisionsActive():
            base.localAvatar.walkControls.setCollisionsActive(1)
        base.localAvatar.enableAvatarControls()
        

    def exit(self):
        base.localAvatar.lastState = None
        self.fsm.request('off')
        if base.localAvatar.walkControls.getCollisionsActive():
            base.localAvatar.walkControls.setCollisionsActive(0)
        base.localAvatar.disableAvatarControls()
        base.localAvatar.detachCamera()
        base.localAvatar.stopSmartCamera()
        base.localAvatar.stopPosHprBroadcast()
        base.localAvatar.stopBlink()
        base.localAvatar.collisionsOff()
        base.localAvatar.controlManager.placeOnFloor()
        

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterWalking(self):
        if base.localAvatar.getHealth() > 0:
            base.localAvatar.startTrackAnimToSpeed()
            base.localAvatar.setWalkSpeedNormal()
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
