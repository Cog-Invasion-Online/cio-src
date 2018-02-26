"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file GagUtils.py
@author Maverick Liberty
@date August 30, 2015

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
