"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file DropGag.py
@author Maverick Liberty
@date July 16, 2015

"""

from src.coginvasion.gags.Gag import Gag
from src.coginvasion.gags.GagType import GagType
from src.coginvasion.gags.GagState import GagState
from src.coginvasion.phys.WorldCollider import WorldCollider
from src.coginvasion.globals import CIGlobals
from LocationGag import LocationGag
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Sequence, Func, SoundInterval, Wait, LerpScaleInterval, Parallel
from direct.interval.LerpInterval import LerpPosHprInterval,\
    LerpColorScaleInterval
from panda3d.core import CollisionHandlerFloor, Point3, TransparencyAttrib, Vec4
import abc

class DropGag(Gag, LocationGag):
    notify = directNotify.newCategory('DropGag')

    def __init__(self, name, model, anim, damage, hitSfx, missSfx, scale, playRate):
        Gag.__init__(self, name, model, damage, GagType.DROP, hitSfx, anim = anim, playRate = playRate,
                     scale = scale, autoRelease = True)
        LocationGag.__init__(self, 3, 50)
        self.crosshair.wantCrosshair = False
        self.holdGag = False
        self.missSfx = None
        self.fallSoundPath = 'phase_5/audio/sfx/incoming_whistleALT.ogg'
        self.fallSoundInterval = None
        self.fallSfx = None
        self.chooseLocFrame = 34
        self.completeFrame = 77
        self.collHandlerF = CollisionHandlerFloor()
        self.fallDuration = 0.75
        self.isDropping = False
        self.timeout = 3.0
        if game.process == 'client':
            self.missSfx = base.audio3d.loadSfx(missSfx)
            self.fallSfx = base.audio3d.loadSfx(self.fallSoundPath)

        self.dropCollider = None
        self.colliderRadius = 0.75
        self.colliderOfs = Point3(0)

        self.dropMdl = None

        # Variables to handle the drop preview with large drops.
        self.crashSite = None
        self.crashSiteGag = None
        self.crashSiteShadow = None
        self.crashSiteIval = None
        self.crashStartPos = None
        self.crashEndPos = None
        self.crashBegun = False
        self.shadowIdleTaskName = 'Handle-IdleShadow'

        self.lastShadowMoveTime = 0.0

    def build(self):
        self.gag = hidden.attachNewNode('dropGagRoot')
        self.dropMdl = loader.loadModel(self.model)
        self.dropMdl.reparentTo(self.gag)
        self.dropMdl.setScale(self.scale)
        self.dropMdl.setName(self.getName())
        base.audio3d.attachSoundToObject(self.fallSfx, self.gag)
        base.audio3d.attachSoundToObject(self.missSfx, self.gag)

    def tickShadowIdleTask(self, task):
        time = globalClock.getFrameTime()
        if time - self.lastShadowMoveTime >= 0.25:
            self.startCrashEffect()
        return task.cont

    def __shadowMoved(self):
        self.lastShadowMoveTime = globalClock.getFrameTime()

        if self.crashSite:
            self.cleanupCrashIval()
            self.crashSite.hide()

    def startCrashEffect(self):
        if not self.getLocationSeeker() or self.crashBegun:
            return
        self.cleanupCrashIval()
        self.crashBegun = True
        if self.crashSite is None:
            self.crashSite = loader.loadModel('phase_6/models/props/piano.bam')
            self.crashSite.setScale(0.5)
            self.crashSite.setTransparency(TransparencyAttrib.MAlpha)
            self.crashSite.setColorScale(1.0, 1.0, 1.0, 0.25)
            self.crashSite.reparentTo(render)
            self.crashSiteGag = self.crashSite.find('**/crashed_piano')
            self.crashSiteGag.setTransparency(TransparencyAttrib.MAlpha)
            self.crashSiteShadow = self.crashSite.find('**/shadow_crack')

            # Clean up the collision nodes.
            for node in self.crashSite.findAllMatches('**/*coll*'):
                node.removeNode()
        self.crashSite.show()

        dropShadow = self.getLocationSeeker().getDropShadow()
        if not dropShadow:
            return
        location = self.getLocationSeeker().getDropShadow().getPos(render)
        self.crashSite.setPos(location.getX(), location.getY(), location.getZ())
        self.crashEndPos = self.crashSiteShadow.getPos()
        self.crashStartPos = Point3(self.crashEndPos.getX(), self.crashEndPos.getY(),
            self.crashEndPos.getZ() + 8.5)

        self.crashSiteIval = Sequence(
            Func(self.crashSiteShadow.hide),
            Func(self.crashSiteGag.headsUp, base.localAvatar),
            Parallel(
                Sequence(
                    LerpPosHprInterval(self.crashSiteGag, duration = 0.75, pos = self.crashEndPos, startPos = self.crashStartPos,
                        startHpr = Point3(0.0, 15.0, 21.30), hpr = Point3(0.0, 0.0, 0.0)),
                    Func(self.crashSiteShadow.show)
                ),
            ),
            LerpColorScaleInterval(self.crashSiteShadow, duration = 0.75, colorScale = Vec4(1.0, 1.0, 1.0, 0.0), startColorScale = Vec4(1.0, 1.0, 1.0, 1.0)),
            Func(self.crashSiteShadow.hide),
            Func(self.crashSiteShadow.setColorScale, 1.0, 1.0, 1.0, 1.0)
        )
        self.crashSiteIval.loop()


    def resetCrashEffect(self):
        base.taskMgr.remove(self.shadowIdleTaskName)
        base.ignore(self.getLocationSeeker().getShadowMovedName())
        self.cleanupCrashIval()
        if self.crashSite:
            self.crashSite.removeNode()
            self.crashSite = None
            self.crashSiteGag = None
            self.crashSiteShadow = None
            self.crashStartPos = None
            self.crashEndPos = None

    def cleanupCrashIval(self):
        self.crashBegun = False
        if self.crashSiteIval:
            self.crashSiteIval.pause()
            self.crashSiteIval = None

    def completeDrop(self):
        LocationGag.complete(self)
        self.isDropping = False
        if game.process != 'client':
            return
        self.reset()

    def equip(self):
        Gag.equip(self)
        LocationGag.equip(self)

        if self.isLocal() and self.getName() == CIGlobals.GrandPiano:
            base.taskMgr.add(self.tickShadowIdleTask, self.shadowIdleTaskName)
            base.accept(self.getLocationSeeker().getShadowMovedName(), self.__shadowMoved)

    def unEquip(self):
        LocationGag.cleanupLocationSeeker(self)
        super(DropGag, self).unEquip()
        if self.state != GagState.LOADED:
            self.completeDrop()

    def onActivate(self, ignore, suit):
        pass

    def buildCollisions(self):
        self.dropCollider = WorldCollider('dropGagCollider', self.colliderRadius, 'gagSensor-into',
                                          offset = self.colliderOfs)
        self.dropCollider.reparentTo(self.gag)
        self.avatar.acceptOnce('gagSensor-into', self.onCollision)

    def onCollision(self, intoNP):
        if not self.gag:
            return
        print "DropGag.onCollision:", intoNP
        avNP = intoNP.getParent()
        hitCog = False
        self.fallSoundInterval.pause()
        self.fallSoundInterval = None
        shrinkTrack = Sequence()
        if self.avatar.doId == base.localAvatar.doId:
            for key in base.cr.doId2do.keys():
                obj = base.cr.doId2do[key]
                if obj.__class__.__name__ in CIGlobals.SuitClasses:
                    if obj.getKey() == avNP.getKey():
                        dist = (obj.getPos(render).getXy() - self.gag.getPos(render).getXy()).length()
                        print dist
                        obj.sendUpdate('hitByGag', [self.getID(), dist * 4])
                        self.avatar.b_trapActivate(self.getID(), self.avatar.doId, 0, obj.doId)
                        hitCog = True
        gagObj = self.gag
        if hitCog:
            SoundInterval(self.hitSfx, node = self.gag).start()
            shrinkTrack.append(Wait(0.5))
        else:
            SoundInterval(self.missSfx, node = self.gag).start()
        shrinkTrack.append(Wait(0.25))
        shrinkTrack.append(LerpScaleInterval(self.dropMdl, 0.3, Point3(0.01, 0.01, 0.01)))
        shrinkTrack.append(Func(self.cleanupGag))
        shrinkTrack.start()

    def onSuitHit(self, suit):
        pass

    @abc.abstractmethod
    def startDrop(self):
        pass

    def cleanupGag(self):
        if not self.isDropping:
            super(DropGag, self).cleanupGag()
        if self.dropCollider:
            self.dropCollider.removeNode()
            self.dropCollider = None

    def release(self):
        print "release that bitch"
        if self.isLocal():
            self.startTimeout()
            self.resetCrashEffect()
        LocationGag.release(self)
        self.build()
        self.isDropping = True
        actorTrack = LocationGag.getActorTrack(self)
        self.fallSoundInterval = LocationGag.getSoundTrack(self)
        if actorTrack:
            actorTrack.append(Func(self.startDrop))
            actorTrack.start()
            self.fallSoundInterval.append(Parallel(SoundInterval(self.fallSfx)))
            self.fallSoundInterval.start()
        if self.isLocal():
            base.localAvatar.sendUpdate('usedGag', [self.id])

    def setEndPos(self, x, y, z):
        LocationGag.setDropLoc(self, x, y, z)
