from panda3d.core import Point3, VBase3

from direct.interval.IntervalGlobal import Parallel, Sequence, Wait, Func
from direct.interval.IntervalGlobal import LerpScaleInterval, LerpHprInterval

from src.coginvasion.attack.BaseAttack import BaseAttack
from src.coginvasion.cog.attacks import EvilEyeShared
from src.coginvasion.attack.Attacks import ATTACK_HOLD_NONE, ATTACK_EVIL_EYE
from src.coginvasion.base.Precache import precacheSound

class EvilEye(BaseAttack):
    Hold = ATTACK_HOLD_NONE
    
    #Name = "Evil-Eye"
    #ID = ATTACK_EVIL_EYE
    #ModelPath = "phase_5/models/props/evil-eye.bam"
    #ModelScale = 11.0
    
    HoldStart = 1.06
    HoldStop = 1.69
    HoldDuration = HoldStop - HoldStart
    EyeHoldDuration = 1.1
    MoveDuration = 1.0
    
    EyeSoundPath = "phase_5/audio/sfx/SA_evil_eye.ogg"
    
    def __init__(self):
        for key in EvilEyeShared.__dict__.keys():
            setattr(self, key, EvilEyeShared.__dict__.get(key))
        print self.Name
        BaseAttack.__init__(self)
        self.eyeSfx = None
        self.eyeRoot = None
        
    def load(self):
        self.eyeRoot = self.avatar.attachNewNode('eyeRoot')
        self.eyeRoot.setPos(self.EyeOrigin)
        
        BaseAttack.load(self)
        
    @classmethod
    def doPrecache(cls):
        super(EvilEye, cls).doPrecache()
        precacheSound(cls.EyeSoundPath)
    
    def equip(self):
        if not BaseAttack.equip(self):
            return False
        
        if not self.eyeSfx:
            self.eyeSfx = base.loadSfxOnNode(self.EyeSoundPath, self.avatar)
        
        return True
    
    def unEquip(self):
        if not BaseAttack.unEquip(self):
            return False
        
        self.avatar.doingActivity = False
        
        return True
    
    def cleanup(self):
        if hasattr(self, 'eyeSfx'):
            base.audio3d.detachSound(self.eyeSfx)
            del self.eyeSfx
        
        if hasattr(self, 'eyeRoot'):
            self.eyeRoot.removeNode()
            del self.eyeRoot
        
        BaseAttack.cleanup(self)
    
    def onSetAction(self, action):
        self.model.show()
        self.model.reparentTo(self.eyeRoot)
        self.model.setHpr(VBase3(-155.0, -20.0, 0.0))
        self.model.setLightOff()
        
        self.avatar.doingActivity = False
        
        if action == self.StateThrow:
            self.avatar.doingActivity = True
            
            eyeTrack = Sequence(
                Wait(self.HoldStart),
                LerpScaleInterval(self.model, self.HoldDuration, Point3(self.ModelScale), startScale = 0.01),
                Wait(self.EyeHoldDuration * 0.3),
                LerpHprInterval(self.model, 0.02, Point3(205, 40, 0)),
                Wait(self.EyeHoldDuration * 0.7),
                Func(self.model.hide)
            )
            
            self.setAnimTrack(
                Parallel(
                    Sequence(Wait(1.3), Func(self.eyeSfx.play)),
                    Sequence(
                        self.getAnimationTrack('glower', endTime = self.HoldStart, fullBody = False),
                        Wait(self.HoldDuration),
                        self.getAnimationTrack('glower', startTime = self.HoldStart, fullBody = False)
                    ),
                    eyeTrack
                )
            , startNow = True)
