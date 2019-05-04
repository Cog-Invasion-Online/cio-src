"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DistributedGagPickup.py
@author Brian Lach
@date April 11, 2019

"""

from panda3d.bullet import BulletGhostNode, BulletSphereShape

from src.coginvasion.base.Precache import precacheSound
from src.coginvasion.szboss.DistributedEntity import DistributedEntity

class DistributedGagPickup(DistributedEntity):

    #PickupSoundPath = "phase_4/audio/sfx/SZ_DD_treasure.ogg"
    PickupSoundPath = "phase_14/audio/sfx/ammo_pickup.wav"

    def __init__(self, cr):
        DistributedEntity.__init__(self, cr)
        self.gagId = 0
        self.pickupState = 0
        self.collNode = None
        self.pickupSound = None
        self.gagMdl = None

    @classmethod
    def doPrecache(cls):
        super(DistributedGagPickup, cls).doPrecache()

        precacheSound(cls.PickupSoundPath)

    def setGagId(self, gagId):
        self.gagId = gagId

        if self.gagMdl:
            self.gagMdl.removeNode()
            self.gagMdl = None

        attackCls = self.cr.attackMgr.getAttackClassByID(gagId)
        if attackCls and attackCls.ModelPath:
            self.gagMdl = loader.loadModel(attackCls.ModelPath)
            self.gagMdl.setScale(attackCls.ModelScale)
            self.gagMdl.reparentTo(self)

    def getGagId(self):
        return self.gagId

    def setPickupState(self, state):
        self.pickupState = state
        if state == 0:
            # hidden
            self.hide()
            base.physicsWorld.remove(self.collNode.node())
        elif state == 1:
            # shown
            self.show()
            base.physicsWorld.attach(self.collNode.node())

    def getPickupState(self):
        return self.pickupState

    def __handleTouchSphere(self, entry):
        self.sendUpdate('requestPickup')

    def pickupAccepted(self):
        self.pickupSound.play()

    def delete(self):
        if self.gagMdl:
            self.gagMdl.removeNode()
        self.gagMdl = None
        if self.collNode:
            self.ignore("enter" + self.collNode.getName())
            if self.pickupState == 1:
                base.physicsWorld.remove(self.collNode.node())
            self.collNode.removeNode()
        self.collNode = None
        self.pickupSound = None
        self.pickupState = None
        self.gagId = None

        DistributedEntity.delete(self)

    def generate(self):
        DistributedEntity.generate(self)

        sph = BulletSphereShape(1.0)
        gn = BulletGhostNode(self.uniqueName("pickupGhost"))
        print gn.getName()
        gn.addShape(sph)
        self.collNode = self.attachNewNode(gn)

        self.pickupSound = base.loadSfx(self.PickupSoundPath)

    def announceGenerate(self):
        DistributedEntity.announceGenerate(self)
        self.reparentTo(render)
        self.accept("enter" + self.collNode.getName(), self.__handleTouchSphere)
