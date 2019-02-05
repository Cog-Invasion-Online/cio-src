"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file HL2Shotgun.py
@author Brian Lach
@date February 5, 2019

@desc Easter egg! Shotgun from Half-Life 2. I wanted to see how easy it
      would be to port it over to Panda since our material system is
      almost identical to Source. It was easy.

"""

from panda3d.core import OmniBoundingVolume, Vec3, Point3, NodePath

from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence, Func, ActorInterval

from src.coginvasion.base.Precache import precacheActor, precacheSound
from src.coginvasion.globals import CIGlobals
from Gag import Gag
from GagType import GagType
import GagGlobals

import random

class HL2Shotgun(Gag):
    name = GagGlobals.HL2Shotgun
    gagType = GagType.TRAP
    multiUse = True
    model = "phase_4/models/props/water-gun.bam"
    
    sgDir = 'phase_14/hl2/v_shotgun/panda/opt/'
    sgActorDef = [sgDir + 'v_shotgun.bam',
	    {'draw': sgDir + 'v_shotgun-draw.egg',
	     'idle': sgDir + 'v_shotgun-idle01.egg',
	     'pump': sgDir + 'v_shotgun-pump.egg',
	     'fire': sgDir + 'v_shotgun-fire01.egg',
	     'altfire': sgDir + 'v_shotgun-altfire.egg',
	     'reload1': sgDir + 'v_shotgun-reload1.egg',
	     'reload2': sgDir + 'v_shotgun-reload2.egg',
	     'reload3': sgDir + 'v_shotgun-reload3.egg'}]
    sgFirePath = 'phase_14/hl2/v_shotgun/shotgun_fire7.wav'
    sgEmptyPath = 'phase_14/hl2/v_shotgun/shotgun_empty.wav'
    sgDblFirePath = 'phase_14/hl2/v_shotgun/shotgun_dbl_fire7.wav'
    sgPumpPath = 'phase_14/hl2/v_shotgun/shotgun_cock.wav'
    sgReloadPaths = ['phase_14/hl2/v_shotgun/shotgun_reload1.wav',
                     'phase_14/hl2/v_shotgun/shotgun_reload2.wav',
                     'phase_14/hl2/v_shotgun/shotgun_reload3.wav']
                     
    actionIdle = 0
    actionPump = 1
    actionBeginReload = 5
    actionEndReload = 6
    actionReload = 2
    actionFire = 3
    actionDblFire = 4
    actionDraw = 7
    
    actionLengths = {
        actionIdle: 0,
        actionPump: 0.666666666667,
        actionReload: 0.5,
        actionBeginReload: 0.625,
        actionEndReload: 0.541666666667,
        actionFire: 0.416666666667,
        actionDblFire: 0.625,
        actionDraw: 0.916666666667
    }
    
    def __init__(self):
        Gag.__init__(self)
        self.sgViewModel = None
        
        self.fireSound = base.audio3d.loadSfx(self.sgFirePath)
        self.dblFireSound = base.audio3d.loadSfx(self.sgDblFirePath)
        self.pumpSound = base.audio3d.loadSfx(self.sgPumpPath)
        self.emptySound = base.audio3d.loadSfx(self.sgEmptyPath)
        self.reloadSounds = []
        for rl in self.sgReloadPaths:
            self.reloadSounds.append(base.audio3d.loadSfx(rl))
            
        self.maxClip = 6
        self.clip = 6
        
        self.action = self.actionIdle
        self.actionStartTime = 0
        self.nextAction = None
        
        self.needsPump = False
        
    def _handleShotSomething(self, intoNP, hitPos, distance):
        avNP = intoNP.getParent()
        
        if base.localAvatarReachable() and self.isLocal():
            for obj in base.avatars:
                if CIGlobals.isAvatar(obj) and obj.getKey() == avNP.getKey():
                    obj.handleHitByToon(self.avatar, self.getID(), distance)
        
    def isActionComplete(self):
        return self.getActionTime()  >= self.actionLengths[self.action]
        
    def getActionTime(self):
        return (globalClock.getFrameTime() - self.actionStartTime)
        
    def setNextAction(self, action):
        self.nextAction = action
        
    def setAction(self, action):
        self.actionStartTime = globalClock.getFrameTime()
        self.action = action
        
        vm = self.getViewModel()
        fpsCam = self.getFPSCam()
        track = Sequence()
        
        if action == self.actionIdle:
            track.append(Func(vm.loop, "idle"))
        elif action == self.actionDraw:
            track.append(ActorInterval(vm, "draw"))
        elif action == self.actionPump:
            track.append(Func(self.pumpSound.play))
            track.append(ActorInterval(vm, "pump"))
            
        elif action == self.actionFire:
            camQuat = camera.getQuat(render)
            pFrom = camera.getPos(render)
            pTo = pFrom + camQuat.xform(Vec3.forward() * 10000)
            hitPos = Point3(pTo)
            result = base.physicsWorld.rayTestClosest(pFrom, pTo, CIGlobals.WorldGroup)
            if result.hasHit():
                node = result.getNode()
                hitPos = result.getHitPos()
                distance = (hitPos - pFrom).length()
                self._handleShotSomething(NodePath(node), hitPos, distance)
                    
            self.clip -= 1
            fpsCam = self.getFPSCam()
            if base.localAvatar.isFirstPerson():
                fpsCam.addViewPunch(Vec3(random.uniform(-2, 2), random.uniform(2, 1), 0))
                
            base.localAvatar.sendUpdate('usedGag', [self.id])
                    
            track.append(Func(self.fireSound.play))
            track.append(ActorInterval(vm, "fire"))
            
        elif action == self.actionDblFire:
            track.append(Func(self.dblFireSound.play))
            track.append(ActorInterval(vm, "altfire"))
        elif action == self.actionReload:
            sound = random.choice(self.reloadSounds)
            track.append(Func(sound.play))
            track.append(ActorInterval(vm, "reload2"))
        elif action == self.actionBeginReload:
            track.append(ActorInterval(vm, "reload1"))
        elif action == self.actionEndReload:
            track.append(ActorInterval(vm, "reload3"))
            
        fpsCam.setVMAnimTrack(track)
        
    def __tick(self, task):
        complete = self.isActionComplete()
        
        if complete and self.nextAction is None:
            nextAction = self.actionIdle
            if self.action == self.actionFire:
                if self.clip <= 0:
                    self.needsPump = True
                    nextAction = self.actionBeginReload
                else:
                    nextAction = self.actionPump
            elif self.action == self.actionBeginReload:
                nextAction = self.actionReload
            elif self.action == self.actionReload:
                self.clip += 1
                if self.clip < self.maxClip and self.clip < self.avatar.backpack.getSupply(self.getID()):
                    nextAction = self.actionReload
                else:
                    nextAction = self.actionEndReload
            elif self.action == self.actionEndReload:
                if self.needsPump:
                    nextAction = self.actionPump
                    self.needsPump = False
                else:
                    nextAction = self.actionIdle
            elif self.action == self.actionDraw:
                if self.clip <= 0:
                    self.needsPump = True
                    nextAction = self.actionBeginReload
                elif self.needsPump:
                    nextAction = self.actionPump
                    self.needsPump = False
                else:
                    nextAction = self.actionIdle
                    
            self.setAction(nextAction)
            
        elif ((complete) or
               (not complete and self.action == self.actionPump and
                self.getActionTime() >= 0.5 and self.nextAction == self.actionFire)):
                    
            self.setAction(self.nextAction)
            self.nextAction = None
        
        return task.cont
        
    def __doReload(self):
        if self.action == self.actionIdle and self.clip < self.maxClip:
            self.setNextAction(self.actionBeginReload)
        
    @classmethod
    def doPrecache(cls):
        precacheActor(cls.sgActorDef)
        
        precacheSound(cls.sgFirePath)
        precacheSound(cls.sgDblFirePath)
        precacheSound(cls.sgPumpPath)
        precacheSound(cls.sgEmptyPath)
        for rl in cls.sgReloadPaths:
            precacheSound(rl)
        
    def equip(self):
        Gag.equip(self)
        
        base.audio3d.attachSoundToObject(self.fireSound, self.avatar)
        base.audio3d.attachSoundToObject(self.dblFireSound, self.avatar)
        base.audio3d.attachSoundToObject(self.pumpSound, self.avatar)
        base.audio3d.attachSoundToObject(self.emptySound, self.avatar)
        for s in self.reloadSounds:
            base.audio3d.attachSoundToObject(s, self.avatar)
        
        if self.isLocal():
            self.sgViewModel = Actor(self.sgActorDef[0], self.sgActorDef[1])
            self.sgViewModel.node().setBounds(OmniBoundingVolume())
            self.sgViewModel.node().setFinal(1)
            self.sgViewModel.setBlend(frameBlend = base.config.GetBool('interpolate-frames', False))
            self.sgViewModel.setH(180)
            self.sgViewModel.find("**/shell").setBSPMaterial('phase_14/hl2/casing01.mat')
            
            fpsCam = self.getFPSCam()
            fpsCam.swapViewModel(self.sgViewModel, 54.0)
            self.setAction(self.actionDraw)
            self.accept('r', self.__doReload)
            
            taskMgr.add(self.__tick, "HL2ShotgunTick")
            
    def start(self):
            
        Gag.start(self)
        
        if self.isLocal():
            fpsCam = self.getFPSCam()
            if self.action in [self.actionReload, self.actionIdle, self.actionBeginReload,
                               self.actionEndReload, self.actionPump]:
                
                if self.clip <= 0:
                    self.emptySound.play()
                    return
                    
                self.setNextAction(self.actionFire)
                    
            
    def unEquip(self):
        if self.isLocal():
            self.getFPSCam().restoreViewModel()
            self.sgViewModel.cleanup()
            self.sgViewModel.removeNode()
            self.sgViewModel = None
            if self.action == self.actionFire:
                self.needsPump = True
            self.ignore('r')
            taskMgr.remove("HL2ShotgunTick")
