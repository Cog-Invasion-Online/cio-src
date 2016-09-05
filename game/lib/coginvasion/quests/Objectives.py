"""

Copyright (c) Cog Invasion Online. All rights reserved.

@file Objectives.py
@author Brian Lach
@date 2016-07-29

"""

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.hood import ZoneUtil
from lib.coginvasion.cog import SuitBank
import QuestGlobals

####################################
# Objective types

DefeatCog = 1
DefeatCogDept = 2
DefeatCogInvasion = 3
DefeatCogTournament = 4
DefeatCogLevel = 11
DefeatCogBuilding = 13

PlayMinigame = 14

VisitNPC = 5
VisitHQOfficer = 12
#####################################

# This is so we know what objectives react to QuestManagerAI.cogDefeated
DefeatCogObjectives = [DefeatCog, DefeatCogDept, DefeatCogLevel]

# This is so we know which objectives you have to defeat stuff.
DefeatObjectives = [DefeatCog, DefeatCogDept, DefeatCogInvasion, DefeatCogTournament, DefeatCogLevel, DefeatCogBuilding]

class Objective:
    """ [goal, area] """

    # Examples of headers: Defeat, Recover, Deliver
    Header = ""

    # Does this objective have progress that needs to be tracked over time?
    HasProgress = False

    # Does this objective sometimes have to be completed in a certain area only?
    AreaSpecific = True

    def __init__(self, goal, area):
        """`progress` and `quest` are automatically passed. Do not add them to your objective template."""

        # A handle to the quest this objective belongs to.
        self.quest = None

        # Set the int objective type based on the class.
        self.type = ObjectiveClass2ObjectiveType[self.__class__]

        # The goal (number)
        self.goal = goal

        if self.AreaSpecific:
            # The area this quest has to be completed in (a playground zoneId or Anywhere)
            self.area = area

        # The current progress on this objective (number)
        self.progress = None

        self.showAsComplete = 0

        self.didEditLeft = False

    def getDidEditLeft(self):
        return self.didEditLeft

    def setupQuestPoster(self):
        if self.HasProgress:
            self.quest.setProgressText(self.getProgressText())

    def getInfoText(self):
        if self.goal > 1:
            return str(self.goal) + ' '
        else:
            return 'A '

    def setCogsGeneralIcon(self):
        # Let's load up the general Cogs picture.
        icon = QuestGlobals.getCogIcon()

        if self.didEditLeft:
            self.quest.setLeftIconGeom(icon)
            self.quest.setLeftIconScale(icon.getScale())
        else:
            self.quest.setRightIconGeom(icon)
            self.quest.setRightIconScale(icon.getScale())

    def setCogSpecificIcon(self, cog, poster):
        # Let's load up the head.
        head = SuitBank.getSuitByName(cog).getHead().generate()
        head.setName('%sHead' % CIGlobals.Suit)
        head.setScale(2)
        head.setH(180)
        head.setDepthWrite(1)
        head.setDepthTest(1)
        poster.fitGeometry(head, fFlip = 1)

        if leftFrame:
           self.quest.setLeftIconGeom(head)
        else:
           self.quest.setRightIconGeom(head)

    def getProgressText(self):
        return "%d of %d " % (self.progress, self.goal) + QuestGlobals.makePastTense(self.Header)

    def handleProgress(self):
        # We have nothing to do here
        pass

    def getTaskInfo(self):
        return ""

    def isComplete(self):
        return self.progress >= self.goal

class VisitNPCObjective(Objective):
    """
    [npcId, showAsComplete = 0]
    0 npcId = HQ Officer
    """

    Header = "Visit"

    def __init__(self, npcId, showAsComplete = 0):
        Objective.__init__(self, None, None)

        self.npcId = npcId

        self.showAsComplete = showAsComplete

        if npcId == 0:
            # Providing 0 as the npcId makes it an HQ officer.
            self.type = VisitHQOfficer
            self.npcZone = 0
        else:
            self.npcZone = CIGlobals.NPCToonDict[npcId][0]

    def isComplete(self):
        return False

class DefeatObjective(Objective):
    Header = "Defeat"
    HasProgress = True

    def isValidLocation(self, hood):
        return (self.area == QuestGlobals.Anywhere or
            ZoneUtil.getHoodId(self.area, 1) == hood or
            ZoneUtil.getHoodId(self.area, 1) == CIGlobals.ToontownCentral and
            hood == CIGlobals.BattleTTC)

class CogObjective(DefeatObjective):
    """ [cogName, goal, area] """

    def __init__(self, cog, goal, area):
        DefeatObjective.__init__(self, goal, area)
        self.cog = cog

    def setupQuestPoster(self, poster):
        leftFrame = True
        self.didEditLeft = leftFrame
        frameColor = QuestGlobals.BLUE
        auxText = self.Header

        infoText = self.getInfoText()

        if self.cog == QuestGlobals.Any:
            self.setCogsGeneralIcon()
            text = CIGlobals.Suit if self.goal == 1 else CIGlobals.Suits
            infoText += text
        else:
            nameText = self.cog
            if self.goal > 1:
                nameText = QuestGlobals.makePlural(self.cog)
            infoText += nameText

            self.setCogSpecificIcon(self.cog, poster)

        if leftFrame:
           self.quest.setInfoText(infoText)
           self.quest.setAuxTex(self.Header)
        else:
           self.quest.setInfo02Text(infoText)
           self.quest.setInfo02Pos(QuestGlobals.RECOVER_INFO2_POS)
           self.quest.setRightPicturePos(QuestGlobals.DEFAULT_RIGHT_PICTURE_POS)

        self.quest.setPictureFrameColor(frameColor)

    def handleProgress(self, cog):
        if not self.isComplete():

            if (self.cog == QuestGlobals.Any) or (self.cog == cog.suitPlan.getName()):

                if self.isValidLocation(cog.getHood()):

                    self.quest.questMgr.incrementQuestObjectiveProgress(self.quest.questId)

    def getTaskInfo(self):
        if self.cog == QuestGlobals.Any:
            taskInfo = CIGlobals.Suits
        else:
            if self.goal > 1:
                taskInfo = QuestGlobals.makePlural(self.cog)
            else:
                taskInfo = self.cog

        return taskInfo

class CogLevelObjective(DefeatObjective):
    """ [minCogLevel, goal, area] """

    def __init__(self, minCogLevel, goal, area):
        DefeatObjective.__init__(self, goal, area)
        self.minCogLevel = minCogLevel

    def setupQuestPoster(self):
        leftFrame = True
        self.didEditLeft = leftFrame
        frameColor = QuestGlobals.BLUE
        auxText = self.Header

        self.setCogsGeneralIcon()

        infoText = self.getInfoText()

        infoText += "Level %s+ %s" % (self.minCogLevel, CIGlobals.Suit if self.goal == 1 else CIGlobals.Suits)

        if leftFrame:
            self.quest.setInfoText(infoText)
            self.quest.setAuxText(auxText)
        else:
            self.quest.setInfo02Text(infoText)
            self.quest.setInfo02Pos(QuestGlobals.RECOVER_INFO2_POS)
            self.quest.setRightPicturePos(QuestGlobals.DEFAULT_RIGHT_PICTURE_POS)

        self.quest.setProgressText('%s of %s %s' % (self.progress, self.goal, QuestGlobals.makePastTense(auxText).lower()))
        self.quest.setPictureFrameColor(frameColor)

    def handleProgress(self, cog):
        if not self.isComplete():

            if (cog.getLevel() >= self.minCogLevel) and self.isValidLocation(cog.getHood()):

                    self.quest.questMgr.incrementQuestObjectiveProgress(self.quest.questId)

    def getTaskInfo(self):
        if self.goal > 1:
            taskInfo = "Level %d+ %s" % (self.minCogLevel, CIGlobals.Suits)
        else:
            taskInfo = "Level %d+ %s" % (self.minCogLevel, CIGlobals.Suit)

        return taskInfo

class CogDeptObjective(DefeatObjective):
    """ [dept, goal, area] """

    def __init__(self, dept, goal, area):
        DefeatObjective.__init__(self, goal, area)
        self.dept = dept

    def setupQuestPoster(self):
        leftFrame = True
        self.didEditLeft = leftFrame
        frameColor = QuestGlobals.BLUE
        auxText = self.Header

        self.setCogsGeneralIcon()

        infoText = self.getInfoText()

        infoText += self.dept.getName() if self.goal == 1 else QuestGlobals.makePlural(self.dept.getName())

        if leftFrame:
            self.quest.setInfoText(infoText)
            self.quest.setAuxText(auxText)
        else:
            self.quest.setInfo02Text(infoText)
            self.quest.setInfo02Pos(QuestGlobals.RECOVER_INFO2_POS)
            self.quest.setRightPicturePos(QuestGlobals.DEFAULT_RIGHT_PICTURE_POS)

        self.quest.setProgressText('%s of %s %s' % (self.progress, self.goal, QuestGlobals.makePastTense(auxText).lower()))
        self.quest.setPictureFrameColor(frameColor)

    def handleProgress(self, cog):
        if not self.isComplete():

            if self.dept == cog.dept:

                if self.isValidLocation(cog.getHood()):

                    self.quest.questMgr.incrementQuestObjectiveProgress(self.quest.questId)

    def getTaskInfo(self):
        if self.goal > 1:
            taskInfo = self.dept.getName()
        else:
            taskInfo = QuestGlobals.makeSingular(self.dept.getName())

        return taskInfo

class CogInvasionObjective(DefeatObjective):
    """ [goal, area] """

    Name = "Cog Invasion"

    def handleProgress(self, hood):
        if not self.isComplete():

            if self.isValidLocation(hood):

                self.quest.questMgr.incrementQuestObjectiveProgress(self.quest.questId)

    def getTaskInfo(self):
        if self.goal > 1:
            taskInfo = QuestGlobals.QuestSubjects[1]
        else:
            taskInfo = QuestGlobals.makeSingular(self.Name)

        return taskInfo

class CogTournamentObjective(DefeatObjective):
    """ [goal, area] """

    Name = "Cog Tournament"

    def handleProgress(self, hood):
        if not self.isComplete():

            if self.isValidLocation(hood):

                self.quest.questMgr.incrementQuestObjectiveProgress(self.quest.questId)

    def getTaskInfo(self):
        if self.goal > 1:
            taskInfo = self.Name
        else:
            taskInfo = QuestGlobals.makeSingular(self.Name)

        return taskInfo

class CogBuildingObjective(DefeatObjective):
    """ [dept, minFloors, goal, area] """

    Name = "%s Building"

    def __init__(self, dept, minFloors, goal, area):
        DefeatObjective.__init__(self, goal, area)
        self.dept = dept
        self.minFloors = minFloors

    def handleProgress(self, hood, dept, numFloors):
        if not self.isComplete():

            if self.isValidLocation(hood):

                if (self.dept == QuestGlobals.Any or self.dept == dept) and (numFloors >= self.minFloors or self.minFloors == QuestGlobals.Any):

                    self.quest.questMgr.incrementQuestObjectiveProgress(self.quest.questId)

    def getTaskInfo(self):
        taskInfo = ""
        if self.minFloors != QuestGlobals.Any:
            taskInfo += "%s+ Story " % QuestGlobals.getNumName(self.minFloors)

        if self.dept == QuestGlobals.Any:
            subject = self.Name % CIGlobals.Suit
        else:
            subject = self.Name % self.dept.getName()

        if self.goal > 1:
            subject = QuestGlobals.makePlural(subject)

        taskInfo += subject

        return taskInfo

class RecoverObjective(Objective):
    Header = "Recover"
    HasProgress = True

    # Not implemented.

class MinigameObjective(Objective):
    """ [minigameName, goal] """

    Header = "Play"
    HasProgress = True
    AreaSpecific = False

    def __init__(self, minigame, goal):
        Objective.__init__(self, goal, None)
        self.minigame = minigame

    def handleProgress(self, minigame):

        if not self.isComplete():

            if minigame == self.minigame:
                self.quest.questMgr.incrementQuestObjectiveProgress(self.quest.questId)

    def getTaskInfo(self):
        if self.goal > 1:
            taskInfo = "games of %s"
        else:
            taskInfo = "game of %s"
        taskInfo = taskInfo % self.minigame
        return taskInfo

ObjectiveType2ObjectiveClass = {
    DefeatCog:           CogObjective,
    DefeatCogLevel:      CogLevelObjective,
    DefeatCogDept:       CogDeptObjective,
    DefeatCogInvasion:   CogInvasionObjective,
    DefeatCogTournament: CogTournamentObjective,
    DefeatCogBuilding:   CogBuildingObjective,

    PlayMinigame:        MinigameObjective,

    VisitNPC:            VisitNPCObjective,
}

ObjectiveClass2ObjectiveType = {v: k for k, v in ObjectiveType2ObjectiveClass.items()}
