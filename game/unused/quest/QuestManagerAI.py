########################################
# Filename: QuestManagerAI.py
# Created by: DecodedLogic (18Jul16)
########################################

from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.quest.QuestManagerBase import QuestManagerBase
from src.coginvasion.quest.objective.CogObjective import CogObjective
from src.coginvasion.quest.objective.VisitNPCObjective import VisitNPCObjective
from src.coginvasion.quest.QuestBank import Quests, tier, requirements

import random

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
    
    """
    Returns the pickable quest list with an NPC's doId
    """
    
    def getPickableQuestList(self, npcDoId):
        # Each NPC is random!
        generator = random.Random()
        generator.seed(npcDoId)

        # This is the final quest list that will eventually hold the quests the avatar can choose.
        # This variable will be returned at the end of the method.
        quests = []

        # Our possible quest list is every Quest, right now. We will go down the line and remove quests that shouldn't be available.
        possibleQuestIds = list(Quests.keys())
        
        for questId in possibleQuestIds:
            quest = Quests.get(questId)
            
            # Quests have to be the same tier.
            if quest.get(tier) != self.avatar.getTier():
                possibleQuestIds.remove(questId)
                continue
            
            # We can't do Quests we already have or done.
            if questId in self.avatar.getQuestHistory():
                possibleQuestIds.remove(questId)
                continue
            
            # Next, let's make sure we have completed all the quests needed to start this one.
            requiredQuests = quest.get(requirements) if requirements in quest.keys() else []
            for reqQuestId in requiredQuests:
                if not reqQuestId in self.avatar.getQuestHistory() or reqQuestId in self.quests.keys():
                    possibleQuestIds.remove(questId)
                    break
                
        # Let's make sure we're not on the final quest in a tier.
        for quest in self.quests.values():
            if quest.isFinalQuestInTier():
                possibleQuestIds = []
                break
        
        if len(possibleQuestIds) > 3:
            # We have 4 or more quests available. Choose a random 3 out of that list.
            quests += generator.sample(possibleQuestIds, 3)
        else:
            # We have less than 4 quests, use the stripped down quest list directly.
            quests = possibleQuestIds
        
        return quests

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
