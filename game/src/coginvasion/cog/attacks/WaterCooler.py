from panda3d.core import Point3

from direct.interval.IntervalGlobal import Parallel, Sequence, LerpScaleInterval, SoundInterval, Wait, Func

from src.coginvasion.attack.BaseAttack import BaseAttack
from src.coginvasion.attack.Attacks import ATTACK_HOLD_LEFT, ATTACK_WATER_COOLER
from src.coginvasion.cog.attacks.WaterCoolerShared import WaterCoolerShared
from src.coginvasion.base.Precache import precacheSound, precacheModel
from src.coginvasion.globals import CIGlobals

class WaterCooler(BaseAttack, WaterCoolerShared):
    ModelPath = "phase_5/models/props/watercooler.bam"
    ModelOrigin = Point3(0.48, 0.11, -0.92)
    ModelAngles = Point3(20.403, 33.158, 69.511)
    Hold = ATTACK_HOLD_LEFT
    
    Name = "Water Cooler"
    ID = ATTACK_WATER_COOLER
    
    SprayOnlyPath = "phase_5/audio/sfx/SA_watercooler_spray_only.ogg"
    CoolerAppearPath = "phase_5/audio/sfx/SA_watercooler_appear_only.ogg"
    SprayPath = "phase_3.5/models/props/spray.bam"
    
    def __init__(self):
        BaseAttack.__init__(self)
        self.sprayOnlySfx = None
        self.coolerAppearSfx = None
        self.sprayMdl = None
        self.splash = None
        
    @classmethod
    def doPrecache(cls):
        super(WaterCooler, cls).doPrecache()
        precacheSound(cls.SprayOnlyPath)
        precacheSound(cls.CoolerAppearPath)
        precacheModel(cls.SprayPath)
    
    def equip(self):
        if not BaseAttack.equip(self):
            return False
        
        if not self.sprayOnlySfx:
            self.sprayOnlySfx = base.loadSfxOnNode(self.SprayOnlyPath, self.avatar)
        
        if not self.coolerAppearSfx:
            self.coolerAppearSfx = base.loadSfxOnNode(self.CoolerAppearPath, self.avatar)
            
        if not self.sprayMdl:
            self.sprayMdl = loader.loadModel(self.SprayPath)
            self.sprayMdl.setTransparency(1)
            self.sprayMdl.setColor(0.75, 0.75, 1.0, 0.8)
            self.sprayMdl.setScale(0.3, 1.0, 0.3)
            self.sprayMdl.setLightOff()
            self.sprayMdl.reparentTo(self.model.find('**/joint_toSpray'))
            self.sprayMdl.hide()
            
        if not self.splash:
            self.splash = CIGlobals.makeSplat(Point3(0), (0.75, 0.75, 1.0, 0.8), 0.3, None)
            
        return True
            
    def unEquip(self):
        if not BaseAttack.unEquip(self):
            return False
        
        self.avatar.doingActivity = False
        
        return True

    def onSetAction(self, action):
        self.model.show()
        self.model.setPos(self.ModelOrigin)
        self.model.setHpr(self.ModelAngles)
        self.model.setLightOff()
        
        self.avatar.doingActivity = False
        
        if action == self.StateAttack:
            self.avatar.doingActivity = True
            
            joint = self.model.find('**/joint_toSpray')
            
            def positionAndOrientSpray():
                self.sprayMdl.setPos(joint.getPos(render))
                self.sprayMdl.setHpr(joint.getHpr(render))
            
            self.setAnimTrack(
                Parallel(
                    self.getAnimationTrack('watercooler', fullBody = False),
                    Sequence(
                        Wait(1.01),
                        Func(self.model.show),
                        LerpScaleInterval(self.model, 0.5, Point3(1.15, 1.15, 1.15)),
                        Wait(1.6),
                        Func(self.sprayMdl.show),
                        Func(self.sprayMdl.reparentTo, render),
                        Func(positionAndOrientSpray),
                        LerpScaleInterval(self.sprayMdl, duration = 0.3, scale = (1.0, 15.0, 1.0), startScale = (1.0, 1.0, 1.0)),
                        Func(self.sprayMdl.hide),
                        Func(self.sprayMdl.reparentTo, hidden)
                    ),
                    Sequence(
                        Wait(1.1),
                        SoundInterval(self.coolerAppearSfx, duration = 1.4722),
                        Wait(0.4),
                        SoundInterval(self.sprayOnlySfx, duration = 2.313)
                    )
                )
            , startNow = True)
    
    def cleanup(self):
        if hasattr(self, 'sprayOnlySfx') and self.sprayOnlySfx:
            base.audio3d.detachSound(self.sprayOnlySfx)
            del self.sprayOnlySfx
            
        if hasattr(self, 'coolerAppearSfx') and self.coolerAppearSfx:
            base.audio3d.detachSound(self.coolerAppearSfx)
            del self.coolerAppearSfx
        
        if hasattr(self, 'sprayMdl'):
            if self.sprayMdl:
                self.sprayMdl.removeNode()
            del self.sprayMdl
        
        if hasattr(self, 'splash') and self.splash:
            self.splash.cleanup()
            del self.splash
            
        BaseAttack.cleanup(self)
