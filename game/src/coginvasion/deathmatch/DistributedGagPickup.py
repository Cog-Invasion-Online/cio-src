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
from src.coginvasion.globals import CIGlobals
from src.coginvasion.szboss.UseableObject import UseableObject

class DistributedGagPickup(DistributedEntity, UseableObject):

    PickupSoundPath = "phase_4/audio/sfx/SZ_DD_treasure.ogg"
    #PickupSoundPath = "phase_14/audio/sfx/ammo_pickup.wav"

    def __init__(self, cr):
        DistributedEntity.__init__(self, cr)
        UseableObject.__init__(self)
        self.gagId = 0
        self.pickupState = 0
        self.cost = 0
        self.collNode = None
        self.pickupSound = None
        self.gagMdl = None
        
        self.hasPhysGeom = True
        self.underneathSelf = True
        
        self.infoText = None

    @classmethod
    def doPrecache(cls):
        super(DistributedGagPickup, cls).doPrecache()

        precacheSound(cls.PickupSoundPath)
        
    def setCost(self, cost):
        self.cost = cost
        
    def getCost(self):
        return self.cost

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
            base.physicsWorld.remove(self.bodyNP.node())
        elif state == 1:
            # shown
            self.show()
            base.physicsWorld.attach(self.bodyNP.node())

    def getPickupState(self):
        return self.pickupState

    def startUse(self):
        self.sendUpdate('requestPickup')
        
    def __handleTouch(self, intoNP):
        self.sendUpdate('requestPickup')
        
    def __handleLookAt(self, entry):
        name = self.cr.attackMgr.getAttackName(self.gagId)
        from panda3d.core import TextNode
        if self.cost > 0:
            costStr = str(self.cost) + " Jellybean"
            if self.cost != 1:
                costStr += "s"
        else:
            costStr = "Free"
        nameText = TextNode('gagnametext')
        nameText.setText("%s\n%s\n\nPress E to purchase" % (name, costStr))
        nameText.setTextColor((1, 1, 1, 1))
        nameText.setFont(CIGlobals.getToonFont())
        nameText.setAlign(TextNode.ACenter)
        tnp = self.attachNewNode(nameText)
        tnp.setBillboardAxis()
        tnp.setZ(2)
        tnp.setScale(0.25)
        self.infoText = tnp
        
    def __handleLookAway(self, entry):
        if self.infoText:
            self.infoText.removeNode()
        self.infoText = None

    def pickupAccepted(self):
        self.pickupSound.play()

    def delete(self):
        if self.gagMdl:
            self.gagMdl.removeNode()
        self.gagMdl = None
        if self.bodyNP:
            self.ignore("rayenter" + self.bodyNP.getName())
            self.ignore("rayexit" + self.bodyNP.getName())
            self.ignore("enter" + self.bodyNP.getName())
        UseableObject.removeNode(self)
        self.pickupSound = None
        self.pickupState = None
        self.gagId = None
        self.cost = None

        DistributedEntity.delete(self)

    def generate(self):
        DistributedEntity.generate(self)

        self.pickupSound = base.loadSfx(self.PickupSoundPath)

    def announceGenerate(self):
        DistributedEntity.announceGenerate(self)
        UseableObject.load(self, self.uniqueName('gagPickup'))
        self.reparentTo(render)
        self.accept("enter" + self.bodyNP.getName(), self.__handleTouch)
        #self.accept("rayenter" + self.bodyNP.getName(), self.__handleLookAt)
        #self.accept("rayexit" + self.bodyNP.getName(), self.__handleLookAway)
