"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file ToonEffects.py
@author Maverick Liberty
@date March 3, 2018
@desc Global files for special interval effects on Toons

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Sequence, Func, LerpColorScaleInterval

from panda3d.core import VBase4
import itertools

notify = directNotify.newCategory('ToonEffects')
DEFAULT_COLOR = VBase4(1.0, 1.0, 1.0, 1.0)
TOON_FROZEN_COLOR = VBase4(0.5, 0.5, 1.0, 1.0)
ICE_CUBE_LOOSE_COLOR = VBase4(0.76, 0.76, 1.0, 0.0)
ICE_CUBE_SOLID_COLOR = VBase4(0.76, 0.76, 1.0, 1.0) 
ICE_CUBE_FORM_SFX = base.loadSfx('phase_4/audio/sfx/ice_cube_form.ogg')
ICE_CUBE_THAW_SFX = base.loadSfx('phase_4/audio/sfx/ice_cube_break.ogg')

def generateIceCube(avatar):
    """ Generates an ice cube model for special effects and reparents it to the specified toon """
    
    if avatar is None or avatar.isEmpty():
        notify.warning('Received a None or empty avatar reference!')
        return None
    
    iceCube = loader.loadModel('phase_8/models/props/icecube.bam')
    
    for node in itertools.chain(iceCube.findAllMatches('**/billboard*'), \
                                iceCube.findAllMatches('**/drop_shadow*'), \
                                iceCube.findAllMatches('**/prop_mailboxcollisions*')):
        node.removeNode()
    
    iceCube.reparentTo(avatar)
    iceCube.setScale(1.2, 1.0, avatar.getHeight() / 1.7)
    iceCube.setTransparency(1)
    iceCube.setColorScale(ICE_CUBE_LOOSE_COLOR)
    return iceCube

def getToonFreezeInterval(avatar, duration = 0.5, colorScale = TOON_FROZEN_COLOR, blendType = 'easeOut'):
    """ Creates a frozen animation on the specified toon with the specified modifiers """
    
    if avatar is None or avatar.isEmpty():
        notify.warning('Received a None or empty avatar reference!')
        return None
    
    return LerpColorScaleInterval(
        avatar.getGeomNode(),
        duration = duration,
        colorScale = colorScale,
        startColorScale = avatar.getGeomNode().getColorScale(),
        blendType = blendType
    )

def getToonThawInterval(avatar, duration = 0.5, blendType = 'easeOut'):
    """ Creates a thaw animation on the specified toon with the specified modifiers """

    if avatar is None or avatar.isEmpty():
        notify.warning('Received a None or empty avatar reference!')
        return None
    
    return LerpColorScaleInterval(
        avatar.getGeomNode(),
        duration = duration,
        colorScale = DEFAULT_COLOR,
        startColorScale = avatar.getGeomNode().getColorScale(),
        blendType = blendType
    )
    
def getIceCubeFormInterval(iceCube, duration = 0.5, blendType = 'easeInOut'):
    """ Creates the ice cube formation animation on the specified ice cube """
    
    if iceCube is None or iceCube.isEmpty():
        notify.warning('Received a None or empty iceCube reference!')
        return None

    return Sequence(
        Func(base.playSfx, ICE_CUBE_FORM_SFX, node=iceCube),
        LerpColorScaleInterval(
            iceCube,
            duration = duration,
            colorScale = ICE_CUBE_SOLID_COLOR,
            startColorScale = iceCube.getColorScale(),
            blendType = blendType
        )
    )

def getIceCubeThawInterval(iceCube, duration, blendType = 'easeInOut'):
    """ Creates the ice cube formation animation on the specified ice cube """
    
    if iceCube is None or iceCube.isEmpty():
        notify.warning('Received a None or empty iceCube reference!')
        return None
    
    return Sequence(
        Func(base.playSfx, ICE_CUBE_THAW_SFX, node=iceCube),
        LerpColorScaleInterval(
            iceCube,
            duration = duration,
            colorScale = ICE_CUBE_LOOSE_COLOR,
            startColorScale = iceCube.getColorScale(),
            blendType = blendType
        )
    )
