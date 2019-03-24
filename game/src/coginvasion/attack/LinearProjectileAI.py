from src.coginvasion.attack.BaseProjectileAI import BaseProjectileAI
from src.coginvasion.attack.LinearProjectileShared import LinearProjectileShared

class LinearProjectileAI(BaseProjectileAI, LinearProjectileShared):

    def __init__(self, air):
        BaseProjectileAI.__init__(self, air)
        LinearProjectileShared.__init__(self)

    def onSpawn(self):
        self.playLinear()

    def delete(self):
        LinearProjectileShared.cleanup(self)
        BaseProjectileAI.delete(self)
