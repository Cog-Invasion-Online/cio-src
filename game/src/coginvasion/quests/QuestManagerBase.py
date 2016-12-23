# Filename: QuestManagerBase.py
# Created by:  blach (30Jul15)

import Objectives
import Quests
from src.coginvasion.globals import CIGlobals

class QuestManagerBase:

    def __init__(self):
        # A dictionary of questId -> quest instance
        self.quests = {}

    def cleanup(self):
        del self.quests

    def isOnLastObjectiveOfQuest(self, questId):
        """Returns whether or not the current objective of the quest specified is the last objective of the quest."""

        quest = self.quests.get(questId)
        return quest.currentObjectiveIndex >= quest.numObjectives - 1

    def getVisitQuest(self, npcId):
        """Returns the quest instance and the quest ID where the current objective of the quest is to visit the NPC specified."""
        
        print "getVisitQuest"
        for questId, quest in self.quests.items():
            currObjective = quest.getCurrentObjective()

            isHQ = CIGlobals.NPCToonDict[npcId][3] == CIGlobals.NPC_HQ

            if currObjective.type == Objectives.VisitNPC:
                # Check if the npcIds match.
                if (currObjective.npcId == npcId):
                    # Yep, return the questId and quest instance.
                    return [questId, quest]

            elif currObjective.type == Objectives.VisitHQOfficer:
                # Check if the npc specified is an HQ Officer.
                if isHQ:
                    # Yep, return the questId and quest instance.
                    return [questId, quest]

            else:
                # If it's not a visit objective, we have to visit the NPC who assigned us the objective.
                if isHQ:
                    if (currObjective.assigner == 0) and currObjective.isComplete():
                        print "quest {0} is complete and we are visiting an HQ Officer".format(questId)
                        return [questId, quest]
                else:
                    if (currObjective.assigner == npcId) and currObjective.isComplete():
                        return [questId, quest]

        # We have no quest where the current objective is to visit the NPC specified.
        return None

    def makeQuestsFromData(self, avatar):
        """Creates new quest instances based on the questData array from the avatar."""

        # Make sure to cleanup old quests before we override them.
        for quest in self.quests.values():
            quest.cleanup()

        self.quests = {}

        questData = avatar.getQuests()

        # Go through each quest in the quest data and create the quest instances.
        for i in xrange(len(questData[0])):

            questId = questData[0][i]
            currentObjectiveIndex = questData[1][i]
            currentObjectiveProg = questData[2][i]

            # Create the quest instance.
            quest = Quests.Quest(questId, currentObjectiveIndex, currentObjectiveProg, i, self)

            # Add it to our quests dictionary with the questId as the key.
            self.quests[questId] = quest
