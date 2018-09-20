from DistributedEntity import DistributedEntity
from src.coginvasion.gui.CutsceneGUI import CutsceneGUI

from direct.interval.IntervalGlobal import Sequence, Wait, Func, Parallel, LerpPosInterval, LerpHprInterval, LerpPosHprInterval, ActorInterval

from src.coginvasion.globals import CIGlobals

import random

class TestCutscene:

    def __init__(self, dcs):
        self.dcs = dcs
        self.ival = None

    def run(self):
        
        boss = base.bspLoader.getPyEntityByTargetName("groom_boss_suit")
        boss.show()
        boss.cleanupPropeller()
        boss.animFSM.request('neutral')
        camera.reparentTo(boss)
        
        numGoons = 6
        
        goonWakeup = Parallel()
        for i in xrange(numGoons):
            delay = random.uniform(0.0, 0.5)
            goon = base.bspLoader.getPyEntityByTargetName("groom_goon_{0}".format(i))
            goonWakeup.append(Sequence(Wait(delay), Func(goon.wakeup)))
            
        bdoor = base.bspLoader.getPyEntityByTargetName("to_groom_botdoor")
        tdoor = base.bspLoader.getPyEntityByTargetName("to_groom_topdoor")
        
        bossTrack = Parallel(#Sequence(ActorInterval(boss, "pie"), Func(boss.loop, "neutral")),
                             Sequence(Func(boss.setChat, "This sewer has no room in its budget for Toons."), 
                                      Wait(5.5), Func(boss.setChat, "Goons, ATTACK!!!")))
        camTrack = Sequence(Func(camera.setPos, 2.5, 14, 7), Func(camera.lookAt, boss, 0, 0, 4), Wait(3.0),
                            Func(camera.reparentTo, render), Func(camera.setPosHpr, 4.351, 126.686, 5.5, -154.16, 16.11, 0),
                            Wait(0.3),
                            Func(bdoor.request, 'Closing'),
                            Func(tdoor.request, 'Closing'),
                            Wait(1.7),
                            Func(camera.reparentTo, boss),
                            Func(camera.setPos, 2.5, 17, 7), Func(camera.lookAt, boss, 0, 0, 4),
                            LerpPosHprInterval(camera, duration = 0.75, blendType = 'easeOut', pos = (1, 5, 4), hpr = (165, 20, 0)),
                            Wait(1.75),
                            Func(camera.reparentTo, render), Func(camera.setPosHpr, 88 / 16.0, 2746 / 16.0, 127 / 16.0, 71 - 90, -10, 0))
        goonTrack = Sequence(Wait(7.5), goonWakeup)
        
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
            
        self.dispatchOutput("OnBegin")

        base.localAvatar.stopPlay()
        base.localAvatar.loop("neutral")
        self.gui.enter()

        self.cutsceneImpl = impl(self)
        self.cutsceneImpl.run()

    def endCutscene(self, exitGui = True, startPlay = True):
        self.dispatchOutput("OnFinish")
        if self.cutsceneImpl:
            self.cutsceneImpl.stop()
            self.cutsceneImpl.cleanup()
            self.cutsceneImpl = None
        if exitGui:
            self.gui.exit()
        if startPlay:
            base.localAvatar.startPlay(gags = True, laff = True)