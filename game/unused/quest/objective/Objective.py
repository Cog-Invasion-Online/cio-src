"""

  Filename: Objective.py
  Created by: DecodedLogic (13Nov15)

  Explanation:
      Each step in a quest is suppose to be an objective. The whole idea is that each quest
      has a series of objectives you must complete to get the reward. Objectives are what
      gets displayed in a player's quest menu.

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.globals import CIGlobals

class Objective:
    notify = directNotify.newCategory('Objective')

    def __init__(self, location, assigner, neededAmount):
        self.quest = None
        self.location = location
        self.assigner = assigner
        self.amount = 0
        self.neededAmount = neededAmount
        
    def getTaskInfo(self, speech = False):
        pass

    def updateInfo(self):
        pass
            
    def setQuest(self, quest):
        self.quest = quest
        
    def getQuest(self):
        return self.quest

    def increment(self):
        self.amount += 1
    
    def getProgress(self):
        return self.amount
    
    def getNeededAmount(self):
        return self.neededAmount
    
    def finished(self):
        return self.amount >= self.neededAmount
    
    def getAssigner(self):
        return self.assigner

    def isOnLocation(self, zoneId):
        if not self.location:
            return True
        elif self.location in CIGlobals.ZoneId2Hood.keys():
            return zoneId - (zoneId % 1000) == self.location
        else:
            return self.location == zoneId

    def getLocation(self):
        return self.location

    def updateQuest(self):
        pass
