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
    StateDraw   = 2
    
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
        self.actionLengths.update({self.StateFire   :   1.0,
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

    def doTraceAndDamage(self, traces = 1):
        BaseGagAI.doTraceAndDamage(self, self.traceOrigin, self.traceVector, self.AttackRange, traces)
        
    def onSetAction(self, action):
        
        if action == self.StateFire:
            if self.UsesAmmo:
                self.takeAmmo(-1)
            if self.HasClip:
                self.clip -= 1
            self.doTraceAndDamage()
            
    def canUse(self):
        # Hitscan gags do not have ammo, and thus, are always usable
        return self.action == [self.StateIdle, self.StateFire]
        
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
        if not BaseGagAI.unEquip(self):
            return False
        
        return True
