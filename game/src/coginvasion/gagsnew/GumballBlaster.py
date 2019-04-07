from panda3d.core import Vec3

from BaseHitscan import BaseHitscan
from src.coginvasion.attack.Attacks import ATTACK_GUMBALLBLASTER, ATTACK_HOLD_RIGHT
from src.coginvasion.gags import GagGlobals
from src.coginvasion.base.Precache import precacheSound, precacheModel
from src.coginvasion.globals import CIGlobals

from direct.interval.IntervalGlobal import ActorInterval, Func

import random

class GumballBlaster(BaseHitscan):
    ID = ATTACK_GUMBALLBLASTER
    Name = GagGlobals.GumballBlaster
    Hold = ATTACK_HOLD_RIGHT

    ModelPath = "phase_14/models/props/gumballShooter.bam"
    ModelVMOrigin = (-0.53, 0.28, 0.52)
    ModelVMAngles = (72.68, 350.58, 351.82)
    ModelVMScale = 0.169
    
    ModelOrigin = (-0.57, 1.01, 0.30)
    ModelScale = ModelVMScale
    ModelAngles = (60.0, 0.0, 90.0)

    FireSoundPath = "phase_14/audio/sfx/gumball_fire.ogg"
    BallsModelPath = "phase_14/models/props/gumballShooter_balls.bam"

    AutoFireDelay = 0.1

    def __init__(self):
        BaseHitscan.__init__(self)

        self.firing = False
        self.lastFire = 0.0
        self.vmSpinNode = None

        self.fireSound = base.audio3d.loadSfx(self.FireSoundPath)
        self.balls = None

    @classmethod
    def doPrecache(cls):
        super(GumballBlaster, cls).doPrecache()
        precacheSound(cls.FireSoundPath)
        precacheModel(cls.BallsModelPath)

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
            model = self.getVMGag()
        
        CIGlobals.putVec3(dg, model.find('**/Emitter1').getPos(render))

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
        
        parent = self.model

        if self.isFirstPerson():
            parent = self.getVMGag()
            self.getFPSCam().setViewModelFOV(54.0)
        
        self.balls = loader.loadModel(self.BallsModelPath)
        self.balls.reparentTo(parent)
        self.adjustBalls(self.ammo, self.ammo, adjustColors=True)

        # I'm not sure if you can change the color after you flatten geom nodes, so this line is commented out.
        # self.balls.flattenStrong()

        base.audio3d.attachSoundToObject(self.fireSound, self.avatar)
        
        self.doDrawAndHold('squirt', 0, 43, 1.0, 43, 43)
    
        return True

    def unEquip(self):
        if not BaseHitscan.unEquip(self):
            return False

        if self.isFirstPerson():
            self.getFPSCam().restoreViewModelFOV()

            if self.vmSpinNode:
                self.vmSpinNode.detachNode()
                self.vmSpinNode = None
                
        if self.balls:
            self.balls.removeNode()
            self.balls = None

        base.audio3d.detachSound(self.fireSound)

        return True
    
    def adjustBalls(self, lastAmmo, newAmmo, adjustColors=False):
        if not self.balls: return

        if not self.hasAmmo():
            self.balls.hide()
            return
        
        if(lastAmmo <= 0 and newAmmo > 0):
            adjustColors = True
        
        self.balls.show()
        
        gumballs = self.balls.findAllMatches("**/+GeomNode")
        ballsToShow = int((float(newAmmo) / float(self.getMaxAmmo())) * len(gumballs))
        
        if (ballsToShow > len(gumballs)):
            ballsToShow = len(gumballs)
        
        for i, gumball in enumerate(gumballs):
            if adjustColors:
                gumball.setColorScale(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), 1.0, 1)

            if (i + 1) <= ballsToShow:
                gumball.show()
            else:
                gumball.hide()
                
    def setAmmo(self, ammo):
        curAmmo = self.ammo
        BaseHitscan.setAmmo(self, ammo)
        self.adjustBalls(curAmmo, self.ammo, adjustColors=False)

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
