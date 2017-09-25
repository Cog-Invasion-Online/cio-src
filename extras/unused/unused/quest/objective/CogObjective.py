"""

  Filename: CogObjective.py
  Created by: DecodedLogic (13Nov15)

  Explanation:
      This is suppose to handle Cog objectives, like defeat of a certain level,
      department, location, variant, or name.

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.globals import CIGlobals
from src.coginvasion.quest.objective.Objective import Objective
from src.coginvasion.quest import QuestGlobals
from src.coginvasion.cog import Variant

class CogObjective(Objective):
    notify = directNotify.newCategory('CogObjective')

    def __init__(self, location, assigner, amount,
            level = None, levelRange = None, name = None, variant = None, dept = None):
        Objective.__init__(self, location, assigner, neededAmount = amount)
        self.level = level
        self.levelRange = levelRange
        self.name = name
        self.dept = dept
        self.variant = variant
        
    # Has a required amt variable 
    def getTaskInfo(self, speech = False, forcePlural = False):
        Objective.getTaskInfo(self, speech=speech)
        
        forcePlural = True if self.neededAmount > 1 or forcePlural else False
        
        infoText = '' if not speech else (QuestGlobals.DEFEAT + ' ');
        infoText += (str(self.neededAmount)) if forcePlural else 'a ' if not self.name else ''
        
        if self.level:
            infoText += (str('%s Level %s' % (infoText, str(self.level))))
        elif self.levelRange:
            infoText += str('%s Level %s+' % (infoText, str(self.levelRange[0])))
            
        if self.variant:
            variantTxt = Variant.VariantToName.get(self.variant)
            if forcePlural:
                variantTxt = QuestGlobals.makePlural(variantTxt)
            infoText = str('%s %s' % (infoText, variantTxt))
            
        if self.dept:
            deptName = self.dept.getName() if not forcePlural else QuestGlobals.makePlural(self.dept.getName())
            infoText = str('%s %s' % (infoText, deptName))
        elif not self.name:
            text = CIGlobals.Suit if not forcePlural else CIGlobals.Suits
            infoText = str('%s %s' % (infoText, text))
        elif self.name:
            nameText = self.name if not forcePlural else QuestGlobals.makePlural(self.name)
            infoText = str('%s %s' % (infoText, nameText))

        return infoText

    # This method should always be called when a Cog dies and the
    # a player is currently on this objective.
    def isNeededCog(self, cog):
        if not self.location or self.isOnLocation(cog.zoneId):
            if self.level and not cog.getLevel() == self.level:
                return False

            if self.levelRange and not self.isInLevelRange(cog.getLevel()):
                return False

            if self.name and not cog.getName() == self.name:
                return False

            if self.dept and not cog.getDept() == self.dept:
                return False

            if self.variant and not cog.getVariant() == self.variant:
                return False

            return True

    def isInLevelRange(self, level):
        if self.levelRange:
            return self.levelRange[0] <= level and self.levelRange[1] >= level
        return True

    def getName(self):
        return self.name

    def getLevel(self):
        return self.level

    def getLevelRange(self):
        return self.levelRange

    def getDept(self):
        return self.dept

    def getVariant(self):
        return self.variant
