from src.coginvasion.globals import CIGlobals

class BaseBehaviorAI:
    MaxVisionAngle = 130

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

    def isPlayerVisible(self, plyr, checkVisionAngle = True):
        # Check if player is potentially visible from my leaf.
        if not self.isPlayerInPVS(plyr):
            return False

        if checkVisionAngle:
            # Is the player in my angle of vision?
            angle = CIGlobals.getHeadsUpDistance(self.suit, plyr)
            if abs(angle) > self.MaxVisionAngle:
                return False

        # Is the player occluded by any BSP faces?
        return self.battle.traceLine(self.suit.getPos(render) + (0, 0, 3.5 / 2), plyr.getPos(render) + (0, 0, 2.0))
