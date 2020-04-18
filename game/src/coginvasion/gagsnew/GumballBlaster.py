from panda3d.core import Vec3, VBase4

from BaseHitscan import BaseHitscan
from src.coginvasion.attack.Attacks import ATTACK_GUMBALLBLASTER, ATTACK_HOLD_LEFT, ATTACK_HOLD_RIGHT
from src.coginvasion.gags import GagGlobals
from src.coginvasion.base.Precache import precacheSound, precacheModel, precacheOther
from src.coginvasion.globals import CIGlobals

from direct.interval.IntervalGlobal import ActorInterval, Func

import random

class GumballBlaster(BaseHitscan):
    ID = ATTACK_GUMBALLBLASTER
    Name = GagGlobals.GumballBlaster
    Hold = ATTACK_HOLD_LEFT

    ModelPath = "phase_14/models/props/gumballShooter.bam"
    
    ModelOrigin = (-0.57, 1.01, 0.30)
    ModelScale = 0.169
    ModelAngles = (60.0, 0.0, 90.0)

    FireSoundPath = "phase_14/audio/sfx/gumball_fire.ogg"
    BallsModelPath = "phase_14/models/props/gumballShooter_balls.bam"

    AutoFireDelay = 0.1

    SpecialVM = True
    gbDir = "phase_14/models/weapons/v_gumball_launcher/"
    SpecialVMActor = [gbDir + "v_gumball_launcher.bam",
                      {"gumball_idle": gbDir + "v_gumball_launcher-gumball_idle.bam",
                       "gumball_draw": gbDir + "v_gumball_launcher-gumball_draw.bam",
                       "gumball_fire": gbDir + "v_gumball_launcher-gumball_fire.bam"}]
    SpecialVMFov = 54.0
    SpecialVMAngles = (180, 0, 0)
    SpecialVMOrigin = (0, -9 / 16.0, 0)
    SpecialVMScale = 0.625

    def __init__(self):
        BaseHitscan.__init__(self)

        self.firing = False
        self.lastFire = 0.0
        self.vmSpinNode = None

        self.fireSound = base.audio3d.loadSfx(self.FireSoundPath)

    @classmethod
    def doPrecache(cls):
        super(GumballBlaster, cls).doPrecache()
        precacheSound(cls.FireSoundPath)
        
        precacheOther("GumballProjectile", "src.coginvasion.gagsnew.GumballProjectile")

    def think(self):
        if not self.isLocal():
            return

        now = globalClock.getFrameTime()
        if self.firing and now - self.lastFire > self.AutoFireDelay:
            self.primaryFirePress()

    def addPrimaryPressData(self, dg):
        BaseHitscan.addPrimaryPressData(self, dg)
        
        model = self.model
        if self.isFirstPerson():
            model = self.specialViewModel
        
        CIGlobals.putVec3(dg, model.find('**/Emitter1').getPos(render))

    def primaryFirePress(self, data = None):
        self.firing = True
        self.lastFire = globalClock.getFrameTime()
        BaseHitscan.primaryFirePress(self, data)

    def primaryFireRelease(self, data = None):
        self.firing = False
        BaseHitscan.primaryFireRelease(self, data)
        
    def load(self):
        BaseHitscan.load(self)

        if self.isFirstPerson():
            self.specialViewModel.exposeJoint(None, "modelRoot", "def_weapon_muzzle")
            self.specialViewModel.find("**/def_weapon_muzzle").setName("Emitter1")

            self.specialViewModel.find("**/gumball0").setColorScale((1, 0, 0, 1), 1)
            self.specialViewModel.find("**/gumball1").setColorScale((0, 0, 1, 1), 1)
            self.specialViewModel.find("**/gumball2").setColorScale((0, 1, 0, 1), 1)
            self.specialViewModel.find("**/gumball3").setColorScale((1, 0, 1, 1), 1)
            self.specialViewModel.find("**/gumball4").setColorScale((0, 1, 1, 1), 1)
            self.specialViewModel.find("**/gumball5").setColorScale((1, 1, 0, 1), 1)
            self.specialViewModel.flattenStrong()

    def equip(self):
        if not self.isLocal() or not self.isFirstPerson():
            self.Hold = ATTACK_HOLD_RIGHT

        if not BaseHitscan.equip(self):
            return False
        
        base.audio3d.attachSoundToObject(self.fireSound, self.avatar)
        
        self.doDrawAndHold('squirt', 0, 43, 1.0, 43, 43)
    
        return True
        

    def unEquip(self):
        if not BaseHitscan.unEquip(self):
            return False

        if self.isFirstPerson():

            if self.vmSpinNode:
                self.vmSpinNode.detachNode()
                self.vmSpinNode = None

        if self.fireSound:
            base.audio3d.detachSound(self.fireSound)

        return True

    def cleanup(self):
        self.firing = None
        self.lastFire = None
        self.fireSound = None
        self.vmSpinNode = None
        BaseHitscan.cleanup(self)
        
    def onSetAction(self, action):
        if action == self.StateFire:
            self.fireSound.play()

    def onSetAction_firstPerson(self, action):
        fpsCam = self.getFPSCam()
        vm = self.getViewModel()

        if action == self.StateIdle:
            fpsCam.setVMAnimTrack(Func(vm.loop, "gumball_idle"))
        elif action == self.StateDraw:
            fpsCam.setVMAnimTrack(ActorInterval(vm, "gumball_draw"))
        elif action == self.StateFire:
            self.fireSound.play()
            fpsCam.addViewPunch(Vec3(random.uniform(-0.5, 0.5), random.uniform(1, 2), 0.0))
            fpsCam.setVMAnimTrack(ActorInterval(vm, "gumball_fire"))
            if self.vmSpinNode:
                self.vmSpinNode.hprInterval(0.5, (0, 0, 360), (0, 0, 0)).play()
