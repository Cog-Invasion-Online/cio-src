from src.coginvasion.attack.LinearProjectileAI import LinearProjectileAI
from src.coginvasion.globals import CIGlobals
from src.coginvasion.phys.WorldCollider import WorldCollider

class EvilEyeProjectileAI(LinearProjectileAI):

    def doInitCollider(self):
        WorldCollider.__init__(self, "wholeCreamPieCollider", 1.0, needSelfInArgs = True,
                          useSweep = True, resultInArgs = True, startNow = False,
                          mask = CIGlobals.WorldGroup | CIGlobals.CharacterGroup)
        self.world = self.air.getPhysicsWorld(self.zoneId)
