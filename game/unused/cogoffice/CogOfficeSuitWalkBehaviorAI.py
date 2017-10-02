# Filename: CogOfficeSuitWalkBehaviorAI.py
# Created by:  blach (17Dec15)

from pandac.PandaModules import Point3

from src.coginvasion.cog.SuitPathBehaviorAI import SuitPathBehaviorAI
from CogOfficeConstants import *

class CogOfficeSuitWalkBehaviorAI(SuitPathBehaviorAI):

    def __init__(self, suit, spot):
        SuitPathBehaviorAI.__init__(self, suit)
        self.spot = spot

    def unload(self):
        del self.spot
        SuitPathBehaviorAI.unload(self)

    def enter(self):
        SuitPathBehaviorAI.enter(self)
        self.createPath()

    def createPath(self):
        if self.suit.battle.currentFloor in self.suit.battle.UNIQUE_FLOORS:
            points = POINTS[self.suit.battle.deptClass][self.suit.battle.currentFloor]['battle']
        else:
            points = POINTS[self.suit.battle.currentFloor]['battle']
        path = Point3(points[self.spot][0], points[self.spot][1], points[self.spot][2])
        durationFactor = 0.1
        startIndex = -1
        endIndex = self.spot
        pathList = [[path.getX(), path.getY()]]
        self.startPath(pathList, 0, durationFactor)
