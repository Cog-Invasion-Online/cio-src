"""
  
  Filename: ParticleLoader.py
  Created by: blach (09July14)
  
"""

from panda3d.core import Filename

from src.coginvasion.base.CIParticleEffect import CIParticleEffect

def loadParticleEffect(file):
	p = CIParticleEffect()
	p.loadConfig(Filename(file))
	return p
