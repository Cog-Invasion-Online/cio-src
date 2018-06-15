"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file SquirtGag.py
@author Maverick Liberty
@date July 10, 2015

"""

from panda3d.core import Point3, Vec3, NodePath, CollisionSphere, CollisionHandlerEvent, CollisionNode

from direct.interval.IntervalGlobal import Sequence, Func, Wait, LerpScaleInterval, Parallel
from direct.interval.IntervalGlobal import ActorInterval, LerpFunc

from src.coginvasion.gags import GagGlobals
from src.coginvasion.gags.Gag import Gag
from src.coginvasion.gags.GagType import GagType
from src.coginvasion.globals import CIGlobals
from src.coginvasion.gags.GagState import GagState
from src.coginvasion.toon import ParticleLoader

import abc

class SquirtGag(Gag):

    def __init__(self, name, model, hitSfx, scale = 1):
        Gag.__init__(self, name, model, GagType.SQUIRT, hitSfx, scale = scale)
        self.splatDist = None

        self.sprayParticleRoot = None
        self.waterStreamParent = None
        self.spRootUpdateTask = None
        self.sprayParticle = None
        self.sprayParticleFile = 'phase_14/etc/spray.ptf'
        self.sprayJoint = 'joint_water_stream'
        self.spraySound = base.audio3d.loadSfx("phase_14/audio/sfx/squirtgun_spray_loop.ogg")
        self.spraySound.setVolume(0.0)
        self.sprayParticleDist = 50.0
        self.sprayParticleLife = 0.5
        self.lastDmgTime = 0.0
        self.dmgIval = 0.2
        self.spraySoundSpeed = 4.0
        self.spraySoundIval = None

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
        pFrom = camera.getPos(render)
        pTo = pFrom + camera.getQuat(render).xform(Vec3.forward()) * (self.sprayParticleDist + (pFrom - streamPos).length())
        hitPos = Point3(pTo)
        result = base.physicsWorld.rayTestClosest(pFrom, pTo, CIGlobals.WorldGroup)
        distance = self.sprayParticleDist
        if result.hasHit():
            node = result.getNode()
            hitPos = result.getHitPos()
            distance = (hitPos - streamPos).length()
            if time - self.lastDmgTime >= self.dmgIval:
                self._handleSprayCollision(NodePath(node), hitPos, distance)
                self.lastDmgTime = time
            
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
        gag = self.gag if not self.isLocal() else self.getVMGag()
        self.waterStreamParent = gag.find("**/" + self.sprayJoint).attachNewNode("particleParent")
        self.sprayParticle = ParticleLoader.loadParticleEffect(self.sprayParticleFile)
        if self.isLocal():
            # Update now to prevent one particle spraying out the side when we begin.
            self.__updateParticleParent()

    def equip(self):
        Gag.equip(self)
        self.sprayParticleRoot = render.attachNewNode('sprayParticleRoot')
        self.sprayParticleRoot.setLightOff()
        self.sprayParticleRoot.setMaterialOff()
        self.sprayParticleRoot.setShaderOff()

    def start(self):
        Gag.start(self)

        base.audio3d.attachSoundToObject(self.spraySound, self.avatar)
        self.spraySound.setLoop(True)

        # Start and fade in the spray sound.
        self.doSpraySoundIval(0)

        self.loadParticle()
        self.sprayParticle.start(self.waterStreamParent, self.sprayParticleRoot)

        if self.isLocal():
            self.spRootUpdateTask = taskMgr.add(self.__updateParticleParent, "FH.uPP", sort = -100)

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
            for key in base.cr.doId2do.keys():
                obj = base.cr.doId2do[key]
                if obj.__class__.__name__ in CIGlobals.SuitClasses:
                    if obj.getKey() == avNP.getKey():
                        obj.sendUpdate('hitByGag', [self.getID(), distance])
                elif obj.__class__.__name__ == "DistributedToon":
                    if obj.getKey() == avNP.getKey():
                        if obj.getHealth() < obj.getMaxHealth():
                            self.avatar.sendUpdate('toonHitByPie', [obj.doId, self.getID()])

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
        size = origSize * (self.splatDist / self.sprayParticleDist)
        size = max(origSize / 3.0, size)
        CIGlobals.makeSplat(self.splatPos, GagGlobals.WATER_SPRAY_COLOR, size)
        self.splatPos = None
        self.splatDist = None
