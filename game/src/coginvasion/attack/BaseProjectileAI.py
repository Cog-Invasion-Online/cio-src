from direct.distributed.DistributedSmoothNodeAI import DistributedSmoothNodeAI

from src.coginvasion.phys.WorldCollider import WorldCollider
from src.coginvasion.globals import CIGlobals
from src.coginvasion.attack.BaseProjectileShared import BaseProjectileShared

class BaseProjectileAI(DistributedSmoothNodeAI, BaseProjectileShared, WorldCollider):

    WantNPInit = False

    def __init__(self, air):
        DistributedSmoothNodeAI.__init__(self, air)
        BaseProjectileShared.__init__(self)
        # Defer initialization of WorldCollider, so each projectile
        # can have a unique WorldCollider setup.

    def d_impact(self, pos):
        pos = [pos[0], pos[1], pos[2]]
        self.sendUpdate('impact', [pos])

    def doInitCollider(self):
        WorldCollider.__init__(self, "none", 1.0, needSelfInArgs = True, resultInArgs = True,
                          useSweep = True, startNow = False, initNp = False, mask = CIGlobals.WorldGroup | CIGlobals.CharacterGroup)
        self.world = self.air.getPhysicsWorld(self.zoneId)

    def announceGenerate(self):
        pos = self.getPos(render)
        self.doInitCollider()
        self.reparentTo(render)
        self.setPos(pos)
        DistributedSmoothNodeAI.announceGenerate(self)
        self.stopPosHprBroadcast()
        self.start()
        self.onSpawn()

    def delete(self):
        BaseProjectileShared.cleanup(self)
        self.stop()
        DistributedSmoothNodeAI.delete(self)
