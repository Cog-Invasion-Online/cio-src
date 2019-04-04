"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file Slap.py
@author CheezedFish
@date March 9, 2019

@desc Default melee gag, useful in a pinch

"""

from direct.interval.IntervalGlobal import Func, ActorInterval, Parallel

from BaseHitscan import BaseHitscan
from BaseHitscanShared import BaseHitscanShared

from src.coginvasion.base.Precache import precacheSound
from src.coginvasion.gags import GagGlobals
from src.coginvasion.attack.Attacks import ATTACK_SLAP
    
class Slap(BaseHitscan, BaseHitscanShared):
    Name = GagGlobals.Slap
    ID = ATTACK_SLAP
    
    slapFirePath = 'phase_14/audio/sfx/slap_swish.ogg'
    slapHitPath = 'phase_5/audio/sfx/SA_hardball_impact_only_alt.ogg'
    
    def __init__(self):
        BaseHitscan.__init__(self)
         
        self.fireSound = base.audio3d.loadSfx(self.slapFirePath)
        self.hitSound = base.audio3d.loadSfx(self.slapHitPath)
            
    @classmethod
    def doPrecache(cls):
        super(Slap, cls).doPrecache()
        
        precacheSound(cls.slapFirePath)
        precacheSound(cls.slapHitPath)
        
    def equip(self):
        if not BaseHitscan.equip(self):
            return False
            
        base.audio3d.attachSoundToObject(self.fireSound, self.avatar)

        if self.isFirstPerson():
            fpsCam = self.getFPSCam()
            vm = self.getViewModel()
            vm.show()
            fpsCam.setVMAnimTrack(Func(vm.loop, 'slap_idle'))

        return True
        
    def unEquip(self):
        if not BaseHitscan.unEquip(self):
            return False
            
        base.audio3d.detachSound(self.fireSound)
        
        return True
        
    def onSetAction_firstPerson(self, action):
        fpsCam = self.getFPSCam()
        vm = self.getViewModel()

        if action == self.StateFire:
            fpsCam.addViewPunch(self.getViewPunch())
            fpsCam.setVMAnimTrack(Parallel(Func(self.fireSound.play), ActorInterval(vm, 'slap_hit')))

        elif action == self.StateIdle:
            fpsCam.setVMAnimTrack(Func(vm.loop, 'slap_idle'))
            
        elif action == self.StateDraw:
            fpsCam.setVMAnimTrack(Func(vm.play, 'slap_idle'))
            
    def onSetAction(self, action):

        if action == self.StateFire:
            self.fireSound.play()
            self.doDrawNoHold('toss', 0, 30)

        elif action == self.StateIdle:
            self.doHold('toss', 30, 30, 1.0)
            
        elif action == self.StateDraw:
            self.doHold('toss', 30, 30, 1.0)
