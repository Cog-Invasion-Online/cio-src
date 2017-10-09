"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file RegenTreasurePlannerAI.py
@author Maverick Liberty
@date July 15, 2015

"""

from TreasurePlannerAI import TreasurePlannerAI
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.task.Task import Task
import random

class RegenTreasurePlannerAI(TreasurePlannerAI):
    notify = directNotify.newCategory('RegenTreasurePlannerAI')

    def __init__(self, zoneId, treasureConstructor, taskName, spawnInterval, maxTreasures, callback = None):
        TreasurePlannerAI.__init__(self, zoneId, treasureConstructor, callback)
        self.taskName = '%s-%s' % (taskName, zoneId)
        self.spawnInterval = spawnInterval
        self.maxTreasures = maxTreasures

    def stopSpawning(self):
        taskMgr.remove(self.taskName)

    def startSpawning(self):
        self.stopSpawning()

    def start(self):
        self.preSpawnTreasures()
        taskMgr.doMethodLater(self.spawnInterval, self.upkeepTreasurePopulation, self.taskName)

    def stop(self):
        self.stopSpawning()

    def upkeepTreasurePopulation(self, task):
        if self.numTreasures() < self.maxTreasures:
            self.placeRandomTreasure()
        taskMgr.doMethodLater(self.spawnInterval, self.upkeepTreasurePopulation, self.taskName)
        return Task.done

    def placeRandomTreasure(self):
        self.notify.debug('Placing a Treasure...')
        spawnPointIndex = self.nthEmptyIndex(random.randrange(self.countEmptySpawnPoints()))
        self.placeTreasure(spawnPointIndex)

    def preSpawnTreasures(self):
        for _ in range(self.maxTreasures): self.placeRandomTreasure()
