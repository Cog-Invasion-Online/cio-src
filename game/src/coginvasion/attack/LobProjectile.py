from src.coginvasion.attack.BaseProjectile import BaseProjectile
from src.coginvasion.attack.LobProjectileShared import LobProjectileShared


class LobProjectile(BaseProjectile, LobProjectileShared):

    def __init__(self, cr):
        BaseProjectile.__init__(self, cr)
        LobProjectileShared.__init__(self)

    def onSpawn(self):
        self.playProjectile()

    def disable(self):
        LobProjectileShared.cleanup(self)
        BaseProjectile.disable(self)
