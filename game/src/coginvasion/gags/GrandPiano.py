"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file GrandPiano.py
@author Maverick Liberty
@date July 16, 2015

"""

from src.coginvasion.gags.DropGag import DropGag
from src.coginvasion.gags import GagGlobals
from src.coginvasion.globals import CIGlobals
from direct.interval.IntervalGlobal import Sequence, LerpPosInterval, LerpScaleInterval, Func, Wait, Parallel
from direct.showutil import Effects
from panda3d.core import OmniBoundingVolume, Point3, CollisionSphere, CollisionNode, BitMask32, CollisionHandlerEvent

class GrandPiano(DropGag):

    def __init__(self):
        DropGag.__init__(self, CIGlobals.GrandPiano, 'phase_5/models/props/piano-mod.bam', 'phase_5/models/props/piano-chan.bam',
                         170, GagGlobals.PIANO_DROP_SFX, GagGlobals.PIANO_MISS_SFX, 1, 1)
        self.setImage('phase_3.5/maps/grand-piano.png')
        self.colliderRadius = 5
        self.colliderOfs = Point3(0, 1.5, 0)

    def startDrop(self):
        if self.gag and self.getLocation():
            endPos = self.getLocation()
            startPos = Point3(endPos.getX(), endPos.getY(), endPos.getZ() + 20)
            self.gag.setPos(startPos.getX(), startPos.getY() + 2, startPos.getZ())
            self.dropMdl.setScale(5)
            self.gag.setP(90)
            self.gag.headsUp(self.avatar)
            self.gag.setH(self.gag.getH() - 180)
            self.gag.node().setBounds(OmniBoundingVolume())
            self.gag.node().setFinal(1)
            self.buildCollisions()
            objectTrack = Sequence()
            animProp = LerpPosInterval(self.gag, self.fallDuration, endPos, startPos = startPos)
            bounceProp = Effects.createZBounce(self.gag, 2, endPos, 0.5, 1.5)
            objAnimShrink = Sequence(Func(self.gag.setP, 90), Wait(0.5), Func(self.gag.reparentTo, render), animProp, bounceProp)
            objectTrack.append(objAnimShrink)
            dropShadow = CIGlobals.makeDropShadow(1.0)
            dropShadow.reparentTo(hidden)
            dropShadow.setPos(endPos)
            shadowTrack = Sequence(Func(dropShadow.reparentTo, render), LerpScaleInterval(dropShadow, self.fallDuration + 0.1, (2, 2, 2),
                                startScale=Point3(0.01, 0.01, 0.01)), Wait(0.8), Func(dropShadow.removeNode))
            Parallel(Sequence(Wait(self.fallDuration), Func(self.completeDrop), Wait(4), Func(self.cleanupGag)), objectTrack, shadowTrack).start()
            self.dropLoc = None
