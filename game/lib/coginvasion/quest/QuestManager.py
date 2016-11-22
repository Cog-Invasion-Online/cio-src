########################################
# Filename: QuestManager.py
# Created by: DecodedLogic (18Jul16)
########################################

from lib.coginvasion.quest.QuestManagerBase import QuestManagerBase
from lib.coginvasion.quest import QuestBank

class QuestManager(QuestManagerBase):
    
    def __init__(self, cr):
        QuestManagerBase.__init__(self)
        self.quests.append(QuestBank.getQuests()[0])
        
    def setCurrentObjective(self, questId, objIndex):
        quest = self.getQuestByID(questId)
        quest.setCurrentObjective(quest.getObjectives()[objIndex])
        
    def getCurrentObjective(self, questId):
        quest = self.getQuestByID(questId)
        return quest.getCurrentObjective()
        
    def incrementObjective(self, questId):
        QuestManagerBase.incrementObjective(self, self.getQuestByID(questId))
