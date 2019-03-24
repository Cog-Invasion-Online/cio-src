from panda3d.core import Point3

from src.coginvasion.attack.LinearProjectile import LinearProjectile

class ClipOnTieProjectile(LinearProjectile):
    ModelPath = "phase_5/models/props/power-tie.bam"
    ModelScale = 4
    ImpactSoundPath = "phase_5/audio/sfx/SA_powertie_impact.ogg"
    ThrowSoundPath = "phase_5/audio/sfx/SA_powertie_throw.ogg"

    def __init__(self, cr):
        LinearProjectile.__init__(self, cr)
        self.throwSound = None

    def disable(self):
        if self.throwSound:
            base.audio3d.detachSound(self.throwSound)
        self.throwSound = None
        LinearProjectile.disable(self)

    def announceGenerate(self):
        LinearProjectile.announceGenerate(self)

        if not self.throwSound:
            self.throwSound = base.loadSfxOnNode(self.ThrowSoundPath, self)
        self.throwSound.play()

        vecEnd = Point3(*self.linearStart)
        vecStart = Point3(*self.linearEnd)
        throwDir = (vecEnd - vecStart).normalized()
        self.model.reparentTo(render)
        self.model.setPos(0, 0, 0)
        self.model.headsUp(throwDir)
        rot = self.model.getHpr(render)
        self.model.reparentTo(self)
        self.model.setHpr(rot[0], 0, 0)

    def impact(self, pos):
        base.audio3d.attachSoundToObject(self.impactSound, self)
        self.impactSound.play()
