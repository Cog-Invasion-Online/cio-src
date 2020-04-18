from panda3d.core import Point3, VBase4

from src.coginvasion.attack.LobProjectile import LobProjectile
from src.coginvasion.globals import CIGlobals

import random

class WholeCreamPieProjectile(LobProjectile):
    ModelPath = "phase_14/models/props/creampie.bam"
    ModelAngles = (0, -90, 0)
    ImpactSoundPath = "phase_4/audio/sfx/AA_wholepie_only.ogg"

    SplatColor = VBase4(250.0 / 255.0, 241.0 / 255.0, 232.0 / 255.0, 1.0)
    SplatScale = 0.5

    def impact(self, pos, lastPos):
        pos = Point3(pos)
        lastPos = Point3(lastPos)
        
        CIGlobals.makeSplat(pos, self.SplatColor, self.SplatScale, self.impactSound)

        dir = (pos - lastPos).normalized()
        base.bspLoader.traceDecal("phase_14/materials/pie_splat.mat", 5, random.randint(1, 360), lastPos, pos + dir)
