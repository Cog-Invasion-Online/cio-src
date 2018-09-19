from DistributedEntity import DistributedEntity
from src.coginvasion.gui.CutsceneGUI import CutsceneGUI

from direct.interval.IntervalGlobal import Sequence, Wait, Func, Parallel, LerpPosInterval, LerpHprInterval

from src.coginvasion.globals import CIGlobals

import random

class TestCutscene:

    def __init__(self, dcs):
        self.dcs = dcs
        self.ival = None

    def run(self):
        
        boss = base.bspLoader.getPyEntityByTargetName("groom_boss_suit")
        camera.reparentTo(boss)
        
        numGoons = 6
        
        goonWakeup = Parallel()
        for i in xrange(numGoons):
            delay = random.uniform(0.0, 0.5)
            goon = base.bspLoader.getPyEntityByTargetName("groom_goon_{0}".format(i))
            goonWakeup.append(Sequence(Wait(delay), Func(goon.wakeup)))
        
        bossTrack = Parallel(Sequence(Func(boss.setChat, "What's this?! How did a Toon get down here?"), Wait(3.5), Func(boss.setChat, "Goons, attack!!!")))
        camTrack = Sequence(Func(camera.setPos, 5, 20, 2), Func(camera.lookAt, boss, 0, 0, 4), Wait(5.5),
                            Func(camera.reparentTo, render), Func(camera.setPosHpr, 88 / 16.0, 2746 / 16.0, 127 / 16.0, 71 - 90, -10, 0))
        goonTrack = Sequence(Wait(5.5), goonWakeup)
        
        self.ival = Parallel(camTrack, bossTrack, goonTrack)
        self.ival.start()

    def stop(self):
        if self.ival:
            self.ival.pause()
            self.ival = None
        
    def cleanup(self):
        self.dcs = None

# cutsceneId -> cutscene impl class
id2impl = {
    "generatorRoomBegin"    :   TestCutscene
}

class DistributedCutscene(DistributedEntity):

    def __init__(self, cr):
        DistributedEntity.__init__(self, cr)
        self.cutsceneImpl = None
        self.gui = CutsceneGUI(barDur = 1.0, fov = CIGlobals.DefaultCameraFov * 1.1)

    def disable(self):
        self.endCutscene(False)
        if self.gui:
            self.gui.unload()
            self.gui = None
        DistributedEntity.disable(self)

    def doCutscene(self, cutsceneId):
        print "doCutscene:", cutsceneId
        impl = id2impl.get(cutsceneId, None)
        if not impl:
            return

        base.localAvatar.stopPlay()
        self.gui.enter()

        self.cutsceneImpl = impl(self)
        self.cutsceneImpl.run()

    def endCutscene(self, exitGui = True, startPlay = True):
        if self.cutsceneImpl:
            self.cutsceneImpl.stop()
            self.cutsceneImpl.cleanup()
            self.cutsceneImpl = None
        if exitGui:
            self.gui.exit()
        if startPlay:
            base.localAvatar.startPlay(gags = True, laff = True)