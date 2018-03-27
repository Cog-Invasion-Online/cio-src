"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file SZTreasurePlannerAI.py
@author Maverick Liberty
@date July 15, 2015

"""

from RegenTreasurePlannerAI import RegenTreasurePlannerAI
from direct.directnotify.DirectNotifyGlobal import directNotify

class SZTreasurePlannerAI(RegenTreasurePlannerAI):
    notify = directNotify.newCategory('SZTreasurePlannerAI')

    def __init__(self, air, zoneId, treasureType, healAmount, spawnPoints, spawnRate, maxTreasures):
        self.air = air
        self.zoneId = zoneId
        self.spawnPoints = spawnPoints
        self.healAmount = healAmount
        self.canHealSad = True
        
        # The starfish are underwater in Donald's Dock.
        # During the CHRISTMAS holiday, we need to bring them to the surface.
        if self.zoneId == 1000 and air.holidayMgr.holiday == 1:
            for index, spawnPoint in enumerate(self.spawnPoints):
                # We need to convert the tuple into a list, update the Z,
                # then, convert that new list back to a tuple.
                xyz = list(spawnPoint)
                xyz[2] = 1.0
                spawnPoint = tuple(xyz)
                self.spawnPoints[index] = spawnPoint
                
        
        RegenTreasurePlannerAI.__init__(self, zoneId, treasureType, 'SZTreasurePlanner-%d' % zoneId, spawnRate, maxTreasures)

    def initSpawnPoints(self):
        pass

    def validAvatar(self, treasure, av):
        if av.getHealth() < av.getMaxHealth() or av.getHealth() == 0 and self.canHealSad:
            av.toonUp(self.healAmount, sound = 0)
            return True
        return False
