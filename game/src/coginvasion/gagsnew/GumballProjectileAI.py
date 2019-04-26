from src.coginvasion.attack.LobProjectileAI import LobProjectileAI
from src.coginvasion.globals import CIGlobals
from src.coginvasion.phys.WorldColliderAI import WorldColliderAI

class GumballProjectileAI(LobProjectileAI):

    def doInitCollider(self):

        WorldColliderAI.__init__(self, "GumballCollider", 0.15, needSelfInArgs = True,
                          useSweep = True, resultInArgs = True, startNow = False, mask = CIGlobals.WorldGroup | CIGlobals.CharacterGroup)
        self.world = self.air.getPhysicsWorld(self.zoneId)
