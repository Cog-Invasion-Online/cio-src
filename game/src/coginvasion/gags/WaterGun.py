"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file WaterGun.py
@author Brian Lach
@date November 15, 2015

"""

from panda3d.core import Point3, VBase3, Vec3, Quat

from direct.interval.IntervalGlobal import Sequence, Parallel, Wait, Func, ActorInterval

from src.coginvasion.phys import PhysicsUtils
from src.coginvasion.globals import CIGlobals
from src.coginvasion.gags.GagType import GagType
from Gag import Gag
from WaterPellet import WaterPellet
from src.coginvasion.gui.Crosshair import CrosshairData
import GagGlobals

import random

class WaterGun(Gag):

    InspectIval = [10, 25]
    
    gagType = GagType.SQUIRT
    name = GagGlobals.WaterGun
    model = "phase_4/models/props/water-gun.bam"
    hitSfxPath = "phase_4/audio/sfx/AA_squirt_seltzer_miss.ogg"
    dmgIval = 0.4
    
    multiUse = True
    
    pelletSpeed = 300

    def __init__(self):
        Gag.__init__(self)
        self.shootSfx = None
        self.timeout = 3.0
        self.inspectTask = None
        
        self.crosshair = CrosshairData(crosshairScale = 0.6, crosshairRot = 45)

    def doInspect(self, task):
        task.delayTime = random.uniform(*self.InspectIval)

        cam = self.getFPSCam()
        if cam.vmAnimTrack and cam.vmAnimTrack.isPlaying():
            return task.again

        vm = self.getViewModel()
        cam.setVMAnimTrack(Sequence(ActorInterval(vm, "sg_inspect"), Func(vm.loop, "sg_idle")))

        return task.again

    def equip(self):
        Gag.equip(self)

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

        self.doDrawAndHold('squirt', 0, 43, 1.0, 43, 43)

    def unEquip(self):
        if self.isLocal():
            taskMgr.remove("sg_inspectTask")
        Gag.unEquip(self)

    def start(self):
        Gag.start(self)
        
        self.hitSfx.play()
        
        gag = self.gag
        if self.isLocal():
            vm = self.getViewModel()
            fpsCam = self.getFPSCam()
            fpsCam.setVMAnimTrack(Sequence(ActorInterval(vm, "sg_shoot_begin"), ActorInterval(vm, "sg_shoot_end"), Func(vm.loop, "sg_idle")))
            gag = self.getVMGag()
            
        nozzle = gag.find("**/joint_nozzle")
            
        if self.isLocal() and base.localAvatar.battleControls:
            if base.localAvatar.isFirstPerson():
                self.getFPSCam().resetViewPunch()
                self.getFPSCam().addViewPunch(Vec3(random.uniform(-0.6, 0.6), random.uniform(-0.25, -0.5), 0.0))
                startPos = camera.getPos(render)
            else:
                startPos = nozzle.getPos(render)
            hitPos = PhysicsUtils.getHitPosFromCamera()
        else:
            startPos = nozzle.getPos(render)
            quat = Quat()
            quat.setHpr(self.avatar.getHpr(render) + (0, self.avatar.lookPitch, 0))
            hitPos = quat.xform(Vec3.forward() * 10000)
            hit = PhysicsUtils.rayTestClosestNotMe(self.avatar, startPos,
                hitPos,
                CIGlobals.WorldGroup | CIGlobals.LocalAvGroup)
            if hit is not None:
                hitPos = hit.getHitPos()
            
        pellet = WaterPellet(self.isLocal())
        pellet.addToWorld(nozzle.getPos(render), lookAt = hitPos, velo = Vec3.forward() * self.pelletSpeed)
        
        if self.isLocal():
            base.localAvatar.sendUpdate('usedGag', [self.id])
