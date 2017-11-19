"""

Copyright (c) Cog Invasion Online. All rights reserved.

@file QuestManagerAI.py
@author Brian Lach
@date July 29, 2015

"""

from src.coginvasion.quests.QuestManagerBase import QuestManagerBase
from src.coginvasion.quests.Quest import Quest
from src.coginvasion.quests import Quests
from src.coginvasion.quests import QuestData
from src.coginvasion.quests.Objectives import *
from src.coginvasion.quests.QuestGlobals import *

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
        
        # Give the rewards associated with the quest.
        quest.giveRewards(self.avatar)

        # Remove the quest.
        self.removeEntireQuest(questId)

    def wasLastObjectiveToVisit(self, npcId, checkCurrentCompleted = False):
        """
        If checkCurrentCompleted is True, the method will check if the last objective
        was to visit this npc, and the current objective is done.

        If checkCurrentCompleted is False, the method will only check if the last objective
        was to visit this npc.
        
        NOTE: This disregards visit objectives inside of ObjectiveCollections, the idea
        behind this method is to check if the last objective before the collection was to visit the assigner.
        """

        for quest in self.quests.values():
            questId = quest.id

            accessibleObjectives = quest.accessibleObjectives

            lastObjectiveIndex = quest.currentObjectiveIndex - 1
            if lastObjectiveIndex < 0:
                # Don't worry about this quest if it's only on the first objective.
                continue

            lastObjectiveData = Quests.Quests[questId][Quests.objectives][lastObjectiveIndex]
            lastObjectiveType = lastObjectiveData[Quests.objType]

            if lastObjectiveType == VisitNPC:
                # Check if the npcId for the last objective matches the npcId provided.
                if lastObjectiveData[Quests.args][0] == npcId:
                    return (not checkCurrentCompleted) or (checkCurrentCompleted 
                        and accessibleObjectives.isComplete())

            elif lastObjectiveType == VisitHQOfficer:
                # As long as the NPC is an HQ officer, we're good.
                if CIGlobals.NPCToonDict[npcId][3] == CIGlobals.NPC_HQ:
                    return (not checkCurrentCompleted) or (checkCurrentCompleted 
                        and accessibleObjectives.isComplete())

        # We had no matches.
        return False

    def hasAnObjectiveToVisit(self, npcId, zoneId):
        """Returns whether or not we have an objective to visit the NPC provided."""

        for quest in self.quests.values():
            objectives = quest.accessibleObjectives

            isHQ = CIGlobals.NPCToonDict[npcId][3] == CIGlobals.NPC_HQ
            
            for objective in objectives:
                if objective.type == VisitNPC:
                    # Make sure the npcIds match.
                    if objective.npcId == npcId:
                        # Make sure the zones match.
                        return objective.npcZone == zoneId
                elif objective.type == VisitHQOfficer:
                    # When the objective is to visit an HQ officer, we can visit any HQ officer.
                    # Just make sure that the NPC is an HQ Officer.
                    return isHQ
                else:
                    return (objective.isComplete()) and ((isHQ and objective.assigner == 0) 
                        or (objective.assigner == npcId))

        # I guess we have no objective to visit this npc.
        return False


    def checkIfObjectiveIsComplete(self, questId):
        """
        Checks if the current objective(s) on the questId is/are complete.
        If they are complete, it will increment the quest objective.
        """

        quest = self.quests.get(questId)

        if quest.accessibleObjectives.isComplete():
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

            objectives = quest.accessibleObjectives
            
            for objective in objectives:
                if not objective:
                    self.notify.info('Attempted to do __doProgress on a None object! Quest Id: %d.' % questId)
                    continue
                
                if objective.type in types:
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
        quest = Quest(questId, self)
        quest.setupCurrentObjectiveFromData(-1, 0, [0])
        
        quests = list(self.quests.values())
        quests.append(quest)
        questData = QuestData.toDataStump(quests, self.trackingId)

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

        del self.quests[questId]
        questData = QuestData.toDataStump(self.quests.values(), self.trackingId)

        # Update the information on the network and database.
        self.avatar.b_setQuests(questData)

    def incrementQuestObjective(self, questId, increment = 1):
        """
        Move to the next objective inside the quest.
        Mainly called when an objective is complete or when switching to the next objective.
        """
        
        currentObjectives = []
        
        for quest in self.quests.values():
            if quest.id != questId:
                currentObjectives.append(quest.currentObjectiveIndex)
            else:
                currentObjectives.append(quest.currentObjectiveIndex + increment)
        questData = QuestData.toDataStump(self.quests.values(), self.trackingId, currentObjectives)

        # Update the information on the network and database.
        self.avatar.b_setQuests(questData)

    def updateQuestObjective(self, questId, value):
        """Change the objective on the quest specified to the value specified."""
        currentObjectives = []
        
        for quest in self.quests.values():
            if quest.id != questId:
                currentObjectives.append(quest.currentObjectiveIndex)
            else:
                currentObjectives.append(value)
        questData = QuestData.toDataStump(self.quests.values(), self.trackingId, currentObjectives = currentObjectives)

        # Update the information on the network and database.
        self.avatar.b_setQuests(questData)
        
    def updateQuestData(self, currentObjectives = [], objectiveProgresses = []):
        questData, _, _ = QuestData.toDataStump(self.quests.values(), self.trackingId, currentObjectives, objectiveProgresses)
        self.avatar.b_setQuests(questData)

    def incrementQuestObjectiveProgress(self, questId, objIndex, increment = 1):
        """Increment the progress on the current objective of the quest specified by the increment."""

        progresses = []
        
        for quest in self.quests.values():
            if quest.id != questId:
                progress = []
                for objective in quest.accessibleObjectives:
                    progress.append(objective.progress)
                progresses.append(progress)
            else:
                progress = []
                for i, objective in enumerate(quest.accessibleObjectives):
                    if not i is objIndex:
                        progress.append(objective.progress)
                    else:
                        progress.append(objective.progress + increment)
                progresses.append(progress)
        return QuestData.toDataStump(self.quests.values(), self.trackingId, objectiveProgresses = progresses)

        # Let's see the if the objective is complete, now that we've updated the progress.
        #self.checkIfObjectiveIsComplete(questId)
        
    def getObjectiveIndex(self, questId, objective):
        """ Fetches the relative index of an objective inside of accessible objectives. """
        quest = self.quests[questId]
        
        for i, obj in enumerate(quest.accessibleObjectives):
            if obj == objective:
                return i
        return -1

    def updateQuestObjectiveProgress(self, questId, objIndex, value):
        """ Generates the quest data with the current objective progress on the quest specified to the value."""

        progresses = []
        
        for quest in self.quests.values():
            if quest.id != questId:
                progress = []
                for objective in quest.accessibleObjectives:
                    progress.append(objective.progress)
                progresses.append(progress)
            else:
                progress = []
                for i, objective in enumerate(quest.accessibleObjectives):
                    if not i is objIndex:
                        progress.append(objective.progress)
                    else:
                        progress.append(value)
                progresses.append(progress)
        return QuestData.toDataStump(self.quests.values(), self.trackingId, objectiveProgresses = progresses)
