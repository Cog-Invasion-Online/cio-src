"""

  Filename: SquirtGag.py
  Created by: DecodedLogic (10Jul15)

"""

from src.coginvasion.gags import GagGlobals
from src.coginvasion.gags.Gag import Gag
from src.coginvasion.gags.GagType import GagType
from src.coginvasion.globals import CIGlobals
from direct.interval.IntervalGlobal import Sequence, Func, Wait, LerpScaleInterval, Parallel
from direct.interval.IntervalGlobal import ActorInterval
from pandac.PandaModules import Point3, Vec3, NodePath, CollisionSphere, CollisionHandlerEvent, CollisionNode
import abc

class SquirtGag(Gag):

    def __init__(self, name, model, damage, hitSfx, spraySfx, missSfx, toonAnim, enableReleaseFrame, completeSquirtFrame, startAnimFrame = 0, scale = 1, playRate = 1):
        Gag.__init__(self, name, model, damage, GagType.SQUIRT, hitSfx, scale = scale, autoRelease = True, playRate = playRate)
        self.sprayScale = GagGlobals.splatSizes.get(self.name)
        self.spraySfx = None
        self.missSfx = None
        self.origin = None
        self.sprayRange = None
        self.spray = None
        self.sprayJoint = None
        self.canSquirt = False
        self.hitSomething = False
        self.toonAnim = toonAnim
        self.startAnimFrame = 0
        self.enableReleaseFrame = enableReleaseFrame
        self.completeSquirtFrame = completeSquirtFrame
        self.lastFrame = 0
        self.tracks = None
        self.sprayTrack = None
        self.sprayAttempt = None
        self.sprayRotation = Vec3(0, 0, 0)

        if game.process == 'client':
            if spraySfx:
                self.spraySfx = base.audio3d.loadSfx(spraySfx)
            if missSfx:
                self.missSfx = base.audio3d.loadSfx(missSfx)

    def start(self):
        Gag.start(self)
        if self.sprayTrack:
            self.sprayTrack.pause()
            self.sprayTrack = None
        if self.tracks:
            self.tracks.pause()
            self.tracks = None
        if self.anim:
            self.build()
            self.equip()
            duration = base.localAvatar.getDuration(self.toonAnim, toFrame = self.enableReleaseFrame)
            self.sprayAttempt = Parallel(ActorInterval(self.avatar, self.toonAnim, startFrame = self.startAnimFrame, endFrame = self.enableReleaseFrame, playRate = self.playRate),
                     Wait(duration - 0.15), Func(self.setSquirtEnabled, True)).start()

    def startSquirt(self, sprayScale, containerHold):
        def startSpray():
            self.doSpray(sprayScale, containerHold, sprayScale)
        Sequence(ActorInterval(self.avatar, self.toonAnim, startFrame = self.enableReleaseFrame, endFrame = self.completeSquirtFrame), Func(startSpray)).start()

    def setSquirtEnabled(self, flag):
        self.canSquirt = flag
        self.sprayAttempt = None

    def doSpray(self, scaleUp, scaleDown, hold, horizScale = 1.0, vertScale = 1.0):
        base.audio3d.attachSoundToObject(self.spraySfx, self.gag)
        base.playSfx(self.spraySfx, node = self.gag)
        spraySequence = self.getSprayTrack(self.origin, self.sprayRange, scaleUp, hold, scaleDown, horizScale, vertScale)
        self.sprayTrack = spraySequence
        self.sprayTrack.start()

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

    def onCollision(self, entry):
        self.hitSomething = True
        base.audio3d.attachSoundToObject(self.hitSfx, self.sprayNP)
        base.playSfx(self.hitSfx, node = self.sprayNP)
        intoNP = entry.getIntoNodePath()
        avNP = intoNP.getParent()
        if self.avatar.doId == base.localAvatar.doId:
            for key in base.cr.doId2do.keys():
                obj = base.cr.doId2do[key]
                if obj.__class__.__name__ in CIGlobals.SuitClasses:
                    if obj.getKey() == avNP.getKey():
                        obj.sendUpdate('hitByGag', [self.getID()])
                elif obj.__class__.__name__ == "DistributedToon":
                    if obj.getKey() == avNP.getKey():
                        if obj.getHealth() < obj.getMaxHealth():
                            self.avatar.sendUpdate('toonHitByPie', [obj.doId, self.getID()])
        if base.localAvatar == self.avatar:
            self.splatPos = self.sprayNP.getPos(render)
            gagPos = self.sprayNP.getPos(render)
            self.handleSplat()
            self.avatar.sendUpdate('setSplatPos', [self.getID(), gagPos.getX(), gagPos.getY(), gagPos.getZ()])

    def handleMiss(self):
        if self.spray and self.hitSomething == False:
            base.audio3d.attachSoundToObject(self.missSfx, self.spray)
            base.playSfx(self.missSfx, node = self.spray)
            self.cleanupSpray()

    def handleSplat(self):
        self.cleanupSplat()
        self.buildSplat(GagGlobals.splatSizes.get(self.getName()), GagGlobals.WATER_SPRAY_COLOR)
        self.splat.setPos(self.splatPos)
        self.splat.reparentTo(render)
        self.splatPos = None
        taskMgr.doMethodLater(0.5, self.delSplat, 'Delete Splat')

    def getSprayTrack(self, origin, target, scaleUp, hold, scaleDown, horizScale = 1.0, vertScale = 1.0):
        if self.sprayJoint.isEmpty():
            self.build()
            self.origin = self.getSprayStartPos()
        base.localAvatar.stop(self.toonAnim)
        self.lastFrame = self.avatar.getCurrentFrame(self.toonAnim)
        track = Sequence()
        sprayProp = loader.loadModel(GagGlobals.SPRAY_MDL)
        sprayProp.setTwoSided(1)
        sprayScale = hidden.attachNewNode('spray-parent')
        sprayRot = hidden.attachNewNode('spray-rotate')
        sprayRot.setColor(GagGlobals.WATER_SPRAY_COLOR)
        sprayRot.setTransparency(1)

        collNode = CollisionNode('Collision')
        spraySphere = CollisionSphere(0, 0, 0, 1)
        spraySphere.setTangible(0)
        collNode.addSolid(spraySphere)
        collNode.setCollideMask(CIGlobals.WallBitmask)
        sprayNP = sprayRot.attachNewNode(collNode)
        sprayNP.setY(1)
        self.sprayNP = sprayNP
        event = CollisionHandlerEvent()
        event.set_in_pattern("%fn-into")
        event.set_out_pattern("%fn-out")
        base.cTrav.add_collider(sprayNP, event)
        self.avatar.acceptOnce(sprayNP.node().getName() + '-into', self.onCollision)

        def showSpray(sprayScale, sprayProp, origin, target):
            objects = [sprayRot, sprayScale, sprayProp]
            for item in objects:
                index = objects.index(item)
                if index == 0:
                    item.reparentTo(self.sprayJoint)
                    item.setPos(0, 0, 0)
                    item.setHpr(self.sprayRotation)
                    item.wrtReparentTo(render)
                else:
                    item.reparentTo(objects[index - 1])

        track.append(Func(showSpray, sprayScale, sprayProp, origin, target))
        self.spray = sprayRot

        def calcTargetScale():
            distance = Vec3(target - origin).length()
            yScale = distance / GagGlobals.SPRAY_LEN
            targetScale = Point3(yScale * horizScale, yScale, yScale * vertScale)
            return targetScale
        track.append(Parallel(LerpScaleInterval(sprayScale, scaleUp, calcTargetScale, startScale = GagGlobals.PNT3NEAR0), sprayNP.posInterval(0.25, self.spray.getPos(render) + Point3(0, 50, 0), startPos = self.spray.getPos(render) + Point3(0, 5, 0))))
        track.append(Wait(hold))
        track.append(Func(self.handleMiss))
        track.append(LerpScaleInterval(sprayScale, 0.75, GagGlobals.PNT3NEAR0))

        def hideSpray():
            lambda prop: prop.removeNode(), [sprayProp, sprayRot, sprayScale]
        track.append(Func(hideSpray))
        track.append(Func(self.completeSquirt))
        return track

    def getSprayRange(self):
        sprayRange = NodePath('Squirt Range')
        sprayRange.reparentTo(self.avatar)
        sprayRange.setScale(render, 1)
        sprayRange.setPos(0, 160, -90)
        sprayRange.setHpr(90, -90, 90)
        return sprayRange

    @abc.abstractmethod
    def getSprayStartPos(self):
        return Point3(0, 0, 0)

    def cleanupSpray(self):
        if self.spray:
            self.spray.removeNode()
            self.spray = None
        if self.sprayAttempt:
            self.sprayAttempt.pause()
            self.sprayAttempt = None
        self.hitSomething = False
        self.canSquirt = False
