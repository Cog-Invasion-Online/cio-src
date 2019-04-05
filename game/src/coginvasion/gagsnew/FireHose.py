"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file FireHose.py
@author Brian Lach
@date April 04, 2019

"""

from panda3d.core import Vec3, Point3, Quat

from direct.interval.IntervalGlobal import Sequence, Wait, Func, ActorInterval, LerpFunc, LerpScaleInterval, Parallel

from src.coginvasion.globals import CIGlobals
from src.coginvasion.attack.Attacks import ATTACK_GAG_FIREHOSE, ATTACK_HOLD_LEFT
from src.coginvasion.gags import GagGlobals
from src.coginvasion.gagsnew.BaseHitscan import BaseHitscan
from src.coginvasion.base.Precache import precacheSound
from src.coginvasion.gui.WaterBar import WaterBar
from src.coginvasion.phys import PhysicsUtils
from FireHoseShared import FireHoseShared

import math
import random

class FireHose(BaseHitscan, FireHoseShared):

    ID = ATTACK_GAG_FIREHOSE
    Name = GagGlobals.FireHose
    ModelPath = "phase_5/models/props/firehose-mod.bam"
    ModelAnimPath = "phase_5/models/props/firehose-chan.bam"
    ModelVMOrigin = (-1.8, 1.06, -4.13)
    ModelVMAngles = (0, 90, 0)
    ModelVMScale = 1
    ModelVMAnimate = False
    Hold = ATTACK_HOLD_LEFT

    sprayParticleDist = 50.0
    sprayParticleLife = 0.5
    spraySoundSpeed = 4.0
    sprayParticleFile = 'phase_14/etc/spray.ptf'
    sprayJoint = 'joint_water_stream'
    spraySoundPath = "phase_14/audio/sfx/squirtgun_spray_loop.ogg"

    def __init__(self):
        BaseHitscan.__init__(self)
        self.sprayParticleRoot = None
        self.waterStreamParent = None
        self.sprayParticle = None
        self.spraySound = base.audio3d.loadSfx(self.spraySoundPath)
        self.spraySound.setVolume(0.0)
        self.lastSprayTime = 0.0
        self.spraySoundIval = None
        
        self.waterBar = None

        self.hydrant = None
        self.hydrantNode = None
        self.hydrantScale = None
        self.hoseJoint = None
        self.released = True

    @classmethod
    def doPrecache(cls):
        super(FireHose, cls).doPrecache()
        precacheSound(cls.spraySoundPath)

    def cleanupHydrantNode(self):
        if self.hydrantNode:
            self.hydrantNode.removeNode()
            self.hydrentNode = None

    def __doBob(self):
        self.setAnimTrack(self.getBobSequence('firehose', 30, 30, 1.0), startNow = True, looping = True)

    def stopSpraySoundIval(self):
        if self.spraySoundIval:
            self.spraySoundIval.pause()
            self.spraySoundIval = None

    def __updateSprayVol(self, val):
        self.spraySound.setVolume(val)

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

    def loadParticle(self):
        self.stopParticle()
        gag = self.model
        if self.isFirstPerson():
            gag = self.getVMGag()
        self.waterStreamParent = gag.find("**/" + self.sprayJoint).attachNewNode("particleParent")
        self.sprayParticle = loader.loadParticleEffect(self.sprayParticleFile)
        # Update now to prevent one particle spraying out the side when we begin.
        self.__updateParticleParent()

    def __doSplat(self, distance, pos):
        self.splatDist = distance
        self.splatPos = pos

        origSize = GagGlobals.splatSizes.get(self.getName())
        if self.splatDist is not None and self.sprayParticleDist is not None:
            size = origSize * (self.splatDist / self.sprayParticleDist)
        else:
            size = origSize
        size = max(origSize / 3.0, size)
        CIGlobals.makeSplat(self.splatPos, GagGlobals.WATER_SPRAY_COLOR, size)

    def primaryFireRelease(self, data = None):
        BaseHitscan.primaryFireRelease(self, data)
        self.released = True

    def primaryFirePress(self, auto = False):
        if not auto:
            self.released = False
        BaseHitscan.primaryFirePress(self, None)

    def __updateParticleParent(self):
        time = globalClock.getFrameTime()
        
        streamPos = self.waterStreamParent.getPos(render)
        distance = self.sprayParticleDist

        if self.isLocal():
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

            if time - self.lastSprayTime >= self.SprayTraceIval and not self.released:
                if result.hasHit():
                    self.__doSplat(distance, hitPos)
                self.getFPSCam().addViewPunch(Vec3(random.uniform(-0.6, 0.6),
                                                   random.uniform(0.25, 1.0),
                                                   0.0))
                self.primaryFirePress(True)
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

    def stopParticle(self):
        if self.waterStreamParent:
            self.waterStreamParent.removeNode()
            self.waterStreamParent = None
        if self.sprayParticle:
            self.sprayParticle.softStop()
            self.sprayParticle = None

    def cleanupWaterBar(self):
        if self.waterBar:
            self.waterBar.removeNode()
        self.waterBar = None

    def __updateWaterBar(self):
        if self.waterBar:
            perct = float(self.ammo) / float(self.maxAmmo)

            self.waterBar.range = self.maxAmmo
            self.waterBar.value = self.ammo

            return perct

        return 1.0

    def think(self):
        BaseHitscan.think(self)

        if CIGlobals.isNodePathOk(self.hoseJoint):
            hand = self.avatar.getLeftHandNode()
            self.hoseJoint.setHpr(self.avatar, hand.getHpr(self.avatar) + (-5, 5, 0))
            self.hoseJoint.setPos(self.avatar, hand.getPos(self.avatar) + (-0.1, 0.2, 0.1))

        if self.action == self.StateFire:
            self.__updateParticleParent()

        if self.isLocal():

            if self.waterBar:
                perct = self.__updateWaterBar()
                if perct <= 0.3:
                    time = globalClock.getFrameTime()
                    alpha = 0.5 + ((math.sin(time * 7) + 1) / 4)
                    self.waterBar.setBarAlpha(alpha)

    def equip(self):
        if not BaseHitscan.equip(self):
            return False

        self.sprayParticleRoot = render.attachNewNode('sprayParticleRoot')
        self.sprayParticleRoot.setLightOff(1)
        self.sprayParticleRoot.hide(CIGlobals.ShadowCameraBitmask)

        if self.isLocal():
            self.released = True
            self.waterBar = WaterBar()
            self.__updateWaterBar()
            self.waterBar.reparentTo(base.a2dLeftCenter)
            self.waterBar.setScale(0.6)
            self.waterBar.setX(0.166)

        self.hydrant = loader.loadModel('phase_5/models/props/battle_hydrant.bam')
        self.model.reparentTo(self.hydrant)
        self.model.pose('chan', 2)
        self.hoseJoint = self.model.controlJoint(None, "modelRoot", "joint_x")

        self.hydrantNode = self.avatar.attachNewNode('hydrantNode')
        self.hydrantNode.clearTransform(self.avatar.getGeomNode().getChild(0))
        self.hydrantNode.setHpr(0, 0, 0)
        self.hydrantScale = self.hydrantNode.attachNewNode('hydrantScale')
        self.hydrant.reparentTo(self.hydrantScale)
        self.avatar.pose('firehose', 30)
        self.avatar.update(0)
        torso = self.avatar.getPart('torso')
        if 'dgm' in self.avatar.getTorso():
            self.hydrant.setPos(torso, 0, 0, -1.85)
        else:
            self.hydrant.setPos(torso, 0, 0, -1.45)
        hbase = self.hydrant.find('**/base')
        hbase.setColor(1, 1, 1, 0.5)
        hbase.setPos(self.avatar, 0, 0, 0)

        self.avatar.loop('neutral')

        tAppearDelay = 0.7
        dAnimHold = 5.1
        dHoseHold = 0.7
        tSprayDelay = 2.8
        track = Parallel()
        toonTrack = Sequence(Wait(tAppearDelay),
                             Func(self.avatar.setForcedTorsoAnim, 'firehose'),
                             self.getAnimationTrack('firehose', endFrame = 30),
                             Func(self.__doBob))
        propTrack = Sequence(Func(self.hydrantNode.reparentTo, self.avatar), LerpScaleInterval(self.hydrantScale, tAppearDelay * 0.5, Point3(1, 1, 1.4),
            startScale=Point3(1, 1, 0.01)), LerpScaleInterval(self.hydrantScale, tAppearDelay * 0.3, Point3(1, 1, 0.8), startScale=Point3(1, 1, 1.4)),
            LerpScaleInterval(self.hydrantScale, tAppearDelay * 0.1, Point3(1, 1, 1.2), startScale=Point3(1, 1, 0.8)),
            LerpScaleInterval(self.hydrantScale, tAppearDelay * 0.1, Point3(1, 1, 1), startScale=Point3(1, 1, 1.2)),
            ActorInterval(self.model, 'chan', endFrame = 30))
        track.append(toonTrack)
        track.append(propTrack)
        self.setAnimTrack(track, startNow = True)

        if self.isFirstPerson():
            self.hydrantNode.hide()

        return True

    def deleteHoseStuff(self):
        if self.hoseJoint:
            self.hoseJoint.detachNode()
            if self.model:
                self.model.releaseJoint("modelRoot", "joint_x")
            self.hoseJoint = None
        if self.hydrant:
            self.hydrant.removeNode()
            self.hydrant = None
        if self.hydrantNode:
            self.hydrantNode.removeNode()
            self.hydrantNode = None
        if self.hydrantScale:
            self.hydrantScale.removeNode()
            self.hydrantScale = None

    def unEquip(self):
        if not BaseHitscan.unEquip(self):
            return False

        self.__endSpraying()

        if self.sprayParticleRoot:
            self.sprayParticleRoot.removeNode()
        self.sprayParticleRoot = None
        
        self.deleteHoseStuff()

        if self.isLocal():
            self.cleanupWaterBar()

        return True

    def __beginSpraying(self):
        base.audio3d.attachSoundToObject(self.spraySound, self.avatar)
        self.spraySound.setLoop(True)

        # Start and fade in the spray sound.
        self.doSpraySoundIval(0)

        self.loadParticle()
        self.sprayParticle.start(self.waterStreamParent, self.sprayParticleRoot)

    def __endSpraying(self):
        # Fade out and stop the spray sound
        self.doSpraySoundIval(1)

        self.stopParticle()

    def onSetAction(self, action):
        if action == self.StateFire:
            self.__beginSpraying()
        elif action == self.StateIdle:
            if self.lastAction == self.StateFire:
                self.__endSpraying()

    def onSetAction_firstPerson(self, action):
        vm = self.getViewModel()
        fpsCam = self.getFPSCam()
        track = Sequence()
        if action == self.StateDraw:
            track.append(ActorInterval(vm, "hose_draw"))
            track.append(Func(vm.loop, "hose_idle"))
        elif action == self.StateIdle:
            if self.lastAction == self.StateFire:
                self.__endSpraying()
                track.append(ActorInterval(vm, "hose_shoot_end"))
            track.append(Func(vm.loop, "hose_idle"))
        elif action == self.StateFire:
            self.__beginSpraying()
            track.append(ActorInterval(vm, "hose_shoot_begin"))
            track.append(Func(vm.loop, "hose_shoot_loop"))
        fpsCam.setVMAnimTrack(track)

    def cleanup(self):
        self.deleteHoseStuff()
        self.stopParticle()
        self.cleanupWaterBar()
        self.stopSpraySoundIval()
        if self.spraySound:
            base.audio3d.detachSound(self.spraySound)
        self.spraySound = None
        self.lastSprayTime = None
        self.released = None

        BaseHitscan.cleanup(self)
