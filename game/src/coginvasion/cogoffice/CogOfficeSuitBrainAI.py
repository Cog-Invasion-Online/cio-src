# Filename: CogOfficeSuitBrainAI.py
# Created by:  blach (17Dec15)

from direct.showbase.DirectObject import DirectObject
from direct.fsm import ClassicFSM, State

from CogOfficeConstants import *
from CogOfficeSuitAttackBehavior import CogOfficeSuitAttackBehavior
from CogOfficeSuitWalkBehavior import CogOfficeSuitWalkBehavior

import random

class CogOfficeSuitBrainAI(DirectObject):
    
    def __init__(self, suit):
        self.suit = suit
        self.fsm = ClassicFSM.ClassicFSM('CogOfficeSuitBrainAI', [State.State('off', self.enterOff, self.exitOff),
         State.State('attack', self.enterAttack, self.exitAttack),
         State.State('walk', self.enterWalk, self.exitWalk)], 'off', 'off')
        self.fsm.enterInitialState()
        self.targetToon = None
        self.currentSpot = None
        
    def startThinking(self, task = None):
        self.handleAttackBehaviorDone()
        if task is not None:
            return task.done
        
    def stopThinking(self):
        self.fsm.requestFinalState()
        self.clearStuff()
        
    def clearStuff(self):
        if self.currentSpot is not None and self.currentSpot in self.suit.battle.spotTaken2suitId.keys():
            del self.suit.battle.spotTaken2suitId[self.currentSpot]
        if (self.targetToon is not None and self.targetToon in self.suit.battle.avId2suitsAttacking.keys() and
        self.suit.doId in self.suit.battle.avId2suitsAttacking[self.targetToon]):
            self.suit.battle.avId2suitsAttacking[self.targetToon].remove(self.suit.doId)
        
    def cleanup(self):
        self.stopThinking()
        del self.fsm
        del self.suit
        del self.targetToon
        
    def enterOff(self):
        pass
        
    def exitOff(self):
        pass
        
    def enterAttack(self):
        self.behavior = CogOfficeSuitAttackBehavior(self.suit, self.targetToon)
        self.acceptOnce(self.behavior.doneEvent, self.handleAttackBehaviorDone)
        self.behavior.load()
        self.behavior.enter()
        
    def handleAttackBehaviorDone(self):
        # We're no longer attacking, clear our ID out of the attackers for our target.
        self.clearStuff()
        # We finished the number of attacks we can do, let's walk to a new spot now.
        spotsTaken = self.suit.battle.spotTaken2suitId.keys()
        availableSpots = []
        if self.suit.battle.currentFloor in self.suit.battle.UNIQUE_FLOORS:
            points = list(POINTS[self.suit.battle.deptClass][self.suit.battle.currentFloor]['battle'])
        else:
            points = list(POINTS[self.suit.battle.currentFloor]['battle'])
        for point in points:
            if not points.index(point) in spotsTaken:
                availableSpots.append(points.index(point))
        if self.currentSpot is None:
            if not self.suit.isChair:
                if self.suit.guardPoint in availableSpots:
                    availableSpots.remove(self.suit.guardPoint)
            else:
                if self.suit.battleStartPoint in availableSpots:
                    availableSpots.remove(self.suit.battleStartPoint)
        else:
            if self.currentSpot in availableSpots:
                availableSpots.remove(self.currentSpot)
        newSpot = random.choice(availableSpots)
        self.currentSpot = newSpot
        self.suit.battle.spotTaken2suitId[newSpot] = self.suit.doId
        self.fsm.request('walk', [newSpot])
        
    def exitAttack(self):
        self.ignore(self.behavior.doneEvent)
        self.behavior.exit()
        self.behavior.unload()
        del self.behavior
        
    def enterWalk(self, spot):
        self.behavior = CogOfficeSuitWalkBehavior(self.suit, spot)
        self.acceptOnce(self.behavior.doneEvent, self.handleWalkBehaviorDone)
        self.behavior.load()
        self.behavior.enter()
        
    def handleWalkBehaviorDone(self):
        # We finished walking to a new spot, pick a new toon to target.
        avIds = list(self.suit.battle.avatars)
        # We need to target the toon who has the least amount of attackers.
        avIds.sort(key = lambda avId: len(self.suit.battle.avId2suitsAttacking[avId]))
        # The toon to target is the avId at the top of the list since it's been sorted.
        target = avIds[0]
        self.targetToon = target
        self.suit.battle.avId2suitsAttacking[target].append(self.suit.doId)
        self.fsm.request('attack')
        
    def exitWalk(self):
        self.ignore(self.behavior.doneEvent)
        self.behavior.exit()
        self.behavior.unload()
        del self.behavior
        
    def unloadBehaviors(self):
        pass
