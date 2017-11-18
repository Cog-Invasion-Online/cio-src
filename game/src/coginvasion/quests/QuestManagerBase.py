"""

Copyright (c) Cog Invasion Online. All rights reserved.

@file QuestManagerBase.py
@author Brian Lach
@date July 30, 2015

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

from src.coginvasion.globals import CIGlobals
from src.coginvasion.quests.Quest import Quest
from src.coginvasion.quests import QuestData
from src.coginvasion.quests import Objectives

class QuestManagerBase:
    notify = directNotify.newCategory('QuestManagerBase')

    def __init__(self):
        # A dictionary of questId -> quest instance
        self.quests = {}
        
        # The id of the quest we're tracking.
        self.trackingId = -1

    def cleanup(self):
        del self.quests

    def isOnLastObjectiveOfQuest(self, questId):
        """Returns whether or not the current objective of the quest specified is the last objective of the quest."""

        quest = self.quests.get(questId)
        return quest.currentObjectiveIndex >= quest.numObjectives - 1

    def getVisitQuest(self, npcId):
        """Returns the quest instance and the quest ID where we have an objective to visit the NPC specified."""
        
        for questId, quest in self.quests.items():
            accObjs = quest.accessibleObjectives

            isHQ = CIGlobals.NPCToonDict[npcId][3] == CIGlobals.NPC_HQ
            
            for objective in accObjs:
                if objective.type == Objectives.VisitNPC:
                    # Check if the npcIds match.
                    if (objective.npcId == npcId):
                        # Yep, return the questId and quest instance.
                        return [questId, quest]
    
                elif objective.type == Objectives.VisitHQOfficer:
                    # Check if the npc specified is an HQ Officer.
                    if isHQ:
                        # Yep, return the questId and quest instance.
                        return [questId, quest]
    
                else:
                    # If it's not a visit objective, we have to visit the NPC who assigned us the objective.
                    if isHQ:
                        if (objective.assigner == 0) and objective.isComplete():
                            self.notify.info("quest {0} is complete and we are visiting an HQ Officer".format(questId))
                            return [questId, quest]
                    else:
                        if (objective.assigner == npcId) and objective.isComplete():
                            return [questId, quest]

        # We have no quest with an objective to visit the NPC specified.
        return None
    
    def makeQuestFromData(self, questDataStump):
        id_ = questDataStump[0]
        curObjIndex = questDataStump[1]
        trackObjIndex = questDataStump[2]
        objProgress = questDataStump[3]
        
        quest = Quest(id_, self)
        quest.setupCurrentObjectiveFromData(trackObjIndex, curObjIndex, objProgress)
        self.quests[id_] = quest

    def makeQuestsFromData(self, avatar):
        """Creates new quest instances based on the questData array from the avatar."""

        # Make sure to cleanup old quests before we override them.
        for quest in self.quests.values():
            quest.cleanup()

        self.quests = {}

        QuestData.extractDataAsIntegerLists(avatar.getQuests(), parseDataFunc = self.makeQuestFromData)
