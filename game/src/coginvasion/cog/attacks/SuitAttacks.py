"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file SuitAttacks.py
@author Brian Lach
@date April 01, 2019

"""

ParticlesMdl = None
def getSuitParticle(name):
    global ParticlesMdl

    if not ParticlesMdl:
        ParticlesMdl = loader.loadModel("phase_3.5/models/props/suit-particles.bam")
    return ParticlesMdl.find("**/" + name)
