########################################
# Filename: QuestBank.py
# Created by: DecodedLogic (18Jul16)
########################################

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.quest.Quest import Quest
from lib.coginvasion.quest.VisitNPCObjective import VisitNPCObjective
from lib.coginvasion.quest.CogObjective import CogObjective
from lib.coginvasion.quest.QuestReward import QuestReward
from lib.coginvasion.quest import RewardType

import copy

def addQuest(quest):
    quest.setID(len(quests))
    quests.append(quest)

def removeQuest(quest):
    quests.remove(quest)

def getQuest(quest):
    return copy.deepcopy(quest)

def getQuestById(questId):
    for quest in quests:
        if quest.getID() == questId:
            return quest
    return None

def getQuests():
    return quests

quests = [
    Quest('Schooled', None, -1, 0, [QuestReward(RewardType.LAFF_POINTS, 2)],

        [VisitNPCObjective(2003, ["Nice work completing the tutorial!",
                                "I know you're probably exhausted, but you must see " + CIGlobals.NPCToonNames[2003] + " immediately!"]),

        CogObjective(None, ['Cogs, the primary enemies of Toontown. What would a Quest System be without them?',
                        'Assigning Quests to Toons to defeat the primary enemies of the game helps them level up.',
                        'Speaking of assigning quests, do me a favor and defeat 25 Level 4+ Cogs.',
                        'Have fun!'], 1),

        VisitNPCObjective(2003, [])]
    )
]
