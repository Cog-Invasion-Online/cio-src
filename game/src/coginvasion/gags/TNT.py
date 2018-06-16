"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file TNT.py
@author Maverick Liberty
@date July 08, 2015

"""

from src.coginvasion.gags.TossTrapGag import TossTrapGag
from src.coginvasion.gags.GagState import GagState
from src.coginvasion.gags import GagGlobals
from src.coginvasion.globals import CIGlobals
from direct.interval.IntervalGlobal import Sequence, Wait, Func, ActorInterval
from direct.interval.SoundInterval import SoundInterval
from direct.actor.Actor import Actor

class TNT(TossTrapGag):

    def __init__(self):
        TossTrapGag.__init__(self, CIGlobals.TNT, "phase_5/models/props/tnt-mod.bam", 180, "phase_3.5/audio/sfx/ENC_cogfall_apart.ogg",
                             "phase_5/audio/sfx/TL_dynamite.ogg", particlesFx="phase_5/etc/tnt.ptf", anim = "phase_5/models/props/tnt-chan.bam")
        self.maxDistance = GagGlobals.TNT_RANGE
        self.setImage('phase_3.5/maps/tnt.png')
        self.setRechargeTime(19.5)

    def start(self):
        pass

    def throw(self):
        if self.isLocal():
            base.localAvatar.sendUpdate('createObjectForMe', [base.cr.dclassesByName['DistributedTNTOV'].getNumber()])
            vm = self.getViewModel()
            cam = self.getFPSCam()
            cam.setVMAnimTrack(Func(vm.pose, "pie_draw", 0))

        self.gag.hide()
        self.setAnimTrack(self.getAnimationTrack('toss', 60), startNow = True)

    def equip(self):
        TossTrapGag.equip(self)

        if not self.gag:
            self.build()

        if self.isLocal():
            vm = self.getViewModel()
            cam = self.getFPSCam()
            cam.setVMGag(self.gag, pos = (-0.05, 0.05, 0), hpr = (0, -97.492, 0), scale = 0.5, animate = False)
            cam.setVMAnimTrack(Sequence(ActorInterval(vm, "pie_draw"), Func(vm.loop, "pie_idle")))

        self.doDrawAndHold('toss', 0, 30, 1.0, 30, 33, 1.0)
