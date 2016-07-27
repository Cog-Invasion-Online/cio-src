########################################
# Filename: QuestManagerBase.py
# Created by: DecodedLogic (18Jul16)
########################################

class QuestManagerBase:
    
    def __init__(self):
        self.quests = []
        self.tier = 0
        
    def addQuest(self, quest):
        self.quests.append(quest)
        
    def removeQuest(self, quest):
        self.quests.remove(quest)
        
    def getQuests(self):
        return self.quests
    
    def incrementObjective(self, quest):
        objective = quest.getCurrentObjective()
        objective.increment()
        
    def getQuestByID(self, questId):
        for quest in self.quests:
            if quest.getID() == questId:
                return quest
        return None
        
    def setTier(self, tier):
        self.tier = tier
        
    def getTier(self):
        return self.tier
        
    def cleanup(self):
        self.quests = None
        self.tier = None
        del self.quests
        del self.tier
