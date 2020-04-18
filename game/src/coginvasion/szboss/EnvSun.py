from src.coginvasion.szboss.Entity import Entity

from panda3d.core import CardMaker, ColorBlendAttrib, OmniBoundingVolume
from libpandabsp import GlowNode, BSPFaceAttrib

class EnvSun(Entity):
    
    NeedNode = False
    
    def __init__(self):
        Entity.__init__(self)
        self.pivotNode = None
        self.sunSprite = None
        
    def load(self):
        Entity.load(self)
        
        scale = self.getEntityValueFloat("spriteScale")
        color = self.getEntityValueColor("spriteColor")
        
        sunVec = base.shaderGenerator.getSunVector()
        self.pivotNode = camera.attachNewNode('env_sun-pivot')
        self.pivotNode.lookAt(sunVec)
        self.pivotNode.setCompass()
        
        cm = CardMaker('sun_sprite')
        cm.setFrame(-0.5, 0.5, -0.5, 0.5)
        self.sunSprite = self.pivotNode.attachNewNode(GlowNode(cm.generate(), 32.0 * scale))
        self.sunSprite.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd, ColorBlendAttrib.OOne, ColorBlendAttrib.OOne), 1)
        self.sunSprite.setBSPMaterial("phase_14/materials/sun/sunsprite.mat", 1)
        self.sunSprite.setFogOff(10)
        self.sunSprite.setBillboardPointEye()
        self.sunSprite.setDepthTest(False)
        self.sunSprite.setDepthWrite(False)
        self.sunSprite.setScale(scale * 100)
        self.sunSprite.setColorScale(color, 1)
        self.sunSprite.setY(1000)
        self.sunSprite.node().setBounds(OmniBoundingVolume())
        self.sunSprite.node().setFinal(True)
        
    def unload(self):
        if self.sunSprite:
            self.sunSprite.removeNode()
        self.sunSprite = None
        
        if self.pivotNode:
            self.pivotNode.removeNode()
        self.pivotNode = None
        
        Entity.unload(self)
