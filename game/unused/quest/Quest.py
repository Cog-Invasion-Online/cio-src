"""

  Filename: Quest.py
  Created by: DecodedLogic (13Nov15)

  Explanation:
      The whole idea here is that objectives are parts of a quest instead of objectives
      being their own quests. You can only be rewarded if all quest objectives are completed.
      Since the whole idea is that the QuestManager is suppose to build quests, a remove
      function for objectives has not been built as it doesn't make any sense.

"""

from direct.directnotify.DirectNotifyGlobal import directNotify

class Quest:
    notify = directNotify.newCategory('Quest')

    def __init__(self, name, requirements, tier, questId = -1, rewards = [], objectives = [], isFinalInTier = False):
        self.name = name
        self.requirements = requirements
        self.tier = tier
        self.rewards = rewards
        self.objectives = []
        self.completedObjectives = []
        self.currentObjective = None
        self.deletable = False
        self.id = questId
        self.isFinalInTier = isFinalInTier

        # Strangers are NPCs, such as HQ officers who give out the quest.
        # Owners are who the quest is for. The following arrays are dealt
        # with when an NPC is trying to persuade a player to get the quest.
        # A stranger would explain who the quest is for and an owner
        # would talk about what they need.
        self.assignByStrangerDialog = []
        self.finishedDialog = []
        
        for objective in objectives:
            self.addObjective(objective)

    def setObjectives(self, objectives):
        self.objectives = objectives

    def addObjective(self, objective):
        # Originally, this was not suppose to allow duplicate objectives,
        # however, Talk To objectives were considered and that no longer is
        # the case.
        if objective:
            objective.setQuest(self)
            self.objectives.append(objective)
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

    def getCurrentObjective(self):
        return self.currentObjective

    def getCompletedObjectives(self):
        return self.completedObjectives

    def getObjectiveIndex(self, objective):
        if not objective is None:
            return self.objectives.index(objective)
        return -1

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

    def getRequirements(self):
        return self.requirements

    def getRewards(self):
        return self.rewards
    
    def getAssignDialog(self, isStranger):
        from src.coginvasion.quest import QuestBank
        if isStranger:
            return self.assignByStrangerDialog
        elif self.id in QuestBank.QuestNPCDialogue.keys():
            fullDialogue = QuestBank.QuestNPCDialogue.get(self.id)
            return fullDialogue.get(1) if 1 in fullDialogue.keys() else []
        return []
    
    def getFinishedDialog(self):
        return self.finishedDialog
    
    def isFinalInTier(self):
        return self.isFinalInTier
