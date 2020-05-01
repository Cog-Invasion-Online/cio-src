"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file HL2Shotgun.py
@author Brian Lach
@date February 24, 2019

@desc Easter egg! Shotgun from Half-Life 2. I wanted to see how easy it
      would be to port it over to Panda since our material system is
      almost identical to Source. It was easy.

"""

from panda3d.core import Vec3, OmniBoundingVolume

from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence, Func, ActorInterval

from BaseHitscan import BaseHitscan
from HL2ShotgunShared import HL2ShotgunShared

from src.coginvasion.base.Precache import precacheSound, precacheActor, precacheModel
from src.coginvasion.globals import CIGlobals
from src.coginvasion.gags import GagGlobals
from src.coginvasion.attack.Attacks import ATTACK_HOLD_RIGHT, ATTACK_HL2SHOTGUN

import random
    
class HL2Shotgun(BaseHitscan, HL2ShotgunShared):
    
    ModelPath = "phase_14/hl2/w_shotgun/w_shotgun.bam"
    ModelOrigin = (-0.03, 1.19, -0.14)
    ModelAngles = (2.29, 347.01, 45)
    ModelScale = 2
    
    Name = GagGlobals.HL2Shotgun
    ID = ATTACK_HL2SHOTGUN
    Hold = ATTACK_HOLD_RIGHT
    
    ShellPath = "phase_14/hl2/casing.bam"
    ShellContactSoundPath = "phase_14/hl2/shell{0}.wav"
    ShellContactSoundRange = (1, 3)
    
    sgFirePath = 'phase_14/hl2/v_shotgun/shotgun_fire7.wav'
    sgEmptyPath = 'phase_14/hl2/v_shotgun/shotgun_empty.wav'
    sgDblFirePath = 'phase_14/hl2/v_shotgun/shotgun_dbl_fire7.wav'
    sgPumpPath = 'phase_14/hl2/v_shotgun/shotgun_cock.wav'
    sgReloadPaths = ['phase_14/hl2/v_shotgun/shotgun_reload1.wav',
                     'phase_14/hl2/v_shotgun/shotgun_reload2.wav',
                     'phase_14/hl2/v_shotgun/shotgun_reload3.wav']

    SpecialVM = True
    SpecialVMCull = False
    sgDir = 'phase_14/hl2/v_shotgun/panda/opt/'
    SpecialVMActor = [sgDir + 'v_shotgun.bam',
	    {'draw': sgDir + 'v_shotgun-draw.egg',
	     'idle': sgDir + 'v_shotgun-idle01.egg',
	     'pump': sgDir + 'v_shotgun-pump.egg',
	     'fire': sgDir + 'v_shotgun-fire01.egg',
	     'altfire': sgDir + 'v_shotgun-altfire.egg',
	     'reload1': sgDir + 'v_shotgun-reload1.egg',
	     'reload2': sgDir + 'v_shotgun-reload2.egg',
	     'reload3': sgDir + 'v_shotgun-reload3.egg'}]
    SpecialVMFov = 54.0
    SpecialVMAngles = (180, 0, 0)
    
    def __init__(self):
        BaseHitscan.__init__(self)
        self.fireSound = base.audio3d.loadSfx(self.sgFirePath)
        self.dblFireSound = base.audio3d.loadSfx(self.sgDblFirePath)
        self.pumpSound = base.audio3d.loadSfx(self.sgPumpPath)
        self.emptySound = base.audio3d.loadSfx(self.sgEmptyPath)
        self.reloadSounds = []
        for rl in self.sgReloadPaths:
            self.reloadSounds.append(base.audio3d.loadSfx(rl))
            
        self.fpMuzzleAttach = None
            
    @classmethod
    def doPrecache(cls):
        super(HL2Shotgun, cls).doPrecache()
        
        precacheSound(cls.sgFirePath)
        precacheSound(cls.sgDblFirePath)
        precacheSound(cls.sgPumpPath)
        precacheSound(cls.sgEmptyPath)
        for rl in cls.sgReloadPaths:
            precacheSound(rl)
            
        precacheModel(cls.ShellPath)
        for i in xrange(cls.ShellContactSoundRange[0], cls.ShellContactSoundRange[1] + 1):
            precacheSound(cls.ShellContactSoundPath.format(i))
            
    def addPrimaryPressData(self, dg):
        CIGlobals.putVec3(dg, camera.getPos(render))
        CIGlobals.putVec3(dg, camera.getQuat(render).getForward())

    def addSecondaryPressData(self, dg):
        self.addPrimaryPressData(dg)
            
    def __doBob(self):
        self.setAnimTrack(self.getBobSequence('firehose', 30, 30, 1.0), startNow = True, looping = True)
        
    def cleanup(self):        
        self.fpMuzzleAttach = None
        
        if self.fireSound:
            base.audio3d.detachSound(self.fireSound)
        self.fireSound = None
        
        if self.dblFireSound:
            base.audio3d.detachSound(self.dblFireSound)
        self.dblFireSound = None
        
        if self.pumpSound:
            base.audio3d.detachSound(self.pumpSound)
        self.pumpSound = None
        
        if self.emptySound:
            base.audio3d.detachSound(self.emptySound)
        self.emptySound = None
        
        if self.reloadSounds:
            for snd in self.reloadSounds:
                base.audio3d.detachSound(snd)
        self.reloadSounds = None
        
        BaseHitscan.cleanup(self)
        
    def load(self):
        BaseHitscan.load(self)
        
        base.audio3d.attachSoundToObject(self.fireSound, self.avatar)
        base.audio3d.attachSoundToObject(self.dblFireSound, self.avatar)
        base.audio3d.attachSoundToObject(self.pumpSound, self.avatar)
        base.audio3d.attachSoundToObject(self.emptySound, self.avatar)
        for s in self.reloadSounds:
            base.audio3d.attachSoundToObject(s, self.avatar)
            
    def equip(self):
        if not BaseHitscan.equip(self):
            return False
            
        if self.isFirstPerson():
            self.fpMuzzleAttach = self.specialViewModel.exposeJoint(None, "modelRoot", "ValveBiped.Gun")
            
        toonTrack = Sequence(Func(self.avatar.setForcedTorsoAnim, 'firehose'),
                         self.getAnimationTrack('firehose', endFrame = 30),
                         Func(self.__doBob))
        self.setAnimTrack(toonTrack, startNow = True)
            
        return True
        
    def unEquip(self):
        if not BaseHitscan.unEquip(self):
            return False
            
        if self.isFirstPerson():
            self.specialViewModel.releaseJoint("modelRoot", "ValveBiped.Gun")
            self.fpMuzzleAttach.removeNode()
            
        return True

    def __emitShell(self):
        def __shellThink(shell, task):
            if task.time > 3.0:
                base.physicsWorld.remove(shell.node())
                shell.removeNode()
                return task.done
            
            if not hasattr(task, 'didHitNoise'):
                task.didHitNoise = False
            
            if not task.didHitNoise:
                contact = base.physicsWorld.contactTest(shell.node())
                if contact.getNumContacts() > 0:
                    task.didHitNoise = True
                    hitNoise = base.loadSfxOnNode(self.ShellContactSoundPath.format(random.randint(*self.ShellContactSoundRange)), shell)
                    hitNoise.play()
        
            return task.cont
        
        from panda3d.bullet import BulletCylinderShape, BulletRigidBodyNode, ZUp
        scale = 0.75
        shape = BulletCylinderShape(0.07 * scale, 0.47 * scale, ZUp)
        rbnode = BulletRigidBodyNode('shellrbnode')
        rbnode.setMass(1.0)
        rbnode.addShape(shape)
        rbnode.setCcdMotionThreshold(1e-7)
        rbnode.setCcdSweptSphereRadius(0.1)
        rbnp = render.attachNewNode(rbnode)
        mdl = loader.loadModel(self.ShellPath)
        mdl.reparentTo(rbnp)
        mdl.setScale(0.3 * scale, 0.7 * scale, 0.3 * scale)
        mdl.setP(90)
        mdl.setTransparency(True, 1)

        rbnp.setPos(camera, (1, 2, -0.5))
        rbnp.setHpr(camera, (0, -90, 0))

        localEjectDir = Vec3(1, 0, 0.3)
        rbnode.applyCentralImpulse(camera.getQuat(render).xform(localEjectDir) * 7)
        base.physicsWorld.attach(rbnode)
    
        taskMgr.add(__shellThink, 'shellThink', extraArgs = [rbnp], appendTask = True)
        
    def onSetAction(self, action):
        if action == self.StatePump:
            self.pumpSound.play()
        elif action == self.StateFire:
            self.fireSound.play()
        elif action == self.StateDblFire:
            self.dblFireSound.play()
        elif action == self.StateReload:
            sound = random.choice(self.reloadSounds)
            sound.play()
            
    def onSetAction_firstPerson(self, action):        
        track = Sequence()
        vm = self.getViewModel()
        fpsCam = self.getFPSCam()
        
        if action in [self.StateFire, self.StateDblFire]:
            CIGlobals.makeMuzzleFlash(self.fpMuzzleAttach, (-0.03, 0.51, 32.45), (0, -90, 0), 7.5)
        
        if action == self.StateIdle:
            track.append(Func(vm.loop, "idle"))
        elif action == self.StateDraw:
            track.append(ActorInterval(vm, "draw", playRate=self.Speed))
        elif action == self.StatePump:
            track.append(Func(self.pumpSound.play))
            track.append(Func(self.__emitShell))
            track.append(ActorInterval(vm, "pump", playRate=self.Speed))
        elif action == self.StateFire:
            fpsCam.addViewPunch(Vec3(random.uniform(-2, 2), random.uniform(2, 1), 0))
            track.append(Func(self.fireSound.play))
            track.append(ActorInterval(vm, "fire", playRate=self.Speed))
        elif action == self.StateDblFire:
            fpsCam.addViewPunch(Vec3(0, random.uniform(-5, 5), 0))
            track.append(Func(self.dblFireSound.play))
            track.append(ActorInterval(vm, "altfire", playRate=self.Speed))
        elif action == self.StateReload:
            sound = random.choice(self.reloadSounds)
            track.append(Func(sound.play))
            track.append(ActorInterval(vm, "reload2", playRate=self.Speed))
        elif action == self.StateBeginReload:
            track.append(ActorInterval(vm, "reload1", playRate=self.Speed))
        elif action == self.StateEndReload:
            track.append(ActorInterval(vm, "reload3", playRate=self.Speed))
            
        fpsCam.setVMAnimTrack(track)
