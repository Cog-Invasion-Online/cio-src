"""

  Filename: SZTreasurePlannerAI.py
  Created by: DecodedLogic (15Jul15)

"""

from lib.coginvasion.hood.RegenTreasurePlannerAI import RegenTreasurePlannerAI
from direct.directnotify.DirectNotifyGlobal import directNotify

class SZTreasurePlannerAI(RegenTreasurePlannerAI):
    notify = directNotify.newCategory('SZTreasurePlannerAI')

    def __init__(self, air, zoneId, treasureType, healAmount, spawnPoints, spawnRate, maxTreasures):
        self.air = air
        self.zoneId = zoneId
        self.spawnPoints = spawnPoints
        self.healAmount = healAmount
        self.canHealSad = True
        RegenTreasurePlannerAI.__init__(self, zoneId, treasureType, 'SZTreasurePlanner-%d' % zoneId, spawnRate, maxTreasures)

    def initSpawnPoints(self):
        pass

    def validAvatar(self, treasure, av):
        if av.getHealth() < av.getMaxHealth() or av.getHealth() == 0 and self.canHealSad:
            av.toonUp(self.healAmount, sound = 0)
            return True
        else: return False
