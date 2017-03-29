########################################
# Filename: VisitNPCObjective.py
# Created by: DecodedLogic (18Jul16)
########################################

from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.globals import CIGlobals
from src.coginvasion.quest.objective.Objective import Objective
from src.coginvasion.quest import QuestGlobals

class VisitNPCObjective(Objective):
    notify = directNotify.newCategory('VisitNPCObjective')

    def __init__(self, npcId, assigner, location = None, neededAmount = 0):
        location = CIGlobals.NPCToonDict.get(npcId)[0] if not location else location
        Objective.__init__(self, location, assigner, neededAmount)
        self.npcId = npcId
        
    def getTaskInfo(self, speech=False):
        Objective.getTaskInfo(self, speech=speech)
        
        infoText = '' if not speech else (QuestGlobals.VISIT + ' ');
        infoText += CIGlobals.NPCToonNames[self.npcId]
        
        return infoText

    def getNPCId(self):
        return self.npcId
