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

from src.coginvasion.phys.LocalTNT import LocalTNT

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
            tnt = LocalTNT(self, base.cr)
            tnt.doId = 0
            tnt.dclass = base.cr.dclassesByName['DistributedTNT']
            tnt.generateInit()
            tnt.generate()
            tnt.announceGenerate()
            tnt.postGenerateMessage()
            base.cr.myDistrict.d_spawnTemporaryObject(tnt, tnt.ownershipGranted)
            tnt.setPos(self.avatar.find("**/def_joint_right_hold").getPos(render))
            tnt.toss()

            vm = self.getViewModel()
            cam = self.getFPSCam()
            cam.setVMAnimTrack(Func(vm.pose, "pie_draw", 0))

    def equip(self):
        TossTrapGag.equip(self)
        if self.isLocal():
            vm = self.getViewModel()
            cam = self.getFPSCam()
            cam.setVMGag(self.gag, scale = 0.5, animate = False)
            cam.setVMAnimTrack(Sequence(ActorInterval(vm, "pie_draw"), Func(vm.loop, "pie_idle")))

    def activate(self, node):
        for obj in base.cr.doId2do.values():
            if obj.__class__.__name__ in CIGlobals.SuitClasses:
                if obj.getPlace() == base.localAvatar.zoneId:
                    dist = obj.getDistance(node)
                    if dist <= self.maxDistance:
                        obj.sendUpdate('hitByGag', [self.getID(), dist])
