# Filename: DistributedDeliveryGameSuitAI.py
# Created by:  blach (04Oct15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Sequence, Wait, Func

from src.coginvasion.cog.DistributedSuitAI import DistributedSuitAI
from src.coginvasion.cog import SuitGlobals
from src.coginvasion.npc.NPCWalker import NPCWalkInterval
from src.coginvasion.globals import CIGlobals
import DeliveryGameGlobals as DGG

import random

class DistributedDeliveryGameSuitAI(DistributedSuitAI):
    notify = directNotify.newCategory('DistributedDeliveryGameSuitAI')

    def __init__(self, air, mg):
        DistributedSuitAI.__init__(self, air)
        self.mg = mg
        self.truck = random.choice(self.mg.trucks)
        self.truckIndex = self.mg.trucks.index(self.truck)
        self.spawnPoint = None

    def walkToTruck(self):
        index = DGG.WalkToTruckIndex
        pos = DGG.TruckSuitPointsByIndex[self.truckIndex]
        startPos = self.getPos(render)
        self.b_setSuitState(1, -1, index)
        durationFactor = 0.2
        pathName = self.uniqueName('WalkToTruck')
        self.walkTrack = NPCWalkInterval(self, pos, startPos = startPos,
            name = pathName, durationFactor = durationFactor, fluid = 1
        )
        self.walkTrack.setDoneEvent(self.walkTrack.getName())
        self.acceptOnce(self.walkTrack.getDoneEvent(), self.__walkedToTruck)
        self.walkTrack.start()
        self.b_setAnimState(SuitGlobals.getAnimId(SuitGlobals.getAnimByName('walk')))

    def __walkedToTruck(self):
        self.truck.suitPickUpBarrel(self.doId)
        self.walkBackToSpawnPointWithBarrel()

    def walkBackToSpawnPointWithBarrel(self):
        pos = DGG.SpawnPoints[self.spawnPoint]
        startPos = self.getPos(render)
        self.b_setSuitState(1, -1, self.spawnPoint)
        durationFactor = 0.2
        pathName = self.uniqueName('WalkBackToSpawn')
        self.walkTrack = NPCWalkInterval(self, pos, startPos = startPos,
            name = pathName, durationFactor = durationFactor, fluid = 1
        )
        self.walkTrack.setDoneEvent(self.walkTrack.getName())
        self.acceptOnce(self.walkTrack.getDoneEvent(), self.__walkedBack2Spawn)
        self.walkTrack.start()
        self.b_setAnimState(SuitGlobals.getAnimId(SuitGlobals.getAnimByName('tray-walk')))

    def __walkedBack2Spawn(self):
        self.b_setSuitState(3, self.spawnPoint, self.spawnPoint)
        base.taskMgr.doMethodLater(10, self.__finished, self.uniqueName('finishSuit'))

    def __finished(self, task):
        self.mg.suits.remove(self)
        self.truck.barrelDroppedOff()
        self.requestDelete()
        return task.done

    def spawn(self):
        pos = random.choice(DGG.SpawnPoints)
        index = DGG.SpawnPoints.index(pos)
        self.spawnPoint = index
        self.b_setSuitState(2, index, index)
        flyTrack = self.posInterval(3, pos,
            startPos = pos + (0, 0, 50))
        flyTrack.start()
        self.track = Sequence()
        self.track.append(Wait(5.4))
        self.track.append(Func(self.b_setAnimState, 'neutral'))
        self.track.append(Wait(1.0))
        self.track.append(Func(self.walkToTruck))
        self.track.start()
        self.b_setParent(CIGlobals.SPRender)

    def delete(self):
        base.taskMgr.remove(self.uniqueName('finishSuit'))
        if hasattr(self, 'walkTrack') and self.walkTrack:
            self.ignore(self.walkTrack.getDoneEvent())
            self.walkTrack.finish()
            self.walkTrack = None
        self.mg = None
        self.truck = None
        self.truckIndex = None
        self.spawnPoint = None
        DistributedSuitAI.delete(self)
