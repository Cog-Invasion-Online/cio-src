# Filename: DistributedDeliveryGameAI.py
# Created by:  blach (04Oct15)

from direct.directnotify.DirectNotifyGlobal import directNotify

from lib.coginvasion.cog import SuitBank, Variant
from lib.coginvasion.minigame.DistributedMinigameAI import DistributedMinigameAI
from lib.coginvasion.globals import CIGlobals
from DistributedDeliveryTruckAI import DistributedDeliveryTruckAI
from DistributedDeliveryGameSuitAI import DistributedDeliveryGameSuitAI

import random

class DistributedDeliveryGameAI(DistributedMinigameAI):
    notify = directNotify.newCategory('DistributedDeliveryGameAI')

    NumBarrelsInEachTruck = 18
    SuitSpawnRateByNumPlayers = {1 : 0.55, 2 : 0.45, 3 : 0.35, 4 : 0.25}
    SuitBaseSpawnTime = 20.0

    def __init__(self, air):
        DistributedMinigameAI.__init__(self, air)
        self.trucks = []
        self.suits = []
        self.trucksOutOfBarrels = 0
        self.barrelsRemaining = 0
        self.barrelsStolen = 0
        self.barrelsDelivered = 0
        self.totalBarrels = 0

    def d_gameOver(self, winner=0, winnerDoId=[]):
        amt = self.givePrizes(winnerDoId)
        self.sendUpdate('gameOver', [winner, winnerDoId, amt])

    def truckOutOfBarrels(self):
        self.trucksOutOfBarrels += 1
        if self.trucksOutOfBarrels == len(self.trucks):
            self.stopSuitSpawner()
            for suit in self.suits:
                suit.requestDelete()
            self.suits = []
            self.sendUpdate('allBarrelsGone')
            base.taskMgr.doMethodLater(4.0, self.__gameOverTask, self.uniqueName('gameOverTask'))

    def __gameOverTask(self, task):
        self.d_gameOver()

    def requestDropOffBarrel(self, truckId):
        avId = self.air.getAvatarIdFromSender()
        self.b_setBarrelsDelivered(self.getBarrelsDelivered() + 1)
        for truck in self.trucks:
            if truck.doId == truckId:
                truck.barrelDroppedOff()
        self.sendUpdate('dropOffBarrel', [avId])

    def setBarrelsRemaining(self, num):
        self.barrelsRemaining = num

    def d_setBarrelsRemaining(self, num):
        self.sendUpdate('setBarrelsRemaining', [num])

    def b_setBarrelsRemaining(self, num):
        self.d_setBarrelsRemaining(num)
        self.setBarrelsRemaining(num)

    def getBarrelsRemaining(self):
        return self.barrelsRemaining

    def setBarrelsStolen(self, num):
        self.barrelsStolen = num

    def d_setBarrelsStolen(self, num):
        self.sendUpdate('setBarrelsStolen', [num])

    def b_setBarrelsStolen(self, num):
        self.d_setBarrelsStolen(num)
        self.setBarrelsStolen(num)

    def getBarrelsStolen(self):
        return self.barrelsStolen

    def setBarrelsDelivered(self, num):
        self.barrelsDelivered = num

    def d_setBarrelsDelivered(self, num):
        self.sendUpdate('setBarrelsDelivered', [num])

    def b_setBarrelsDelivered(self, num):
        self.d_setBarrelsDelivered(num)
        self.setBarrelsDelivered(num)

    def getBarrelsDelivered(self):
        return self.barrelsDelivered

    def announceGenerate(self):
        DistributedMinigameAI.announceGenerate(self)
        truck0 = DistributedDeliveryTruckAI(self.air, self, 0)
        truck0.setNumBarrels(self.NumBarrelsInEachTruck)
        truck0.generateWithRequired(self.zoneId)
        self.trucks.append(truck0)
        totalBarrels = 0
        for truck in self.trucks:
            totalBarrels += truck.getNumBarrels()
        self.totalBarrels = totalBarrels
        self.setBarrelsRemaining(totalBarrels)

    def allAvatarsReady(self):
        DistributedMinigameAI.allAvatarsReady(self)
        self.startSuitSpawner()

    def d_gameOver(self, winner = 0, winnerDoId = []):
        DistributedMinigameAI.d_gameOver(self, winner, winnerDoId)
        self.stopSuitSpawner()

    def givePrizes(self, winnerAvId):
        if self.barrelsStolen == 0:
            amt = int(self.totalBarrels * 4)
        else:
            amt = int(self.totalBarrels * 4 / self.barrelsStolen + self.barrelsDelivered)
        for avatar in self.avatars:
            avatar.b_setMoney(avatar.getMoney() + amt)
        return amt

    def getSuitSpawnTime(self):
        minTime = self.SuitBaseSpawnTime * self.SuitSpawnRateByNumPlayers[self.numPlayers]
        return random.randint(minTime, minTime + 3)

    def startSuitSpawner(self):
        time = self.getSuitSpawnTime()
        base.taskMgr.doMethodLater(time, self.__spawnSuit, self.uniqueName('suitSpawner'))

    def __spawnSuit(self, task):
        plan = random.choice(SuitBank.getSuits())
        level = 0
        variant = Variant.NORMAL
        suit = DistributedDeliveryGameSuitAI(self.air, self)
        suit.generateWithRequired(self.zoneId)
        suit.b_setLevel(level)
        suit.b_setSuit(plan, variant)
        suit.b_setPlace(self.zoneId)
        suit.b_setName(plan.getName())
        suit.b_setParent(CIGlobals.SPHidden)
        self.suits.append(suit)
        task.delayTime = self.getSuitSpawnTime()
        return task.again

    def stopSuitSpawner(self):
        base.taskMgr.remove(self.uniqueName('suitSpawner'))

    def delete(self):
        try:
            self.DistributedDeliveryGameAI_deleted
            return
        except:
            self.DistributedDeliveryGameAI_deleted = 1
        self.stopSuitSpawner()
        for truck in self.trucks:
            truck.requestDelete()
        self.trucks = None
        for suit in self.suits:
            suit.disable()
            suit.requestDelete()
        self.suits = None
        self.trucksOutOfBarrels = None
        self.barrelsRemaining = None
        self.barrelsStolen = None
        self.barrelsDelivered = None
        self.totalBarrels = None
        DistributedMinigameAI.delete(self)
