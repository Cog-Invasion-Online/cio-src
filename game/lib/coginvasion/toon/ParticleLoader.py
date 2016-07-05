"""
  
  Filename: ParticleLoader.py
  Created by: blach (09July14)
  
"""

from direct.particles.Particles import Particles
from direct.particles.ParticleEffect import ParticleEffect
from panda3d.core import *

def loadParticleEffect(file):
	p = ParticleEffect()
	p.loadConfig(Filename(file))
	return p
