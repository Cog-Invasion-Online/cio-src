from panda3d.core import VBase4

from src.coginvasion.attack.LobProjectile import LobProjectile
from src.coginvasion.globals import CIGlobals

import random

class GumballProjectile(LobProjectile):

    ModelPath = "models/smiley.egg.pz"
    ModelScale = 0.15
    ImpactSoundPath = "phase_14/audio/sfx/gumball_pop.ogg"

    SplatColor = VBase4(250.0 / 255.0, 241.0 / 255.0, 24.0 / 255.0, 1.0)
    SplatScale = 0.25

    def announceGenerate(self):
        LobProjectile.announceGenerate(self)
        self.model.setBSPMaterial("phase_14/materials/models/gumball.mat", 1)
        self.color = VBase4(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), 1.0)
        self.model.setColorScale(self.color, 1)

    def impact(self, pos):
        CIGlobals.makeSplat(pos, self.color, self.SplatScale, self.impactSound)
