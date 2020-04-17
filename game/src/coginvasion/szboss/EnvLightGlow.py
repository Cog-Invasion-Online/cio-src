from Entity import Entity

from panda3d.core import ColorBlendAttrib

from src.coginvasion.globals import CIGlobals

class EnvLightGlow(Entity):
    
    
    def __init__(self):
        Entity.__init__(self)
        self.setLightOff(1)
        
        self.lightGlow = None
        
    def load(self):
        Entity.load(self)
        
        entnum = self.cEntity.getBspEntnum()
        loader = base.bspLoader
        
        lightColor = self.getEntityValueColor("_light")
        width = self.getEntityValueFloat("width")
        height = self.getEntityValueFloat("height")
        self.lightGlow = CIGlobals.makeLightGlow((width, 1, height))
        self.lightGlow.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd, ColorBlendAttrib.OOne, ColorBlendAttrib.OOne), 1)
        self.lightGlow.reparentTo(self)
        self.lightGlow.setTwoSided(True)
        self.lightGlow.setColorScale(lightColor, 1)
        
        self.reparentTo(render)
        self.setPos(self.cEntity.getOrigin())
        
    def unload(self):
        self.lightGlow.removeNode()
        self.lightGlow = None
        Entity.unload(self)
        
