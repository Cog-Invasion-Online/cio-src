# Filename: DistributedDeliveryGameSuit.py
# Created by:  blach (04Oct15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import LerpPosInterval, Sequence, Wait

from src.coginvasion.cog.DistributedSuit import DistributedSuit
from src.coginvasion.npc.NPCWalker import NPCWalkInterval
import DeliveryGameGlobals as DGG

import random

class DistributedDeliveryGameSuit(DistributedSuit):
    notify = directNotify.newCategory('DistributedDeliveryGameSuit')

    def __init__(self, cr):
        DistributedSuit.__init__(self, cr)
        self.truckIndex = 0

    def setTruckIndex(self, index):
        self.truckIndex = index

    def getTruckIndex(self):
        return self.truckIndex

    def enterFlyingDown(self, startIndex, endIndex, ts = 0.0):
        startPos = DGG.SpawnPoints[startIndex] + (0, 0, 50)
        endPos = DGG.SpawnPoints[endIndex]
        duration = 3
        self.moveIval = LerpPosInterval(self, duration = duration, pos = endPos, startPos = startPos, fluid = 1)
        self.moveIval.start(ts)
        self.animFSM.request('flyDown', [ts])
        yaw = random.uniform(0.0, 360.0)
        self.setH(yaw)

    def enterFlyingUp(self, startIndex, endIndex, ts = 0.0):
        startPos = DGG.SpawnPoints[startIndex]
        endPos = DGG.SpawnPoints[endIndex] + (0, 0, 50)
        duration = 3
        self.moveIval = Sequence(Wait(1.7), LerpPosInterval(self, duration = duration, pos = endPos, startPos = startPos, fluid = 1))
        self.moveIval.start(ts)
        self.animFSM.request('flyAway', [ts])

    def enterWalking(self, startIndex, endIndex, ts = 0.0):
        numPlayers = base.minigame.getNumPlayers()

        durationFactor = 0.2

        if numPlayers == 2:
            durationFactor = 0.15
        elif numPlayers == 3:
            durationFactor = 0.1
        elif numPlayers == 4:
            durationFactor = 0.08

        if startIndex > -1:
            startPos = DGG.SpawnPoints[startIndex]
        else:
            startPos = self.getPos(render)
        if endIndex == DGG.WalkToTruckIndex:
            endPos = DGG.TruckSuitPointsByIndex[self.truckIndex]
        else:
            endPos = DGG.SpawnPoints[endIndex]

        self.stopMoving()

        self.moveIval = NPCWalkInterval(self, endPos, durationFactor, startPos, fluid = 1)
        self.moveIval.start(ts)
