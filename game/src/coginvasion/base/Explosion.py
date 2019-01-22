
from panda3d.core import NodePath

from src.coginvasion.toon import ParticleLoader

class Explosion(NodePath):

    def __init__(self, loc = (0, 0, 0), parent = None):
        NodePath.__init__(self, 'explosion')

        if parent is None:
            parent = render

        self.reparentTo(parent)
        self.setPos(loc)

        self.poof = ParticleLoader.loadParticleEffect('resources/phase_14/etc/explosion_poof.ptf')
        self.poof.start(self)

        self.lines = ParticleLoader.loadParticleEffect('resources/phase_14/etc/explosion_sparks.ptf')
        self.lines.start(self)

        self.smoke = ParticleLoader.loadParticleEffect('resources/phase_14/etc/explosion_smoke.ptf')
        self.smoke.start(self)

        taskMgr.doMethodLater(4.0, self.__cleanupTask, "Explosion_cleanupTask")

    @staticmethod
    def emit(*args, **kwargs):
        return Explosion(*args, **kwargs)

    def __cleanupTask(self, task):
        self.poof.softStop()
        self.lines.softStop()
        self.smoke.softStop()
        self.poof = None
        self.lines = None
        self.smoke = None
        self.removeNode()
        return task.done