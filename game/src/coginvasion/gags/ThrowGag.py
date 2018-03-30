"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file ThrowGag.py
@author Maverick Liberty
@date July 07, 2015

"""

from panda3d.core import CollisionSphere, BitMask32, CollisionNode, NodePath, CollisionHandlerEvent
from direct.interval.IntervalGlobal import Sequence, Func, Wait, Parallel, \
    ParallelEndTogether, ActorInterval, ProjectileInterval
from direct.gui.DirectGui import DirectWaitBar, DGG

from src.coginvasion.gags.Gag import Gag
from src.coginvasion.gags.GagType import GagType
from src.coginvasion.globals import CIGlobals
from direct.actor.Actor import Actor
import GagGlobals

import math

class ThrowGag(Gag):
    
    ReleaseSpeed = 1.0
    ReleasePlayRateMultiplier = 1.0
    BobStartFrame = 27
    BobEndFrame = 40
    BobPlayRateMultiplier = 0.25
    ThrowObjectFrame = 61
    FinalThrowFrame = 90

    def __init__(self, name, model, damage, hitSfx, splatColor, anim = None, scale = 1):
        Gag.__init__(self, name, model, damage, GagType.THROW, hitSfx, anim = anim, scale = scale, autoRelease = True)
        self.splatScale = GagGlobals.splatSizes[self.name]
        self.splatColor = splatColor
        self.entities = []
        self.timeout = 1.0
        self.power = 50
        self.powerBar = None
        self.tossPieStart = 0
        self.pieSpeed = 0.2
        self.pieExponent = 0.75
        self.animTrack = None

    def setAvatar(self, avatar):
        Gag.setAvatar(self, avatar)
        if self.isLocal():
            self.powerBar = DirectWaitBar(range = 150, frameColor = (1, 1, 1, 1),
                         barColor = (0.286, 0.901, 1, 1), relief = DGG.RAISED,
                         borderWidth = (0.04, 0.04), pos = (0, 0, 0.85), scale = 0.2,
                         hpr = (0, 0, 0), parent = aspect2d, frameSize = (-0.85, 0.85, -0.12, 0.12))
            self.powerBar.hide()

    def __getPiePower(self, time):
        elapsed = max(time - self.tossPieStart, 0.0)
        t = elapsed / self.pieSpeed
        t = math.pow(t, self.pieExponent)
        power = int(t * 150) % 300
        if power > 150:
            power = 300 - power
        return power

    def build(self):
        if not self.gag:
            Gag.build(self)
            self.equip()
            if self.anim and self.gag:
                self.gag.loop('chan')
        return self.gag

    def start(self):
        super(ThrowGag, self).start()
        self.build()
        self.clearAnimTrack()
        
        bob = Sequence(
            ParallelEndTogether(
                ActorInterval(self.avatar, 
                    'pie', 
                    startFrame = self.BobStartFrame, 
                    endFrame = self.BobEndFrame,
                    partName = 'head',
                playRate = (self.playRate * self.BobPlayRateMultiplier)),
                ActorInterval(self.avatar, 
                    'pie', 
                    startFrame = self.BobStartFrame, 
                    endFrame = self.BobEndFrame,
                    partName = 'torso-top',
                playRate = (self.playRate * self.BobPlayRateMultiplier))
            ),
            ParallelEndTogether(
                ActorInterval(self.avatar, 
                    'pie', 
                    startFrame = self.BobStartFrame, 
                    endFrame = self.BobEndFrame,
                    partName = 'head',
                playRate = (-1 * (self.playRate * self.BobPlayRateMultiplier))),
                ActorInterval(self.avatar, 
                    'pie', 
                    startFrame = self.BobStartFrame, 
                    endFrame = self.BobEndFrame,
                    partName = 'torso-top',
                playRate = (-1 * (self.playRate * self.BobPlayRateMultiplier)))
            )
        )
        
        def doBob():
            self.clearAnimTrack()
            self.animTrack = bob
            bob.loop()
        
        self.animTrack = Sequence(
            Func(self.avatar.setForcedTorsoAnim, 'pie'),
            Func(self.avatar.setPlayRate, self.playRate, 'pie'),
            ParallelEndTogether(
                ActorInterval(self.avatar, 
                    'pie', 
                    startFrame = 0, 
                    endFrame = self.BobStartFrame,
                    partName = 'head',
                playRate = self.playRate),
                ActorInterval(self.avatar, 
                    'pie', 
                    startFrame = 0, 
                    endFrame = self.BobStartFrame,
                    partName = 'torso-top',
                playRate = self.playRate)
            ),
            Func(doBob)
        )
        
        self.animTrack.start()
        
        if self.isLocal():
            taskMgr.remove("hidePowerBarTask" + str(hash(self)))
            self.powerBar.show()
            self.startPowerBar()

    def startPowerBar(self):
        self.tossPieStart = globalClock.getFrameTime()
        taskMgr.add(self.__powerBarUpdate, "powerBarUpdate" + str(hash(self)))

    def __powerBarUpdate(self, task):
        if self.powerBar is None:
            return task.done
        self.powerBar['value'] = self.__getPiePower(globalClock.getFrameTime())
        return task.cont

    def stopPowerBar(self):
        taskMgr.remove("powerBarUpdate" + str(hash(self)))
        self.power = self.powerBar['value']

    def __hidePowerBarTask(self, task):
        self.powerBar.hide()
        
    def clearAnimTrack(self):
        if self.animTrack:
            self.animTrack.pause()
            self.animTrack = None

    def throw(self):
        if self.isLocal():
            self.stopPowerBar()
            self.power += 50
            self.power = 250 - self.power
            # Make other toons set the throw power on my gag.
            base.localAvatar.sendUpdate('setThrowPower', [self.id, self.power])
            self.startTimeout()
            taskMgr.doMethodLater(1.5, self.__hidePowerBarTask, "hidePowerBarTask" + str(hash(self)))
        self.clearAnimTrack()
        
        if not self.gag:
            self.build()
            
        def shouldCallRelease():
            if self.isLocal():
                base.localAvatar.releaseGag()
                
        def finalize():
            self.clearAnimTrack()
            self.avatar.clearForcedTorsoAnim()
        
        fromFrame = self.avatar.getCurrentFrame('pie', partName = 'torso-top')
        timeUntilRelease = self.avatar.getDuration('pie', fromFrame = fromFrame, toFrame = self.ThrowObjectFrame)
        
        self.animTrack = Parallel(
            Sequence(
                ParallelEndTogether(
                    ActorInterval(self.avatar, 
                        'pie', 
                        startFrame = fromFrame, 
                        endFrame = self.FinalThrowFrame,
                        partName = 'head',
                    playRate = (self.playRate * self.ReleasePlayRateMultiplier)),
                    ActorInterval(self.avatar, 
                        'pie', 
                        startFrame = fromFrame, 
                        endFrame = self.FinalThrowFrame,
                        partName = 'torso-top',
                    playRate = (self.playRate * self.ReleasePlayRateMultiplier)),
                ),
                Func(finalize),
            ),
            Sequence(
                Wait(timeUntilRelease / self.ReleaseSpeed),
                Func(shouldCallRelease)
            )
        )
        
        self.animTrack.start()

    def setPower(self, power):
        self.power = power

    def release(self):
        Gag.release(self)
        base.audio3d.attachSoundToObject(self.woosh, self.gag)
        base.playSfx(self.woosh, node = self.gag)

        throwPath = NodePath('ThrowPath')
        throwPath.reparentTo(self.avatar)
        throwPath.setScale(render, 1)
        throwPath.setPos(0, self.power, -90)
        throwPath.setHpr(90, -90, 90)

        entity = self.gag

        if not entity:
            entity = self.build()

        entity.wrtReparentTo(render)
        entity.setHpr(throwPath.getHpr(render))
        self.gag = None

        if not self.handJoint:
            self.handJoint = self.avatar.find('**/def_joint_right_hold')

        track = ProjectileInterval(entity, startPos = self.handJoint.getPos(render), endPos = throwPath.getPos(render), gravityMult = 0.9, duration = 3)
        event = self.avatar.uniqueName('throwIvalDone') + '-' + str(hash(entity))
        track.setDoneEvent(event)
        base.acceptOnce(event, self.__handlePieIvalDone, [entity])
        track.start()
        self.entities.append([entity, track])
        if self.isLocal():
            self.buildCollisions(entity)
            base.localAvatar.sendUpdate('usedGag', [self.id])
        self.reset()

    def __handlePieIvalDone(self, pie):
        if not pie.isEmpty():
            pie.removeNode()

    def handleSplat(self):
        base.audio3d.detachSound(self.woosh)
        if self.woosh: self.woosh.stop()
        self.buildSplat(self.splatScale, self.splatColor)
        base.audio3d.attachSoundToObject(self.hitSfx, self.splat)
        self.splat.reparentTo(render)
        self.splat.setPos(self.splatPos)
        base.playSfx(self.hitSfx, node = self.splat)
        self.cleanupEntity(self.splatPos)
        self.splatPos = None
        taskMgr.doMethodLater(0.5, self.delSplat, 'Delete Splat')
        return

    def cleanupEntity(self, pos):
        closestPie = None
        trackOfClosestPie = None
        pieHash2range = {}
        for entity, track in self.entities:
            if not entity.isEmpty():
                pieHash2range[hash(entity)] = (entity.getPos(render) - pos).length()
        ranges = []
        for distance in pieHash2range.values():
            ranges.append(distance)
        ranges.sort()
        for pieHash in pieHash2range.keys():
            distance = pieHash2range[pieHash]
            if not distance is None and distance == ranges[0]:
                for entity, track in self.entities:
                    if hash(entity) == pieHash:
                        closestPie = entity
                        trackOfClosestPie = track
                        break
            break
        if closestPie != None and trackOfClosestPie != None:
            if [closestPie, trackOfClosestPie] in self.entities:
                self.entities.remove([closestPie, trackOfClosestPie])
            if not closestPie.isEmpty():
                if isinstance(closestPie, Actor):
                    closestPie.cleanup()
                closestPie.removeNode()

    def onCollision(self, entry):
        intoNP = entry.getIntoNodePath()
        avNP = intoNP.getParent()
        fromNP = entry.getFromNodePath().getParent()

        if fromNP.isEmpty():
            return

        for key in base.cr.doId2do.keys():
            obj = base.cr.doId2do[key]
            if obj.__class__.__name__ in CIGlobals.SuitClasses:
                if obj.getKey() == avNP.getKey():
                    obj.sendUpdate('hitByGag', [self.getID()])
            elif obj.__class__.__name__ == "DistributedToon":
                if obj.getKey() == avNP.getKey():
                    if obj.getHealth() < obj.getMaxHealth():
                        if obj != self.avatar:
                            self.avatar.sendUpdate('toonHitByPie', [obj.doId, self.getID()])
                        else:
                            self.avatar.acceptOnce('gagSensor-into', self.onCollision)
                            return
            elif obj.__class__.__name__ == "DistributedPieTurret":
                if obj.getKey() == avNP.getKey():
                    if obj.getHealth() < obj.getMaxHealth():
                        self.avatar.sendUpdate('toonHitByPie', [obj.doId, self.getID()])

        self.splatPos = fromNP.getPos()
        self.avatar.sendUpdate('setSplatPos', [self.getID(), self.splatPos.getX(), self.splatPos.getY(), self.splatPos.getZ()])
        self.handleSplat()

    def buildCollisions(self, entity):
        pieSphere = CollisionSphere(0, 0, 0, 1)
        pieSensor = CollisionNode('gagSensor')
        pieSensor.addSolid(pieSphere)
        pieNP = entity.attachNewNode(pieSensor)
        pieNP.setCollideMask(BitMask32(0))
        pieNP.node().setFromCollideMask(CIGlobals.WallBitmask | CIGlobals.FloorBitmask)

        event = CollisionHandlerEvent()
        event.set_in_pattern("%fn-into")
        event.set_out_pattern("%fn-out")
        base.cTrav.add_collider(pieNP, event)
        self.avatar.acceptOnce('gagSensor-into', self.onCollision)

    def unEquip(self):
        taskMgr.remove("hidePowerBarTask" + str(hash(self)))
        if self.powerBar:
            self.powerBar.hide()
        Gag.unEquip(self)

    def delete(self):
        taskMgr.remove("powerBarUpdate" + str(hash(self)))
        taskMgr.remove("hidePowerBarTask" + str(hash(self)))
        if self.powerBar:
            self.powerBar.destroy()
            self.powerBar = None
        self.clearAnimTrack()
        Gag.delete(self)
