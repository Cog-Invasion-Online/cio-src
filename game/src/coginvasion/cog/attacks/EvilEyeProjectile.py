from panda3d.core import Point3

from src.coginvasion.attack.LinearProjectile import LinearProjectile
from src.coginvasion.cog.attacks.EvilEyeShared import EyeScale

class EvilEyeProjectile(LinearProjectile):
    ModelPath = "phase_5/models/props/evil-eye.bam"
    ModelScale = EyeScale
    
    def announceGenerate(self):
        LinearProjectile.announceGenerate(self)
        
        vecEnd = Point3(*self.linearStart)
        vecStart = Point3(*self.linearEnd)
        throwDir = (vecEnd - vecStart).normalized()
        self.model.reparentTo(render)
        self.model.setPos(0, 0, 0)
        self.model.headsUp(throwDir)
        
        rot = self.model.getHpr(render)
        self.model.reparentTo(self)
        self.model.setHpr(rot[0], 0, 0)
        self.model.setLightOff()
