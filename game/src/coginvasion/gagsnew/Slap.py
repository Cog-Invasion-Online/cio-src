"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Slap.py
@author CheezedFish
@date February 26, 2019

@desc Default melee gag, useful in a pinch

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
from src.coginvasion.avatar.Attacks import ATTACK_HOLD_NONE, ATTACK_SLAP
from src.coginvasion.avatar.TakeDamageInfo import TakeDamageInfo

import random

class SlapShared:
    StateFire   = 1
    StateIdle   = 2
    StateDraw   = 3
    
class Slap(BaseGag, SlapShared):
    Name = GagGlobals.Slap
    ID = ATTACK_SLAP
    Hold = ATTACK_HOLD_NONE
    
    slapFirePath = 'phase_14/audio/sfx/slap_swish.ogg'
    slapHitPath = 'phase_5/audio/sfx/SA_hardball_impact_only_alt.ogg'
    
    def __init__(self):
        BaseGag.__init__(self)
         
        self.fireSound = base.audio3d.loadSfx(self.slapFirePath)
        self.hitSound = base.audio3d.loadSfx(self.slapHitPath)

        self.crosshair = CrosshairData(crosshairScale = 0.6, crosshairRot = 45)
            
    @classmethod
    def doPrecache(cls):
        super(Slap, cls).doPrecache()
        
        precacheSound(cls.slapFirePath)
        precacheSound(cls.slapHitPath)
            
    def addPrimaryPressData(self, dg):
        CIGlobals.putVec3(dg, camera.getPos(render))
        CIGlobals.putVec3(dg, camera.getQuat(render).getForward())
        
    def equip(self):
        if not BaseGag.equip(self):
            return False
            
        base.audio3d.attachSoundToObject(self.fireSound, self.avatar)

        if self.isFirstPerson():
            fpsCam = self.getFPSCam()
            vm = self.getViewModel()
            vm.show()
            fpsCam.setVMAnimTrack(Func(vm.loop, 'slap_idle'))

        return True
        
    def unEquip(self):
        if not BaseGag.unEquip(self):
            return False
            
        base.audio3d.detachSound(self.fireSound)
            
    def setAction(self, action):
        BaseGag.setAction(self, action)

        if self.isFirstPerson():
            fpsCam = self.getFPSCam()
            vm = self.getViewModel()

        if action == self.StateFire:
            if self.isFirstPerson():
                fpsCam.addViewPunch(self.getViewPunch())
                fpsCam.setVMAnimTrack(Parallel(Func(self.fireSound.play), ActorInterval(vm, 'slap_hit')))
            self.doDrawNoHold('toss', 0, 30)

        elif action == self.StateIdle:
            if self.isFirstPerson():
                fpsCam.setVMAnimTrack(Func(vm.loop, 'slap_idle'))
            self.doHold('toss', 30, 30, 1.0)
            
        elif action == self.StateDraw:
            if self.isFirstPerson():
                fpsCam.setVMAnimTrack(Func(vm.play, 'slap_idle'))
            self.doHold('toss', 30, 30, 1.0)

class SlapAI(BaseGagAI, SlapShared):

    Name = GagGlobals.Slap
    ID = ATTACK_SLAP
    HasClip = False

    FireDelay = 0.6
    
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
        
    def _handleShotSomething(self, hitNode, hitPos, distance):
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
        # to find out what we hit, and adjust the direction of the projectile launch
        traceEnd = self.traceOrigin + (self.traceVector * 5) # Close range attack
        hit = PhysicsUtils.rayTestClosestNotMe(self.avatar,
                                                self.traceOrigin,
                                                traceEnd,
                                                CIGlobals.WorldGroup | CIGlobals.CharacterGroup,
                                                self.avatar.getBattleZone().getPhysicsWorld())
        if hit is not None:
            node = hit.getNode()
            hitPos = hit.getHitPos()
            distance = (hitPos - self.traceOrigin).length()
            self._handleShotSomething(NodePath(node), hitPos, distance)
        
    def setAction(self, action):
        BaseGagAI.setAction(self, action)
        
        if action == self.StateFire:
            self.__doBulletTraceAndDamage()
            
    def canUse(self):
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