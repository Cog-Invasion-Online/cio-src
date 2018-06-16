"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Quicksand.py
@author Maverick Liberty
@date July 26, 2015

"""

from src.coginvasion.gags.ActivateTrapGag import ActivateTrapGag
from src.coginvasion.gags import GagGlobals
from direct.interval.IntervalGlobal import Sequence, Parallel, Wait, Func, LerpScaleInterval, LerpPosInterval, SoundInterval, ActorInterval
from panda3d.core import Point3

class Quicksand(ActivateTrapGag):
    
    def __init__(self):
        ActivateTrapGag.__init__(self, GagGlobals.Quicksand, 'phase_5/models/props/quicksand.bam', 
                                 50, GagGlobals.QUICKSAND_SFX, 2.5, activateSfx = GagGlobals.FALL_SFX)
        self.setImage('phase_3.5/maps/quicksand.png')
        
    def onActivate(self, entity, suit):
        x, y, z = entity.getPos(render)
        sinkPos01 = Point3(x, y, z - 3.1)
        sinkPos02 = Point3(x, y, z - 9.1)
        dropPos = Point3(x, y, z + 15)
        landPos = Point3(x, y, z)
        suit.d_disableMovement()
        suit.setPos(x, y, z)
        entTrack = Sequence(Wait(2.4), LerpScaleInterval(entity, 0.8, GagGlobals.PNT3NEAR0))
        suitTrack = Sequence(
            Wait(0.9),
            LerpPosInterval(suit, 0.9, sinkPos01), 
            LerpPosInterval(suit, 0.4, sinkPos02),
            Func(suit.setPos, dropPos),
            Func(suit.hide),
            Wait(1.1), 
            Func(suit.show),
            Func(suit.setPos, dropPos),
            Parallel(LerpPosInterval(suit, 0.3, landPos), Func(suit.play, 'slip-forward')), 
            Func(self.damageSuit, suit),
            Func(suit.d_enableMovement) 
        )
        animTrack = Sequence(ActorInterval(suit, 'flail'), ActorInterval(suit, 'flail', startTime=1.1), Wait(0.7), ActorInterval(suit, 'slip-forward', duration=2.1))
        soundTrack = Sequence(Wait(0.7), SoundInterval(self.hitSfx, node = suit), Wait(0.1), SoundInterval(self.activateSfx, node = suit))
        Parallel(entTrack, suitTrack, animTrack, soundTrack).start()
        ActivateTrapGag.onActivate(self, entity, suit)
