"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file GagEffects.py
@author Brian Lach
@date June 18, 2018

"""

from direct.interval.IntervalGlobal import Sequence, Wait, Func, Parallel, LerpColorScaleInterval

from src.coginvasion.globals import CIGlobals

GENone = 0
GEAsh = 1
GEPie = 2
GEWater = 4
GESound = 8

def __makeAshEffect(suit):
    return Sequence(Func(suit.setColorScale, 0.3, 0.3, 0.3, 1.0), Wait(1.0), LerpColorScaleInterval(suit, 1.0, (1, 1, 1, 1), (0.3, 0.3, 0.3, 1.0), blendType = 'easeInOut'))

Effects = {GEAsh: __makeAshEffect}

def doGagEffect(suit, flags):
    if not CIGlobals.isNodePathOk(suit):
        return

    effect = Parallel()
    for id in Effects.keys():
        if (flags & id) != 0:
            print "Doing effect", id
            effect.append(Effects[id](suit))
    effect.start()
