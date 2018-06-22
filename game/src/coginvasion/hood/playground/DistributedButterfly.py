"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedButterfly.py
@author Brian Lach
@date December 28, 2017

"""

from panda3d.core import Point3

from direct.actor.Actor import Actor
from direct.distributed.DistributedNode import DistributedNode
from direct.distributed.ClockDelta import globalClockDelta
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.fsm.ClassicFSM import ClassicFSM
from direct.fsm.State import State
from direct.interval.IntervalGlobal import LerpPosInterval, LerpColorScaleInterval, Sequence, Parallel, Wait, Func

import ButterflyGlobals
import random

class DistributedButterfly(DistributedNode):
    notify = directNotify.newCategory('DistributedButterfly')

    def __init__(self, cr):
        DistributedNode.__init__(self, cr)
        self.wingType = None
        self.hood = None
        self.butterfly = None
        self.shadow = None
        self.flyTrack = None
        self.fsm = ClassicFSM('DBF', [State('off', self.enterOff, self.exitOff),
                                      State('sit', self.enterSit, self.exitSit),
                                      State('fly', self.enterFly, self.exitFly)],
                              'off', 'off')
        self.fsm.enterInitialState()

    def setWingType(self, wingType):
        self.wingType = wingType

    def setHood(self, hood):
        self.hood = hood

    def setState(self, state, fromLoc, toLoc, timestamp = None):
        if timestamp is not None:
            ts = globalClockDelta.localElapsedTime(timestamp)
        else:
            ts = 0.0

        self.fsm.request(ButterflyGlobals.StateIdx2State[state], [fromLoc, toLoc, ts])


    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterSit(self, fromLoc, toLoc, ts = 0.0):
        self.butterfly.loop('land')
        spot = ButterflyGlobals.Spots[self.hood][toLoc]
        self.setPos(spot)
        self.shadow.setColorScale(0, 0, 0, 1)
        self.shadow.show()

    def exitSit(self):
        self.butterfly.stop()

    def enterFly(self, fromLoc, toLoc, ts = 0.0):
        endLoc = ButterflyGlobals.Spots[self.hood][toLoc]
        startLoc = ButterflyGlobals.Spots[self.hood][fromLoc]
        distance = (endLoc - startLoc).length()
        time = distance / ButterflyGlobals.Speed

        mp = Point3((endLoc.getX() + startLoc.getX()) / 2.0,
                    (endLoc.getY() + startLoc.getY()) / 2.0,
                    (endLoc.getZ() + startLoc.getZ()) / 2.0)
        mp.setZ(mp.getZ() + random.uniform(10.0, 20.0))

        self.setPos(startLoc)
        self.headsUp(endLoc)
        self.setH(self.getH() - 180)

        self.flyTrack = Parallel(
            LerpColorScaleInterval(self.shadow, 1.0, (0, 0, 0, 0), (0, 0, 0, 1)),
            Sequence(LerpPosInterval(self, time / 2.0, mp, startLoc, blendType = 'easeIn'),
                     LerpPosInterval(self, time / 2.0, endLoc, mp, blendType = 'easeOut')),
            Sequence(Func(self.butterfly.loop, 'flutter'),
                     Wait(time - (time / 4.0)),
                     Func(self.butterfly.loop, 'glide'),
                     Wait(time / 4.0),
                     Func(self.butterfly.loop, 'land'))
        )
        self.flyTrack.start(ts)

    def exitFly(self):
        self.stopFlyTrack()

    def stopFlyTrack(self):
        if self.flyTrack:
            self.flyTrack.finish()
        self.flyTrack = None

    def generate(self):
        self.butterfly = Actor('phase_4/models/props/SZ_butterfly-mod.bam', {'flutter': 'phase_4/models/props/SZ_butterfly-flutter.bam',
                                                                             'glide': 'phase_4/models/props/SZ_butterfly-glide.bam',
                                                                             'land': 'phase_4/models/props/SZ_butterfly-land.bam'})
        self.butterfly.reparentTo(self)
        self.shadow = loader.loadModel("phase_3/models/props/drop_shadow.bam")
        self.shadow.setBillboardAxis(2)
        self.shadow.setColor(0, 0, 0, 0.5, 1)
        self.shadow.setScale(0.08)
        self.shadow.reparentTo(self)
        DistributedNode.generate(self)

    def announceGenerate(self):
        DistributedNode.announceGenerate(self)

        for wingType in range(1, 7):
            if wingType != self.wingType:
                self.butterfly.find("**/wings_" + str(wingType)).removeNode()

        self.reparentTo(render)

    def disable(self):
        self.fsm.requestFinalState()
        self.stopFlyTrack()
        if self.shadow:
            self.shadow.removeNode()
        self.shadow = None
        if self.butterfly:
            self.butterfly.cleanup()
            self.butterfly.removeNode()
        self.butterfly = None
        self.hood = None
        self.wingType = None
        self.fsm = None
        DistributedNode.disable(self)