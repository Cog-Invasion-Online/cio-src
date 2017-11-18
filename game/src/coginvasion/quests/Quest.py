"""

Copyright (c) Cog Invasion Online. All rights reserved.

@file Quest.py
@authors Maverick Liberty, Brian Lach
@date November 13, 2017

@desc Adapted from Brian's original Quest class that was inside of the Quests module. This separate class was
to support multiple rewards, quest setup from blobs of data, and to allow players to work on multiple objectives
at once.

"""

from src.coginvasion.quests.Quests import Quests, RewardType2RewardClass
from src.coginvasion.quests.Quests import name, tier, finalInTier, rewards, collection
from src.coginvasion.quests.Quests import reward, assignSpeech, finishSpeech, objectives
from src.coginvasion.quests.Quests import objType, args, assigner, QuestNPCDialogue
from src.coginvasion.quests.ObjectiveCollection import ObjectiveCollection

class Quest:
    
    def __init__(self, id_, questMgr):
        # Parameters: Quest Id, QuestManager instance
        self.id = id_

        self.questMgr = questMgr
        self.data = Quests.get(self.id)
        self.name = self.data.get(name)
        self.tier = self.data.get(tier)
        self.lastQuestInTier = self.data.get(finalInTier, False)
        self.assignSpeech = self.data.get(assignSpeech)
        self.finishSpeech = self.data.get(finishSpeech)
        
        # List of all the rewards for completing the quest.
        self.rewards = []
        
        # Constructs the 'rewards' list
        for rewardData in self.data.get(rewards, []):
            rewardType = rewardData[0]
            rewardValue = rewardData[1]
            rewardClass = RewardType2RewardClass.get(rewardType)
            self.rewards.append(rewardClass(rewardType, rewardValue))
        
        # How many elements are under the objectives section of the quest data in this quest.
        # ObjectiveCollections count as one big objective.
        self.numObjectives = 0
        
        # Self-explanatory, the index of the current objective or objective(s) if it's a collection.
        self.currentObjectiveIndex = -1
        
        # ObjectiveCollection of all the accessible objectives (The objectives that can worked on)
        self.accessibleObjectives = ObjectiveCollection()
        
        # The current objective that the avatar is tracking with the compass.
        self.trackingObjective = None
        
    def __makeObjectiveFromData(self, objData, progress = 0):
        # Makes an Objective object from a passed dictionary of objType and args.
        objClass = objData.get(objType)
        objArgs = objData.get(args)
        objAssigner = objData.get(assigner, 0)
        
        objective = objClass(*objArgs)
        objective.progress = progress
        objective.assigner = objAssigner
        objective.quest = self
        return objective
        
    def setupCurrentObjectiveFromData(self, trackingObjectiveIndex, currentObjectiveIndex, objectiveProgress):
        objData = self.data.get(objectives)
        objTemplate = objData[currentObjectiveIndex]
        
        self.numObjectives = len(objData)
        self.currentObjectiveIndex = currentObjectiveIndex
        
        if collection in objTemplate.keys():
            # When we aren't passed data for the progress of each objective,
            # let's default to 0.
            
            if not objectiveProgress or len(objectiveProgress) == 0:
                objectiveProgress = []
                
                for _ in range(len(objTemplate.get(collection))):
                    objectiveProgress.append(0)
            
            for i, accObjData in enumerate(objTemplate.get(collection)):
                objective = self.__makeObjectiveFromData(accObjData, objectiveProgress[i])
                
                if trackingObjectiveIndex == i:
                    self.trackingObjective = objective
                self.accessibleObjectives.append(objective)
        else:
            if not objectiveProgress or len(objectiveProgress) == 0:
                objectiveProgress = [0]
            
            objective = self.__makeObjectiveFromData(objTemplate, objectiveProgress[0])
            
            if trackingObjectiveIndex == 0:
                self.trackingObjective = objective
            self.accessibleObjectives.append(objective)
    
    def getNextObjectiveIndex(self):
        # Returns the next objective's index or -1 if we're on the last objective.
        curObjIndex = self.currentObjectiveIndex
        
        if curObjIndex + 1 < self.numObjectives:
            return curObjIndex + 1
        return -1
    
    def getNextObjectiveData(self):
        return self.data.get(objectives)[self.currentObjectiveIndex + 1]
    
    def getCurrObjectiveData(self):
        return self.data.get(objectives)[self.currentObjectiveIndex]
    
    def getNextObjectiveDialogue(self):
        return QuestNPCDialogue.get(self.id).get(self.currentObjectiveIndex + 1)

    def getObjectiveDialogue(self):
        return QuestNPCDialogue.get(self.id).get(self.currentObjectiveIndex)
        
    def isComplete(self):
        # Returns if all accessible objectives are done and we don't have a next objective.
        return self.accessibleObjectives.isComplete() and self.getNextObjectiveIndex() == -1
    
    def giveRewards(self, avatar):
        for reward in self.rewards:
            reward.giveReward(avatar)
                
    def cleanup(self):
        del self.id
        del self.questMgr
        del self.data
        del self.name
        del self.tier
        del self.lastQuestInTier
        del self.assignSpeech
        del self.finishSpeech
        del self.rewards
        del self.numObjectives
        del self.currentObjectiveIndex
        self.accessibleObjectives.cleanup()
        del self.accessibleObjectives
        del self.trackingObjective
    