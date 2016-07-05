# Filename: Quests.py
# Created by:  blach (30Jul15)

from lib.coginvasion.globals.CIGlobals import *

Any = 0

DefeatCog = 1
DefeatCogDept = 2
DefeatCogInvasion = 3
DefeatCogTournament = 4
DefeatCogLevel = 11
VisitNPC = 5
VisitHQOfficer = 12

DefeatCogObjectives = [DefeatCog, DefeatCogDept, DefeatCogLevel]
DefeatObjectives = [DefeatCog, DefeatCogDept, DefeatCogInvasion, DefeatCogTournament, DefeatCogLevel]

RewardNone = 6
RewardGagTrackProgress = 7
RewardJellybeans = 8
RewardHealth = 9
RewardAccess = 10

TierTT = 13
TierDD = 14
TierDG = 15
TierML = 16
TierBR = 17
TierDL = 18

VisHQObj = [VisitHQOfficer, 1, 1, Any]

Quests = {
    #0: {"objectives": [[DefeatCogLevel, 1, 3, Any]], "reward": (RewardHealth, 1), "tier": TierTT},
    #1: {"objectives": [[VisitNPC, 'visitanNPC', 2308, 2801], []]}
    0: {"objectives": [[VisitNPC, 'visitanNPC', 2003, 2516],
                    [DefeatCog, Any, 1, Any],
                    [VisitNPC, 'visitanNPC', 2003, 2516]],
        "reward": (RewardHealth, 1), "tier": TierTT},
    1: {'objectives': [[DefeatCogInvasion, '', 2, ToontownCentralId], VisHQObj], "reward": (RewardHealth, 2), "tier": TierTT, "rq": [0]},
    2: {'objectives': [[DefeatCogLevel, 3, 25, ToontownCentralId], VisHQObj], "reward": (RewardJellybeans, 1000), "tier": TierTT, "rq": [0]},
    3: {'objectives': [[DefeatCogTournament, '', 1, ToontownCentralId], VisHQObj], "reward": (RewardHealth, 2), "tier": TierTT, "rq": [0]},
    4: {'objectives': [[DefeatCogInvasion, '', 10, DonaldsDreamlandId], VisHQObj], "reward": (RewardHealth, 5), "tier": TierTT, "rq": [0, 1, 2, 3]}
}

QuestNPCDialogue = {
    0: [["Hello! My name is Professor Pete.", "I'm an expert in the field of pretty much everything around here.",
        "You're new, so you definitely need to learn some things.", "Let's talk about the Cogs.",
        "Pretty much, you take the Trolley in each playground in order to be taken to CogTropolis, which is where the Cogs are.",
        "In CogTropolis, you are in the present day Toontown. Right now, you're in the past.",
        "Show me that you know how to get to CogTropolis by defeating 1 Cog.",
        "Once you've done that, come back here."], [], ["Great job defeating that Cog! You really have some potential.",
        "Here, take your reward."]]
}

QuestHQOfficerDialogue = {
    0: [["Professor Pete has some tips to help you get started in Cog Invasion Online.",
            "Go see him, he's at the Schoolhouse in Toontown Central.", "Bye!"], [], []],
    1: [['Defeat 2 Cog Invasions in Toontown Central.', 'Have fun!']],
    2: [['Defeat 25 Level 3+ Cogs in Toontown Central', 'Have fun in Cog Invasion!']],
    3: [['Defeat a Cog Tournament anywhere.', 'Bye!']],
    4: [["Defeat 10 Cog Invasions in Donald's Dreamland.", "Good luck!"]]
}

HQOfficerQuestCongrats = "Nice job completing that Quest! You have earned your reward."
HQOfficerNoQuests = "Sorry, but I don't have any quests for you."

DefeatText = "Defeat"
VisitText = "Visit"

class Objective:

    def __init__(self, objectiveArgs, progress):
        self.objectiveArgs = objectiveArgs
        self.type = objectiveArgs[0]
        if self.type == DefeatCogLevel:
            self.minCogLevel = objectiveArgs[1]
        else:
            self.subject = objectiveArgs[1]
        if self.type == VisitNPC:
            self.npcId = objectiveArgs[2]
            self.npcZone = objectiveArgs[3]
        else:
            self.goal = objectiveArgs[2]
            self.area = objectiveArgs[3]
        self.progress = progress

    def isComplete(self):
        return self.progress >= self.goal

class Quest:

    def __init__(self, questId, currentObjectiveIndex, currentObjectiveProgress, index):
        self.questId = questId
        self.numObjectives = len(Quests[questId]["objectives"])
        self.currentObjectiveIndex = currentObjectiveIndex
        self.currentObjectiveProgress = currentObjectiveProgress
        objArgs = Quests[questId]["objectives"][currentObjectiveIndex]
        self.currentObjective = Objective(objArgs, currentObjectiveProgress)
        rewardData = Quests[questId]["reward"]
        self.rewardType = rewardData[0]
        self.rewardValue = rewardData[1]
        self.index = index
        self.tier = Quests[questId]["tier"]
        self.lastQuestInTier = Quests[questId].get("lastQuestInTier", False)

    def isLastQuestInTier(self):
        return self.lastQuestInTier

    def getTier(self):
        return self.tier

    def isComplete(self):
        if not self.currentObjective.type in [VisitNPC, VisitHQOfficer]:
            if self.currentObjective.isComplete() and self.currentObjectiveIndex >= self.numObjectives - 1:
                return True
        else:
            return self.currentObjectiveIndex >= self.numObjectives - 1

    def getCurrentObjectiveProgress(self):
        return self.currentObjectiveProgress

    def getNumObjectives(self):
        return self.numObjectives

    def getCurrentObjective(self):
        return self.currentObjective

    def getCurrentObjectiveIndex(self):
        return self.currentObjectiveIndex

    def getRewardType(self):
        return self.rewardType

    def getRewardValue(self):
        return self.rewardValue

    def getReward(self):
        return [self.rewardType, self.rewardValue]

    def getIndex(self):
        return self.index

    def cleanup(self):
        self.questId = None
        self.numObjectives = None
        self.currentObjectiveIndex = None
        self.currentObjectiveProgress = None
        self.currentObjective = None
        self.rewardType = None
        self.rewardValue = None
        self.index = None
        self.tier = None
