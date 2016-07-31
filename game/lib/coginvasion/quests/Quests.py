# Filename: Quests.py
# Created by:  blach (30Jul15)

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.cog import SuitGlobals, Dept

from QuestGlobals import Tiers, Any, Anywhere
from Objectives import *
from Rewards import *

VisHQObj = [VisitHQOfficer, 1, 1]

Quests = {

    0: {"objectives": [[VisitNPC, 2003, 2516],
                    [DefeatCog, 1, CIGlobals.ToontownCentralId, SuitGlobals.Flunky],
                    [VisitNPC, 2003, 2516]],
        "reward": (Health, 1), "tier": Tiers.TT,
        "assignSpeech": ("Nice work completing the tutorial!\x07You're probably already exhausted, but " + CIGlobals.NPCToonNames[2003] + " needs"
                         " you right away.\x07"),
        "finishSpeech": ("Great job, young lad.\x07I see loads of potential in you.\x07One day you will be one of the best Cog busters around!\x07")},

    1: {"objectives": [[DefeatCogBuilding, 1, CIGlobals.DaisyGardensId, Dept.BOSS, Any], VisHQObj], "reward": (GagSlot, 3), "tier": Tiers.TT},
    2: {"objectives": [[DefeatCogBuilding, 3, Anywhere, Any, 3], VisHQObj], "reward": (Health, 2), "tier": Tiers.TT},
    3: {"objectives": [[PlayMinigame, 1, CIGlobals.UnoGame], VisHQObj], "reward": (Health, 1), "tier": Tiers.TT}

}

QuestNPCDialogue = {
    0: {1: ("Hello! I'm glad you stopped by.\x07My name is " + CIGlobals.NPCToonNames[2003] + ", PhD in Sillytology.\x07I'm conducting a study"
            " on new Toons to see how much potential they have.\x07Let's see how much potential you have...\x07Go out, defeat a Flunky"
            " and report back immediately!")}
}

class Quest:

    def __init__(self, questId, currentObjectiveIndex, currentObjectiveProgress, index, questMgr):
        self.questId = questId

        self.questMgr = questMgr

        self.numObjectives = len(Quests[questId]["objectives"])

        self.currentObjectiveIndex = currentObjectiveIndex
        self.currentObjectiveProgress = currentObjectiveProgress

        self.questData = Quests[questId]

        objArgs = self.questData["objectives"][currentObjectiveIndex]
        # Get the objective class from the objective type
        objClass = ObjectiveType2ObjectiveClass[objArgs[0]]
        # Create an instance of the objective class
        self.currentObjective = objClass(objArgs, currentObjectiveProgress, self)

        rewardData = self.questData["reward"]
        rewardType = rewardData[0]
        rewardValue = rewardData[1]
        self.reward = RewardType2RewardClass[rewardType](rewardType, rewardValue)

        self.index = index

        self.tier = self.questData["tier"]

        self.assignSpeech = self.questData.get("assignSpeech")
        self.finishSpeech = self.questData.get("finishSpeech")

        self.objectiveDialogue = QuestNPCDialogue.get(questId)

        self.lastQuestInTier = self.questData.get("lastQuestInTier", False)

    def getIndex(self):
        return self.index

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

    ##############################################
    # Objectives

    def getNextObjectiveType(self):
        return self.questData["objectives"][self.currentObjectiveIndex + 1][0]

    def getNextObjectiveDialogue(self):
        return self.objectiveDialogue.get(self.currentObjectiveIndex + 1)

    def getObjectiveDialogue(self):
        return self.objectiveDialogue.get(self.currentObjectiveIndex)

    def getCurrentObjectiveProgress(self):
        return self.currentObjectiveProgress

    def getNumObjectives(self):
        return self.numObjectives

    def getCurrentObjective(self):
        return self.currentObjective

    def getCurrentObjectiveIndex(self):
        return self.currentObjectiveIndex

    ############################################

    ############################################
    # Rewards

    def giveReward(self, avatar):
        self.reward.giveReward(avatar)

    def getRewardType(self):
        return self.reward.rewardType

    def getRewardValue(self):
        return self.reward.rewardValue

    def getReward(self):
        return self.reward

    ###########################################
