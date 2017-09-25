########################################
# Filename: RecoverItemObjective.py
# Created by: DecodedLogic (19Jul16)
########################################

from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.quest.objective.CogObjective import CogObjective
from src.coginvasion.quest import QuestGlobals

class RecoverItemObjective(CogObjective):
    notify = directNotify.newCategory('RecoverItemObjective')

    def __init__(self, amount, itemName, assigner, location = None,
        itemIcon = QuestGlobals.getPackageIcon(), level = None, levelRange = None, name = None,
        variant = None, dept = None):
        CogObjective.__init__(self, location, assigner, amount = amount, level = level, levelRange = levelRange,
            name = name, variant = variant, dept = dept)
        self.itemName = itemName
        self.itemIcon = itemIcon
        
    def getTaskInfo(self, speech=False):
        cogObjInfo = CogObjective.getTaskInfo(self, speech = False, forcePlural = True)
        infoText = '' if not speech else (QuestGlobals.RECOVER + ' ');
        infoText += str('a %s' % self.itemName) if self.neededAmount == 1 else str('%d %s' % (self.neededAmount, QuestGlobals.makePlural(self.itemName)))
        infoText = str('%s from %s' % (infoText, cogObjInfo))
        
        return cogObjInfo
