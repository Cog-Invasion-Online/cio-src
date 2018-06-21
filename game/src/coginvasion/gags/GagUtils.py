"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file GagUtils.py
@author Maverick Liberty
@date August 30, 2015

"""

from direct.actor.Actor import Actor

from src.coginvasion.base.CIParticleEffect import CIParticleEffect

def loadParticle(phase, name):
    particle = CIParticleEffect()
    particle.loadConfig('phase_%s/etc/%s.ptf' % (str(phase), name))
    return particle

def destroyProp(prop):
    if isinstance(prop, Actor):
        prop.cleanup()
    prop.removeNode()
