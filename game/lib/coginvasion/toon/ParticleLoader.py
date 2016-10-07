"""
  
  Filename: ParticleLoader.py
  Created by: blach (09July14)
  
"""

from direct.particles.Particles import Particles
from direct.particles.ParticleEffect import ParticleEffect
from pandac.PandaModules import Filename

def loadParticleEffect(file):
	p = ParticleEffect()
	p.loadConfig(Filename(file))
	return p
