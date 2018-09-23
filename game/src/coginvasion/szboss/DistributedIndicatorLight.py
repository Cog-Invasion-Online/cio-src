from DistributedEntity import DistributedEntity

class DistributedIndicatorLight(DistributedEntity):

    def __init__(self, cr):
        DistributedEntity.__init__(self, cr)
        self.lightMdl = None
        self.lightGlow = None
        self.soundFile = None
        self.lightColor = (1, 1, 0.75, 1.0)
        
        self.lightState = 0
        
    def setLightState(self, state):
        if self.lightState != state:
            self.sound.play()
            
        self.lightState = state
        if state == 0:
            # off
            self.lightGlow.hide()
            self.lightMdl.find("**/__lightsrc__").setColorScale(0.75, 0.75, 0.75, 0.5, 1)
        elif state == 1:
            # on
            self.lightGlow.show()
            self.setLightColor(self.lightColor[0], self.lightColor[1], self.lightColor[2])
            
        #self.ls()
        
    def setLightColor(self, r, g, b):
        self.lightColor = (r, g, b, 1.0)
        if self.lightState == 1:
            self.lightMdl.find("**/__lightsrc__").setColorScale(self.lightColor, 1)
            self.lightGlow.setColorScale(self.lightColor, 1)
            
    
        
    def load(self):
        DistributedEntity.load(self)
        
        self.sound = base.loadSfxOnNode(base.bspLoader.getEntityValue(self.entnum, "changeSound"), self)
        self.lightMdl = loader.loadModel("phase_14/models/props/indicator_light.bam")
        self.lightMdl.find("**/__lightsrc__").setTransparency(1)
        self.lightMdl.reparentTo(self)
        self.lightMdl.setBin("fixed", 0)
        self.lightGlow = loader.loadModel("phase_14/models/props/light_glow.bam")
        self.lightGlow.reparentTo(self)
        self.lightGlow.setTwoSided(True)
        self.lightGlow.setDepthOffset(2)
        self.lightGlow.setY(1.5)
        self.lightGlow.setScale(1.5)
        #self.lightGlow.setBillboardPointEye()
        #self.lightGlow.setScale()
        
        self.reparentTo(render)
        self.setPos(self.cEntity.getOrigin())
        self.setHpr(self.cEntity.getAngles())
        