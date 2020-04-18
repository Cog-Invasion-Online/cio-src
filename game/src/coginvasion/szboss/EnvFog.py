from panda3d.core import Fog

from src.coginvasion.globals import CIGlobals
from DistributedEntity import DistributedEntity

class EnvFog(DistributedEntity):

    FadeInDuration = 0.5
    FadeOutDuration = 0.5
    
    NeedNode = False

    def __init__(self, cr):
        DistributedEntity.__init__(self, cr)
        self.fogNode = None
        self.fogDensity = 0.0

    def load(self):
        DistributedEntity.load(self)

        density = self.getEntityValueFloat("fogdensity")
        self.fogDensity = density
        color = self.getEntityValueColor("fogcolor")
        self.fogNode = Fog('env_fog')
        self.fogNode.setExpDensity(density)
        self.fogNode.setColor(color)
        
        base.shaderGenerator.setFog(self.fogNode)

    def think(self):
        elapsed = self.getEntityStateElapsed()
        state = self.getEntityState()

        if state == 1:
            if elapsed < self.FadeInDuration:
                self.fogNode.setExpDensity(CIGlobals.lerp2(0.0, self.fogDensity, elapsed / self.FadeInDuration))
            else:
                self.fogNode.setExpDensity(self.fogDensity)

        elif state == 0:
            if elapsed < self.FadeOutDuration:
                self.fogNode.setExpDensity(CIGlobals.lerp2(self.fogDensity, 0.0, elapsed / self.FadeOutDuration))
            else:
                self.fogNode.setExpDensity(0.0)

    def disable(self):
        self.fogNode = None
        self.fogDensity = None

        base.shaderGenerator.clearFog()

        DistributedEntity.disable(self)
