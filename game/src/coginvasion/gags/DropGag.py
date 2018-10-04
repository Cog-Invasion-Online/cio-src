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
from src.coginvasion.gags import GagGlobals
from src.coginvasion.phys.WorldCollider import WorldCollider
from src.coginvasion.globals import CIGlobals
from LocationGag import LocationGag
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.IntervalGlobal import Sequence, Func, SoundInterval, Wait, LerpScaleInterval, Parallel
from direct.interval.LerpInterval import LerpPosHprInterval,\
    LerpColorScaleInterval
    
from panda3d.core import CollisionHandlerFloor, Point3, TransparencyAttrib, Vec4, NodePath

from datetime import datetime
import abc

SoundTrackName = 'SoundTrack'

class DropGag(Gag, LocationGag):
    notify = directNotify.newCategory('DropGag')

    def __init__(self, name, model, anim, damage, hitSfx, missSfx, scale, playRate):
        Gag.__init__(self, name, model, GagType.DROP, hitSfx, anim = anim, scale = scale)
        LocationGag.__init__(self, 3, 50)
        self.crosshair.wantCrosshair = False
        self.holdGag = False
        self.missSfx = None
        self.fallSoundPath = 'phase_5/audio/sfx/incoming_whistleALT.ogg'
        self.fallSfx = None
        self.chooseLocFrame = 34
        self.completeFrame = 77
        self.collHandlerF = CollisionHandlerFloor()
        self.fallDuration = 0.75
        self.isDropping = False
        self.timeout = 3.0
        if metadata.PROCESS == 'client':
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
        # Let's move away from using the `gag` attribute and instead
        # use a local scope `entity` attribute and return the entity.
        entity = hidden.attachNewNode('dropGagRoot')
        
        # We can't rely on an avatar doId nor a regular date. So let's use
        # seconds and microseconds.
        now = datetime.now()
        entity.setName('DropDebris-{0}'.format(now.strftime('%S %f')))
        
        dropMdl = loader.loadModel(self.model)
        dropMdl.reparentTo(entity)
        dropMdl.setScale(self.scale)
        dropMdl.setName('DropMdl')
        
        base.audio3d.attachSoundToObject(self.fallSfx, entity)
        base.audio3d.attachSoundToObject(self.missSfx, entity)

        return entity

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
        if self.getLocationSeeker():
            self.ignore(self.getLocationSeeker().getShadowMovedName())
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
        if metadata.PROCESS != 'client':
            return
        self.reset()

    def equip(self):
        Gag.equip(self)
        LocationGag.equip(self)

        if self.isLocal() and self.getName() == GagGlobals.GrandPiano:
            base.taskMgr.add(self.tickShadowIdleTask, self.shadowIdleTaskName)
            self.accept(self.getLocationSeeker().getShadowMovedName(), self.__shadowMoved)

    def unEquip(self):
        if self.isLocal():
            self.resetCrashEffect()
        LocationGag.cleanup(self)
        Gag.unEquip(self)
        if self.state != GagState.LOADED:
            self.completeDrop()

    def onActivate(self, ignore, suit):
        pass

    def buildCollisions(self, entity):
        dropCollider = WorldCollider('dropGagCollider', self.colliderRadius, 'gagSensor-into',
                                          offset = self.colliderOfs)
        dropCollider.reparentTo(entity)
        self.avatar.acceptOnce('gagSensor-into', self.onCollision, extraArgs = [entity])

    def onCollision(self, entity, intoNP):
        if not entity or entity.isEmpty():
            return
        
        dropMdl = entity.find('**/DropMdl')
        soundTrack = entity.getPythonTag(SoundTrackName)
        print entity.getName()
        print "DropGag.onCollision:", intoNP
        avNP = intoNP.getParent()
        hitCog = False
        soundTrack.pause()
        shrinkTrack = Sequence()
        if self.avatar.doId == base.localAvatar.doId:
            for obj in base.avatars:
                if CIGlobals.isAvatar(obj) and obj.getKey() == avNP.getKey():
                    dist = (obj.getPos(render).getXy() - entity.getPos(render).getXy()).length()
                    print dist
                    obj.handleHitByToon(self.avatar, self.getID(), dist * 4)
                    doId = 0 if not obj.isDistributed() else obj.doId
                    self.avatar.b_trapActivate(self.getID(), self.avatar.doId, 0, doId)
                    hitCog = True

        if hitCog:
            base.audio3d.attachSoundToObject(self.hitSfx, entity)
            SoundInterval(self.hitSfx, node = entity).start()
            shrinkTrack.append(Wait(0.5))
        else:
            base.audio3d.attachSoundToObject(self.missSfx, entity)
            SoundInterval(self.missSfx, node = entity).start()
        shrinkTrack.append(Wait(0.25))
        shrinkTrack.append(LerpScaleInterval(dropMdl, 0.3, Point3(0.01, 0.01, 0.01)))
        shrinkTrack.append(Func(self.clearEntity, entity))
        shrinkTrack.start()

    def onSuitHit(self, suit):
        pass

    @abc.abstractmethod
    def startDrop(self, entity):
        pass

    def cleanupGag(self):
        if not self.isDropping:
            super(DropGag, self).cleanupGag()
            
    def clearEntity(self, entity):
        if entity and not entity.isEmpty():
            # We have to explicitly remove the world collider.
            for child in entity.findAllMatches('*'):
                if isinstance(child, NodePath) and not child.isEmpty():
                    child.removeNode()

            entity.removeNode()

    def release(self):
        print "release that bitch"
        if self.isLocal():
            self.startTimeout()
            self.resetCrashEffect()
        LocationGag.release(self)
        entity = self.build()
        self.isDropping = True
        actorTrack = LocationGag.getActorTrack(self)
        soundTrack = LocationGag.getSoundTrack(self)
        if actorTrack:
            actorTrack.append(Func(self.startDrop, entity))
            actorTrack.start()
            soundTrack.append(Parallel(SoundInterval(self.fallSfx)))
            soundTrack.start()
        entity.setPythonTag(SoundTrackName, soundTrack)
        if self.isLocal():
            base.localAvatar.sendUpdate('usedGag', [self.id])

    def setEndPos(self, x, y, z):
        LocationGag.setDropLoc(self, x, y, z)
