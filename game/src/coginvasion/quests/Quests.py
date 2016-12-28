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
        finishSpeech: ("Great job, young lad.\x07I see loads of potential in you.\x07One day you will be one of the best Cog busters around!\x07")},

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
                       "There's this one about a clock that--\x07You know what, I should let you be on your way.\x07Here, take this as a reward for your awesome help...\x07")}
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

        #self.resetGUIVariables()

    #################################################################
    # GUI methods

    def resetGUIVariables(self):
        # Variables that handle creation of the posters.
        self.auxText = ''
        self.auxTextPos = QuestGlobals.DEFAULT_AUX_POS
        self.infoText = ''
        self.infoPos = QuestGlobals.DEFAULT_INFO_POS
        self.info02Text = ''
        self.info02Pos = QuestGlobals.DEFAULT_INFO2_POS
        self.lPicturePos = QuestGlobals.DEFAULT_LEFT_PICTURE_POS
        self.lIconGeom = QuestGlobals.getPackageIcon()
        self.lIconScale = self.lIconGeom.getScale()
        self.rPicturePos = QuestGlobals.DEFAULT_RIGHT_PICTURE_POS
        self.rIconGeom = QuestGlobals.getPackageIcon()
        self.rIconScale = self.rIconGeom.getScale()
        self.pictureFrameColor = Vec4(*QuestGlobals.GREEN)
        self.progressBarText = ''
        self.locationText = 'N/A'
        self.locationY = 0
        self.middleText = ''

    def setAuxText(self, text):
        self.auxText = text

    def getAuxText(self):
        return self.auxText

    def setAuxPos(self, pos):
        self.auxTextPos = pos

    def getAuxPos(self):
        return self.auxTextPos

    def setInfoPos(self, pos):
        self.infoPos = pos

    def getInfoPos(self):
        return self.infoPos

    def setInfoText(self, text):
        self.infoText = text

    def getInfoText(self):
        return self.infoText

    def setInfo02Pos(self, pos):
        self.info02Pos = pos

    def getInfo02Pos(self):
        return self.info02Pos

    def setInfo02Text(self, text):
        self.info02Text = text

    def getInfo02Text(self):
        return self.info02Text

    def setLeftPicturePos(self, pos):
        self.lPicturePos = pos

    def getLeftPicturePos(self):
        return self.lPicturePos

    def setLeftIconGeom(self, geom):
        self.lIconGeom = geom

    def getLeftIconGeom(self):
        return self.lIconGeom

    def setLeftIconScale(self, scale):
        self.lIconScale = scale

    def getLeftIconScale(self):
        return self.lIconScale

    def setRightIconGeom(self, geom):
        self.rIconGeom = geom

    def getRightIconGeom(self):
        return self.rIconGeom

    def setRightIconScale(self, scale):
        self.rIconScale = scale

    def getRightIconScale(self):
        return self.rIconScale

    def setRightPicturePos(self, pos):
        self.rPicturePos = pos

    def getRightPicturePos(self):
        return self.rPicturePos

    def setPictureFrameColor(self, color):
        self.pictureFrameColor = Vec4(*color)

    def getPictureFrameColor(self):
        return self.pictureFrameColor

    def setLocationText(self, text):
        self.locationText = text

    def getLocationText(self):
        return self.locationText

    def setLocationY(self, y):
        self.locationY = y

    def getLocationY(self):
        return self.locationY

    def setProgressText(self, text):
        self.progressBarText = text

    def getProgressText(self):
        return self.progressBarText

    def setMiddleText(self, text):
        self.middleText = text

    def getMiddleText(self):
        return self.middleText

    ##########################################################

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
