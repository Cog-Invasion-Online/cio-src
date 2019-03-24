from src.coginvasion.attack.BaseProjectileAI import BaseProjectileAI
from src.coginvasion.attack.LobProjectileShared import LobProjectileShared

class LobProjectileAI(BaseProjectileAI, LobProjectileShared):

    def __init__(self, air):
        LobProjectileShared.__init__(self)
        BaseProjectileAI.__init__(self, air)

    def onSpawn(self):
        self.playProjectile()

    def delete(self):
        LobProjectileShared.cleanup(self)
        BaseProjectileAI.delete(self)
