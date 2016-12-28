# Filename: QuestManagerAI.py
# Created by:  blach (29Jul15)

from src.coginvasion.hood import ZoneUtil
from src.coginvasion.globals import CIGlobals

from QuestManagerBase import QuestManagerBase
from QuestGlobals import *
import Quests
from Objectives import *

import random

class QuestManagerAI(QuestManagerBase):

    def __init__(self, avatar):
        QuestManagerBase.__init__(self)
        # This is the DistributedToonAI we will be managing the quests of.
        self.avatar = avatar

    def cleanup(self):
        QuestManagerBase.cleanup(self)
        del self.avatar

    def getPickableQuestList(self, npc):
        """
        This method generates a list of quest IDs that can be chosen by the avatar.
        You have to pass in the DistributedHQNPCToonAI instance of the HQ officer that the avatar walked up to.
        """

        # Each NPC is random!
        generator = random.Random()
        generator.seed(npc.doId)

        # This is the final quest list that will eventually hold the quests the avatar can choose.
        # This variable will be returned at the end of the method.
        quests = []

        # Our possible quest list is every Quest, right now. We will go down the line and remove quests that shouldn't be available.
        possibleQuestIds = list(Quests.Quests.keys())

        for questId in possibleQuestIds:

            if Quests.Quests[questId][Quests.tier] != self.avatar.getTier():
                # This quest isn't in our tier. Remove it from the possible choices.
                possibleQuestIds.remove(questId)
                break

            for reqQuest in Quests.Quests[questId].get(Quests.requiredQuests, []):
                # Some quests need to have other quests completed before they are able to be chosen.
                if not reqQuest in self.avatar.getQuestHistory() and questId in possibleQuestIds:
                    # A required quest is not in our avatar's quest history. We can't choose it.
                    possibleQuestIds.remove(questId)

        for questId in self.avatar.getQuestHistory():
            if questId in possibleQuestIds:
                # We can't choose quests that we have already chosen or completed!
                possibleQuestIds.remove(questId)

        if len(possibleQuestIds) > 1:
            # We have more than one quest to choose from.
            for questId in possibleQuestIds:

                if Quests.Quests[questId].get(Quests.finalInTier, False) == True:
                    # We cannot choose the final quest for our tier if we still have other quests to complete.
                    possibleQuestIds.remove(questId)

        if len(possibleQuestIds) > 3:
            # We have 4 or more quests available. Choose a random 3 out of that list.
            quests += generator.sample(possibleQuestIds, 3)
        else:
            # We have less than 4 quests, use the stripped down quest list directly.
            quests = possibleQuestIds

        # And there's our quest list!
        return quests

    def completedQuest(self, questId):
        """Gives out the reward for the quest provided and removes the quest from our list."""

        quest = self.quests.get(questId)
        # Give the reward.
        quest.giveReward(self.avatar)

        # Remove the quest.
        self.removeEntireQuest(questId)

    def wasLastObjectiveToVisit(self, npcId, checkCurrentCompleted = False):
        """
        If checkCurrentCompleted is True, the method will check if the last objective
        was to visit this npc, and the current objective is done.

        If checkCurrentCompleted is False, the method will only check if the last objective
        was to visit this npc.
        """

        for quest in self.quests.values():
            questId = quest.questId

            currentObjectiveIndex = quest.currentObjectiveIndex
            currentObjective = quest.getCurrentObjective()

            lastObjectiveIndex = quest.currentObjectiveIndex - 1
            if lastObjectiveIndex < 0:
                # Don't worry about this quest if it's only on the first objective.
                continue

            lastObjectiveData = Quests.Quests[questId][Quests.objectives][lastObjectiveIndex]
            lastObjectiveType = lastObjectiveData[Quests.objType]

            if lastObjectiveType == VisitNPC:
                # Check if the npcId for the last objective matches the npcId provided.
                if lastObjectiveData[Quests.args][0] == npcId:
                    if not checkCurrentCompleted:
                        # We don't have to check if the current objective is complete. Just return True.
                        return True
                    else:
                        # We have an npc match, now we just have to make sure the current objective is complete.
                        if currentObjective.isComplete():
                            # Yep, it is.
                            return True

            elif lastObjectiveType == VisitHQOfficer:
                # As long as the NPC is an HQ officer, we're good.
                if CIGlobals.NPCToonDict[npcId][3] == CIGlobals.NPC_HQ:
                    if not checkCurrentCompleted:
                        # We don't have to check if the current objective is complete. Just return True.
                        return True
                    else:
                        # We have an npc match, now we just have to make sure the current objective is complete.
                        if currentObjective.isComplete():
                            # Yep, it is.
                            return True

        # We had no matches.
        return False

    def hasAnObjectiveToVisit(self, npcId, zoneId):
        """Returns whether or not we have an objective to visit the NPC provided."""

        for quest in self.quests.values():
            currObjective = quest.getCurrentObjective()

            isHQ = CIGlobals.NPCToonDict[npcId][3] == CIGlobals.NPC_HQ

            if currObjective.type == VisitNPC:
                # Make sure the npcIds match.
                if currObjective.npcId == npcId:
                    # Make sure the zones match.
                    if currObjective.npcZone == zoneId:
                        return True

            elif currObjective.type == VisitHQOfficer:
                # When the objective is to visit an HQ officer, we can visit any HQ officer.
                # Just make sure that the NPC is an HQ Officer.
                if isHQ:
                    return True

            else:
                if isHQ:
                    print "current objective is complete, needs to visit HQ Officer"
                    if (currObjective.isComplete() and currObjective.assigner == 0):
                        return True
                else:
                    if (currObjective.isComplete() and currObjective.assigner == npcId):
                        return True

        # I guess we have no objective to visit this npc.
        return False


    def checkIfObjectiveIsComplete(self, questId):
        """
        Checks if the current objective on the questId is complete.
        If it is compelete, it will increment the quest objective.
        """

        quest = self.quests.get(questId)

        if quest.currentObjective.isComplete():
            # It is complete. Increment the objective on this quest.
            self.incrementQuestObjective(questId)

    ################################################################
    # Objective progress methods

    def __doProgress(self, types, args):
        """
        Call this method when progress may have to be incremented on an objective.

        types: list of objective types that progress would be incremented on
        args:  list of arguments to pass onto the `handleProgress` method
        """

        for questId, quest in self.quests.items():

            objective = quest.getCurrentObjective()

            if objective is None:
                print "this objective is None"
                print questId
                continue

            if objective.type in types:
                print "__doProgress"
                objective.handleProgress(*args)

    def minigamePlayed(self, minigame):
        print "minigamePlayed: " + minigame
        self.__doProgress([PlayMinigame], [minigame])

    def cogDefeated(self, cog):
        self.__doProgress(DefeatCogObjectives, [cog])

    def cogBuildingDefeated(self, hood, dept, numFloors):
        self.__doProgress([DefeatCogBuilding], [hood, dept, numFloors])

    def invasionDefeated(self, hood, size = None):
        self.__doProgress([DefeatCogInvasion], [hood])

    def tournamentDefeated(self, hood):
        self.__doProgress([DefeatCogTournament], [hood])

    ######################################################################

    def makeQuestsFromData(self):
        QuestManagerBase.makeQuestsFromData(self, self.avatar)

    def addNewQuest(self, questId):
        """Add the specified quest to the avatar's quest history and current quests."""

        questHistory = list(self.avatar.getQuestHistory())

        questData = list(self.avatar.getQuests())
        questData[0].append(questId)
        # A new quest starts on the first objective.
        questData[1].append(0)
        # A new objective starts with no progress.
        questData[2].append(0)

        # Add this questId to the quest history.
        questHistory.append(questId)

        # Update this stuff on the network and database.
        self.avatar.b_setQuests(questData)
        self.avatar.b_setQuestHistory(questHistory)

    def removeEntireQuest(self, questId):
        """
        Remove the specified quest from the avatars current quest list.
        This is mainly called when a quest is completed.
        """

        quest = self.quests[questId]
        questData = list(self.avatar.getQuests())

        # Remove data for this quest from each questData array. (questId, objective, objective progress)
        for array in questData:
            del array[quest.index]

        # Update the information on the network and database.
        self.avatar.b_setQuests(questData)

    def incrementQuestObjective(self, questId, increment = 1):
        """
        Move the objective on the quest specified up by the increment specified.
        Mainly called when an objective is complete or when switching to the next objective.
        """

        quest = self.quests[questId]
        questData = list(self.avatar.getQuests())
        # Bump the objective index.
        questData[1][quest.index] += increment
        # New objectives start at 0 progress.
        questData[2][quest.index] = 0

        # Update the information on the network and database.
        self.avatar.b_setQuests(questData)

    def updateQuestObjective(self, questId, value):
        """Change the objective on the quest specified to the value specified."""

        quest = self.quests[questId]
        questData = list(self.avatar.getQuests())
        # The current objective index becomes value.
        questData[1][quest.index] = value

        # Update the information on the network and database.
        self.avatar.b_setQuests(questData)

    def incrementQuestObjectiveProgress(self, questId, increment = 1):
        """Increment the progress on the current objective of the quest specified by the increment."""

        quest = self.quests[questId]
        questData = list(self.avatar.getQuests())
        # Increment objective progress.
        questData[2][quest.index] += increment

        # Update the information on the network and database.
        self.avatar.b_setQuests(questData)

        # Let's see the if the objective is complete, now that we've updated the progress.
        #self.checkIfObjectiveIsComplete(questId)

    def updateQuestObjectiveProgress(self, questId, value):
        """Change the current objective progress on the quest specified to the value."""

        quest = self.quests[questId]
        questData = list(self.avatar.getQuests())
        # Change the current objective to `value`
        questData[2][quest.index] = value

        # Update the information on the network and database.
        self.avatar.b_setQuests(questData)
