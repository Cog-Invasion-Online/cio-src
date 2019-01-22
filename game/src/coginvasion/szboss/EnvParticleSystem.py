from Entity import Entity

from src.coginvasion.toon import ParticleLoader

class EnvParticleSystem(Entity):

    StartsEnabled = 1
    WorldVelocities = 2

    def __init__(self):
        Entity.__init__(self)
        self.setLightOff(1)
        #self.setShaderOff(1)
        
        self.system = None
        self.spawnflags = 0
        
    def Start(self):
        if not self.system:
            return
            
        if self.spawnflags & self.WorldVelocities:
            self.system.start(self)#, render)
        else:
            self.system.start(self)
            
    def Stop(self):
        if not self.system:
            return
            
        self.system.softStop()
        
    def load(self):
        Entity.load(self)
        
        entnum = self.cEntity.getEntnum()
        loader = base.bspLoader
        
        ptfFile = loader.getEntityValue(entnum, "file")
        scale = loader.getEntityValueFloat(entnum, "scale")
        self.spawnflags = loader.getEntityValueInt(entnum, "spawnflags")
        self.system = ParticleLoader.loadParticleEffect(ptfFile)
        #self.system.setShaderOff(1)
        self.system.setLightOff(1)
        self.system.setScale(scale)
        
        self.setPos(self.cEntity.getOrigin())
        self.setHpr(self.cEntity.getAngles())
        self.reparentTo(render)
        
        if self.spawnflags & self.StartsEnabled:
            self.Start()
            
    def unload(self):
        self.Stop()
        self.system = None
        self.spawnflags = None
        Entity.unload(self)
        