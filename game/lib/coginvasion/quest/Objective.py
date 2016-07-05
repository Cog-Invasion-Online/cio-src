"""

  Filename: Objective.py
  Created by: DecodedLogic (13Nov15)
  
  Explanation:
      Each step in a quest is suppose to be an objective. The whole idea is that each quest
      has a series of objectives you must complete to get the reward. Objectives are what
      gets displayed in a player's quest menu.

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

class Objective:
    notify = directNotify.newCategory('Objective')
    
    def __init__(self, quest, location, assignDialog):
        self.quest = quest
        self.location = location
        
        # This is the dialog the NPC says before the objective is given to you.
        self.assignDialog = assignDialog
        
    def setAssignDialog(self, dialog):
        self.assignDialog = dialog
        
    def getAssignDialog(self, dialog):
        return self.assignDialog
    
    def isOnLocation(self, zoneId):
        if not isinstance(self.location, (list, tuple)):
            return self.location == zoneId
        else:
            return zoneId in self.location
    
    def updateQuest(self):
        pass
        
    def finished(self):
        pass
