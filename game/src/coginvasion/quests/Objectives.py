"""

Copyright (c) Cog Invasion Online. All rights reserved.

@file Objectives.py
@author Brian Lach
@date 2016-07-29

"""

from src.coginvasion.globals import CIGlobals
from src.coginvasion.hood import ZoneUtil
from src.coginvasion.cog import Variant
from src.coginvasion.gags import GagGlobals
import QuestGlobals

####################################
# Objective types

DefeatCog = 1
RecoverItem = 2
DeliverItem = 6
DefeatCogInvasion = 3
DefeatCogTournament = 4
DefeatCogBuilding = 13
InspectLocation = 15

PlayMinigame = 14

VisitNPC = 5
VisitHQOfficer = 12
#####################################

# This is so we know what objectives react to QuestManagerAI.cogDefeated
DefeatCogObjectives = [DefeatCog]

# This is so we know which objectives you have to defeat stuff.
DefeatObjectives = [DefeatCog, DefeatCogInvasion, DefeatCogTournament, DefeatCogBuilding]

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
        
        # The area this quest has to be completed in (a playground zoneId or Anywhere)
        self.area = area if self.AreaSpecific else None

        # The current progress on this objective (number)
        self.progress = None

        self.showAsComplete = 0

    def setupQuestPoster(self):
        if self.HasProgress:
            self.quest.setProgressText(self.getProgressText())

    def getProgressText(self):
        return "%d of %d " % (self.progress, self.goal) + CIGlobals.makePastTense(self.Header)

    def handleProgress(self):
        # We have nothing to do here
        pass

    def getTaskInfo(self, speech = False):
        return ""

    def isComplete(self):
        return self.progress >= self.goal

class VisitNPCObjective(Objective):
    """
    [npcId, goal = None, area = None, showAsComplete = 0]
    0 npcId = HQ Officer
    """

    Header = QuestGlobals.VISIT

    def __init__(self, npcId, goal = None, area = None, showAsComplete = 0):
        Objective.__init__(self, goal, area)

        self.npcId = npcId

        self.showAsComplete = showAsComplete

        if npcId == 0:
            # Providing 0 as the npcId makes it an HQ officer.
            self.type = VisitHQOfficer
            self.npcZone = 0
        else:
            self.npcZone = CIGlobals.NPCToonDict[npcId][0]
            self.area = self.npcZone 

    def isComplete(self):
        return False

class DefeatObjective(Objective):
    Header = QuestGlobals.DEFEAT
    HasProgress = True

    def isValidLocation(self, hood):
        return (self.area == QuestGlobals.Anywhere or
            ZoneUtil.getHoodId(self.area, 1) == hood or
            ZoneUtil.getHoodId(self.area, 1) == CIGlobals.ToontownCentral and
            hood == CIGlobals.BattleTTC)

class CogObjective(DefeatObjective):
    """ [cogName, goal, area, level, levelRange, name, variant, dept] """

    def __init__(self, name, goal, area, level = None, levelRange = None, 
            variant = None, dept = None):
        DefeatObjective.__init__(self, goal, area)
        self.cog = name
        self.level = level
        self.levelRange = levelRange
        self.dept = dept
        self.variant = variant

    def handleProgress(self, cog):
        if not self.isComplete() and self.isNeededCog(cog):
            self.quest.questMgr.incrementQuestObjectiveProgress(self.quest.id, 
                self.quest.questMgr.getObjectiveIndex(self))
            
    def handleProgressFromDeadCogData(self, deadCogData):
        if not self.isComplete() and self.isNeededCogFromDeadCogData(deadCogData):
            self.quest.questMgr.incrementQuestObjectiveProgress(self.quest.id,
                self.quest.questMgr.getObjectiveIndex(self.quest.id, self))
            
    def isNeededCogFromDeadCogData(self, deadCogData):
        if not self.isValidLocation(deadCogData.location):
            return False
        
        if self.levelRange and not self.isInLevelRange(deadCogData.level):
            return False
        
        if self.cog and not self.cog == QuestGlobals.Any and not deadCogData.name == self.cog:
            return False
        
        if self.dept and not deadCogData.dept == self.dept:
            return False
        
        if self.variant and not deadCogData.variant == self.variant:
            return False
        
        return True
                    
    def isNeededCog(self, cog):
        if not self.isValidLocation(cog.getHood()):
            return False

        if self.levelRange and not self.isInLevelRange(cog.level):
            return False
        
        if self.cog and not self.cog == QuestGlobals.Any and not cog.name == self.cog:
            return False
        
        if self.dept and not cog.dept == self.dept:
            return False
        
        if self.variant and not cog.variant == self.variant:
            return False
        
        return True
        
    def isInLevelRange(self, level):
        if self.levelRange:
            return self.levelRange[0] <= level and self.levelRange[1] >= level
        return True
                    
    def getTaskInfo(self, speech = False):
        infoText = QuestGlobals.DEFEAT + ' ' if speech else ''
        infoText += (str(self.goal)) if self.goal > 1 else 'A'
        
        if self.level:
            infoText += (str('%s Level %s' % (infoText, str(self.level))))
        elif self.levelRange:
            infoText += str('%s Level %s+' % (infoText, str(self.levelRange[0])))
            
        if self.variant:
            variantTxt = Variant.VariantToName.get(self.variant)
            if self.goal > 1:
                variantTxt = CIGlobals.makePlural(variantTxt)
            infoText = str('%s %s' % (infoText, variantTxt))
            
        if self.dept:
            deptName = self.dept.getName() if not self.goal > 1 else CIGlobals.makePlural(self.dept.getName())
            infoText = str('%s %s' % (infoText, deptName))
        elif self.cog == QuestGlobals.Any:
            text = CIGlobals.Suit if not self.goal > 1 else CIGlobals.Suits
            infoText = str('%s %s' % (infoText, text))
        elif not self.cog == QuestGlobals.Any:
            nameText = self.cog if not self.goal > 1 else CIGlobals.makePlural(self.cog)
            infoText = str('%s %s' % (infoText, nameText))

        return infoText

from abc import ABCMeta

class ItemObjective:
    """ This is a base class for item-based objectives """
    __metaclass__ = ABCMeta
    
    def __init__(self, itemName, itemIcon = QuestGlobals.getPackageIcon()):
        self.itemName = itemName
        self.itemIcon = itemIcon
        
        if self.itemName in GagGlobals.gagIds.values():
            invIcons = loader.loadModel('phase_3.5/models/gui/inventory_icons.bam')
            self.itemIcon = invIcons.find('**/%s' % GagGlobals.InventoryIconByName[self.itemName])
            invIcons.removeNode()
    
class DeliverItemObjective(ItemObjective, VisitNPCObjective):
    """ [itemName, goal, npcId, itemIcon = QuestGlobals.getPackageIcon(), showAsComplete = 0)] """
    
    Header = QuestGlobals.DELIVER
    HasProgress = True
    
    def __init__(self, itemName, goal, npcId, 
                 itemIcon = QuestGlobals.getPackageIcon(), showAsComplete = 0):
        ItemObjective.__init__(self, itemName, itemIcon)
        VisitNPCObjective.__init__(self, npcId, goal, showAsComplete = showAsComplete)
    
class RecoverItemObjective(CogObjective):
    """ [itemName, goal, area, recoverChance (0 <= n <= 100), itemIcon = QuestGlobals.getPackageIcon(),
            name = QuestGlobals.Any, level = None, levelRange = None, variant = None, dept = None] """
    
    Header = QuestGlobals.RECOVER
    HasProgress = True
    
    def __init__(self, itemName, goal, area, recoverChance, itemIcon = QuestGlobals.getPackageIcon(),
            name = QuestGlobals.Any, level = None, levelRange = None, 
        variant = None, dept = None):
        ItemObjective.__init__(self, itemName, itemIcon = QuestGlobals.getPackageIcon())
        CogObjective.__init__(self, name, goal, area, level, levelRange, variant, dept)
        
        # We're expecting that the recover chance be (0 <= n <= 100).
        if 0 <= recoverChance <= 100:
            self.recoverChance = recoverChance
        else:
            raise ValueError('RecoverItemObjective: \'recoverChance\' member must be 0 <= n <= 100. '
                             / + 'Instead received {0}.'.format(recoverChance))
        
    def getTaskInfo(self, speech = False):
        cogObjInfo = CogObjective.getTaskInfo(self)
        infoText = self.Header + ' ';
        infoText += CIGlobals.getAmountString(self.itemName, self.goal)
        infoText = str('%s from %s' % (infoText, cogObjInfo))
        return infoText

class CogInvasionObjective(DefeatObjective):
    """ [goal, area] """

    Name = "Cog Invasion"

    def handleProgress(self, hood):
        if not self.isComplete():

            if self.isValidLocation(hood):
                self.quest.questMgr.incrementQuestObjectiveProgress(self.quest.id, 
                    self.quest.questMgr.getObjectiveIndex(self))

    def getTaskInfo(self, speech = False):
        if self.goal > 1:
            taskInfo = QuestGlobals.QuestSubjects[1]
        else:
            taskInfo = CIGlobals.makeSingular(self.Name)

        return taskInfo

class CogTournamentObjective(DefeatObjective):
    """ [goal, area] """

    Name = "Cog Tournament"

    def handleProgress(self, hood):
        if not self.isComplete():

            if self.isValidLocation(hood):
                self.quest.questMgr.incrementQuestObjectiveProgress(self.quest.id, 
                    self.quest.questMgr.getObjectiveIndex(self))

    def getTaskInfo(self, speech = False):
        if self.goal > 1:
            taskInfo = self.Name
        else:
            taskInfo = CIGlobals.makeSingular(self.Name)

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
                    self.quest.questMgr.incrementQuestObjectiveProgress(self.quest.id, 
                        self.quest.questMgr.getObjectiveIndex(self.quest.id, self))
                    
    def isAcceptable(self, hood, dept, numFloors):
        if not self.isComplete() and self.isValidLocation(hood):
            return (self.dept == QuestGlobals.Any or self.dept == dept) and (numFloors >= self.minFloors 
                or self.minFloors == QuestGlobals.Any)

    def getTaskInfo(self, speech = False):
        taskInfo = 'A ' if self.goal == 1 else '%d ' % self.goal
        if self.minFloors != QuestGlobals.Any:
            taskInfo += "%s+ Story " % QuestGlobals.getNumName(self.minFloors)
        
        name = self.Name
        if not speech:
            name = '%s\nBuilding'
        
        if self.dept == QuestGlobals.Any:
            subject = name % CIGlobals.Suit
        else:
            subject = name % self.dept.getName()

        if self.goal > 1:
            subject = CIGlobals.makePlural(subject)

        taskInfo += subject

        return taskInfo

class MinigameObjective(Objective):
    """ [minigameName, goal] """

    Header = "Play"
    HasProgress = True
    AreaSpecific = False

    def __init__(self, minigame, goal):
        Objective.__init__(self, goal, None)
        self.minigame = minigame
        self.area = CIGlobals.MinigameAreaId

    def handleProgress(self, minigame):

        if not self.isComplete():

            if minigame == self.minigame:
                self.quest.questMgr.incrementQuestObjectiveProgress(self.quest.id, 
                    self.quest.questMgr.getObjectiveIndex(self))

    def getTaskInfo(self, speech = False):
        if self.goal > 1:
            taskInfo = str(self.goal) + " Rounds of %s"
        else:
            taskInfo = "A Round of %s"
        taskInfo = taskInfo % self.minigame
        return taskInfo
    
class InspectLocation(Objective):
    
    Header = QuestGlobals.INSPECT
    HasProgress = True
    
    def __init__(self, inspectionSiteId):
        
        Objective.__init__(self, goal = 1, area = area)
    
# The objectives listed below require the double frame poster style.
DoubleFrameObjectives = [RecoverItemObjective, DeliverItemObjective]

# Objectives that are okay to end a quest on.
SafeEndObjectives = [VisitNPCObjective, DeliverItemObjective, RecoverItemObjective]

ObjectiveType2ObjectiveClass = {
    DefeatCog:                  CogObjective,
    RecoverItem:                RecoverItemObjective,
    DeliverItem:                DeliverItemObjective,
    DefeatCogInvasion:          CogInvasionObjective,
    DefeatCogTournament:        CogTournamentObjective,
    DefeatCogBuilding:          CogBuildingObjective,

    PlayMinigame:               MinigameObjective,

    VisitNPC:                   VisitNPCObjective,
}

ObjectiveClass2ObjectiveType = {v: k for k, v in ObjectiveType2ObjectiveClass.items()}
