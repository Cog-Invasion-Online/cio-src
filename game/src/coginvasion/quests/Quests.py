# Filename: Quests.py
# Created by:  blach (30Jul15)

from src.coginvasion.globals import CIGlobals
from src.coginvasion.cog import SuitGlobals, Dept

from QuestGlobals import Tiers, Any, Anywhere
from Objectives import *
from Rewards import *

VisHQObj = [VisitNPCObjective, 0, 1]

objectives = "objectives"
reward = "reward"
assignSpeech = "assignSpeech"
finishSpeech = "finishSpeech"
requiredQuests = "rq"
tier = "tier"
finalInTier = "lastQuestInTier"

args = "args"
assigner = "assigner"
objType = "objType"
name = "name"

"""
1: {objectives: [
        {objType: CogBuildingObjective, args: [Dept.BOSS, 0, 1, CIGlobals.DaisyGardensId]}
    ],
    reward: (GagSlot, 3),
    tier: Tiers.TT,
    requiredQuests: [0]},

2: {objectives: [
        {objType: CogBuildingObjective, args: [Any, 3, 3, Anywhere]}
    ],
    reward: (Health, 2),
    tier: Tiers.TT,
    requiredQuests: [0]},

3: {objectives: [
        {objType: MinigameObjective, args: [CIGlobals.UnoGame, 1]}
    ],
    reward: (Health, 1),
    tier: Tiers.TT,
    requiredQuests: [0]},
"""

Quests = {

    0: {objectives: [
            {objType: VisitNPCObjective, args: [2003]},
            {objType: CogObjective, args: [SuitGlobals.Flunky, 1, CIGlobals.ToontownCentralId], assigner: 2003}
        ],
        reward: (Health, 1),
        tier: Tiers.TT,
        assignSpeech: (
            "Nice work completing the tutorial!\x07You're probably already exhausted, but " + CIGlobals.NPCToonNames[2003] + " needs"
            " you right away.\x07"
        ),
        finishSpeech: ("Great job, young lad.\x07I see loads of potential in you.\x07One day you will be one of the best Cog busters around!\x07"),
        name: 'Schooled'},
          
    3: {objectives: [
            {objType: MinigameObjective, args: [CIGlobals.UnoGame, 1]}
        ],
        reward: (Health, 1),
        tier: Tiers.TT,
        requiredQuests: [0],
        name: 'Minigame Layout'},

    4: {objectives: [
            {objType: VisitNPCObjective, args: [2322]},
            {objType: VisitNPCObjective, args: [2108]},
            {objType: VisitNPCObjective, args: [2322]}
        ],
        reward: (Access, CIGlobals.DonaldsDockId),
        tier: Tiers.TT,
        finalInTier: True,
        assignSpeech: (
               "Something strange is going on at " + CIGlobals.zone2TitleDict[CIGlobals.NPCToonDict[2322][0]][0] + ".\x07"
               "Nobody else has been available to help, and " + CIGlobals.NPCToonNames[2322] + " is in desperate need of someone.\x07"
               "Go see him and find out what the problem is.\x07"),
        finishSpeech: ("What a great friend " + CIGlobals.NPCToonNames[2108] + " is, right?\x07Wow, thank you so much!\x07You know, some of his books are really great. "
                       "There's this one about a clock that--\x07You know what, I should let you be on your way.\x07Here, take this as a reward for your awesome help...\x07"),
        name: 'Strange Occurrences'},
          
    5: {objectives: [
            {objType: RecoverItemObjective, args: [5, CIGlobals.ToontownCentralId, 'Lipgloss', QuestGlobals.getPackageIcon(), SuitGlobals.TheMingler]}
        ],
        reward: (Jellybeans, 350),
        tier: Tiers.TT,
        assignSpeech: (
            "Nice work completing the tutorial!\x07You're probably already exhausted, but " + CIGlobals.NPCToonNames[2003] + " needs"
            " you right away.\x07"
        ),
        finishSpeech: ("Great job, young lad.\x07I see loads of potential in you.\x07One day you will be one of the best Cog busters around!\x07"),
        name: 'Mingle Mangle'},
          
    20: {objectives: [
            {objType: CogBuildingObjective, args: [Any, Any, 1, CIGlobals.DaisyGardensId]}
        ],
        reward: (GagSlot, 2),
        tier: Tiers.TT,
        requiredQuests: [0],
        name: 'Pick 1, Pick Anyone!'},
}

QuestNPCDialogue = {
    0: {1: ("Hello! I'm glad you stopped by.\x07My name is " + CIGlobals.NPCToonNames[2003] + ", PhD in Sillytology.\x07I'm conducting a study"
            " on new Toons to see how much potential they have.\x07Let's see how much potential you have...\x07Go out, defeat a Flunky"
            " and report back immediately!")},

    4: {1: ("Oh, thank goodness you are here!\x07The recipe for my signature whipped cream has gone missing!\x07"
            "I have absolutely no idea where it went.\x07It was right here, on my desk!\x07"
            "I went back to the kitchen to check on an order, and when I got back... it was gone!\x07My restaurant is far too busy today... "
            "there's no way I can leave this spot.\x07I wonder if my friend " + CIGlobals.NPCToonNames[2108] + " knows where it went."
            "\x07Could you please go ask him if he knows where it went?\x07"),
        2: ("Whipped cream recipe, eh?\x07I haven't seen " + CIGlobals.NPCToonNames[2322] + " all day, and I never saw a whipped cream recipe anywhere.\x07Oh, wait! "
            "I remember " + CIGlobals.NPCToonNames[2322] + " emailed me that recipe!\x07It's truly the best whipped cream I've ever had. "
            "I love putting it on waffles.\x07Here, let me print out a copy of the recipe, and you can give it to " + CIGlobals.NPCToonNames[2322] + ".\x07"
            "Okay... here you go!\x07Tell " + CIGlobals.NPCToonNames[2322] + " I said hi!")}
}

class Quest:

    def __init__(self, questId, currentObjectiveIndex, currentObjectiveProgress, index, questMgr):
        self.questId = questId

        self.questMgr = questMgr

        self.questData = Quests[questId]

        self.numObjectives = len(self.questData[objectives])

        self.currentObjectiveIndex = currentObjectiveIndex
        self.currentObjectiveProgress = currentObjectiveProgress

        objTemplate = self.questData[objectives][currentObjectiveIndex]
        objClass = objTemplate[objType]
        objArgs = objTemplate[args]
        objAssigner = objTemplate.get(assigner, 0)

        # Create an instance of the objective class
        self.currentObjective = objClass(*objArgs)
        self.currentObjective.progress = currentObjectiveProgress
        self.currentObjective.quest = self
        self.currentObjective.assigner = objAssigner

        rewardData = self.questData[reward]
        rewardType = rewardData[0]
        rewardValue = rewardData[1]
        self.reward = RewardType2RewardClass[rewardType](rewardType, rewardValue)

        self.index = index

        self.tier = self.questData[tier]

        self.assignSpeech = self.questData.get(assignSpeech)
        self.finishSpeech = self.questData.get(finishSpeech)

        self.objectiveDialogue = QuestNPCDialogue.get(questId)

        self.lastQuestInTier = self.questData.get(finalInTier, False)
        self.name = self.questData[name]

    def getIndex(self):
        return self.index

    def isLastQuestInTier(self):
        return self.lastQuestInTier

    def getTier(self):
        return self.tier

    def isComplete(self):
        if self.currentObjective.type not in [VisitNPC, VisitHQOfficer]:
            if self.currentObjective.isComplete() and self.currentObjectiveIndex >= self.numObjectives - 1:
                return True
        else:
            # If the current and last objective is to visit an npc, the quest is complete.
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

    def getNextObjectiveData(self):
        return self.questData[objectives][self.currentObjectiveIndex + 1]

    def getCurrObjectiveData(self):
        return self.questData[objectives][self.currentObjectiveIndex]

    def getNextObjectiveType(self):
        return self.questData[objectives][self.currentObjectiveIndex + 1][objType]

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
    
    def getName(self):
        return self.name

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
