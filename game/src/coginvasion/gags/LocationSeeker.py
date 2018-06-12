"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file LocationSeeker.py
@author Maverick Liberty
@date July 24, 2015

"""

from panda3d.core import Point3, NodePath, CardMaker
from panda3d.bullet import BulletGhostNode

from direct.interval.IntervalGlobal import Sequence, Func, Parallel, LerpHprInterval, LerpScaleInterval

from src.coginvasion.globals import CIGlobals
from src.coginvasion.phys import PhysicsUtils

class LocationSeeker:

    MovedEpsilon = 0.25

    GoodCS = (0.0, 1.0, 0.0, 0.6)
    BadCS = (1.0, 0.0, 0.0, 0.6)
    
    def __init__(self, avatar, gag, minDistance, maxDistance, shadowScale = 1):
        self.dropShadowPath = 'phase_3.5/models/props/glow.bam'
        self.rejectSoundPath = 'phase_4/audio/sfx/ring_miss.ogg'
        self.moveShadowTaskName = 'Move Shadow'
        self.locationSelectedName = 'Location Selected'
        self.dropShadow = None
        self.shadowScale = shadowScale
        self.gag = gag
        self.rejectSfx = loader.loadSfx(self.rejectSoundPath)
        self.confirmSfx = loader.loadSfx('phase_3/audio/sfx/GUI_create_toon_back.ogg')
        self.avatar = avatar
        self.minDistance = minDistance
        self.maxDistance = maxDistance
        self.moveShadowEventName = 'LocationSeeker-MoveShadow'
        self.prevPos = Point3(0)

        self.confirmIndTrack = None

        self.goodSpot = False
        
    def startSeeking(self):
        if not hasattr(self, 'avatar') or (hasattr(self, 'avatar') and not self.avatar): return
        self.cleanupShadow()
        self.buildShadow()
        
        # Let's increase the distance if the shadow is smaller than expected.
        scale = self.dropShadow.getScale()
        if scale < 1.0:
            self.maxDistance += 40
            
        # Let's setup the drop shadow's initial position.
        x, y, z = self.avatar.getPos(render)
        self.dropShadow.reparentTo(render)
        self.dropShadow.setPos(x, y + 5, z)
        
        # Finally, let's start moving the shadow with the mouse and accept left mouse clicks.
        base.taskMgr.add(self.__moveShadow, self.moveShadowTaskName)
        self.avatar.accept('mouse1', self.locationChosen)
        
    def stopSeeking(self):
        self.avatar.ignore('mouse1')
        base.taskMgr.remove(self.moveShadowTaskName)
        
    def __moveShadow(self, task):
        if base.mouseWatcherNode.hasMouse():

            currPos = self.dropShadow.getPos(render)
            if (currPos - self.prevPos).length() >= self.MovedEpsilon:
                # Shadow moved.
                messenger.send(self.moveShadowEventName)

            mouse = base.mouseWatcherNode.getMouse()
            pFrom = Point3(0)
            pTo = Point3(0)
            base.camLens.extrude(mouse, pFrom, pTo)

            pFrom = render.getRelativePoint(base.cam, pFrom)
            pTo = render.getRelativePoint(base.cam, pTo)

            groups = [CIGlobals.WallGroup, CIGlobals.FloorGroup, CIGlobals.StreetVisGroup]

            result, hits = PhysicsUtils.rayTestAllSorted(pFrom, pTo,
                                                      (CIGlobals.WallGroup |
                                                       CIGlobals.FloorGroup |
                                                       CIGlobals.StreetVisGroup))
            if result.hasHits():
                for i in xrange(len(hits)):
                    hit = hits[i]
                    node = hit.getNode()
                    if node.isOfType(BulletGhostNode.getClassType()):
                        continue
                    mask = node.getIntoCollideMask()

                    # Figure out what we hit.
                    if mask not in groups:
                        # Ignore this hit.
                        continue
                    elif mask == CIGlobals.WallGroup:
                        # A wall is blocking the floor, bad spot!
                        self.goodSpot = False
                        break
                    else:
                        # The other two possibilities are floors, so this must be a good spot.
                        self.dropShadow.setPos(hit.getHitPos())
                        self.goodSpot = True
                        break
            else:
                # We might be aiming at the sky or something? Bad spot!
                self.goodSpot = False

            distance = self.avatar.getDistance(self.dropShadow)
            if self.goodSpot and (distance < self.minDistance or distance > self.maxDistance):
                # Spot is either too close or too far, guess it's not a good spot after all.
                self.goodSpot = False

            if self.goodSpot:
                self.dropShadow.setColorScale(self.GoodCS, 1)
            else:
                self.dropShadow.setColorScale(self.BadCS, 1)

            self.prevPos = currPos

        return task.cont
        
    def locationChosen(self):
        if self.goodSpot:
            self.avatar.ignore('mouse1')
            base.taskMgr.remove(self.moveShadowTaskName)
            x, y, z = self.getLocation()
            self.avatar.sendUpdate('setDropLoc', [self.gag.getID(), x, y, z])
            messenger.send(self.locationSelectedName)
            self.confirmSfx.play()
            self.confirmIndTrack.start()
        else:
            self.rejectSfx.play()
        
    def buildShadow(self):
        self.cleanupShadow()
        if not self.dropShadowPath or not self.avatar: return
        
        self.dropShadow = NodePath('locationIndicatorRoot')

        cm = CardMaker('locationIndicator')
        cm.setFrame(-1, 1, -1, 1)
        indicatorNP = self.dropShadow.attachNewNode(cm.generate())
        indicatorNP.setTexture(loader.loadTexture(self.gag.crosshair.crosshairTex), 1)
        indicatorNP.setScale(self.shadowScale * 2.5)
        indicatorNP.setDepthOffset(5)
        indicatorNP.setTransparency(1)
        indicatorNP.setP(-90)

        self.confirmIndTrack = Sequence(Parallel(LerpHprInterval(self.dropShadow, duration = 0.2, hpr = (360, 0, 0), startHpr = (0, 0, 0)),
                                                 LerpScaleInterval(self.dropShadow, duration = 0.2, scale = 0.01, startScale = 1)),
                                        Func(self.gag.cleanupLocationSeeker))
        
    def setShadowType(self, isCircle = False, scale = 1):
        self.shadowScale = scale
        
    def getDropShadow(self):
        return self.dropShadow
        
    def getLocation(self):
        if self.dropShadow:
            return self.dropShadow.getPos(render)
        return self.avatar.getPos(render)
    
    def getLocationSelectedName(self):
        return self.locationSelectedName
    
    def getShadowMovedName(self):
        return self.moveShadowEventName
    
    def cleanupShadow(self):
        if hasattr(self, 'dropShadow') and self.dropShadow:
            self.dropShadow.removeNode()
            self.dropShadow = None
            
    def cleanup(self):
        if hasattr(self, 'avatar') and self.avatar:
            if self.confirmIndTrack:
                self.confirmIndTrack.pause()
                self.confirmIndTrack = None
            base.taskMgr.remove(self.moveShadowTaskName)
            self.avatar.ignore('mouse1')
            self.cleanupShadow()
            self.rejectSfx.stop()
            self.rejectSfx = None
            self.avatar = None
            self.dropShadowPath = None
            self.rejectSoundPath = None
            self.locationSelectedName = None
            self.moveShadowTaskName = None
            self.moveShadowEventName = None
            del self.minDistance
            del self.maxDistance
            del self.dropShadow
            del self.shadowScale
            del self.rejectSfx
            del self.avatar
            del self.dropShadowPath
            del self.rejectSoundPath
            del self.locationSelectedName
            del self.moveShadowTaskName
            del self.moveShadowEventName
        