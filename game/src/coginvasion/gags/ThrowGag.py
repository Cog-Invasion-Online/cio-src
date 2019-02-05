"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file ThrowGag.py
@author Maverick Liberty
@date July 07, 2015

"""

from panda3d.core import CollisionSphere, BitMask32, CollisionNode, NodePath, CollisionHandlerEvent, Vec3
from panda3d.bullet import BulletSphereShape, BulletGhostNode
from direct.interval.IntervalGlobal import Sequence, Func, Wait, Parallel, ProjectileInterval, ActorInterval
from direct.gui.DirectGui import DirectWaitBar, DGG

from src.coginvasion.minigame.FlightProjectileInterval import FlightProjectileInterval
from src.coginvasion.gags.Gag import Gag
from src.coginvasion.gags.GagType import GagType
from src.coginvasion.globals import CIGlobals
from src.coginvasion.phys import PhysicsUtils, WorldCollider
from direct.actor.Actor import Actor
import GagGlobals
from PowerBar import PowerBar

import math

class ThrowGag(Gag):
    
    ReleaseSpeed = 1.0
    ReleasePlayRateMultiplier = 1.0
    BobStartFrame = 30
    BobEndFrame = 40
    BobPlayRateMultiplier = 0.25
    ThrowObjectFrame = 62
    FinalThrowFrame = 90
    
    splatColor = (1, 1, 1, 1)
    gagType = GagType.THROW

    def __init__(self):
        Gag.__init__(self)
        self.splatScale = GagGlobals.splatSizes[self.name]
        self.entities = []
        self.timeout = 1.0
        self.powerBar = None

    def setAvatar(self, avatar):
        Gag.setAvatar(self, avatar)
        if self.isLocal():
            self.powerBar = PowerBar()

    def build(self):
        if not self.gag:
            Gag.build(self)
            self.equip()
            if self.anim and self.gag:
                self.gag.loop('chan')
        return self.gag

    def __doDraw(self):
        self.doDrawAndHold('pie', 0, self.BobStartFrame, self.playRate, self.BobStartFrame,
                           self.BobEndFrame, self.playRate * self.BobPlayRateMultiplier)

    def equip(self):
        Gag.equip(self)

        if self.isLocal():
            vmGag = base.localAvatar.getFPSCam().vmGag
            if vmGag:
                vmGag.setPosHpr(0.07, 0.17, -0.01, 0, -100, -10)
                vmGag.setScale(self.gag.getScale() * 0.567)
            vm = base.localAvatar.getViewModel()
            fpsCam = base.localAvatar.getFPSCam()
            fpsCam.setVMAnimTrack(Sequence(ActorInterval(vm, "pie_draw"), Func(vm.loop, "pie_idle")))

        self.__doDraw()

    def start(self):
        Gag.start(self)
        if not self.gag:
            self.build()

        if self.isLocal():
            self.powerBar.start()

    def throw(self):
        if self.isLocal():
            self.powerBar.stop(hideAfter = 1.5)
            self.power = self.powerBar.getPower() + 50
            self.power = 250 - self.power
            # Make other toons set the throw power on my gag.
            base.localAvatar.sendUpdate('setThrowPower', [self.id, self.power])
            self.startTimeout()
        self.clearAnimTrack()
        
        if not self.gag:
            self.build()

        def shouldRelease():
            if self.isLocal():
                base.localAvatar.releaseGag()
                vm = base.localAvatar.getViewModel()
                fpsCam = base.localAvatar.getFPSCam()
                fpsCam.clearVMGag()
                fpsCam.setVMAnimTrack(Sequence(ActorInterval(vm, "tnt_throw", startFrame = 27), Func(vm.hide), Func(vm.pose, "pie_draw", 0)))
        
        self.setAnimTrack(
            Parallel(
                Sequence(
                    self.getAnimationTrack('pie', startFrame=self.ThrowObjectFrame,
                                           playRate=(self.playRate * self.ReleasePlayRateMultiplier)),
                    Func(self.__doDraw),
                ),
                Sequence(
                    Func(shouldRelease)
                )
            )
        )
        
        self.animTrack.start()

    def setPower(self, power):
        self.power = power

    def release(self):
        Gag.release(self)
        base.audio3d.attachSoundToObject(self.woosh, self.gag)
        base.playSfx(self.woosh, node = self.gag)
        
        if self.isLocal() and base.localAvatar.battleControls:
            if base.localAvatar.isFirstPerson():
                startPos = camera.getPos(render) + camera.getQuat(render).xform(Vec3.right())
                push = 0.0
            else:
                startPos = self.handJoint.getPos(render)
                push = (startPos - camera.getPos(render)).length()
            hitPos = PhysicsUtils.getHitPosFromCamera()
        else:
            startPos = self.handJoint.getPos(render)
            quat = Quat()
            quat.setHpr(self.avatar.getHpr(render) + (0, self.avatar.lookPitch, 0))
            hitPos = quat.xform(Vec3.forward() * self.power)
            hit = PhysicsUtils.rayTestClosestNotMe(self.avatar, startPos,
                hitPos,
                CIGlobals.WorldGroup | CIGlobals.LocalAvGroup)
            if hit is not None:
                hitPos = hit.getHitPos()
                
        throwDir = (hitPos - startPos).normalized()
        endPos = startPos + (throwDir * self.power) - (0, 0, 90)

        entity = self.gag

        if not entity:
            entity = self.build()
            
        gagRoot = render.attachNewNode('gagRoot')
        gagRoot.setPos(startPos)

        entity.reparentTo(render)
        entity.setPos(0, 0, 0)
        entity.headsUp(throwDir)
        rot = entity.getHpr(render)
        entity.reparentTo(gagRoot)
        entity.setHpr(rot[0], -90, 0)
        self.gag = None

        if not self.handJoint:
            self.handJoint = self.avatar.find('**/def_joint_right_hold')

        track = FlightProjectileInterval(gagRoot, startPos = startPos, endPos = endPos, gravityMult = 1.07, duration = 2.5)
        event = self.avatar.uniqueName('throwIvalDone') + '-' + str(hash(entity))
        track.setDoneEvent(event)
        base.acceptOnce(event, self.__handlePieIvalDone, [entity])
        track.start()
        
        if self.isLocal():
            collider = self.buildCollisions(entity)
            self.entities.append([gagRoot, track, collider])
            base.localAvatar.sendUpdate('usedGag', [self.id])
        else:
            self.entities.append([gagRoot, track, NodePath()])
        self.reset()

    def __handlePieIvalDone(self, pie):
        if not pie.isEmpty():
            pie.removeNode()

    def handleSplat(self):
        base.audio3d.detachSound(self.woosh)
        if self.woosh:
            self.woosh.stop()

        CIGlobals.makeSplat(self.splatPos, self.splatColor, self.splatScale, self.hitSfx)

        self.cleanupEntity(self.splatPos)
        self.splatPos = None

    def cleanupEntity(self, pos):
        closestPie = None
        trackOfClosestPie = None
        colliderOfClosestPie = None
        pieHash2range = {}
        for entity, track, collider in self.entities:
            if not entity.isEmpty():
                pieHash2range[hash(entity)] = (entity.getPos(render) - pos).length()
        ranges = []
        for distance in pieHash2range.values():
            ranges.append(distance)
        ranges.sort()
        for pieHash in pieHash2range.keys():
            distance = pieHash2range[pieHash]
            if not distance is None and distance == ranges[0]:
                for entity, track, collData in self.entities:
                    if hash(entity) == pieHash:
                        closestPie = entity
                        trackOfClosestPie = track
                        colliderOfClosestPie = collData
                        break
            break
        if closestPie != None and trackOfClosestPie != None and colliderOfClosestPie != None:
            if [closestPie, trackOfClosestPie, colliderOfClosestPie] in self.entities:
                self.entities.remove([closestPie, trackOfClosestPie, colliderOfClosestPie])
            if not colliderOfClosestPie.isEmpty():
                print colliderOfClosestPie, "removing!"
                colliderOfClosestPie.removeNode()
            if not closestPie.isEmpty():
                if isinstance(closestPie, Actor):
                    closestPie.cleanup()
                closestPie.removeNode()

    def onCollision(self, contact, frNp, intoNP):
        print "onCollision:", frNp, "->", intoNP
        avNP = intoNP.getParent()
        fromNP = frNp.getParent()

        if fromNP.isEmpty():
            return

        for obj in base.avatars:
            if CIGlobals.isAvatar(obj) and obj.getKey() == avNP.getKey():
                obj.handleHitByToon(self.avatar, self.getID(), self.avatar.getDistance(obj))
            elif obj.__class__.__name__ == "DistributedPieTurret":
                if obj.getKey() == avNP.getKey():
                    if obj.getHealth() < obj.getMaxHealth():
                        self.avatar.sendUpdate('toonHitByPie', [obj.doId, self.getID()])

        self.splatPos = fromNP.getPos(render)
        self.avatar.sendUpdate('setSplatPos', [self.getID(), self.splatPos.getX(), self.splatPos.getY(), self.splatPos.getZ()])
        self.handleSplat()

    def buildCollisions(self, entity):
        collider = WorldCollider.WorldCollider('gagSensor', 1, 'throwGagCollide', needSelfInArgs = True, resultInArgs = True)
        collider.reparentTo(entity)
        self.avatar.acceptOnce('throwGagCollide', self.onCollision)
        return collider

    def unEquip(self):
        if self.powerBar:
            self.powerBar.hide()
        Gag.unEquip(self)

    def delete(self):
        if self.powerBar:
            self.powerBar.destroy()
            self.powerBar = None
        self.clearAnimTrack()
        Gag.delete(self)
