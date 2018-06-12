"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file LightDropGag.py
@author Maverick Liberty
@date August 13, 2015

"""

from src.coginvasion.gags.DropGag import DropGag
from src.coginvasion.globals import CIGlobals
from src.coginvasion.minigame.FlightProjectileInterval import FlightProjectileInterval
from direct.interval.IntervalGlobal import Sequence, LerpPosInterval, LerpScaleInterval, Func, Wait, Parallel
from direct.showutil import Effects
from panda3d.core import OmniBoundingVolume, Point3, CollisionSphere, CollisionNode, CollisionHandlerEvent, BitMask32

class LightDropGag(DropGag):

    def __init__(self, name, model, anim, damage, hitSfx, missSfx, rotate90 = False):
        DropGag.__init__(self, name, model, anim, damage, hitSfx, missSfx, scale = 1, playRate = 1)
        DropGag.setShadowData(self, isCircle = True, shadowScale = 0.5)
        self.stunTime = 1.5
        self.objTrack = None
        self.rotate90 = rotate90

    def startDrop(self):
        if self.gag and self.dropLoc:
            x, y, z = self.dropLoc
            startPos = Point3(x, y, z + 20)
            self.gag.setPos(startPos)
            self.gag.node().setBounds(OmniBoundingVolume())
            self.gag.node().setFinal(1)
            self.gag.headsUp(self.avatar)
            if self.rotate90:
                self.gag.setH(self.gag.getH() - 90)
            self.buildCollisions()
            objectTrack = Sequence()
            animProp = LerpPosInterval(self.gag, self.fallDuration, self.dropLoc, startPos = startPos)
            bounceProp = Effects.createZBounce(self.gag, 2, self.dropLoc, 0.5, 1.5)
            objAnimShrink = Sequence(Wait(0.5), Func(self.gag.reparentTo, render), animProp, bounceProp)
            objectTrack.append(objAnimShrink)
            dropShadow = CIGlobals.makeDropShadow(1.0)
            dropShadow.reparentTo(hidden)
            dropShadow.setPos(self.dropLoc)
            dropShadow.setScale(0.01)
            shadowTrack = Sequence(Func(dropShadow.reparentTo, render), LerpScaleInterval(dropShadow, self.fallDuration + 0.1, self.getShadowScale(),
                                startScale=Point3(0.01, 0.01, 0.01)), Wait(0.8), Func(dropShadow.removeNode))
            self.objTrack = Parallel(Sequence(Wait(self.fallDuration), Func(self.completeDrop)), objectTrack, shadowTrack)
            self.objTrack.start()
            self.dropLoc = None

    def onActivate(self, ignore, suit):
        self.objTrack.finish()
        self.objTrack = None
        if not suit.isDead():
            suit.setAnimState('drop-react')
        suit.d_disableMovement(wantRay = True)
        
        if not self.gag or self.gag.isEmpty():
            self.build()

        self.gag.setPos(suit.find('**/joint_head').getPos(render))
        if self.name == CIGlobals.FlowerPot:
            self.gag.setZ(self.gag, 3.5)
        bounce = Effects.createScaleZBounce(self.dropMdl, 1, self.dropMdl.getScale(render), 0.3, 0.75)
        dummyNode = suit.attachNewNode('fallOffNode')
        dummyNode.setX(2)
        dummyNode.setY(-2)
        flightIval = FlightProjectileInterval(
            self.gag,
            startPos = self.gag.getPos(render),
            endPos = dummyNode.getPos(render),
            duration = 0.8,
            gravityMult = .35
        )
        Sequence(
            Parallel(bounce,
                    flightIval),
            Wait(self.stunTime),
            Func(suit.d_enableMovement)
        ).start()

        dummyNode.removeNode()
        del dummyNode
