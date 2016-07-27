"""

  Filename: CogObjective.py
  Created by: DecodedLogic (13Nov15)
  
  Explanation:
      This is suppose to handle Cog objectives, like defeat of a certain level,
      department, location, variant, or name.

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.quest.Objective import Objective
from lib.coginvasion.quest import QuestGlobals
from lib.coginvasion.cog import SuitBank

class CogObjective(Objective):
    notify = directNotify.newCategory('CogObjective')
    
    def __init__(self, quest, location, assignDialog, amount, 
            level = None, levelRange = None, name = None, variant = None, dept = None):
        Objective.__init__(self, quest, location, assignDialog)
        self.neededAmount = amount
        self.amount = 0
        self.level = level
        self.levelRange = levelRange
        self.name = name
        self.dept = dept
        self.variant = variant
        self.didEditLeft = True
        
    def updateInfo(self, leftFrame = True, auxText = QuestGlobals.DEFEAT, frameColor = QuestGlobals.BLUE):
        Objective.updateInfo(self)
        self.didEditLeft = leftFrame
        
        if self.neededAmount > 1: 
            infoText = str(self.neededAmount)
        elif not self.name:
            infoText = 'A'
        else:
            infoText = ''
        
        if self.level:
            infoText = str('%s Level %s' % (infoText, str(self.level)))
        elif self.levelRange:
            infoText = str('%s Level %s+' % (infoText, str(self.levelRange[0])))
            
        if self.variant:
            variantText = CIGlobals.Skelesuit
            if self.neededAmount > 1:
                variantText = QuestGlobals.makePlural(variantText)
            infoText = str('%s %s' % (infoText, self.variant if self.neededAmount == 1 else QuestGlobals.makePlural(variantText)))
            
        if self.dept:
            infoText = str('%s %s' % (infoText, self.dept))
        elif not self.name:
            # Let's load up the general Cogs picture.
            icon = QuestGlobals.getCogIcon()
            
            if leftFrame:
                self.quest.setLeftIconGeom(icon)
                self.quest.setLeftIconScale(icon.getScale())
            else:
                self.quest.setRightIconGeom(icon)
                self.quest.setRightIconScale(icon.getScale())
            
            text = CIGlobals.Suit if self.neededAmount == 1 else CIGlobals.Suits
            infoText = str('%s %s' % (infoText, text))
            
        if self.name:
            nameText = self.name
            if self.neededAmount > 1:
                nameText = QuestGlobals.makePlural(self.name)
            infoText = str('%s %s' % (infoText, nameText))
            
            # Let's load up the head.
            head = SuitBank.getSuitByName(self.name).getHead().generate()
            head.setName('%sHead' % CIGlobals.Suit)
            head.setScale(2)
            head.setH(180)
            
            if leftFrame:
                self.quest.setLeftIconGeom(head)
            else:
                self.quest.setRightIconGeom(head)

        if leftFrame:
            self.quest.setInfoText(infoText)
            self.quest.setAuxText(auxText)
        else:
            self.quest.setInfo02Text(infoText)
            self.quest.setInfo02Pos(QuestGlobals.RECOVER_INFO2_POS)
            self.quest.setRightPicturePos(QuestGlobals.DEFAULT_RIGHT_PICTURE_POS)
        self.quest.setProgressText('%s of %s %s' % (self.amount, self.neededAmount, QuestGlobals.makePastTense(auxText).lower()))
        self.quest.setPictureFrameColor(frameColor)
    
    # This method should always be called when a Cog dies and the
    # a player is currently on this objective.    
    def isNeededCog(self, cog):
        if not self.location or self.isOnLocation(cog.zoneId):
            if self.level and not cog.getLevel() == self.level:
                print 'Level fail'
                return False
            
            if self.levelRange and not self.isInLevelRange(cog.getLevel()):
                print 'Range fail'
                return False
            
            if self.name and not cog.getName() == self.name:
                print 'Name Fail'
                return False
            
            if self.dept and not cog.getDept() == self.dept:
                print 'Department fail'
                return False
            
            if self.variant and not cog.getVariant() == self.variant:
                print 'Variant fail'
                return False
            
            return True
            
    def increment(self):
        Objective.increment(self)
        self.amount += 1
        self.updateQuest()
            
    def finished(self):
        return self.amount == self.neededAmount
            
    def isInLevelRange(self, level):
        if self.levelRange:
            return self.levelRange[0] <= level and self.levelRange[1] >= level
        return True
    
    def getDidEditLeft(self):
        return self.didEditLeft
    
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
    
    def getProgress(self):
        return self.amount
    
    def getNeededAmount(self):
        return self.neededAmount