from Entity import Entity

class EnvLightGlow(Entity):
    
    
    def __init__(self):
        Entity.__init__(self)
        self.setLightOff(1)
        self.setShaderOff(1)
        self.setMaterialOff(1)
        
        self.lightGlow = None
        
    def load(self):
        Entity.load(self)
        
        entnum = self.cEntity.getEntnum()
        loader = base.bspLoader
        
        lightColor = loader.getEntityValueColor(entnum, "_light")
        width = loader.getEntityValueFloat(entnum, "width")
        height = loader.getEntityValueFloat(entnum, "height")
        print width, height
        self.lightGlow = base.loader.loadModel("phase_14/models/props/light_glow.bam")
        self.lightGlow.reparentTo(self)
        self.lightGlow.setTwoSided(True)
        self.lightGlow.setDepthOffset(2)
        self.lightGlow.setScale(width, 1, height)
        self.lightGlow.setColorScale(lightColor, 1)
        
        self.lightGlow.clearModelNodes()
        self.lightGlow.flattenStrong()
        
        self.reparentTo(render)
        self.setPos(self.cEntity.getOrigin())
        
    def unload(self):
        self.lightGlow.removeNode()
        self.lightGlow = None
        Entity.unload(self)
        