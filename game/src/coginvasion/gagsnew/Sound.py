from src.coginvasion.gagsnew.BaseGag import BaseGag
from src.coginvasion.attack.Attacks import ATTACK_HOLD_RIGHT, ATTACK_SOUND
from direct.interval.IntervalGlobal import Sequence, Wait, Func, ActorInterval, Parallel
from src.coginvasion.gags import GagGlobals

import random

class Sound(BaseGag):
    ModelPath = "phase_14/models/props/megaphone.bam"
    ModelScale = 1.0
    Hold = ATTACK_HOLD_RIGHT
    
    ModelVMOrigin = (0.21, 0.04, -0.04)
    ModelVMAngles = (95, 102.99, 85.43)
    
    Name = "Sound"
    ID = ATTACK_SOUND
    
    StateFire = 1
    
    AppearSounds = [GagGlobals.AOOGAH_APPEAR_SFX,
                    GagGlobals.FOG_APPEAR_SFX,
                    GagGlobals.ELEPHANT_APPEAR_SFX]
    SoundSounds = [GagGlobals.AOOGAH_SFX,
                   GagGlobals.FOG_SFX,
                   GagGlobals.ELEPHANT_SFX]
    
    def __init__(self):
        BaseGag.__init__(self)
        self.appearSfx = []
        self.soundSfx = []
        
    def load(self):
        BaseGag.load(self)
        for i in range(len(self.AppearSounds)):
            self.appearSfx.append(base.loadSfxOnNode(self.AppearSounds[i], self.avatar))
            self.soundSfx.append(base.loadSfxOnNode(self.SoundSounds[i], self.avatar))
        
    def cleanup(self):
        self.appearSfx = None
        self.soundSfx = None
        BaseGag.cleanup(self)
        
    def unEquip(self):
        if not BaseGag.unEquip(self):
            return False
            
        if self.isFirstPerson():
            fpsCam = self.getFPSCam()
            fpsCam.vmRoot2.setY(0.0)
    
    def onSetAction_firstPerson(self, action):
        vm = self.getViewModel()
        fpsCam = self.getFPSCam()
        vm.hide()
        if action == self.StateFire:
            sound = random.randint(0, len(self.appearSfx) - 1)
            appearSfx = self.appearSfx[sound]
            soundSfx = self.soundSfx[sound]
            fpsCam.setVMAnimTrack(Parallel(
                    Sequence(Func(fpsCam.vmRoot2.setY, 0.5), Wait(0.75), Func(vm.show),
                ActorInterval(vm, "sound"), Func(fpsCam.vmRoot2.setY, 0.0), Func(vm.hide)),
                
                Sequence(Wait(1.0), Func(appearSfx.play), Wait(1.5), Func(soundSfx.play))))
