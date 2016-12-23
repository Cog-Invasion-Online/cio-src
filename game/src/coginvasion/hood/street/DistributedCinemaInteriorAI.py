# Filename: DistributedCinemaInteriorAI.py
# Created by:  blach (29Jul15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.ClockDelta import globalClockDelta
from direct.fsm import ClassicFSM, State
from direct.task import Task

from src.coginvasion.hood import DistributedToonInteriorAI
import CinemaGlobals

class DistributedCinemaInteriorAI(DistributedToonInteriorAI.DistributedToonInteriorAI):
    notify = directNotify.newCategory("DistributedCinemaInteriorAI")

    def __init__(self, air, block, doorToZone, cinemaIndex):
        DistributedToonInteriorAI.DistributedToonInteriorAI.__init__(self, air, block, doorToZone)
        self.cinemaIndex = cinemaIndex
        self.fsm = ClassicFSM.ClassicFSM('DCinemaInteriorAI', [State.State('off', self.enterOff, self.exitOff),
            State.State('show', self.enterShow, self.exitShow),
            State.State('intermission', self.enterIntermission, self.exitIntermission)],
            'off', 'off')
        self.fsm.enterInitialState()
        self.state = 'off'
        self.stateTimestamp = 0

    def announceGenerate(self):
        DistributedToonInteriorAI.DistributedToonInteriorAI.announceGenerate(self)
        self.b_setState('intermission')

    def delete(self):
        self.fsm.requestFinalState()
        del self.fsm
        del self.state
        del self.cinemaIndex
        del self.stateTimestamp
        DistributedToonInteriorAI.DistributedToonInteriorAI.delete(self)

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterShow(self):
        base.taskMgr.doMethodLater(CinemaGlobals.CinemaLengths[self.cinemaIndex],
            self.__showOver, self.uniqueName('showOver'))

    def __showOver(self, task):
        self.b_setState('intermission')
        return Task.done

    def exitShow(self):
        base.taskMgr.remove(self.uniqueName('showOver'))

    def enterIntermission(self):
        base.taskMgr.doMethodLater(CinemaGlobals.IntermissionLength, self.__intermissionOver,
            self.uniqueName('intermissionOver'))

    def __intermissionOver(self, task):
        self.b_setState('show')
        return Task.done

    def exitIntermission(self):
        base.taskMgr.remove(self.uniqueName('intermissionOver'))

    def requestStateAndTimestamp(self):
        avId = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId(avId, 'setState', self.getState())

    def setState(self, state):
        self.state = state
        self.fsm.request(state)

    def d_setState(self, state):
        self.stateTimestamp = globalClockDelta.getRealNetworkTime()
        self.sendUpdate('setState', [state, self.stateTimestamp])

    def b_setState(self, state):
        self.d_setState(state)
        self.setState(state)

    def getState(self):
        return [self.state, self.stateTimestamp]

    def getCinemaIndex(self):
        return self.cinemaIndex
