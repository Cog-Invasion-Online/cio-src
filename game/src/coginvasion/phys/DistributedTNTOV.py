"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedTNTOV.py
@author Brian Lach
@date June 15, 2018

"""

from panda3d.core import Vec3

from direct.distributed.DistributedObjectOV import DistributedObjectOV

from src.coginvasion.globals import CIGlobals
from src.coginvasion.gags import GagGlobals
from src.coginvasion.globals import CIGlobals
from src.coginvasion.phys import PhysicsUtils
from DistributedTNT import DistributedTNT

import random

class DistributedTNTOV(DistributedTNT, DistributedObjectOV):

    def __init__(self, cr):
        DistributedTNT.__init__(self, cr)
        self.explodeTask = None

    def toss(self, power = 50.0):
        self.explodeTask = taskMgr.doMethodLater(2.1, self.__explodeTask, 'TNT_explodeTask')

        # Toss the TNT!
        vel = self.getQuat(render).xform(Vec3(0, 1, 0.25)) * power
        self.node().setLinearVelocity(vel)
        
        # Spin it like we threw it
        #self.node().setAngularVelocity(Vec3(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)) * 25)

    def announceGenerate(self):
        DistributedTNT.announceGenerate(self)
        self.stopSmooth()
        self.startPosHprBroadcast()
        
        pos = base.localAvatar.getPos(render)
        # Make sure to start the TNT out in front of our capsule to prevent weird physics
        extrude = base.localAvatar.getQuat(render).xform(Vec3(0, 1.0 + 0.3925, base.localAvatar.getHeight() / 2.0))
        self.setPos(pos + extrude)

        push = ((pos + (0, 0, base.localAvatar.getHeight() / 2.0)) - camera.getPos(render)).length()
        self.lookAt(render, PhysicsUtils.getHitPosFromCamera(push = push))
        self.d_clearSmoothing()
        self.d_broadcastPosHpr()
        
        power = 50.0
        bp = base.localAvatar.backpack
        if bp:
            gag = bp.getGagByID(GagGlobals.gagIdByName[GagGlobals.TNT])
            if gag and gag.powerBar:
                power = gag.powerBar.getPower()
        self.toss(power)

    def b_explode(self):
        self.explode()
        self.sendUpdate('explode')

        for obj in base.avatars:
            if CIGlobals.isAvatar(obj):
                dist = obj.getDistance(self)
                if dist <= GagGlobals.TNT_RANGE:
                    obj.handleHitByToon(base.localAvatar, GagGlobals.gagIdByName[GagGlobals.TNT], dist)

    def getPhysBody(self):
        body = DistributedTNT.getPhysBody(self)
        body.setKinematic(False)
        body.setMass(5.0)
        body.setAngularDamping(0.3)
        body.setLinearDamping(0.8)
        return body

    def doSetupPhysics(self):
        self.setupPhysics(self.getPhysBody(), False)

    def __explodeTask(self, task):
        self.b_explode()
        return task.done

    def disable(self):
        self.stopPosHprBroadcast()
        self.gag = None
        if self.explodeTask:
            self.explodeTask.remove()
        self.explodeTask = None
        DistributedTNT.disable(self)
