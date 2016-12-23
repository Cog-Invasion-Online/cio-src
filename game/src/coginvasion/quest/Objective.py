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
from src.coginvasion.quest import QuestGlobals
from src.coginvasion.hood import ZoneUtil

class Objective:
    notify = directNotify.newCategory('Objective')

    def __init__(self, location, assignDialog):
        self.quest = None
        self.location = location

        # This is the dialog the NPC says before the objective is given to you.
        self.assignDialog = assignDialog

    def updateInfo(self):
        # Setup the location text.
        if(self.location in CIGlobals.ZoneId2Hood.keys()):
            self.quest.setLocationText('%s\n%s' % (QuestGlobals.ANYWHERE,
                CIGlobals.ZoneId2Hood.get(self.location)))
            self.quest.setLocationY(0)
        elif(self.location in CIGlobals.BranchZone2StreetName.keys()):
            self.quest.setLocationText('%s\n%s' % (CIGlobals.BranchZone2StreetName.get(self.location),
                CIGlobals.ZoneId2Hood.get(self.location - (self.location % 1000))))
            self.quest.setLocationY(0)
        elif(self.location in CIGlobals.zone2TitleDict.keys()):
            shop = CIGlobals.zone2TitleDict.get(self.location)[0]
            streetZone = ZoneUtil.getBranchZone(self.location)
            if streetZone % 1000 >= 100:
                streetName = CIGlobals.BranchZone2StreetName[streetZone]
            else:
                streetName = QuestGlobals.PLAYGROUND
            hoodName = ZoneUtil.getHoodId(streetZone, 1)
            self.quest.setLocationText('%s\n%s\n%s' % (shop, streetName, hoodName))
            self.quest.setLocationY(0.025)
        elif not self.location:
            self.quest.setLocationText(QuestGlobals.ANYWHERE)
            
    def setQuest(self, quest):
        self.quest = quest
        
    def getQuest(self):
        return self.quest

    def increment(self):
        pass

    def setAssignDialog(self, dialog):
        self.assignDialog = dialog

    def getAssignDialog(self):
        return self.assignDialog

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

    def finished(self):
        pass
