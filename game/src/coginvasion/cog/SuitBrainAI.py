########################################
# Filename: SuitBrainAI.py
# Created by: DecodedLogic (03Sep15)
########################################

from direct.showbase.DirectObject import DirectObject
from src.coginvasion.cog.SuitHabitualBehaviorAI import SuitHabitualBehaviorAI
from src.coginvasion.cog.SuitPathBehaviorAI import SuitPathBehaviorAI
from direct.task.Task import Task
import operator

class SuitBrain(DirectObject):

    def __init__(self, suit):
        self.suit = suit
        self.behaviors = {}
        self.queuedBehavior = None
        self.currentBehavior = None
        self.thinkTaskName = self.suit.uniqueName('think')
        self.isThinking = False

    def addBehavior(self, behavior, priority):
        self.behaviors.update({behavior : priority})
        behavior.load()
        self.organizeBehaviors()

    def removeBehavior(self, behavior):
        for iBehavior in self.behaviors.keys():
            if iBehavior == behavior:
                self.behaviors.remove(iBehavior)
                if self.currentBehavior == behavior:
                    self.exitCurrentBehavior()
        self.organizeBehaviors()
        
    def queueBehavior(self, behavior):
        self.queuedBehavior = behavior
            
    def removeQueuedBehavior(self):
        self.queuedBehavior = None

    def setPriorityOfBehavior(self, behaviorType, priority):
        # Update the priority on this behavior.
        for behavior in self.behaviors.keys():
            if behavior.__class__ == behaviorType:
                self.behaviors.update({behavior : priority})
                break
        # Now, push the behaviors with lower priorities down.
        for behavior, oldPrior in self.behaviors.keys():
            if behavior.__class__ != behaviorType:
                if priority >= oldPrior:
                    self.behaviors.update({behavior, oldPrior + 1})

    def getPriorityOfBehavior(self, behaviorType):
        for behavior, priority in self.behaviors.items():
            if behavior.__class__ == behaviorType:
                return priority

    def getBehavior(self, behaviorType):
        for behavior in self.behaviors.keys():
            if behavior.__class__ == behaviorType:
                return behavior

    def exitCurrentBehavior(self):
        if self.currentBehavior:
            self.currentBehavior.exit()
            if isinstance(self.currentBehavior, SuitPathBehaviorAI):
                self.currentBehavior.clearWalkTrack()
            if isinstance(self.currentBehavior, SuitHabitualBehaviorAI) and self.currentBehavior.isActive():
                self.ignore(self.currentBehavior.getDoneEvent())
                if self.isThinking and not taskMgr.hasTaskNamed(self.thinkTaskName):
                    taskMgr.add(self.__think, self.thinkTaskName)
            self.currentBehavior = None

    def organizeBehaviors(self):
        behaviors = {}
        for behavior, priority in self.behaviors.items():
            behaviors[behavior] = priority
        sorted_behaviors = sorted(behaviors.items(), key = operator.itemgetter(1))
        self.behaviors = {}
        for behaviorEntry in sorted_behaviors:
            behavior = behaviorEntry[0]
            priority = behaviorEntry[1]
            self.behaviors.update({behavior : priority})

    def startThinking(self, task = None):
        if not self.isThinking and not taskMgr.hasTaskNamed(self.thinkTaskName):
            self.isThinking = True
            taskMgr.add(self.__think, self.thinkTaskName)
            if task:
                return Task.done

    def stopThinking(self):
        self.isThinking = False
        taskMgr.remove(self.thinkTaskName)
        self.exitCurrentBehavior()

    def unloadBehaviors(self):
        for behavior in self.behaviors.keys():
            behavior.unload()
            del self.behaviors[behavior]
        if self.suit:
            self.suit = None
        del self.suit
        del self.behaviors
        del self.thinkTaskName
        del self.isThinking
        del self.queuedBehavior

    def isThinking(self):
        return self.isThinking

    def __think(self, task = None):
        # Let's delay our next behavior.
        if task and self.currentBehavior:
            task.delayTime = 1

        # Am I dead or have I been requested to stop thinking?
        if not hasattr(self, 'suit'):
            return Task.done

        if self.suit.isDead() or not self.isThinking:
            self.exitCurrentBehavior()
            self.isThinking = False
            return Task.done
        
        # Let's see if we have any queued behaviors.
        if not self.queuedBehavior is None:
            self.exitCurrentBehavior()
            for behavior in self.behaviors.keys():
                if behavior.__class__ == self.queuedBehavior:
                    behavior.enter()
                    self.currentBehavior = behavior
                    break
            self.queuedBehavior = None
            return Task.again

        readyBehaviors = []
        # Let's figure out which behaviors are ready (shouldStart = True).
        for behavior in self.behaviors.keys():
            # Don't even check if it should start if it's already entered.
            if behavior.isEntered == 1:
                continue
            if behavior.shouldStart():
                readyBehaviors.append(behavior)
        if len(readyBehaviors) > 0:
            # Sort our list of ready behaviors so the ready behavior with the highest priority is entered.
            readyBehaviors.sort(key = lambda behavior: self.behaviors[behavior], reverse = True)
            # Now, enter the highest priority ready behavior.
            behavior = readyBehaviors[0]
            self.exitCurrentBehavior()
            behavior.enter()
            self.currentBehavior = behavior

        # Should I continue thinking?
        if task:
            if isinstance(self.currentBehavior, SuitHabitualBehaviorAI) and self.currentBehavior.isActive():
                # This is a behavior that we can't override, we must wait until it completes.
                self.acceptOnce(self.currentBehavior.getDoneEvent(), self.startThinking)
                self.isThinking = False
                return Task.done
            return Task.again
