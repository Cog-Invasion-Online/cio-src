"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file TNT.py
@author Maverick Liberty
@date July 08, 2015

"""

from direct.interval.IntervalGlobal import Sequence, Wait, Func, ActorInterval, Parallel
from direct.interval.SoundInterval import SoundInterval
from direct.actor.Actor import Actor

from src.coginvasion.globals import CIGlobals
from src.coginvasion.gags.TossTrapGag import TossTrapGag
from src.coginvasion.gags.GagState import GagState
from src.coginvasion.gags import GagGlobals
from src.coginvasion.toon import ParticleLoader
from PowerBar import PowerBar

class TNT(TossTrapGag):
        
    name = GagGlobals.TNT
    model = "phase_5/models/props/tnt-mod.bam"
    idleSfxPath = "phase_5/audio/sfx/TL_dynamite.ogg"
    hitSfxPath = "phase_3.5/audio/sfx/ENC_cogfall_apart.ogg"
    particlesFx = "phase_5/etc/tnt.ptf"
    anim = "phase_5/models/props/tnt-chan.bam"
    

    def __init__(self):
        TossTrapGag.__init__(self)
        self.maxDistance = GagGlobals.TNT_RANGE
        self.setImage('phase_3.5/maps/tnt.png')
        self.setRechargeTime(0.0)
        self.timeout = 2.5

        self.tntSound = None
        self.lightSound = None
        self.particle = None
        
        self.powerBar = None
        
    def startPowerBar(self):
        self.stopPowerBar()
        
        self.powerBar = PowerBar()
        self.powerBar.start()
        
    def stopPowerBar(self):
        if self.powerBar:
            self.powerBar.destroy()
        self.powerBar = None

    def unEquip(self):
        self.stopPowerBar()
        self.__cleanupFakeStuff()
        TossTrapGag.unEquip(self)

    def __doFakeStuff(self):
        self.__cleanupFakeStuff()

        self.lightSound = base.audio3d.loadSfx("phase_14/audio/sfx/tnt_snap.ogg")
        base.audio3d.attachSoundToObject(self.lightSound, self.getVMGag())
        self.lightSound.play()
        self.tntSound = base.audio3d.loadSfx("phase_14/audio/sfx/dynamite_loop.ogg")
        self.tntSound.setLoop(True)
        base.audio3d.attachSoundToObject(self.tntSound, self.getVMGag())
        self.tntSound.play()
        self.particle = ParticleLoader.loadParticleEffect("phase_14/etc/tnt_spark.ptf")
        self.particle.start(self.getVMGag().find('**/joint_attachEmitter'), CIGlobals.getParticleRender())

    def __cleanupFakeStuff(self):
        if self.lightSound:
            self.lightSound.stop()
        self.lightSound = None
        if self.tntSound:
            self.tntSound.stop()
        self.tntSound = None
        if self.particle:
            self.particle.softStop()
        self.particle = None

    def __actuallyThrow(self):
        self.__cleanupFakeStuff()
        self.getVMGag().hide()
        base.localAvatar.sendUpdate('createObjectForMe', [base.cr.dclassesByName['DistributedTNTOV'].getNumber()])
        base.localAvatar.sendUpdate('usedGag', [self.id])

    def start(self):
        if self.isLocal():
            self.startPowerBar()

    def throw(self):
        self.state = GagState.RELEASED
        
        if self.isLocal():
            if self.powerBar:
                self.powerBar.stop()
                self.powerBar.hide()
            self.startTimeout()
            if base.localAvatar.isFirstPerson():
                vm = self.getViewModel()
                cam = self.getFPSCam()
                #fps = 24.0
                #playRate = 1.0
                #snapTime = 13.0 / fps
                #throwTime = 29.0 / fps
                #cam.setVMAnimTrack(Parallel(ActorInterval(vm, "tnt_throw", playRate = playRate),
                #                            Sequence(Wait(snapTime / playRate), Func(self.__doFakeStuff)),
                #                            Sequence(Wait(throwTime / playRate), Func(self.__actuallyThrow))))
                cam.setVMAnimTrack(ActorInterval(vm, "tnt_throw", startFrame = 27))
            #else:
                #self.__actuallyThrow()
            self.__actuallyThrow()

        self.gag.hide()

        self.setAnimTrack(self.getAnimationTrack('toss', 60), startNow = True)

    def equip(self):
        TossTrapGag.equip(self)

        if not self.gag:
            self.build()

        self.gag.show()

        if self.isLocal():
            vm = self.getViewModel()
            cam = self.getFPSCam()
            cam.setVMGag(self.gag, pos = (-0.23, 0.26, 0.05), hpr = (321.45, 55.74, 120.67), scale = 0.5, animate = False)
            cam.setVMAnimTrack(Sequence(ActorInterval(vm, "tnt_draw"), Func(vm.loop, "tnt_idle")))

        self.doDrawAndHold('toss', 0, 30, 1.0, 30, 30, 1.0)
