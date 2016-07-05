# Filename: DistributedCityCartAI.py
# Created by:  blach (13Aug15)

from direct.distributed.DistributedNodeAI import DistributedNodeAI
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.distributed.ClockDelta import globalClockDelta

import CityCartGlobals

import random

class DistributedCityCartAI(DistributedNodeAI):
    notify = directNotify.newCategory('DistributedCityCartAI')

    squishDamage = 10.0

    def __init__(self, air, pathIndex):
        DistributedNodeAI.__init__(self, air)
        self.state = ''
        self.stateTimestamp = 0
        self.pathIndex = pathIndex
        ivalStart = 0
        ivalEnd = CityCartGlobals.index2Duration[self.pathIndex]
        self.ivalTDisplace = 0

    def announceGenerate(self):
        DistributedNodeAI.announceGenerate(self)
        self.b_setState('pathFollow')

    def delete(self):
        del self.state
        del self.stateTimestamp
        del self.pathIndex
        del self.ivalTDisplace
        DistributedNodeAI.delete(self)

    def getIvalTDisplace(self):
        return self.ivalTDisplace

    def getPathIndex(self):
        return self.pathIndex

    def setState(self, state):
        self.state = state

    def d_setState(self, state):
        self.stateTimestamp = globalClockDelta.getFrameNetworkTime()
        self.sendUpdate('setState', [state, self.stateTimestamp])

    def b_setState(self, state):
        self.d_setState(state)
        self.setState(state)

    def getState(self):
        return [self.state, self.stateTimestamp]

    def hitByCar(self):
        avatarId = self.air.getAvatarIdFromSender()
        avatar = self.air.doId2do.get(avatarId)
        if avatar:
            dmg = self.squishDamage
            hp = avatar.getHealth() - dmg
            if hp < 0:
                hp = 0
            avatar.b_setHealth(hp)
            avatar.d_announceHealth(0, dmg)
