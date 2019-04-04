from panda3d.core import Vec3

from direct.interval.IntervalGlobal import Sequence, ActorInterval, Func

from BaseGag import BaseGag
from WholeCreamPieShared import WholeCreamPieShared
from src.coginvasion.attack.Attacks import ATTACK_HOLD_RIGHT, ATTACK_GAG_WHOLECREAMPIE
from src.coginvasion.base.Precache import precacheSound
from src.coginvasion.gags import GagGlobals
from src.coginvasion.globals import CIGlobals

import random

class WholeCreamPie(BaseGag, WholeCreamPieShared):
    ModelPath = "phase_14/models/props/creampie.bam"
    ModelScale = 0.85
    Hold = ATTACK_HOLD_RIGHT

    Name = GagGlobals.WholeCreamPie
    ID = ATTACK_GAG_WHOLECREAMPIE

    ModelVMOrigin = (0.07, 0.17, -0.01)
    ModelVMAngles = (0, -100, -10)
    ModelVMScale = ModelScale * 0.567

    ReleaseSpeed = 1.0
    ReleasePlayRateMultiplier = 1.0
    BobStartFrame = 30
    BobEndFrame = 40
    BobPlayRateMultiplier = 0.25
    ThrowObjectFrame = 62
    FinalThrowFrame = 90

    ThrowSoundPath = "phase_3.5/audio/sfx/AA_pie_throw_only.ogg"

    def __init__(self):
        BaseGag.__init__(self)
        self.throwSound = None

    @classmethod
    def doPrecache(cls):
        super(WholeCreamPie, cls).doPrecache()
        precacheSound(cls.ThrowSoundPath)

    def getViewPunch(self):
        return Vec3(random.uniform(.5, 1), random.uniform(-.5, -1), 0)

    def addPrimaryPressData(self, dg):
        # Send our precise hand position to the server
        # so the pie launches from the correct spot.
        CIGlobals.putVec3(dg, self.avatar.getRightHandNode().getPos(render))
        CIGlobals.putVec3(dg, camera.getPos(render))
        CIGlobals.putVec3(dg, camera.getQuat(render).getForward())
        
    def load(self):
        BaseGag.load(self)
        self.throwSound = base.loadSfxOnNode(self.ThrowSoundPath, self.avatar)

    def cleanup(self):
        if self.throwSound:
            self.throwSound.stop()
            base.audio3d.detachSound(self.throwSound)
        self.throwSound = None
        
        BaseGag.cleanup(self)

    def __doDraw(self):
        self.doDrawNoHold('pie', 0, self.BobStartFrame, self.PlayRate)

    def __doHold(self):
        self.doHold('pie', self.BobStartFrame, self.BobEndFrame, self.PlayRate * self.BobPlayRateMultiplier)
        
    def onSetAction_firstPerson(self, action):        
        vm = self.getViewModel()
        vm.show()
        vmGag = self.getVMGag()
        vmGag.show()
        fpsCam = self.getFPSCam()

        if action == self.StateThrow:

            if self.throwSound:
                self.throwSound.play()

            vmGag.hide()
            fpsCam.setVMAnimTrack(Sequence(ActorInterval(vm, "tnt_throw", startFrame = 27),
                                           Func(vm.hide)))
            fpsCam.addViewPunch(self.getViewPunch())

        elif action == self.StateDraw:
            fpsCam.setVMAnimTrack(Sequence(ActorInterval(vm, "pie_draw")))

        elif action == self.StateIdle:
            fpsCam.setVMAnimTrack(Sequence(Func(vm.loop, "pie_idle")))

    def onSetAction(self, action):        

        self.model.show()

        if action == self.StateThrow:

            if self.throwSound:
                self.throwSound.play()

            self.model.hide()

            self.setAnimTrack(
                self.getAnimationTrack('pie', startFrame=self.ThrowObjectFrame,
                                       playRate=(self.PlayRate * self.ReleasePlayRateMultiplier)),
                startNow = True)

        elif action == self.StateDraw:
            self.__doDraw()

        elif action == self.StateIdle:
            self.__doHold()
