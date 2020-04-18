from DistributedEntity import DistributedEntity

from src.coginvasion.toon import ParticleLoader
from src.coginvasion.globals import BSPUtility, CIGlobals

class EnvParticleSystem(DistributedEntity):

    WorldVelocities = 1 << 1
    
    StateDead = 0
    StateAlive = 1

    def __init__(self, cr):
        DistributedEntity.__init__(self, cr)
        self.setLightOff(1)
        self.hide(CIGlobals.ShadowCameraBitmask)
        
        self.system = None
        
    def setEntityState(self, state):
        oldState = self.getEntityState()
        DistributedEntity.setEntityState(self, state)
        
        if not self.system:
            return
            
        if state == self.StateAlive:
            self.system.clearToInitial()
            if self.hasSpawnFlags(self.WorldVelocities):
                self.system.start(self)#, render)
            else:
                self.system.start(self)
        elif state == self.StateDead and oldState == self.StateAlive:
            self.system.softStop()
        
    def load(self):
        DistributedEntity.load(self)
        
        ptfFile = self.getEntityValue("file")
        scale = self.getEntityValueFloat("scale")
        self.system = ParticleLoader.loadParticleEffect(ptfFile)
        self.system.setScale(scale)
            
    def unload(self):
        if self.system:
            self.system.softStop()
        self.system = None
        DistributedEntity.unload(self)
        
