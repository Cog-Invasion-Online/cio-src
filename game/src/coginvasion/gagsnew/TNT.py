from panda3d.core import Vec3
from direct.interval.IntervalGlobal import ActorInterval, Func

from BaseGag import BaseGag
from TNTShared import TNTShared
from src.coginvasion.attack.Attacks import ATTACK_GAG_TNT, ATTACK_HOLD_RIGHT
from src.coginvasion.gags import GagGlobals
from src.coginvasion.globals import CIGlobals

import random

class TNT(BaseGag, TNTShared):
    ID = ATTACK_GAG_TNT
    Name = GagGlobals.TNT

    ModelPath = "phase_14/models/props/tnt.bam"
    Hold = ATTACK_HOLD_RIGHT

    ModelVMOrigin = (-0.23, 0.26, 0.05)
    ModelVMAngles = (321.45, 55.74, 120.67)
    ModelVMScale = 0.5

    def getViewPunch(self):
        return Vec3(random.uniform(.5, 1), random.uniform(-.5, -1), 0)

    def addPrimaryPressData(self, dg):
        CIGlobals.putVec3(dg, self.avatar.getRightHandNode().getPos(render))
        CIGlobals.putVec3(dg, camera.getPos(render))
        CIGlobals.putVec3(dg, camera.getQuat(render).getForward())
        
    def onSetAction_firstPerson(self, action):
        fpsCam = self.getFPSCam()
        vm = self.getViewModel()
        vmGag = self.getVMGag()
        vmGag.show()

        if action == self.StateDraw:
            fpsCam.setVMAnimTrack(ActorInterval(vm, 'tnt_draw'))

        elif action == self.StateIdle:
            fpsCam.setVMAnimTrack(Func(vm.loop, 'tnt_idle'))
            
        elif action == self.StateThrow:
            vmGag.hide()
            fpsCam.addViewPunch(self.getViewPunch())
            fpsCam.setVMAnimTrack(ActorInterval(vm, 'tnt_throw', startFrame = 27))

    def onSetAction(self, action):

        if action == self.StateDraw:
            self.doDrawNoHold('toss', 0, 30)

        elif action == self.StateIdle:
            self.doHold('toss', 30, 30, 1.0)

        elif action == self.StateThrow:
            self.setAnimTrack(self.getAnimationTrack('toss', 60), startNow = True)
