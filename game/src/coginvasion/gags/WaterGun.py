"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file WaterGun.py
@author Brian Lach
@date November 15, 2015

"""

from panda3d.core import Point3, VBase3

from direct.interval.IntervalGlobal import Sequence, Parallel, Wait, Func, ActorInterval

from SquirtGag import SquirtGag
import GagGlobals

import random

class WaterGun(SquirtGag):

    InspectIval = [10, 25]

    def __init__(self):
        SquirtGag.__init__(self, GagGlobals.WaterGun, "phase_4/models/props/water-gun.bam", GagGlobals.WATERGUN_SFX)
        self.anim = 'squirt'
        self.sprayJoint = 'joint_nozzle'
        self.dmgIval = 0.4
        self.scale = 1.0
        self.shootSfx = None
        self.timeout = 3.0
        self.inspectTask = None

    def doInspect(self, task):
        task.delayTime = random.uniform(*self.InspectIval)

        cam = self.getFPSCam()
        if cam.vmAnimTrack and cam.vmAnimTrack.isPlaying():
            return task.again

        vm = self.getViewModel()
        cam.setVMAnimTrack(Sequence(ActorInterval(vm, "sg_inspect"), Func(vm.loop, "sg_idle")))

        return task.again

    def equip(self):
        SquirtGag.equip(self)

        if self.isLocal():
            vm = self.getViewModel()
            fpsCam = self.getFPSCam()
            vmGag = self.getVMGag()
            vmGag.setPosHprScale(0.07, 0.17, -0.01,
                                 -90, 0, 0,
                                 0.685, 0.685, 0.685)
            fpsCam.setVMAnimTrack(Sequence(ActorInterval(vm, "sg_draw"), Func(vm.loop, "sg_idle")))
            taskMgr.doMethodLater(random.uniform(*self.InspectIval), self.doInspect, "sg_inspectTask")

        self.gag.setPos(Point3(0.28, -0.09, 0.08))
        self.gag.setHpr(VBase3(73.00, 9.27, 94.43))

        self.doDrawAndHold('squirt', 0, 48, 1.0, 48, 48)

    def unEquip(self):
        if self.isLocal():
            taskMgr.remove("sg_inspectTask")
        SquirtGag.unEquip(self)

    def start(self):
        SquirtGag.start(self)

        if self.isLocal():
            vm = self.getViewModel()
            fpsCam = self.getFPSCam()
            fpsCam.setVMAnimTrack(Sequence(ActorInterval(vm, "sg_shoot_begin"), Func(vm.loop, "sg_shoot_loop")))

    def throw(self):
        SquirtGag.throw(self)
            
        if self.isLocal():
            vm = self.getViewModel()
            fpsCam = self.getFPSCam()
            fpsCam.setVMAnimTrack(Sequence(ActorInterval(vm, "sg_shoot_end"), Func(vm.loop, "sg_idle")))
