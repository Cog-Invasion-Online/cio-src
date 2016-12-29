########################################
# Filename: SuitRandomStrollBehaviorAI.py
# Created by: DecodedLogic (03Sep15)
########################################

from src.coginvasion.cog.SuitPathBehaviorAI import SuitPathBehaviorAI

class SuitRandomStrollBehaviorAI(SuitPathBehaviorAI):
    
    def __init__(self, suit):
        SuitPathBehaviorAI.__init__(self, suit)
        self.isEntered = 0
        
    def enter(self):
        SuitPathBehaviorAI.enter(self)
        self.createPath(fromCurPos = True)
    
    def shouldStart(self):
        return True