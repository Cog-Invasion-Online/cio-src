from src.coginvasion.attack.LobProjectileAI import LobProjectileAI
from src.coginvasion.phys.WorldCollider import WorldCollider
from src.coginvasion.globals import CIGlobals

class WholeCreamPieProjectileAI(LobProjectileAI):

    def doInitCollider(self):

        WorldCollider.__init__(self, "wholeCreamPieCollider", 1.0, needSelfInArgs = True,
                          useSweep = True, resultInArgs = True, startNow = False, mask = CIGlobals.WorldGroup | CIGlobals.CharacterGroup)
        self.world = self.air.getPhysicsWorld(self.zoneId)
