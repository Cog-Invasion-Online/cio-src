from panda3d.core import Point3, Vec3

from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from direct.distributed.ClockDelta import globalClockDelta

from BaseGagAI import BaseGagAI
from WholeCreamPieShared import WholeCreamPieShared
from WholeCreamPieProjectileAI import WholeCreamPieProjectileAI
from src.coginvasion.attack.Attacks import ATTACK_GAG_WHOLECREAMPIE
from src.coginvasion.attack.TakeDamageInfo import TakeDamageInfo
from src.coginvasion.cog.ai.RelationshipsAI import RELATIONSHIP_FRIEND
from src.coginvasion.cog.ai.BaseNPCAI import BaseNPCAI
from src.coginvasion.gags import GagGlobals
from src.coginvasion.globals import CIGlobals
from src.coginvasion.phys import PhysicsUtils
from src.coginvasion.battle.SoundEmitterSystemAI import SOUND_COMBAT

import random

#########################################################################

from src.coginvasion.szboss.DistributedEntityAI import DistributedEntityAI

class PieGibAI(DistributedEntityAI):
    
    def announceGenerate(self):
        DistributedEntityAI.announceGenerate(self)
        
        self.b_setModel("phase_14/models/props/creampie_gib.bam")
        self.setMass(5.0)
        self.setSolid(self.SOLID_MESH)
        self.initPhysics()
        self.getPhysNode().setFriction(50.0)
        #self.getPhysNode().setLinearDamping(3.0)
        #self.getPhysNode().setAngularDamping(3.0)
        self.startPosHprBroadcast()
        self.setNextThink(3.0)
        
    def delete(self):
        self.stopPosHprBroadcast()
        DistributedEntityAI.delete(self)

    def think(self):
        self.requestDelete()
        self.setNextThink(-1)
        
#########################################################################

class WholeCreamPieAI(BaseGagAI, WholeCreamPieShared):

    Name = GagGlobals.WholeCreamPie
    ID = ATTACK_GAG_WHOLECREAMPIE

    ThrowPower = 300.0
    
    Cost = 100
    
    NPC_DRAW_TIME = 1.5
    
    HealFriends = True
    HealAmount = 5

    def __init__(self):
        BaseGagAI.__init__(self)
        self.actionLengths.update({self.StateDraw   :   0.5,
                                   self.StateThrow  :   1.0})

        self.throwOrigin = Point3(0)
        self.traceOrigin = Point3(0)
        self.traceVector = Vec3(0)

        self.ammo = 100
        self.maxAmmo = 100

        self.__projs = []

        self.throwTime = 0
        
    def setAvatar(self, avatar):
        BaseGagAI.setAvatar(self, avatar)
        #from src.coginvasion.cog.ai.BaseNPCAI import BaseNPCAI
        #if isinstance(avatar, BaseNPCAI):
        #    # Match the draw time with the third person animation
        #    self.actionLengths[self.StateDraw] = self.NPC_DRAW_TIME
        #else:
        #    self.actionLengths[self.StateDraw] = 0.5

    def getBaseDamage(self):
        return 30

    def equip(self):
        if not BaseGagAI.equip(self):
            return False

        self.throwTime = globalClock.getFrameTime()

        # Draw the whole cream pie!
        self.b_setAction(self.StateDraw)

        return True

    def determineNextAction(self, completedAction):
        if completedAction == self.StateDraw:
            return self.StateIdle
        elif completedAction == self.StateThrow:
            self.avatar.npcFinishAttack()
            return self.StateDraw

        return self.StateIdle

    def onProjectileHit(self, contact, collider, intoNP):
        BaseGagAI.onProjectileHit(self, contact, collider, intoNP, False)

        gib = base.air.createObjectByName("PieGibAI")
        gib.generateWithRequired(self.avatar.getBattleZone().zoneId)
        gib.setPos(collider.getPos(render))
        gib.setHpr(collider.getHpr(render) + (0, -90, 0))
        gib.d_clearSmoothing()
        gib.d_broadcastPosHpr()

        gibVel = CIGlobals.reflect(collider.getAbsVelocity() * 0.04, contact.getHitNormal())
        gib.getPhysNode().setLinearVelocity(gibVel)
        gib.getPhysNode().setAngularVelocity(Vec3(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1)) * 5)

        collider.requestDelete()

    def setAction(self, action):
        BaseGagAI.setAction(self, action)

        if action == self.StateThrow:
            if not isinstance(self.avatar, BaseNPCAI):
                self.takeAmmo(-1)

            throwVector = PhysicsUtils.getThrowVector(self.avatar.getViewOrigin(),
                                                      self.traceVector,
                                                      self.avatar.getViewOrigin(),
                                                      self.avatar,
                                                      self.avatar.getBattleZone().getPhysicsWorld())
            endPos = CIGlobals.extrude(self.avatar.getViewOrigin(), self.ThrowPower, throwVector) - (0, 0, 90)
            
            proj = WholeCreamPieProjectileAI(base.air)
            proj.setProjectile(2.5, self.avatar.getViewOrigin(),
                endPos, 1.07, globalClockDelta.getFrameNetworkTime())
            proj.generateWithRequired(self.avatar.getBattleZone().zoneId)
            proj.addHitCallback(self.onProjectileHit)
            proj.addExclusion(self.avatar)
            
            self.avatar.emitSound(SOUND_COMBAT, self.avatar.getViewOrigin(), duration = 0.5)

            self.throwTime = globalClock.getFrameTime()
            
    def canUse(self):
        return self.hasAmmo() and (globalClock.getFrameTime() - self.throwTime >= 0.5)

    def primaryFirePress(self, data):
        if not self.canUse():
            return
        
        self.traceVector = self.avatar.getViewVector(1)
        self.b_setAction(self.StateThrow)

    def npcUseAttack(self, target):
        if not self.canUse():
            return False

        self.traceVector = (
            target.getViewOrigin() - self.avatar.getViewOrigin()
        ).normalized()
        self.setNextAction(self.StateThrow)
        
        return True

    def checkCapable(self, dot, squaredDistance):
        return squaredDistance <= 35*35
