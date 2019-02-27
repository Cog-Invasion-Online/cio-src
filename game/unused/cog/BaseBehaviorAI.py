from src.coginvasion.globals import CIGlobals

class BaseBehaviorAI:
    MaxVisionAngle = 130
    MaxVisionDistance = 75

    def isPlayerAlive(self, plyr):
        return not plyr.isDead()

    def isSameLeafAsPlayer(self, plyr):
        plLeaf = self.battle.bspLoader.findLeaf(plyr)
        myLeaf = self.battle.bspLoader.findLeaf(self.suit)
        return plLeaf == myLeaf

    def isPlayerInPVS(self, plyr):
        plLeaf = self.battle.bspLoader.findLeaf(plyr)
        myLeaf = self.battle.bspLoader.findLeaf(self.suit)
        return self.battle.bspLoader.isClusterVisible(myLeaf, plLeaf)

    def isPlayerAudible(self, plyr):
        return self.isPlayerInPVS(plyr) and self.suit.getDistance(plyr) < 50.0
        
    def doesLineTraceToPlayer(self, plyr):
        # Is the player occluded by any BSP faces?
        return self.battle.traceLine(self.suit.getPos(render) + (0, 0, 3.5 / 2), plyr.getPos(render) + (0, 0, 2.0))
        
    def isPlayerInVisionCone(self, plyr):
        # Is the player in my angle of vision?
        angle = CIGlobals.getHeadsUpDistance(self.suit, plyr)
        return abs(angle) <= self.MaxVisionAngle
        
    def isPlayerInVisionRange(self, plyr):
        # Is the player close enough to where I could see them?
        return self.suit.getDistance(plyr) <= self.MaxVisionDistance

    def isPlayerVisible(self, plyr, checkVisionAngle = True, checkVisionDistance = True):
        # Check if player is potentially visible from my leaf.
        if not self.isPlayerInPVS(plyr):
            return False

        if checkVisionAngle and not self.isPlayerInVisionCone(plyr):
            return False
                
        if checkVisionDistance and not self.isPlayerInVisionRange(plyr):
            return False

        return self.doesLineTraceToPlayer(plyr)
