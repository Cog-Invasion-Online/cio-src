from src.coginvasion.attack.LobProjectileAI import LobProjectileAI
from src.coginvasion.phys.WorldColliderAI import WorldColliderAI
from src.coginvasion.globals import CIGlobals

class WholeCreamPieProjectileAI(LobProjectileAI):

    def doInitCollider(self):

        WorldColliderAI.__init__(self, "wholeCreamPieCollider", 1.0, needSelfInArgs = True,
                          useSweep = True, resultInArgs = True, startNow = False, mask = CIGlobals.WorldGroup | CIGlobals.CharacterGroup)
        self.world = self.air.getPhysicsWorld(self.zoneId)
