"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file BSPUtility.py
@author Maverick Liberty
@date January 24, 2019

@desc Utility class for various BSP methods.

"""

from panda3d.bsp import BSPMaterialAttrib, BSPMaterial

from direct.directnotify.DirectNotifyGlobal import directNotify

notify = directNotify.newCategory('BSPUtility')

def getMaterialFile(filepath):
    """ Fetches a material file using a string file path """
    return BSPMaterial.getFromFile(filepath)

def makeOverrideShader(nodepath, overrideShader):
    """ Tries to apply an override shader to the specified nodepath/geometry. """
    
    try:
        nodepath.setAttrib(BSPMaterialAttrib.makeOverrideShader(overrideShader))
    except:
        nodeName = "N/A"
        matName = "N/A"
        
        try:
            nodeName = nodepath.getName()
        except: pass
        
        try:
            matName = str(overrideShader)
        except: pass
        
        notify.warning('Failed to apply shader to {0} with Material file called: {1}'.format(nodeName, matName))
        
UNLIT_MATERIAL = getMaterialFile("phase_14/materials/unlit.mat")

def applyUnlitOverride(nodepath):
    makeOverrideShader(nodepath, UNLIT_MATERIAL)


