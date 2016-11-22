"""

  Filename: Quest.py
  Created by: DecodedLogic (13Nov15)

  Explanation:
      The whole idea here is that objectives are parts of a quest instead of objectives
      being their own quests. You can only be rewarded if all quest objectives are completed.
      Since the whole idea is that the QuestManager is suppose to build quests, a remove
      function for objectives has not been built as it doesn't make any sense.

"""

from panda3d.core import Vec4

from direct.directnotify.DirectNotifyGlobal import directNotify

from lib.coginvasion.quest import QuestGlobals

class Quest:
    notify = directNotify.newCategory('Quest')

    def __init__(self, name, requirement, tier, questId = -1, rewards = [], objectives = []):
        self.name = name
        self.requirement = requirement
        self.tier = tier
        self.rewards = rewards
        self.objectives = []
        self.completedObjectives = []
        self.currentObjective = None
        self.deletable = False
        self.id = questId
        self.resetGUIVariables()

        # Strangers are NPCs, such as HQ officers who give out the quest.
        # Owners are who the quest is for. The following arrays are dealt
        # with when an NPC is trying to persuade a player to get the quest.
        # A stranger would explain who the quest is for and an owner
        # would talk about what they need.
        self.assignByStrangerDialog = []
        self.assignByOwnerDialog = []
        
        for objective in objectives:
            self.addObjective(objective)

    #############################################
    ## Getters and Setters relating to posters ##
    #############################################

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

    #############################################

    def setObjectives(self, objectives):
        self.objectives = objectives

    def addObjective(self, objective):
        # Originally, this was not suppose to allow duplicate objectives,
        # however, Talk To objectives were considered and that no longer is
        # the case.
        if objective:
            objective.setQuest(self)
            self.objectives.append(objective)
            if not self.currentObjective:
                self.currentObjective = objective
        else:
            self.notify.warning('Attempted to add a None objective to a quest!')

    def getLastObjective(self):
        objectiveIndex = self.getObjectiveIndex(self.currentObjective)
        if not self.currentObjective:
            return None
        elif not objectiveIndex is None and (objectiveIndex - 1) >= 0:
            return self.objectives[objectiveIndex - 1]

    def getNextObjective(self):
        objectiveIndex = self.getObjectiveIndex(self.currentObjective)
        if not self.currentObjective:
            if len(self.objectives) > 0:
                return self.objectives[0]
            else:
                self.notify.warning('Quest is empty and has no objectives!')
                return None
        elif not objectiveIndex is None and (len(self.objectives) - 1) != objectiveIndex:
            return self.objectives[objectiveIndex + 1]
        return None

    def setCurrentObjective(self, obj):
        self.currentObjective = obj
        self.resetGUIVariables()

    def getCurrentObjective(self):
        return self.currentObjective

    def getCompletedObjectives(self):
        return self.completedObjectives

    def getObjectiveIndex(self, objective):
        return self.objectives.index(objective)

    def getObjectives(self):
        return self.objectives

    def isCompleted(self):
        finishedObjectives = 0
        for objective in self.objectives:
            if objective.finished():
                finishedObjectives += 1
        return len(self.objectives) == finishedObjectives

    def setDeletable(self, flag):
        self.deletable = flag

    def isDeletable(self):
        return self.deletable

    def setID(self, _id):
        self.id = _id

    def getID(self):
        return self.id

    def getName(self):
        return self.name

    def getTier(self):
        return self.tier

    def getRequirement(self):
        return self.requirement

    def getRewards(self):
        return self.rewards
    
    def setAssignByStrangerDialog(self, dialog):
        self.assignByStrangerDialog = dialog
    
    def getAssignByStrangerDialog(self):
        return self.assignByStrangerDialog
    
    def setAssignByOwnerDialog(self, dialog):
        self.assignByOwnerDialog = dialog
    
    def getAssignByOwnerDialog(self):
        return self.assignByOwnerDialog
