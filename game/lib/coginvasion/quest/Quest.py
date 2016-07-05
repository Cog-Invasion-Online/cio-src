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
    
    def __init__(self, name, requirement, tier, reward):
        self.name = name
        self.requirement = requirement
        self.tier = tier
        self.reward = reward
        self.objectives = []
        self.completedObjectives = []
        self.currentObjective = None
        
        # Strangers are NPCs, such as HQ officers who give out the quest.
        # Owners are who the quest is for. The following arrays are dealt
        # with when an NPC is trying to persuade a player to get the quest.
        # A stranger would explain who the quest is for and an owner
        # would talk about what they need.
        self.assignByStrangerDialog = []
        self.assignByOwnerDialog = []
        
    def setObjectives(self, objectives):
        self.objectives = objectives
        
    def addObjective(self, objective):
        # Originally, this was not suppose to allow duplicate objectives,
        # however, Talk To objectives were considered and that no longer is
        # the case.
        if objective:
            self.objectives.append(objective)
        else:
            self.notify.warning('Attempted to add a None objective to a quest!')
        
    def getNextObjective(self):
        objectiveIndex = self.getObjectiveIndex(self.currentObjective)
        if not self.currentObjective:
            if len(self.objectives) > 0:
                return self.objectives[0]
            else:
                self.notify.warning('Quest is empty and has no objectives!')
                return None
        elif objectiveIndex and (len(self.objectives) - 1) != objectiveIndex:
            return self.objectives[objectiveIndex + 1]
        return None
    
    def getCurrentObjective(self):
        return self.currentObjective
    
    def getCompletedObjectives(self):
        return self.completedObjectives
        
    def getObjectiveIndex(self, objective):
        return self.objectives.index(objective)
        
    def isCompleted(self):
        finishedObjectives = 0
        for objective in self.objectives:
            if objective.finished():
                finishedObjectives += 1
        return len(self.objectives) == finishedObjectives
    
    def getName(self):
        return self.name
    
    def getTier(self):
        return self.tier
    
    def getRequirement(self):
        return self.requirement
    
    def getReward(self):
        return self.reward