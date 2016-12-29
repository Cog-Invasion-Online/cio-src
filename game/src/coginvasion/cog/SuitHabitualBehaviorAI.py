########################################
# Filename: SuitHabitualBehaviorAI.py
# Created by: DecodedLogic (03Sep15)
########################################

from src.coginvasion.cog.SuitBehaviorBaseAI import SuitBehaviorBaseAI

class SuitHabitualBehaviorAI(SuitBehaviorBaseAI):
    
    def __init__(self, suit, doneEvent = None):
        if doneEvent == None:
            doneEvent = 'suit%s-behaviorDone' % (suit.doId)
        SuitBehaviorBaseAI.__init__(self, suit, doneEvent)
        self.isEntered = 0