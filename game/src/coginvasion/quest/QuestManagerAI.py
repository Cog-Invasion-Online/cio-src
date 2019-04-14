"""

Copyright (c) Cog Invasion Online. All rights reserved.

@file QuestManagerAI.py
@author Brian Lach
@date July 29, 2015

"""

from src.coginvasion.quest.QuestManagerBase import QuestManagerBase
from src.coginvasion.quest.Quest import Quest
from src.coginvasion.quest import QuestData
from src.coginvasion.quest.Objectives import PlayMinigame, DefeatCogObjectives, DefeatCogBuilding

class QuestManagerAI(QuestManagerBase):

    def __init__(self, avatar):
        QuestManagerBase.__init__(self, avatar)

    def cleanup(self):
        QuestManagerBase.cleanup(self)
        del self.avatar

    def completedQuest(self, questId):
        """Gives out the reward for the quest provided and removes the quest from our list."""

        quest = self.quests.get(questId)
        
        # Give the rewards associated with the quest.
        quest.giveRewards(self.avatar)

        # Remove the quest.
        self.removeEntireQuest(questId)

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
        self.__doProgress([PlayMinigame], [minigame])

    def cogDefeated(self, cog):
        self.__doProgress(DefeatCogObjectives, [cog])

    def cogBuildingDefeated(self, hood, dept, numFloors):
        self.__doProgress([DefeatCogBuilding], [hood, dept, numFloors])

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
        questData, _, _ = QuestData.toDataStump(quests, self.trackingId)

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
        questData, _, _ = QuestData.toDataStump(self.quests.values(), self.trackingId)

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
        questData, _, _ = QuestData.toDataStump(self.quests.values(), self.trackingId, currentObjectives)

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
        questData, _, _ = QuestData.toDataStump(self.quests.values(), self.trackingId, currentObjectives = currentObjectives)

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
                    if i != objIndex:
                        progress.append(objective.progress)
                    else:
                        progress.append(objective.progress + increment)
                progresses.append(progress)

        return QuestData.toDataStump(self.quests.values(), self.trackingId, objectiveProgresses = progresses)
        
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
