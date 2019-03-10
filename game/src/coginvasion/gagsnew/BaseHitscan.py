"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file BaseHitscan.py
@author CheezedFish
@date March 9, 2019

@desc Base Hitscan class, to be used for all other Hitscans

"""

from panda3d.core import Point3, Vec3, NodePath, OmniBoundingVolume

from direct.actor.Actor import Actor
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from direct.interval.IntervalGlobal import Sequence, Func, ActorInterval, Parallel

from BaseGag import BaseGag, BaseGagAI

from src.coginvasion.base.Precache import precacheSound, precacheActor
from src.coginvasion.cog.ai.RelationshipsAI import RELATIONSHIP_FRIEND
from src.coginvasion.gui.Crosshair import CrosshairData
from src.coginvasion.globals import CIGlobals
from src.coginvasion.phys import PhysicsUtils
from src.coginvasion.gags import GagGlobals
from src.coginvasion.avatar.Attacks import ATTACK_HOLD_NONE, ATTACK_NONE
from src.coginvasion.avatar.TakeDamageInfo import TakeDamageInfo

class BaseHitscanShared:
    StateFire   = 1
    StateIdle   = 2
    StateDraw   = 3
    
class BaseHitscan(BaseGag, BaseHitscanShared):
    Name = 'BASE HITSCAN: DO NOT USE'
    ID = ATTACK_NONE
    Hold = ATTACK_HOLD_NONE
    
    def __init__(self):
        BaseGag.__init__(self)

        self.crosshair = CrosshairData(crosshairScale = 0.6, crosshairRot = 45)
            
    @classmethod
    def doPrecache(cls):
        super(BaseHitscan, cls).doPrecache()
            
    def addPrimaryPressData(self, dg):
        CIGlobals.putVec3(dg, camera.getPos(render))
        CIGlobals.putVec3(dg, camera.getQuat(render).getForward())
        
    def equip(self):
        if not BaseGag.equip(self):
            return False

        return True
        
    def unEquip(self):
        if not BaseGag.unEquip(self):
            return False
            
        return True
        
    def setAction(self, action):
        BaseGag.setAction(self, action)

class BaseHitscanAI(BaseGagAI, BaseHitscanShared):

    Name = 'BASE HITSCAN: DO NOT USE'
    ID = ATTACK_NONE
    HasClip = False
    UsesAmmo = False

    FireDelay = 0.1
    AttackRange = 100.0
    
    def __init__(self):
        BaseGagAI.__init__(self)
        self.actionLengths.update({self.StateIdle   :   1.0,
                                   self.StateFire   :   1.0,
                                   self.StateDraw   :   0.1})
        self.maxAmmo = 1
        self.ammo = 1

        self.traceOrigin = Point3(0)
        self.traceVector = Vec3(0)

    def shouldGoToNextAction(self, complete):
        return ((complete) or
               (not complete and self.action == self.StateFire and
                self.getActionTime() >= self.FireDelay and self.nextAction == self.StateFire))
                                   
    def determineNextAction(self, completedAction):
        return self.StateIdle
        
    def _handleHitSomething(self, hitNode, hitPos, distance):
        avNP = hitNode.getParent()
        
        for obj in base.air.avatars[self.avatar.zoneId]:
            if (CIGlobals.isAvatar(obj) and obj.getKey() == avNP.getKey() and 
            self.avatar.getRelationshipTo(obj) != RELATIONSHIP_FRIEND):
                
                dmgInfo = TakeDamageInfo(self.avatar, self.getID(),
                                    self.calcDamage(distance),
                                    hitPos, self.traceOrigin)
                
                obj.takeDamage(dmgInfo)

                break

    def __doBulletTraceAndDamage(self):
        # Trace a line from the trace origin outward along the trace direction
        # to find out what we hit, and adjust the direction of the hitscan
        traceEnd = self.traceOrigin + (self.traceVector * self.AttackRange)
        hit = PhysicsUtils.rayTestClosestNotMe(self.avatar,
                                                self.traceOrigin,
                                                traceEnd,
                                                CIGlobals.WorldGroup | CIGlobals.CharacterGroup,
                                                self.avatar.getBattleZone().getPhysicsWorld())
        if hit is not None:
            node = hit.getNode()
            hitPos = hit.getHitPos()
            distance = (hitPos - self.traceOrigin).length()
            self._handleHitSomething(NodePath(node), hitPos, distance)
        
    def setAction(self, action):
        BaseGagAI.setAction(self, action)
        
        if action == self.StateFire:
            if self.UsesAmmo:
                self.takeAmmo(-1)
                self.clip -= 1
            self.__doBulletTraceAndDamage()
            
    def canUse(self):
        # Hitscan gags do not have ammo, and thus, are always usable
        return True
        
    def primaryFirePress(self, data):
        if not self.canUse():
            return

        dg = PyDatagram(data)
        dgi = PyDatagramIterator(dg)
        self.traceOrigin = CIGlobals.getVec3(dgi)
        self.traceVector = CIGlobals.getVec3(dgi)
        self.setNextAction(self.StateFire)
        
    def equip(self):
        if not BaseGagAI.equip(self):
            return False
            
        self.b_setAction(self.StateDraw)
        
        return True
        
    def unEquip(self):
        if not BaseGagAI.equip(self):
            return False
        
        return True