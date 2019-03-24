from panda3d.core import Point3, VBase4

from src.coginvasion.attack.LobProjectile import LobProjectile
from src.coginvasion.globals import CIGlobals

class WholeCreamPieProjectile(LobProjectile):
    ModelPath = "phase_14/models/props/creampie.bam"
    ModelScale = 0.85
    ImpactSoundPath = "phase_4/audio/sfx/AA_wholepie_only.ogg"

    SplatColor = VBase4(250.0 / 255.0, 241.0 / 255.0, 24.0 / 255.0, 1.0)
    SplatScale = 0.5

    def announceGenerate(self):
        LobProjectile.announceGenerate(self)

        vecEnd = Point3(*self.projEnd) + (0, 0, 90)
        vecStart = Point3(*self.projStart)
        throwDir = (vecEnd - vecStart).normalized()
        self.model.reparentTo(render)
        self.model.setPos(0, 0, 0)
        self.model.headsUp(throwDir)
        rot = self.model.getHpr(render)
        self.model.reparentTo(self)
        self.model.setHpr(rot[0], -90, 0)

    def impact(self, pos):
        CIGlobals.makeSplat(pos, self.SplatColor, self.SplatScale, self.impactSound)