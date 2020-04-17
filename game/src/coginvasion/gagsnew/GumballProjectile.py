from panda3d.core import VBase4, Point3

from src.coginvasion.base.Precache import precacheSound, precacheMaterial
from src.coginvasion.attack.LobProjectile import LobProjectile
from src.coginvasion.globals import CIGlobals

import random

class GumballProjectile(LobProjectile):

    ModelPath = "models/smiley.egg.pz"
    ModelScale = 0.1
    ImpactSoundPath = "phase_14/audio/sfx/gumball_pop.ogg"
    
    GumballMaterialPath = "phase_14/materials/models/gumball.mat"
    SplatMaterialPath = "phase_14/materials/pie_splat.mat"

    SplatColor = VBase4(250.0 / 255.0, 241.0 / 255.0, 24.0 / 255.0, 1.0)
    SplatScale = 0.1
    
    @classmethod
    def doPrecache(cls):
        super(GumballProjectile, cls).doPrecache()
        precacheMaterial(cls.GumballMaterialPath)
        precacheMaterial(cls.SplatMaterialPath)

    def announceGenerate(self):
        LobProjectile.announceGenerate(self)
        self.model.setBSPMaterial(self.GumballMaterialPath, 1)
        self.color = VBase4(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), 1.0)
        self.model.setColorScale(self.color, 1)
        self.model.hide(CIGlobals.ShadowCameraBitmask|CIGlobals.ReflectionCameraBitmask)

    def impact(self, pos, lastPos):
        pos = Point3(pos)
        lastPos = Point3(lastPos)
        
        CIGlobals.makeSplat(pos, self.color, self.SplatScale, self.impactSound)
        
        dir = (pos - lastPos).normalized()
        base.bspLoader.traceDecal(self.SplatMaterialPath, 1.5, random.randint(1, 360), lastPos, pos + (dir * 2), self.color)
