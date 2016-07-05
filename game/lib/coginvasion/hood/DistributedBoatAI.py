# Filename: DistributedBoatAI.py
# Created by:  blach (27Jul15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed import DistributedObjectAI, ClockDelta

class DistributedBoatAI(DistributedObjectAI.DistributedObjectAI):
    notify = directNotify.newCategory("DistributedBoatAI")

    StateInterval = 35.0

    def __init__(self, air):
        DistributedObjectAI.DistributedObjectAI.__init__(self, air)
        self.states = ['eastToWest', 'westToEast']
        self.state = ''
        self.stateTimestamp = 0

    def requestCurrentStateAndTimestamp(self):
        avId = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId(avId, 'currentStateAndTimestamp', self.getState())

    def __sailingTask(self, task):
        if self.state == self.states[0]:
            self.b_setState(self.states[1])

        elif self.state == self.states[1]:
            self.b_setState(self.states[0])

        else:
            self.b_setState(self.states[0])

        task.delayTime = self.StateInterval
        return task.again

    def setState(self, state):
        self.state = state

    def d_setState(self, state):
        self.stateTimestamp = ClockDelta.globalClockDelta.getRealNetworkTime()
        self.sendUpdate('setState', [state, self.stateTimestamp])

    def b_setState(self, state):
        self.d_setState(state)
        self.setState(state)

    def getState(self):
        return [self.state, self.stateTimestamp]

    def announceGenerate(self):
        DistributedObjectAI.DistributedObjectAI.announceGenerate(self)
        base.taskMgr.add(self.__sailingTask, self.uniqueName('DBoatAI.__sailingTask'))

    def delete(self):
        base.taskMgr.remove(self.uniqueName('DBoatAI.__sailingTask'))
        self.state = None
        self.states = None
        DistributedObjectAI.DistributedObjectAI.delete(self)
