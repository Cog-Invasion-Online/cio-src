"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file AnisotropicFiltering.py
@author Brian Lach
@date March 13, 2017

"""

from src.coginvasion.globals import CIGlobals

def __applyAF(task):
    af = CIGlobals.getSettingsMgr().getSetting("af")
    for tex in render.findAllTextures():
        if tex.getAnisotropicDegree() != af:
            tex.setAnisotropicDegree(af)
    return task.cont

def startApplying():
    """ Begin applying anisotropic filtering to all textures. """
    taskMgr.add(__applyAF, "applyAF")

def stopApplying():
    taskMgr.remove("applyAF")