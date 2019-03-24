from panda3d.core import Vec3

from BaseHitscan import BaseHitscan
from src.coginvasion.attack.Attacks import ATTACK_GUMBALLBLASTER, ATTACK_HOLD_LEFT
from src.coginvasion.gags import GagGlobals
from src.coginvasion.base.Precache import precacheSound
from src.coginvasion.globals import CIGlobals

from direct.interval.IntervalGlobal import ActorInterval, Func

import random

class GumballBlaster(BaseHitscan):
    ID = ATTACK_GUMBALLBLASTER
    Name = GagGlobals.GumballBlaster
    Hold = ATTACK_HOLD_LEFT

    ModelPath = "phase_14/models/props/gumballShooter.bam"
    ModelVMOrigin = (-0.53, 0.28, 0.52)
    ModelVMAngles = (72.68, 350.58, 351.82)
    ModelVMScale = 0.169

    FireSoundPath = "phase_14/audio/sfx/gumball_fire.ogg"

    AutoFireDelay = 0.1

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

    def think(self):
        if not self.isLocal():
            return

        now = globalClock.getFrameTime()
        if self.firing and now - self.lastFire > self.AutoFireDelay:
            self.primaryFirePress()

    def addPrimaryPressData(self, dg):
        BaseHitscan.addPrimaryPressData(self, dg)
        CIGlobals.putVec3(dg, self.getVMGag().find("**/Emitter1").getPos(render))

    def primaryFirePress(self, data = None):
        self.firing = True
        self.lastFire = globalClock.getFrameTime()
        BaseHitscan.primaryFirePress(self, data)

    def primaryFireRelease(self, data = None):
        self.firing = False
        BaseHitscan.primaryFireRelease(self, data)

    def equip(self):
        if not BaseHitscan.equip(self):
            return False

        if self.isFirstPerson():
            self.getFPSCam().setViewModelFOV(54.0)
            balls = loader.loadModel("phase_14/models/props/gumballShooter_balls.bam")
            balls.reparentTo(self.getVMGag())
            for gumball in balls.findAllMatches("**/+GeomNode"):
                gumball.setColorScale(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), 1.0, 1)
            balls.flattenStrong()

        base.audio3d.attachSoundToObject(self.fireSound, self.avatar)
    
        return True

    def unEquip(self):
        if not BaseHitscan.unEquip(self):
            return False

        if self.isFirstPerson():
            self.getFPSCam().restoreViewModelFOV()

            if self.vmSpinNode:
                self.vmSpinNode.detachNode()
                self.vmSpinNode = None

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

        if self.isFirstPerson():
            fpsCam = self.getFPSCam()
            vm = self.getViewModel()

            if action == self.StateIdle:
                fpsCam.setVMAnimTrack(Func(vm.loop, "gumball_idle"))
            elif action == self.StateDraw:
                fpsCam.setVMAnimTrack(ActorInterval(vm, "gumball_draw"))
            elif action == self.StateFire:
                fpsCam.addViewPunch(Vec3(random.uniform(-0.5, 0.5), random.uniform(1, 2), 0.0))
                fpsCam.setVMAnimTrack(ActorInterval(vm, "gumball_fire"))
                if self.vmSpinNode:
                    self.vmSpinNode.hprInterval(0.5, (0, 0, 360), (0, 0, 0)).play()
