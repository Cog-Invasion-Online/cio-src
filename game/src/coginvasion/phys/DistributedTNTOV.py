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
        self.setPos(base.localAvatar.find("**/def_joint_right_hold").getPos(render))
        self.lookAt(render, PhysicsUtils.getHitPosFromCamera())
        self.toss()

    def b_explode(self):
        self.explode()
        self.sendUpdate('explode')

        for obj in self.cr.doId2do.values():
            if obj.__class__.__name__ in CIGlobals.SuitClasses:
                if obj.getPlace() == base.localAvatar.zoneId:
                    dist = obj.getDistance(self)
                    if dist <= GagGlobals.TNT_RANGE:
                        obj.sendUpdate('hitByGag', [GagGlobals.gagIdByName[GagGlobals.TNT], dist])

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