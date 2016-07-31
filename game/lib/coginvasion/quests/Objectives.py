"""

Copyright (c) Cog Invasion Online. All rights reserved.

@file Objectives.py
@author Brian Lach
@date 2016-07-29

"""

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.hood import ZoneUtil
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
    # Examples of headers: Defeat, Recover, Deliver
    Header = ""

    # Does this objective have progress that needs to be tracked over time?
    HasProgress = False

    # Does this objective sometimes have to be completed in a certain area only?
    AreaSpecific = True

    def __init__(self, objectiveArgs, progress, quest):
        # A handle to the quest this objective belongs to.
        self.quest = quest

        # A list of arguments for this objective.
        self.objectiveArgs = objectiveArgs

        # The objective type (they are defined above)
        self.type = objectiveArgs[0]

        # The goal (number)
        self.goal = objectiveArgs[1]

        if self.AreaSpecific:
            # The area this quest has to be completed in (a playground zoneId or Anywhere)
            self.area = objectiveArgs[2]

        # The current progress on this objective (number)
        self.progress = progress

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
    Header = "Visit"

    def __init__(self, objectiveArgs, progress, quest):
        Objective.__init__(self, objectiveArgs, progress, quest)
        # DoID of the NPC.
        self.npcId = objectiveArgs[1]
        # ZoneId the NPC resides at.
        self.npcZone = objectiveArgs[2]

        # We don't need these variables.
        del self.goal
        del self.area

class DefeatObjective(Objective):
    Header = "Defeat"
    HasProgress = True

    def isValidLocation(self, hood):
        return (self.area == QuestGlobals.Anywhere or
            ZoneUtil.getHoodId(self.area, 1) == hood or
            ZoneUtil.getHoodId(self.area, 1) == CIGlobals.ToontownCentral and
            hood == CIGlobals.BattleTTC)

class CogObjective(DefeatObjective):

    def __init__(self, objectiveArgs, progress, quest):
        DefeatObjective.__init__(self, objectiveArgs, progress, quest)
        self.cog = objectiveArgs[3]

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

    def __init__(self, objectiveArgs, progress, quest):
        DefeatObjective.__init__(self, objectiveArgs, progress, quest)
        self.minCogLevel = objectiveArgs[3]

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

    def __init__(self, objectiveArgs, progress, quest):
        DefeatObjective.__init__(self, objectiveArgs, progress, quest)
        self.dept = objectiveArgs[3]

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
    Name = "%s Building"

    def __init__(self, objectiveArgs, progress, quest):
        DefeatObjective.__init__(self, objectiveArgs, progress, quest)
        self.dept = objectiveArgs[3]
        self.minFloors = objectiveArgs[4]

    def handleProgress(self, hood, dept, numFloors):
        if not self.isComplete():

            if self.isValidLocation(hood):

                if (self.dept == QuestGlobals.Any or self.dept == dept) and (numFloors >= self.minFloors or self.minFloors == QuestGlobals.Any):

                    self.quest.questMgr.incrementQuestObjectiveProgress(self.quest.questId)

    def getTaskInfo(self):
        taskInfo = ""
        if self.minFloors != QuestGlobals.Any:
            taskInfo += "%s+ Story " % self.minFloors

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
    Header = "Play"
    HasProgress = True
    AreaSpecific = False

    def __init__(self, objectiveArgs, progress, quest):
        Objective.__init__(self, objectiveArgs, progress, quest)
        self.minigame = objectiveArgs[2]

    def handleProgress(self, minigame):

        if not self.isComplete():

            if minigame == self.minigame:
                self.quest.questMgr.incrementQuestObjectiveProgress(self.quest.questId)

    def getTaskInfo(self):
        if self.goal > 1:
            taskInfo = "games of %s"
        else:
            taskInfo =  "game of %s"
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
    VisitHQOfficer:      VisitNPCObjective,
}
