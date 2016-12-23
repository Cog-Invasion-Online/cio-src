"""

  Filename: GagUtils.py
  Created by: DecodedLogic (30Aug15)

"""

from direct.particles.ParticleEffect import ParticleEffect
from direct.actor.Actor import Actor

def loadParticle(phase, name):
    particle = ParticleEffect()
    particle.loadConfig('phase_%s/etc/%s.ptf' % (str(phase), name))
    return particle

def destroyProp(prop):
    if isinstance(prop, Actor):
        prop.cleanup()
    prop.removeNode()