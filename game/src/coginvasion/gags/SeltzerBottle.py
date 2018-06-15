"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file SeltzerBottle.py
@author Maverick Liberty
@date July 10, 2015

"""

from src.coginvasion.gags.SquirtGag import SquirtGag
from src.coginvasion.gags import GagGlobals
from src.coginvasion.globals import CIGlobals
from panda3d.core import Point3

class SeltzerBottle(SquirtGag):

    def __init__(self):
        SquirtGag.__init__(self, CIGlobals.SeltzerBottle, "phase_3.5/models/props/bottle.bam", GagGlobals.SELTZER_HIT_SFX)
        self.setHealth(GagGlobals.SELTZER_HEAL)
        self.setImage('phase_3.5/maps/seltzer_bottle.png')
        self.anim = 'hold-bottle'
        self.holdTime = 2
        self.sprayScale = 0.2
        self.timeout = 3.0

    def start(self):
        super(SeltzerBottle, self).start()
        self.origin = self.getSprayStartPos()

    def release(self):
        if self.isLocal():
            self.startTimeout()
        if self.canSquirt:
            self.sprayRange = self.avatar.getPos(render) + Point3(0, GagGlobals.SELTZER_RANGE, 0)
            self.startSquirt(self.sprayScale, self.holdTime)
        else:
            self.completeSquirt()
        if self.isLocal():
            base.localAvatar.sendUpdate('usedGag', [self.id])

    def getSprayStartPos(self):
        self.sprayJoint = self.gag.find('**/joint_toSpray')
        startNode = hidden.attachNewNode('pointBehindSprayProp')
        startNode.reparentTo(self.avatar)
        startNode.setPos(self.sprayJoint.getPos(self.avatar) + Point3(0, -0.4, 0))
        point = startNode.getPos(render)
        startNode.removeNode()
        del startNode
        return point
