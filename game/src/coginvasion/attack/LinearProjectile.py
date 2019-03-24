from src.coginvasion.attack.BaseProjectile import BaseProjectile
from src.coginvasion.attack.LinearProjectileShared import LinearProjectileShared

class LinearProjectile(BaseProjectile, LinearProjectileShared):

    def __init__(self, cr):
        BaseProjectile.__init__(self, cr)
        LinearProjectileShared.__init__(self)

    def onSpawn(self):
        self.playLinear()

    def disable(self):
        LinearProjectileShared.cleanup(self)
        BaseProjectile.disable(self)
