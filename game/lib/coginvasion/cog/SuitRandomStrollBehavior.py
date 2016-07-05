########################################
# Filename: SuitRandomStrollBehavior.py
# Created by: DecodedLogic (03Sep15)
########################################

from lib.coginvasion.cog.SuitPathBehavior import SuitPathBehavior

class SuitRandomStrollBehavior(SuitPathBehavior):
    
    def __init__(self, suit):
        SuitPathBehavior.__init__(self, suit)
        self.isEntered = 0
        
    def enter(self):
        SuitPathBehavior.enter(self)
        self.createPath(fromCurPos = True)
    
    def shouldStart(self):
        return True