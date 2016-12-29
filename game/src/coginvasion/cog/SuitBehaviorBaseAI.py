########################################
# Filename: SuitBehaviorBaseAI.py
# Created by: DecodedLogic (02Sep15)
########################################

from direct.showbase.DirectObject import DirectObject

class SuitBehaviorBaseAI(DirectObject):
    
    def __init__(self, suit, doneEvent = None):
        if doneEvent == None:
            doneEvent = 'suit%s-behaviorDone' % (suit.doId)
        self.doneEvent = doneEvent
        self.suit = suit
        
    def isAvatarReachable(self, var, exitFSM = False):
        if var == None or var.isEmpty():
            if hasattr(self, 'fsm') and exitFSM:
                self.fsm.enterInitialState()
                self.suit.getBrain().exitCurrentBehavior()
            return False
        return True
        
    def enter(self):
        if self.isEntered == 1:
            return
        self.isEntered = 1
        
    def exit(self):
        if self.isEntered == 1:
            self.isEntered = 0
            messenger.send(self.doneEvent)
            if self.suit and self.suit.brain:
                if self.suit.brain.currentBehavior == self:
                    self.suit.brain.currentBehavior = None
            
    def canEnter(self):
        return not self.isEntered
    
    def load(self):
        pass
    
    def unload(self):
        if hasattr(self, 'suit'):
            self.suit = None
            del self.suit
        del self.isEntered
        del self.doneEvent
        
    def shouldStart(self):
        pass
    
    def isActive(self):
        return self.isEntered
    
    def getDoneEvent(self):
        return self.doneEvent