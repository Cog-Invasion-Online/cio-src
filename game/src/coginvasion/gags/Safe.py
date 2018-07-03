"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Safe.py
@author Maverick Liberty
@date July 16, 2015

"""

from src.coginvasion.gags.DropGag import DropGag
from src.coginvasion.gags import GagGlobals
from src.coginvasion.globals import CIGlobals
from direct.interval.IntervalGlobal import Sequence, LerpPosInterval, LerpScaleInterval, Func, Wait, Parallel
from direct.showutil import Effects
from panda3d.core import OmniBoundingVolume, Point3

class Safe(DropGag):

    def __init__(self):
        DropGag.__init__(self, GagGlobals.Safe, 'phase_5/models/props/safe-mod.bam', 'phase_5/models/props/safe-chan.bam',
                         60, GagGlobals.SAFE_DROP_SFX, GagGlobals.SAFE_MISS_SFX, 1, 1)
        self.setImage('phase_3.5/maps/safe.png')
        self.colliderOfs = Point3(0, 0, 0.25)
        self.colliderRadius = 2

    def startDrop(self, entity):
        if entity and self.dropLoc:
            endPos = self.dropLoc
            dropMdl = entity.find('**/DropMdl')
            startPos = Point3(endPos.getX(), endPos.getY(), endPos.getZ() + 20)
            entity.setPos(startPos.getX(), startPos.getY() + 2, startPos.getZ())
            dropMdl.setScale(5 * 0.85)
            entity.node().setBounds(OmniBoundingVolume())
            entity.node().setFinal(1)
            entity.headsUp(self.avatar)
            self.buildCollisions(entity)
            objectTrack = Sequence()
            animProp = LerpPosInterval(entity, self.fallDuration, endPos, startPos = startPos)
            bounceProp = Effects.createZBounce(entity, 2, endPos, 0.5, 1.5)
            objAnimShrink = Sequence(Func(dropMdl.setScale, 5), Wait(0.5), Func(entity.reparentTo, render), animProp, bounceProp)
            objectTrack.append(objAnimShrink)
            dropShadow = CIGlobals.makeDropShadow(1.0)
            dropShadow.reparentTo(hidden)
            dropShadow.setPos(endPos)
            shadowTrack = Sequence(Func(dropShadow.reparentTo, render), LerpScaleInterval(dropShadow, self.fallDuration + 0.1, (1, 1, 1),
                                startScale=Point3(0.01, 0.01, 0.01)), Wait(0.8), Func(dropShadow.removeNode))
            Parallel(Sequence(Wait(self.fallDuration), Func(self.completeDrop)), objectTrack, shadowTrack).start()
            self.dropLoc = None
