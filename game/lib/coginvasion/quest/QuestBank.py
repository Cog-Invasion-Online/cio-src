########################################
# Filename: QuestBank.py
# Created by: DecodedLogic (18Jul16)
########################################

from lib.coginvasion.quest.Quest import Quest
from lib.coginvasion.quest.VisitNPCObjective import VisitNPCObjective
from lib.coginvasion.quest.CogObjective import CogObjective
from lib.coginvasion.quest.QuestReward import QuestReward
from lib.coginvasion.quest import RewardType

import copy

quests = []

def addQuest(quest):
    quest.setID(len(quests))
    quests.append(quest)

def removeQuest(quest):
    quests.remove(quest)

def getQuest(quest):
    return copy.deepcopy(quest)

def getQuests():
    return quests

testQuest = Quest('The Quest System', None, 0, rewards = [QuestReward(RewardType.LAFF_POINTS, 2)])
testQuest.addObjective(CogObjective(testQuest, None,
    ['Cogs, the primary enemies of Toontown. What would a Quest System be without them?',
     'Assigning Quests to Toons to defeat the primary enemies of the game helps them level up.',
     'Speaking of assigning quests, do me a favor and defeat 25 Level 4+ Cogs.',
     'Have fun!'], 1))
testQuest.addObjective(VisitNPCObjective(2003, testQuest, []))
addQuest(testQuest)
