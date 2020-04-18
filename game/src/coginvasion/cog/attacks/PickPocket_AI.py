
from PickPocketShared import PickPocketShared
from src.coginvasion.attack.BaseAttackAI import BaseAttackAI
from src.coginvasion.attack.Attacks import ATTACK_PICKPOCKET

class PickPocket_AI(BaseAttackAI, PickPocketShared):
    Name = "Pick-Pocket"
    ID = ATTACK_PICKPOCKET

    PickTime = 0.4
    PickRange = 5.0

    def __init__(self):
        BaseAttackAI.__init__(self)
        self.actionLengths.update({self.StateAttack  :   3.0})
        self.traceOrigin = None
        self.traceVector = None
        self.didPick = False
        
    def determineNextAction(self, completedAction):
        if completedAction == self.StateAttack:
            self.avatar.npcFinishAttack()
        return BaseAttackAI.determineNextAction(self, completedAction)

    def getBaseDamage(self):
        return 10
        
    def getTauntChance(self):
        return 0.75
        
    def getTauntPhrases(self):
        return ['Let me check your valuables.',
            "Hey, what's that over there?",
            'Like taking candy from a baby.',
            'What a steal.',
            "I'll hold this for you.",
            'Watch my hands at all times.',
            'The hand is quicker than the eye.',
            "There's nothing up my sleeve.",
            'The management is not responsible for lost items.',
            "Finder's keepers.",
            "You'll never see it coming.",
            'One for me, none for you.',
            "Don't mind if I do.",
            "You won't be needing this..."]

    def cleanup(self):
        del self.traceOrigin
        del self.traceVector
        BaseAttackAI.cleanup(self)

    def think(self):
        BaseAttackAI.think(self)
        
        if (self.action == self.StateAttack and
            self.getActionTime() >= self.PickTime and
            not self.didPick):
            
            self.didPick = True
            self.doTraceAndDamage(self.traceOrigin, self.traceVector, self.PickRange)

    def checkCapable(self, dot, squaredDistance):
        return squaredDistance <= 8*8 and dot >= 0.8

    def canUse(self):
        return self.getAction() == self.StateIdle
        
    def onSetAction(self, action):
        if action == self.StateAttack:
            self.didPick = False

    def npcUseAttack(self, target):
        if not self.canUse():
            return False

        self.traceOrigin = self.avatar.getPos() + (0, 0, self.avatar.getHeight() / 2)
        self.traceVector = ((target.getPos() + (0, 0, target.getHeight() / 2.0)) - self.traceOrigin).normalized()
        self.setNextAction(self.StateAttack)
        
        return True
