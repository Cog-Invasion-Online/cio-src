# Filename: QuestManagerAI.py
# Created by:  blach (29Jul15)

import QuestGlobals, Quests
from QuestManagerBase import QuestManagerBase
from lib.coginvasion.hood import ZoneUtil
from lib.coginvasion.globals import CIGlobals

import random

class QuestManagerAI(QuestManagerBase):

    def __init__(self, avatar):
        QuestManagerBase.__init__(self)
        self.avatar = avatar

    def cleanup(self):
        QuestManagerBase.cleanup(self)
        del self.avatar

    def getPickableQuestList(self, npc):
        generator = random.Random()
        generator.seed(npc.doId)
        quests = []
        possibleQuestIds = list(Quests.Quests.keys())
        for questId in possibleQuestIds:
            if Quests.Quests[questId]["tier"] != self.avatar.getTier():
                possibleQuestIds.remove(questId)
                break
            for reqQuest in Quests.Quests[questId].get('rq', []):
                if not reqQuest in self.avatar.getQuestHistory() and questId in possibleQuestIds:
                    possibleQuestIds.remove(questId)
        for questId in self.avatar.getQuestHistory():
            if questId in possibleQuestIds:
                possibleQuestIds.remove(questId)
        if len(possibleQuestIds) > 1:
            for questId in possibleQuestIds:
                if Quests.Quests[questId].get("lastQuestInTier", False) == True:
                    possibleQuestIds.remove(questId)
        if len(possibleQuestIds) > 3:
            quests += generator.sample(possibleQuestIds, 3)
        else:
            quests = possibleQuestIds
        return quests

    def completedQuest(self, questId):
        quest = self.quests.get(questId)
        rewardValue = quest.rewardValue
        if quest.rewardType == Quests.RewardHealth:
            self.avatar.b_setMaxHealth(self.avatar.getMaxHealth() + rewardValue)
            self.avatar.b_setHealth(self.avatar.getMaxHealth())
            self.avatar.d_announceHealth(1, rewardValue)
        elif quest.rewardType == Quests.RewardJellybeans:
            self.avatar.b_setMoney(self.avatar.getMoney() + rewardValue)
        self.removeEntireQuest(questId)

    def isOnLastObjectiveOfQuest(self, questId):
        quest = self.quests.get(questId)
        return quest.currentObjectiveIndex >= quest.numObjectives - 1

    def wasLastObjectiveToVisit(self, npcId, checkCurrentCompleted = False):
        # If checkCurrentCompleted is True, the method will check if the last objective
        # was to visit this npc, and the current objective is done.
        #
        # If checkCurrentCompleted is False, the method will only check if the last objective
        # was to visit this npc.

        for quest in self.quests.values():
            questId = quest.questId
            currentObjectiveIndex = quest.currentObjectiveIndex
            currentObjective = quest.getCurrentObjective()
            lastObjectiveIndex = quest.currentObjectiveIndex - 1
            if lastObjectiveIndex < 0:
                continue
            lastObjectiveData = Quests.Quests[questId]["objectives"][lastObjectiveIndex]
            lastObjectiveType = lastObjectiveData[0]
            if lastObjectiveType == Quests.VisitNPC:
                if lastObjectiveData[2] == npcId:
                    if not checkCurrentCompleted:
                        return True
                    else:
                        if currentObjective.isComplete():
                            return True
            elif lastObjectiveType == Quests.VisitHQOfficer:
                if CIGlobals.NPCToonDict[npcId][3] == CIGlobals.NPC_HQ:
                    if not checkCurrentCompleted:
                        return True
                    else:
                        if currentObjective.isComplete():
                            return True
        return False

    def hasAnObjectiveToVisit(self, npcId, zoneId):
        for quest in self.quests.values():
            currObjective = quest.getCurrentObjective()
            if currObjective.type == Quests.VisitNPC:
                if currObjective.npcId == npcId:
                    if currObjective.npcZone == zoneId:
                        return True
            elif currObjective.type == Quests.VisitHQOfficer:
                if CIGlobals.NPCToonDict[npcId][3] == CIGlobals.NPC_HQ:
                    return True
        return False

    def checkIfObjectiveIsComplete(self, questId):
        quest = self.quests.get(questId)
        if quest.currentObjective.isComplete():
            self.incrementQuestObjective(questId)

    def cogDefeated(self, cog):
        for questId in self.quests.keys():
            quest = self.quests[questId]
            objective = quest.getCurrentObjective()
            if objective.type in Quests.DefeatCogObjectives:
                if not objective.isComplete():
                    if objective.type == Quests.DefeatCog:
                        if objective.subject == Quests.Any:
                            if (objective.area == Quests.Any or
                            ZoneUtil.getHoodId(objective.area, 1) == cog.getHood() or
                            ZoneUtil.getHoodId(objective.area, 1) == CIGlobals.ToontownCentral and
                            cog.getHood() == CIGlobals.BattleTTC):
                                self.incrementQuestObjectiveProgress(questId)
                        elif objective.subject == cog.head:
                            if (objective.area == Quests.Any or
                            ZoneUtil.getHoodId(objective.area, 1) == cog.getHood() or
                            ZoneUtil.getHoodId(objective.area, 1) == CIGlobals.ToontownCentral and
                            cog.getHood() == CIGlobals.BattleTTC):
                                self.incrementQuestObjectiveProgress(questId)
                    elif objective.type == Quests.DefeatCogLevel:
                        if cog.getLevel() >= objective.minCogLevel:
                            if (objective.area == Quests.Any or
                            ZoneUtil.getHoodId(objective.area, 1) == cog.getHood() or
                            ZoneUtil.getHoodId(objective.area, 1) == CIGlobals.ToontownCentral and
                            cog.getHood() == CIGlobals.BattleTTC):
                                self.incrementQuestObjectiveProgress(questId)
                    elif objective.type == Quests.DefeatCogDept:
                        if objective.subject == cog.team:
                            if (objective.area == Quests.Any or
                            ZoneUtil.getHoodId(objective.area, 1) == cog.getHood() or
                            ZoneUtil.getHoodId(objective.area, 1) == CIGlobals.ToontownCentral and
                            cog.getHood() == CIGlobals.BattleTTC):
                                self.incrementQuestObjectiveProgress(questId)

                self.checkIfObjectiveIsComplete(questId)

    def invasionDefeated(self, hood, size = None):
        for questId in self.quests.keys():
            quest = self.quests[questId]
            objective = quest.getCurrentObjective()
            if objective.type == Quests.DefeatCogInvasion:
                if not objective.isComplete():
                    if (objective.area == Quests.Any or
                    ZoneUtil.getHoodId(objective.area, 1) == hood or
                    ZoneUtil.getHoodId(objective.area, 1) == CIGlobals.ToontownCentral and
                    hood == CIGlobals.BattleTTC):
                        self.incrementQuestObjectiveProgress(questId)
                        self.checkIfObjectiveIsComplete(questId)

    def tournamentDefeated(self, hood):
        for questId in self.quests.keys():
            quest = self.quests[questId]
            objective = quest.getCurrentObjective()
            if objective.type == Quests.DefeatCogTournament:
                if not objective.isComplete():
                    if (objective.area == Quests.Any or
                    ZoneUtil.getHoodId(objective.area, 1) == hood or
                    ZoneUtil.getHoodId(objective.area, 1) == CIGlobals.ToontownCentral and
                    hood == CIGlobals.BattleTTC):
                        self.incrementQuestObjectiveProgress(questId)
                        self.checkIfObjectiveIsComplete(questId)

    def makeQuestsFromData(self):
        QuestManagerBase.makeQuestsFromData(self, self.avatar)

    def addNewQuest(self, questId):
        questHistory = list(self.avatar.getQuestHistory())
        questData = list(self.avatar.getQuests())
        questData[0].append(questId)
        questData[1].append(0)
        questData[2].append(0)
        questHistory.append(questId)
        self.avatar.b_setQuests(questData)
        self.avatar.b_setQuestHistory(questHistory)

    def removeEntireQuest(self, questId):
        quest = self.quests[questId]
        questData = list(self.avatar.getQuests())
        for array in questData:
            del array[quest.index]
        self.avatar.b_setQuests(questData)

    def incrementQuestObjective(self, questId, increment = 1):
        quest = self.quests[questId]
        questData = list(self.avatar.getQuests())
        questData[1][quest.index] += increment
        questData[2][quest.index] = 0
        self.avatar.b_setQuests(questData)

    def updateQuestObjective(self, questId, value):
        quest = self.quests[questId]
        questData = list(self.avatar.getQuests())
        questData[1][quest.index] = value
        self.avatar.b_setQuests(questData)

    def incrementQuestObjectiveProgress(self, questId, increment = 1):
        quest = self.quests[questId]
        questData = list(self.avatar.getQuests())
        questData[2][quest.index] += increment
        self.avatar.b_setQuests(questData)

    def updateQuestObjectiveProgress(self, questId, value):
        quest = self.quests[questId]
        questData = list(self.avatar.getQuests())
        questData[2][quest.index] = value
        self.avatar.b_setQuests(questData)
