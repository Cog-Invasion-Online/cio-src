"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file HL2Shotgun.py
@author Brian Lach
@date February 24, 2019

@desc Easter egg! Shotgun from Half-Life 2. I wanted to see how easy it
      would be to port it over to Panda since our material system is
      almost identical to Source. It was easy.

"""

from panda3d.core import Point3, Vec3, NodePath, OmniBoundingVolume

from direct.actor.Actor import Actor
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from direct.interval.IntervalGlobal import Sequence, Func, ActorInterval

from BaseHitscan import BaseHitscan, BaseHitscanAI

from src.coginvasion.base.Precache import precacheSound, precacheActor
from src.coginvasion.globals import CIGlobals
from src.coginvasion.gags import GagGlobals
from src.coginvasion.avatar.Attacks import ATTACK_HOLD_RIGHT, ATTACK_HL2SHOTGUN

import random

class HL2ShotgunShared:    
    StatePump = 3
    StateBeginReload = 4
    StateEndReload = 5
    StateReload = 6
    StateDblFire = 7
    
class HL2Shotgun(BaseHitscan, HL2ShotgunShared):
    
    ModelPath = "phase_14/hl2/w_shotgun/w_shotgun.bam"
    ModelOrigin = (-0.03, 1.19, -0.14)
    ModelAngles = (2.29, 347.01, 45)
    ModelScale = 2
    
    Name = GagGlobals.HL2Shotgun
    ID = ATTACK_HL2SHOTGUN
    Hold = ATTACK_HOLD_RIGHT
    
    sgDir = 'phase_14/hl2/v_shotgun/panda/opt/'
    sgActorDef = [sgDir + 'v_shotgun.bam',
	    {'draw': sgDir + 'v_shotgun-draw.egg',
	     'idle': sgDir + 'v_shotgun-idle01.egg',
	     'pump': sgDir + 'v_shotgun-pump.egg',
	     'fire': sgDir + 'v_shotgun-fire01.egg',
	     'altfire': sgDir + 'v_shotgun-altfire.egg',
	     'reload1': sgDir + 'v_shotgun-reload1.egg',
	     'reload2': sgDir + 'v_shotgun-reload2.egg',
	     'reload3': sgDir + 'v_shotgun-reload3.egg'}]
    sgFirePath = 'phase_14/hl2/v_shotgun/shotgun_fire7.wav'
    sgEmptyPath = 'phase_14/hl2/v_shotgun/shotgun_empty.wav'
    sgDblFirePath = 'phase_14/hl2/v_shotgun/shotgun_dbl_fire7.wav'
    sgPumpPath = 'phase_14/hl2/v_shotgun/shotgun_cock.wav'
    sgReloadPaths = ['phase_14/hl2/v_shotgun/shotgun_reload1.wav',
                     'phase_14/hl2/v_shotgun/shotgun_reload2.wav',
                     'phase_14/hl2/v_shotgun/shotgun_reload3.wav']
                     
    SpecialVM = True
    
    def __init__(self):
        BaseHitscan.__init__(self)
        
        self.sgViewModel = None 
        self.fireSound = base.audio3d.loadSfx(self.sgFirePath)
        self.dblFireSound = base.audio3d.loadSfx(self.sgDblFirePath)
        self.pumpSound = base.audio3d.loadSfx(self.sgPumpPath)
        self.emptySound = base.audio3d.loadSfx(self.sgEmptyPath)
        self.reloadSounds = []
        for rl in self.sgReloadPaths:
            self.reloadSounds.append(base.audio3d.loadSfx(rl))
            
    @classmethod
    def doPrecache(cls):
        super(HL2Shotgun, cls).doPrecache()
        
        precacheActor(cls.sgActorDef)
        
        precacheSound(cls.sgFirePath)
        precacheSound(cls.sgDblFirePath)
        precacheSound(cls.sgPumpPath)
        precacheSound(cls.sgEmptyPath)
        for rl in cls.sgReloadPaths:
            precacheSound(rl)
            
    def addPrimaryPressData(self, dg):
        CIGlobals.putVec3(dg, camera.getPos(render))
        CIGlobals.putVec3(dg, camera.getQuat(render).getForward())

    def addSecondaryPressData(self, dg):
        self.addPrimaryPressData(dg)
            
    def __doBob(self):
        self.setAnimTrack(self.getBobSequence('firehose', 30, 30, 1.0), startNow = True, looping = True)
            
    def equip(self):
        if not BaseHitscan.equip(self):
            return False
            
        base.audio3d.attachSoundToObject(self.fireSound, self.avatar)
        base.audio3d.attachSoundToObject(self.dblFireSound, self.avatar)
        base.audio3d.attachSoundToObject(self.pumpSound, self.avatar)
        base.audio3d.attachSoundToObject(self.emptySound, self.avatar)
        for s in self.reloadSounds:
            base.audio3d.attachSoundToObject(s, self.avatar)
            
        if self.isFirstPerson():
            self.sgViewModel = Actor(self.sgActorDef[0], self.sgActorDef[1])
            self.sgViewModel.node().setBounds(OmniBoundingVolume())
            self.sgViewModel.node().setFinal(1)
            self.sgViewModel.setBlend(frameBlend = base.config.GetBool('interpolate-frames', False))
            self.sgViewModel.setH(180)
            
            fpsCam = self.getFPSCam()
            fpsCam.swapViewModel(self.sgViewModel, 54.0)
            self.getViewModel().show()
            
        toonTrack = Sequence(Func(self.avatar.setForcedTorsoAnim, 'firehose'),
                         self.getAnimationTrack('firehose', endFrame = 30),
                         Func(self.__doBob))
        self.setAnimTrack(toonTrack, startNow = True)
            
        return True
        
    def unEquip(self):
        if not BaseHitscan.unEquip(self):
            return False
            
        if self.isFirstPerson():
            self.getFPSCam().restoreViewModel()
            self.getViewModel().hide()
            self.sgViewModel.cleanup()
            self.sgViewModel.removeNode()
            self.sgViewModel = None
            
        return True
            
    def onSetAction(self, action):        
        if self.isFirstPerson():
            track = Sequence()
            vm = self.getViewModel()
            fpsCam = self.getFPSCam()
            if action == self.StateIdle:
                track.append(Func(vm.loop, "idle"))
            elif action == self.StateDraw:
                track.append(ActorInterval(vm, "draw"))
            elif action == self.StatePump:
                track.append(Func(self.pumpSound.play))
                track.append(ActorInterval(vm, "pump"))
            elif action == self.StateFire:
                fpsCam.addViewPunch(Vec3(random.uniform(-2, 2), random.uniform(2, 1), 0))
                track.append(Func(self.fireSound.play))
                track.append(ActorInterval(vm, "fire"))
            elif action == self.StateDblFire:
                fpsCam.addViewPunch(Vec3(0, random.uniform(-5, 5), 0))
                track.append(Func(self.dblFireSound.play))
                track.append(ActorInterval(vm, "altfire"))
            elif action == self.StateReload:
                sound = random.choice(self.reloadSounds)
                track.append(Func(sound.play))
                track.append(ActorInterval(vm, "reload2"))
            elif action == self.StateBeginReload:
                track.append(ActorInterval(vm, "reload1"))
            elif action == self.StateEndReload:
                track.append(ActorInterval(vm, "reload3"))
            fpsCam.setVMAnimTrack(track)
                
        

class HL2ShotgunAI(BaseHitscanAI, HL2ShotgunShared):

    Name = GagGlobals.HL2Shotgun
    ID = ATTACK_HL2SHOTGUN
    HasClip = True
    AttackRange = 10000
    FireDelay = 0.5
    
    def __init__(self):
        BaseHitscanAI.__init__(self)
        self.actionLengths.update({self.StatePump   :   0.666666666667,
                                   self.StateReload :   0.5,
                                   self.StateBeginReload    :   0.625,
                                   self.StateEndReload  :   0.541666666667,
                                   self.StateFire   :   0.416666666667,
                                   self.StateDblFire    :   0.625,
                                   self.StateDraw   :   0.916666666667})
        self.maxAmmo = 32
        self.ammo = 32
        self.maxClip = 6
        self.clip = 6
        self.needsPump = False

    def shouldGoToNextAction(self, complete):
        return ((complete) or
               (not complete and self.action == self.StatePump and
                self.getActionTime() >= self.FireDelay and self.nextAction == self.StateFire))
                                   
    def determineNextAction(self, completedAction):
        if completedAction in [self.StateFire, self.StateDblFire]:
            if self.clip <= 0 and self.ammo > 0:
                self.needsPump = True
                return self.StateBeginReload
            else:
                return self.StatePump
        elif completedAction == self.StateBeginReload:
            return self.StateReload
        elif completedAction == self.StateReload:
            self.clip += 1
            if self.clip < self.maxClip and self.clip < self.ammo:
                return self.StateReload
            else:
                return self.StateEndReload
        elif completedAction == self.StateEndReload:
            if self.needsPump:
                self.needsPump = False
                return self.StatePump
            else:
                return self.StateIdle
        elif completedAction == self.StateDraw:
            if self.clip <= 0:
                self.needsPump = True
                return self.StateBeginReload
            elif self.needsPump:
                self.needsPump = False
                return self.StatePump
            else:
                return self.StateIdle
                
        return self.StateIdle
        
    def onSetAction(self, action):
        print action
        if action == self.StateFire:
            self.takeAmmo(-1)
            self.clip -= 1
            
            self._doBulletTraceAndDamage(1)

        elif action == self.StateDblFire:
            self.takeAmmo(-2)
            self.clip -= 2

            self._doBulletTraceAndDamage(2)

    def canUseSecondary(self):
        return self.clip >= 2 and self.ammo >= 2 and self.action in [self.StateReload,
                                                                     self.StateIdle,
                                                                     self.StateBeginReload,
                                                                     self.StateEndReload,
                                                                     self.StatePump]
            
    def canUse(self):
        return self.hasClip() and self.hasAmmo() and self.action in [self.StateReload,
                                                                     self.StateIdle,
                                                                     self.StateBeginReload,
                                                                     self.StateEndReload,
                                                                     self.StatePump]

    def secondaryFirePress(self, data):
        if not self.canUseSecondary():
            return

        dg = PyDatagram(data)
        dgi = PyDatagramIterator(dg)
        self.traceOrigin = CIGlobals.getVec3(dgi)
        self.traceVector = CIGlobals.getVec3(dgi)
        self.setNextAction(self.StateDblFire)

    def reloadPress(self, data):
        if self.action == self.StateIdle and not self.isClipFull() and self.ammo > self.clip:
            self.setNextAction(self.StateBeginReload)
        
    def unEquip(self):
        if not BaseHitscanAI.unEquip(self):
            return False
            
        if self.action == self.StateFire:
            self.needsPump = True
            
        return True
        
