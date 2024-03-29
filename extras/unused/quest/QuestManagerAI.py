########################################
# Filename: QuestManagerAI.py
# Created by: DecodedLogic (18Jul16)
########################################

from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.quest.QuestManagerBase import QuestManagerBase
from src.coginvasion.quest.objective import CogObjective.CogObjective
from src.coginvasion.quest import QuestBank
from src.coginvasion.quest.objective import VisitNPCObjective.VisitNPCObjective

class QuestManagerAI(QuestManagerBase):
    notify = directNotify.newCategory('QuestManagerAI')

    def __init__(self, air, avatar):
        QuestManagerBase.__init__(self)
        self.avatar = avatar

    ####################################################
    ## Functions for when an Objective event happens. ##
    ####################################################

    def getQuestToVisit(self, npcId):
        for quest in self.quests:
            objective = quest.getCurrentObjective()
            if objective and isinstance(objective, VisitNPCObjective):
                if objective.getNPCId() == npcId:
                    return quest
        return None
    
    def getPickableQuestList(self):
        pickableQuests = []
        for quest in QuestBank.getQuests():
            if quest.getTier() == self.avatar.getTier():
                if not quest in self.quests:
                    pickableQuests.append(quest.getID())
        return pickableQuests

    def wasLastObjectiveToVisit(self, npcId):
        for quest in self.quests:
            objective = quest.getLastObjective()
            if objective and isinstance(objective, VisitNPCObjective):
                if objective.getNPCId() == npcId:
                    return True
        return False

    def cogDefeated(self, cog):
        for quest in self.quests:
            obj = quest.getCurrentObjective()
            if isinstance(obj, CogObjective) and obj.isNeededCog(cog):
                self.b_incrementObjective(quest)

    def b_setQuestComplete(self, quest):
        for reward in quest.getRewards():
            reward.award()
        self.removeQuest(quest)

    def b_setTier(self, tier):
        self.avatar.b_setTier(tier)

    def b_incrementObjective(self, quest):
        QuestManagerBase.incrementObjective(self, quest)
        self.avatar.d_incrementQuestObjective(quest.getID())
        if quest.getCurrentObjective().finished():
            self.setCurrentObjective(quest, quest.getNextObjective())

    def setCurrentObjective(self, quest, obj):
        quest.setCurrentObjective(obj)
        objIndex = quest.getObjectives().index(obj)
        self.avatar.d_setQuestObjective(quest.getID(), objIndex)

    def getCurrentObjective(self, quest):
        return quest.getCurrentObjective()
