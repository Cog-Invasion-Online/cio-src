"""

  Filename: CogObjective.py
  Created by: DecodedLogic (13Nov15)
  
  Explanation:
      This is suppose to handle Cog objectives, like defeat of a certain level,
      department, location, variant, or name.

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

class CogObjective:
    notify = directNotify.newCategory('CogObjective')
    
    def __init__(self, amount, level = None, levelRange = None, name = None, variant = None, dept = None):
        self.neededAmount = amount
        self.amount = 0
        self.level = level
        self.levelRange = levelRange
        self.name = name
        self.dept = dept
        self.variant = variant
    
    # This method should always be called when a Cog dies and the
    # a player is currently on this objective.    
    def handleCogDeath(self, cog):
        if not self.location or self.isOnLocation(cog.zoneId):
            if self.level and not cog.getLevel() == self.level:
                return
            
            if self.levelRange and not self.isInLevelRange(cog.getLevel()):
                return
            
            if self.name and not cog.getName() == self.name:
                return
            
            if self.dept and not cog.getDept() == self.dept:
                return
            
            if self.variant and not cog.getVariant() == self.variant:
                return
            
            self.amount += 1
            self.updateQuest()
            
    def finished(self):
        return self.amount == self.neededAmount
            
    def isInLevelRange(self, level):
        if self.levelRange:
            return self.levelRange[0] <= level and self.levelRange[1] >= level
        return False