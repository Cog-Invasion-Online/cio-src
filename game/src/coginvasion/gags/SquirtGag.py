"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file SquirtGag.py
@author Maverick Liberty
@date July 10, 2015

"""

from panda3d.core import Point3, Vec3, NodePath, CollisionSphere, CollisionHandlerEvent, CollisionNode, Quat

from direct.interval.IntervalGlobal import Sequence, Func, Wait, LerpScaleInterval, Parallel
from direct.interval.IntervalGlobal import ActorInterval, LerpFunc

from src.coginvasion.gags import GagGlobals
from src.coginvasion.gags.Gag import Gag
from src.coginvasion.gags.GagType import GagType
from src.coginvasion.globals import CIGlobals
from src.coginvasion.gags.GagState import GagState
from src.coginvasion.toon import ParticleLoader
from src.coginvasion.gui.WaterBar import WaterBar
from src.coginvasion.phys import PhysicsUtils
from src.coginvasion.base.Precache import precacheSound

import abc
import math

class SquirtGag(Gag):
    
    gagType = GagType.SQUIRT
    sprayParticleFile = 'phase_14/etc/spray.ptf'
    sprayJoint = 'joint_water_stream'
    spraySoundPath = "phase_14/audio/sfx/squirtgun_spray_loop.ogg"
    dmgIval = 0.2
    sprayParticleDist = 50.0
    sprayParticleLife = 0.5
    spraySoundSpeed = 4.0

    def __init__(self):
        Gag.__init__(self)
        self.splatDist = None
        self.sprayParticleRoot = None
        self.waterStreamParent = None
        self.spRootUpdateTask = None
        self.sprayParticle = None
        self.spraySound = base.audio3d.loadSfx(self.spraySoundPath)
        self.spraySound.setVolume(0.0)
        self.lastDmgTime = 0.0
        self.lastSprayTime = 0.0
        self.spraySoundIval = None
        
        self.waterBar = None
        self.barTask = None
        
    @classmethod
    def doPrecache(cls):
        super(SquirtGag, cls).doPrecache()
        precacheSound(cls.spraySoundPath)

    def stopSpraySoundIval(self):
        if self.spraySoundIval:
            self.spraySoundIval.pause()
            self.spraySoundIval = None

    def doSpraySoundIval(self, dir = 0):
        self.stopSpraySoundIval()

        currVol = self.spraySound.getVolume()
        if dir == 0:
            goalVol = 1
        else:
            goalVol = 0
        dist = abs(currVol - goalVol)
        dur = dist / self.spraySoundSpeed
        ival = Sequence()
        if dir == 0:
            ival.append(Func(self.spraySound.play))
        ival.append(LerpFunc(self.__updateSprayVol, dur, currVol, goalVol))
        if dir == 1:
            ival.append(Func(self.spraySound.stop))

        self.spraySoundIval = ival
        self.spraySoundIval.start()

    def stopParticle(self):
        if self.spRootUpdateTask:
            self.spRootUpdateTask.remove()
            self.spRootUpdateTask = None
        if self.waterStreamParent:
            self.waterStreamParent.removeNode()
            self.waterStreamParent = None
        if self.sprayParticle:
            self.sprayParticle.softStop()
            self.sprayParticle = None

    def reset(self):
        self.stopParticle()
        self.stopSpraySoundIval()
        if self.spraySound:
            self.spraySound.stop()
        if self.spRootUpdateTask:
            taskMgr.remove(self.spRootUpdateTask)
            self.spRootUpdateTask = None
        if self.sprayParticleRoot:
            self.sprayParticleRoot.removeNode()
            self.sprayParticleRoot = None
        Gag.reset(self)

    def __updateParticleParent(self, task = None):
        time = globalClock.getFrameTime()
        
        streamPos = self.waterStreamParent.getPos(render)
        distance = self.sprayParticleDist

        if self.isLocal():
            if base.localAvatar.backpack.getSupply(self.id) <= 0:
                base.localAvatar.b_gagThrow(self.id)
                return task.done

            camQuat = camera.getQuat(render)
            pFrom = camera.getPos(render)
            push = (streamPos - pFrom).length()
            pFrom += camQuat.xform(Vec3.forward()) * push
            pTo = pFrom + camQuat.xform(Vec3.forward()) * (self.sprayParticleDist + (pFrom - streamPos).length())
            hitPos = Point3(pTo)
            result = base.physicsWorld.rayTestClosest(pFrom, pTo, CIGlobals.WorldGroup)
            if result.hasHit():
                node = result.getNode()
                hitPos = result.getHitPos()
                distance = (hitPos - streamPos).length()
                if time - self.lastDmgTime >= self.dmgIval:
                    self._handleSprayCollision(NodePath(node), hitPos, distance)
                    self.lastDmgTime = time

            if time - self.lastSprayTime >= self.dmgIval:
                base.localAvatar.sendUpdate('usedGag', [self.id])
                self.lastSprayTime = time

        else:
            pFrom = self.avatar.getPos(render) + self.avatar.getEyePoint() + (1, 0, 0)
            quat = Quat()
            quat.setHpr(self.avatar.getHpr(render) + (0, self.avatar.lookPitch, 0))
            pTo = pFrom + quat.xform(Vec3.forward()) * (self.sprayParticleDist + (pFrom - streamPos).length())
            hitPos = Point3(pTo)
            hit = PhysicsUtils.rayTestClosestNotMe(self.avatar, pFrom, pTo, CIGlobals.WorldGroup | CIGlobals.LocalAvGroup)
            if hit is not None:
                hitPos = hit.getHitPos()
                distance = (hitPos - streamPos).length()

        self.waterStreamParent.lookAt(render, hitPos)
        
        if self.sprayParticle:
            system = self.sprayParticle.getParticlesNamed('particles-1')
            # Make the particles die off at the hit point.
            lifespan = min(1, distance / self.sprayParticleDist) * self.sprayParticleLife
            system.factory.setLifespanBase(lifespan)
        
        if task:
            return task.cont

    def __updateSprayVol(self, val):
        self.spraySound.setVolume(val)

    def loadParticle(self):
        self.stopParticle()
        gag = self.gag
        if self.isLocal() and base.localAvatar.isFirstPerson():
            gag = self.getVMGag()
        self.waterStreamParent = gag.find("**/" + self.sprayJoint).attachNewNode("particleParent")
        self.sprayParticle = ParticleLoader.loadParticleEffect(self.sprayParticleFile)
        # Update now to prevent one particle spraying out the side when we begin.
        self.__updateParticleParent()
            
    def cleanupWaterBar(self):
        if self.waterBar:
            self.waterBar.removeNode()
        self.waterBar = None
        if self.barTask:
            self.barTask.remove()
        self.barTask = None

    def equip(self):
        Gag.equip(self)
        self.sprayParticleRoot = render.attachNewNode('sprayParticleRoot')
        self.sprayParticleRoot.setLightOff(1)
        #self.sprayParticleRoot.setMaterialOff(1)
        #self.sprayParticleRoot.setShaderOff(1)
        
        if self.isLocal():
            self.waterBar = WaterBar()
            self.__updateWaterBar()
            self.waterBar.reparentTo(base.a2dLeftCenter)
            self.waterBar.setScale(0.6)
            self.waterBar.setX(0.166)
            self.barTask = taskMgr.add(self.__barUpdate, "SquirtGag.barUpdate")
            
    def unEquip(self):
        if self.isLocal():
            self.cleanupWaterBar()
        Gag.unEquip(self)

    def __updateWaterBar(self):
        if self.waterBar:
            max = base.localAvatar.backpack.getMaxSupply(self.id)
            suppl = base.localAvatar.backpack.getSupply(self.id)
            perct = float(suppl) / float(max)

            self.waterBar.range = max
            self.waterBar.value = suppl

            return perct

        return 1.0
        
    def __barUpdate(self, task):
        if self.waterBar:
            perct = self.__updateWaterBar()
            if perct <= 0.3:
                time = globalClock.getFrameTime()
                alpha = 0.5 + ((math.sin(time * 7) + 1) / 4)
                self.waterBar.setBarAlpha(alpha)
            
        return task.cont

    def start(self):
        Gag.start(self)

        base.audio3d.attachSoundToObject(self.spraySound, self.avatar)
        self.spraySound.setLoop(True)

        # Start and fade in the spray sound.
        self.doSpraySoundIval(0)

        self.loadParticle()
        self.sprayParticle.start(self.waterStreamParent, self.sprayParticleRoot)

        self.spRootUpdateTask = taskMgr.add(self.__updateParticleParent, "FH.uPP", sort = -10)

    def throw(self):
        Gag.throw(self)

        # Fade out and stop the spray sound
        self.doSpraySoundIval(1)
        
        if self.avatar.isEmpty():
            return

        self.stopParticle()

        if self.isLocal():
            base.localAvatar.enableGagKeys()

        self.state = GagState.LOADED

    def _handleSprayCollision(self, intoNP, hitPos, distance):
        avNP = intoNP.getParent()
        
        if base.localAvatarReachable() and self.isLocal():
            for obj in base.avatars:
                if CIGlobals.isAvatar(obj) and obj.getKey() == avNP.getKey():
                    obj.handleHitByToon(self.avatar, self.getID(), distance)

            self.splatPos = hitPos
            self.splatDist = distance
            gagPos = hitPos
            self.handleSplat()
            self.avatar.sendUpdate('setSplatPos', [self.getID(), gagPos.getX(), gagPos.getY(), gagPos.getZ()])

    def completeSquirt(self):
        numFrames = base.localAvatar.getNumFrames(self.toonAnim)
        finishSeq = Sequence()
        finishSeq.append(Wait(0.5))
        finishSeq.append(Func(self.avatar.play, self.toonAnim, fromFrame = self.completeSquirtFrame, toFrame = numFrames))
        finishSeq.append(Func(self.reset))
        finishSeq.append(Func(self.avatar.play, 'neutral'))
        finishSeq.append(Func(self.cleanupSpray))
        finishSeq.start()
        if self.avatar == base.localAvatar:
            if base.localAvatar.getBackpack().getSupply() == 0:
                self.cleanupGag()

    def handleSplat(self):
        origSize = GagGlobals.splatSizes.get(self.getName())
        if self.splatDist is not None and self.sprayParticleDist is not None:
            size = origSize * (self.splatDist / self.sprayParticleDist)
        else:
            size = origSize
        size = max(origSize / 3.0, size)
        CIGlobals.makeSplat(self.splatPos, GagGlobals.WATER_SPRAY_COLOR, size)
        self.splatPos = None
        self.splatDist = None
