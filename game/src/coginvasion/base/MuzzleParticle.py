from panda3d.core import NodePath, CardMaker, ColorBlendAttrib

from src.coginvasion.base.Precache import Precacheable, precacheTexture
from src.coginvasion.globals import CIGlobals

import random

class MuzzleParticle(NodePath, Precacheable):
    
    muzzles = [1, 4]
    muzzleroot = "phase_14/hl2/muzzleflash{0}.png"
    
    @classmethod
    def doPrecache(cls):
        super(MuzzleParticle, cls).doPrecache()
        for i in range(cls.muzzles[0], cls.muzzles[1] + 1):
            precacheTexture(cls.muzzleroot.format(i))
    
    def __init__(self, startSize, endSize, roll, color, duration):
        NodePath.__init__(self, 'muzzleParticle')
        
        cm = CardMaker("muzzleSpriteCard")
        cm.setFrame(-1, 1, -1, 1)
        cm.setHasUvs(True)
        cm.setUvRange((0, 0), (1, 1))
        cmnp = self.attachNewNode(cm.generate())
        cmnp.setBillboardAxis()
        
        self.setTexture(loader.loadTexture(self.muzzleroot.format(random.randint(*self.muzzles))), 1)
        #self.setShaderOff(1)
        self.setLightOff(1)
        self.setMaterialOff(1)
        self.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd, ColorBlendAttrib.OOne, ColorBlendAttrib.OOne), 1)
        self.setDepthWrite(False, 1)
        #self.setTransparency(1)
        
        self.startAlpha = 0.5
        self.endAlpha = 0.0
        self.duration = duration
        self.startSize = startSize
        self.endSize = endSize
        self.color = color
        self.startTime = globalClock.getFrameTime()
        self.roll = roll
        taskMgr.add(self.particleUpdate, "muzzleParticleUpdate-" + str(id(self)))
        
    def removeNode(self):
        taskMgr.remove("muzzleParticleUpdate-" + str(id(self)))
        del self.startAlpha
        del self.endAlpha
        del self.duration
        del self.startSize
        del self.endSize
        del self.color
        del self.startTime
        del self.roll
        NodePath.removeNode(self)
    
    def particleUpdate(self, task):
        deltaTime = globalClock.getFrameTime() - self.startTime
        timeFraction = deltaTime / self.duration
        if timeFraction >= 1.0:
            self.removeNode()
            return task.done
            
        alpha = CIGlobals.lerp(self.endAlpha, self.startAlpha, timeFraction)
        size = CIGlobals.lerp(self.endSize, self.startSize, timeFraction)
        
        self.setScale(size)
        self.setR(self.roll)
        self.setColorScale(self.color[0], self.color[1], self.color[2], alpha, 1)
        
        return task.cont
