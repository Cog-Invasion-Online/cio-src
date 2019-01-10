"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file WaterGlass.py
@author Brian Lach
@date November 14, 2015

"""

from panda3d.core import Point3

from direct.interval.IntervalGlobal import Sequence, Wait, Func

from SquirtGag import SquirtGag
import GagGlobals

class WaterGlass(SquirtGag):
        
    name = GagGlobals.WaterGlass
    model = "phase_5/models/props/glass-mod.bam"
    hitSfxPath = GagGlobals.NULL_SFX
    sprayScale = 0.1
    scale = 3.5
    anim = 'spit'

    def __init__(self):
        SquirtGag.__init__(self)
        self.setHealth(GagGlobals.WATERGLASS_HEAL)
        self.setImage('phase_3.5/maps/water-glass.png')
        self.holdTime = 0.0
        self.spitSfx = None
        self.track = None
        self.timeout = 4.0

    def delete(self):
        if self.track:
            self.track.pause()
            self.track = None
        SquirtGag.delete(self)

    def start(self):
        SquirtGag.start(self)
        if self.isLocal():
            self.startTimeout()
        self.origin = self.getSprayStartPos()
        self.spitSfx = base.loadSfx(GagGlobals.SPIT_SFX)

        def playSpit():
            base.playSfx(self.spitSfx, node = self.avatar)

        self.track = Sequence(Wait(1.7), Func(playSpit), Wait(1.75), Func(self.release))
        self.track.start()

    def release(self):
        if self.avatar.isEmpty():
            return
        self.sprayRange = self.avatar.getPos(render) + Point3(0, GagGlobals.SELTZER_RANGE, 0)
        self.doSpray(self.sprayScale, self.holdTime, self.sprayScale, horizScale = 0.3, vertScale = 0.3)
        if self.isLocal():
            base.localAvatar.sendUpdate('usedGag', [self.id])

    def getSprayStartPos(self):
        self.sprayJoint = self.avatar.find('**/joint_head')
        if self.sprayJoint.isEmpty():
            self.sprayJoint = self.avatar.find('**/def_head')
        startNode = hidden.attachNewNode('pointInFrontOfHead')
        startNode.reparentTo(self.avatar)
        startNode.setPos(self.sprayJoint.getPos(self.avatar) + Point3(0, 0.3, -0.2))
        point = startNode.getPos(render)
        startNode.removeNode()
        del startNode
        return point
