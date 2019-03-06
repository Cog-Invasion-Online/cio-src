"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file HL2Pistol.py
@author Brian Lach
@date February 26, 2019

@desc Another easter egg

"""

from panda3d.core import Point3, Vec3, NodePath, OmniBoundingVolume

from direct.actor.Actor import Actor
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from direct.interval.IntervalGlobal import Sequence, Func, ActorInterval

from BaseGag import BaseGag, BaseGagAI

from src.coginvasion.base.Precache import precacheSound, precacheActor
from src.coginvasion.cog.ai.RelationshipsAI import RELATIONSHIP_FRIEND
from src.coginvasion.gui.Crosshair import CrosshairData
from src.coginvasion.globals import CIGlobals
from src.coginvasion.phys import PhysicsUtils
from src.coginvasion.gags import GagGlobals
from src.coginvasion.avatar.Attacks import ATTACK_HOLD_RIGHT, ATTACK_HL2PISTOL
from src.coginvasion.avatar.TakeDamageInfo import TakeDamageInfo

import random

class HL2PistolShared:
    StateFire   = 1
    StateReload = 2
    StateDraw   = 3
    
class HL2Pistol(BaseGag, HL2PistolShared):
    
    #ModelPath = "phase_14/hl2/w_pistol/w_pistol.bam"
    ModelOrigin = (-0.03, 1.19, -0.14)
    ModelAngles = (2.29, 347.01, 45)
    ModelScale = 2
    
    Name = GagGlobals.HL2Pistol
    ID = ATTACK_HL2PISTOL
    Hold = ATTACK_HOLD_RIGHT
    
    sgDir = 'phase_14/hl2/v_pistol/'
    sgActorDef = [sgDir + 'v_pistol.bam',
	    {'draw': sgDir + 'v_pistol-draw.egg',
	     'idle': sgDir + 'v_pistol-idle01.egg',
	     'fire': sgDir + 'v_pistol-fire.egg',
	     'reload': sgDir + 'v_pistol-reload.egg'}]
    sgFirePath = 'phase_14/hl2/v_pistol/pistol_fire2.wav'
    sgEmptyPath = 'phase_14/hl2/v_pistol/pistol_empty.wav'
    sgReloadPath = 'phase_14/hl2/v_pistol/pistol_reload1.wav'
                     
    SpecialVM = True
    
    def __init__(self):
        BaseGag.__init__(self)
        
        self.sgViewModel = None 
        self.fireSound = base.audio3d.loadSfx(self.sgFirePath)
        self.emptySound = base.audio3d.loadSfx(self.sgEmptyPath)
        self.reloadSound = base.audio3d.loadSfx(self.sgReloadPath)

        self.crosshair = CrosshairData(crosshairScale = 0.6, crosshairRot = 45)
            
    @classmethod
    def doPrecache(cls):
        super(HL2Pistol, cls).doPrecache()
        
        precacheActor(cls.sgActorDef)
        
        precacheSound(cls.sgFirePath)
        precacheSound(cls.sgEmptyPath)
        precacheSound(cls.sgReloadPath)
            
    def addPrimaryPressData(self, dg):
        CIGlobals.putVec3(dg, camera.getPos(render))
        CIGlobals.putVec3(dg, camera.getQuat(render).getForward())
            
    def equip(self):
        if not BaseGag.equip(self):
            return False
            
        base.audio3d.attachSoundToObject(self.fireSound, self.avatar)
        base.audio3d.attachSoundToObject(self.emptySound, self.avatar)
        base.audio3d.attachSoundToObject(self.reloadSound, self.avatar)
            
        if self.isFirstPerson():
            self.sgViewModel = Actor(self.sgActorDef[0], self.sgActorDef[1])
            self.sgViewModel.node().setBounds(OmniBoundingVolume())
            self.sgViewModel.node().setFinal(1)
            self.sgViewModel.setBlend(frameBlend = base.config.GetBool('interpolate-frames', False))
            self.sgViewModel.setH(180)
            
            fpsCam = self.getFPSCam()
            fpsCam.swapViewModel(self.sgViewModel, 54.0)
            self.getViewModel().show()

        self.doDrawAndHold('squirt', 0, 43, 1.0, 43, 43)
            
        return True
        
    def unEquip(self):
        if not BaseGag.unEquip(self):
            return False
            
        if self.isFirstPerson():
            self.getFPSCam().restoreViewModel()
            self.getViewModel().hide()
            self.sgViewModel.cleanup()
            self.sgViewModel.removeNode()
            self.sgViewModel = None
            
        return True
            
    def setAction(self, action):
        BaseGag.setAction(self, action)
        
        if self.isFirstPerson():
            track = Sequence()
            vm = self.getViewModel()
            fpsCam = self.getFPSCam()
            if action == self.StateIdle:
                track.append(Func(vm.loop, "idle"))
            elif action == self.StateDraw:
                track.append(ActorInterval(vm, "draw"))
            elif action == self.StateReload:
                track.append(Func(self.reloadSound.play))
                track.append(ActorInterval(vm, "reload"))
            elif action == self.StateFire:
                fpsCam.resetViewPunch()
                fpsCam.addViewPunch(Vec3(random.uniform(-0.6, 0.6), random.uniform(-0.25, -0.5), 0.0))
                track.append(Func(self.fireSound.play))
                track.append(ActorInterval(vm, "fire"))
            fpsCam.setVMAnimTrack(track)

class HL2PistolAI(BaseGagAI, HL2PistolShared):

    Name = GagGlobals.HL2Pistol
    ID = ATTACK_HL2PISTOL
    HasClip = True

    FireDelay = 0.1
    
    def __init__(self):
        BaseGagAI.__init__(self)
        self.actionLengths.update({self.StateDraw   :   1.0,
                                   self.StateReload :   1.79,
                                   self.StateFire   :   0.5})
        self.maxAmmo = 150
        self.ammo = 150
        self.maxClip = 18
        self.clip = 18

        self.traceOrigin = Point3(0)
        self.traceVector = Vec3(0)

    def shouldGoToNextAction(self, complete):
        return ((complete) or
               (not complete and self.action == self.StateFire and
                self.getActionTime() >= self.FireDelay and self.nextAction == self.StateFire))
                                   
    def determineNextAction(self, completedAction):
        if completedAction == self.StateIdle:
            if not self.hasClip():
                # Need to refill clip
                return self.StateReload
        elif completedAction == self.StateReload:
            # refill clip, but limit to ammo if ammo is less than clip size
            if self.ammo >= self.maxClip:
                self.clip = self.maxClip
            else:
                self.clip = self.ammo

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
        traceEnd = self.traceOrigin + (self.traceVector * 10000)
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
            self.takeAmmo(-1)
            self.clip -= 1
            
            self.__doBulletTraceAndDamage()
            
    def canUse(self):
        return self.hasClip() and self.hasAmmo() and (self.action in [self.StateIdle, self.StateFire])
        
    def primaryFirePress(self, data):
        if not self.canUse():
            return

        dg = PyDatagram(data)
        dgi = PyDatagramIterator(dg)
        self.traceOrigin = CIGlobals.getVec3(dgi)
        self.traceVector = CIGlobals.getVec3(dgi)
        self.setNextAction(self.StateFire)

    def reloadPress(self, data):
        if self.action == self.StateIdle and not self.isClipFull() and self.ammo > self.clip:
            self.setNextAction(self.StateReload)
        
    def equip(self):
        if not BaseGagAI.equip(self):
            return False
            
        self.b_setAction(self.StateDraw)
        
        return True