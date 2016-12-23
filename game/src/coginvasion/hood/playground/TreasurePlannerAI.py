"""

  Filename: TreasurePlannerAI.py
  Created by: DecodedLogic (15Jul15)

"""

from direct.showbase.DirectObject import DirectObject
from direct.directnotify.DirectNotifyGlobal import directNotify

class TreasurePlannerAI(DirectObject):
    notify = directNotify.newCategory('TreasurePlannerAI')

    def __init__(self, zoneId, treasureConstructor, callback = None):
        self.zoneId = zoneId
        self.treasureConstructor = treasureConstructor
        self.callback = callback
        self.initSpawnPoints()
        self.treasures = []
        for _ in self.spawnPoints: self.treasures.append(None)
        self.deleteTaskNames = []
        self.lastRequestId = None
        self.requestStartTime = None
        self.requestCount = None

    def initSpawnPoints(self):
        self.spawnPoints = []
        return self.spawnPoints

    def numTreasures(self):
        counter = 0
        for treasure in self.treasures:
            if treasure: counter += 1
        return counter

    def countEmptySpawnPoints(self):
        counter = 0
        for treasure in self.treasures:
            if not treasure: counter += 1
        return counter

    def nthEmptyIndex(self, n):
        emptyCounter = -1
        spawnPointCounter = -1
        while emptyCounter < n:
            spawnPointCounter += 1
            if not self.treasures[spawnPointCounter]: emptyCounter += 1
        return spawnPointCounter

    def findIndexOfTreasureId(self, treasureId):
        counter = 0
        for treasure in self.treasures:
            if not treasure: pass
            elif treasureId == treasure.doId:
                return counter
            counter += 1
        return

    def placeAllTreasures(self):
        index = 0
        for treasure in self.treasures:
            if not treasure: self.placeTreasure(index)
            index += 1

    def placeTreasure(self, index):
        spawnPoint = self.spawnPoints[index]
        treasure = self.treasureConstructor(self.air, self, spawnPoint[0], spawnPoint[1], spawnPoint[2])
        treasure.generateWithRequired(self.zoneId)
        self.treasures[index] = treasure

    def grabAttempt(self, avId, treasureId):
        index = self.findIndexOfTreasureId(treasureId)
        if index == None:
            self.notify.warning('Suspicious: Avatar attempted to pick up non-existent treasure.')
            return
        av = self.air.doId2do.get(avId)
        if not av:
            self.notify.warning('Suspicious: TreasurePlannerAI.grabAttempt Received unknown avatar.')
        else:
            treasure = self.treasures[index]
            if self.validAvatar(treasure, av):
                self.treasures[index] = None
                if self.callback:
                    self.callback(avId)
                treasure.d_setGrab(avId)
                self.deleteTreasureSoon(treasure)
            else:
                treasure.d_setReject()
        if self.lastRequestId == avId:
            self.requestCount += 1
            now = globalClock.getFrameTime()
            elapsed = now - self.requestStartTime
            if elapsed > 10:
                self.requestCount = 1
                self.requestStartTime = now
            else:
                secondsPerGrab = elapsed / self.requestCount
                if self.requestCount >= 3 and secondsPerGrab <= 0.4:
                    self.notify.warning('Suspicious: %s has attempted to collect %s treasures in %s seconds.' % (str(avId), str(self.requestCount), str(elapsed)))
        else:
            self.lastRequestId = avId
            self.requestCount = 1
            self.requestStartTime = globalClock.getFrameTime()

    def deleteTreasureSoon(self, treasure):
        taskName = 'deletingTreasure'
        taskMgr.doMethodLater(5, self.__deleteTreasureNow, taskName, extraArgs = [treasure, taskName])
        self.deleteTaskNames.append(taskName)

    def deleteAllTreasuresNow(self):
        for treasure in self.treasures:
            if treasure: treasure.requestDelete()

        for taskName in self.deleteTaskNames:
            tasks = taskMgr.getTaskNamed(taskName)
            if len(tasks):
                treasure = tasks[0].getArgs()[0]
                treasure.requestDelete()
                taskMgr.remove(taskName)

        self.deleteTaskNames = []
        self.treasures = []
        for _ in self.spawnPoints:
            self.treasures.append(None)

    def __deleteTreasureNow(self, treasure, taskName):
        treasure.requestDelete()
        self.deleteTaskNames.remove(taskName)
