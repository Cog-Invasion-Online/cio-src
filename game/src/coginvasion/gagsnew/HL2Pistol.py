"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file HL2Pistol.py
@author Brian Lach
@date February 26, 2019

@desc Another easter egg

"""

from panda3d.core import Vec3, OmniBoundingVolume

from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence, Func, ActorInterval

from BaseHitscan import BaseHitscan
from HL2PistolShared import HL2PistolShared

from src.coginvasion.base.Precache import precacheSound, precacheActor
from src.coginvasion.gags import GagGlobals
from src.coginvasion.attack.Attacks import ATTACK_HOLD_RIGHT, ATTACK_HL2PISTOL

import random
    
class HL2Pistol(BaseHitscan, HL2PistolShared):
    
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
        BaseHitscan.__init__(self)
        
        self.sgViewModel = None 
        self.fireSound = base.audio3d.loadSfx(self.sgFirePath)
        self.emptySound = base.audio3d.loadSfx(self.sgEmptyPath)
        self.reloadSound = base.audio3d.loadSfx(self.sgReloadPath)
            
    @classmethod
    def doPrecache(cls):
        super(HL2Pistol, cls).doPrecache()
        
        precacheActor(cls.sgActorDef)
        
        precacheSound(cls.sgFirePath)
        precacheSound(cls.sgEmptyPath)
        precacheSound(cls.sgReloadPath)
            
    def equip(self):
        if not BaseHitscan.equip(self):
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
            elif action == self.StateReload:
                track.append(Func(self.reloadSound.play))
                track.append(ActorInterval(vm, "reload"))
            elif action == self.StateFire:
                fpsCam.resetViewPunch()
                fpsCam.addViewPunch(Vec3(random.uniform(-0.6, 0.6), random.uniform(-0.25, -0.5), 0.0))
                track.append(Func(self.fireSound.play))
                track.append(ActorInterval(vm, "fire"))
            fpsCam.setVMAnimTrack(track)
