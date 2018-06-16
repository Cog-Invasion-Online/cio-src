"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file BigWeight.py
@author Maverick Liberty
@date August 30, 2015

"""

from src.coginvasion.gags.DropGag import DropGag
from src.coginvasion.gags import GagGlobals
from src.coginvasion.globals import CIGlobals
from direct.interval.IntervalGlobal import Sequence, LerpPosInterval, LerpScaleInterval, Func, Wait, Parallel
from direct.showutil import Effects
from panda3d.core import OmniBoundingVolume, Point3, CollisionSphere, CollisionNode, CollisionHandlerEvent, BitMask32

class BigWeight(DropGag):

    def __init__(self):
        DropGag.__init__(self, GagGlobals.BigWeight, 'phase_5/models/props/weight-mod.bam', 'phase_5/models/props/weight-chan.bam',
                         45, GagGlobals.WEIGHT_DROP_SFX, GagGlobals.WEIGHT_MISS_SFX, 1, 1)
        self.setImage('phase_3.5/maps/big-weight.png')
        self.colliderRadius = 2

    def startDrop(self):
        if self.gag and self.dropLoc:
            endPos = self.dropLoc
            startPos = Point3(endPos.getX(), endPos.getY(), endPos.getZ() + 20)
            self.gag.setPos(startPos.getX(), startPos.getY() + 2, startPos.getZ())
            self.dropMdl.setScale(self.dropMdl.getScale() * 0.75)
            self.gag.node().setBounds(OmniBoundingVolume())
            self.gag.node().setFinal(1)
            self.gag.headsUp(self.avatar)
            self.buildCollisions()
            objectTrack = Sequence()
            animProp = LerpPosInterval(self.gag, self.fallDuration, endPos, startPos = startPos)
            bounceProp = Effects.createZBounce(self.gag, 2, endPos, 0.5, 1.5)
            objAnimShrink = Sequence(Wait(0.5), Func(self.gag.reparentTo, render), animProp, bounceProp)
            objectTrack.append(objAnimShrink)
            dropShadow = CIGlobals.makeDropShadow(1.0)
            dropShadow.reparentTo(hidden)
            dropShadow.setPos(endPos)
            shadowTrack = Sequence(Func(dropShadow.reparentTo, render), LerpScaleInterval(dropShadow, self.fallDuration + 0.1, (1, 1, 1),
                                startScale=Point3(0.01, 0.01, 0.01)), Wait(0.8), Func(dropShadow.removeNode))
            Parallel(Sequence(Wait(self.fallDuration), Func(self.completeDrop), Wait(4), Func(self.cleanupGag)), objectTrack, shadowTrack).start()
            self.dropLoc = None
