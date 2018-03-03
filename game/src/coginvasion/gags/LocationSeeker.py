"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file LocationSeeker.py
@author Maverick Liberty
@date July 24, 2015

"""

from panda3d.core import CollisionNode, CollisionRay, CollisionHandlerQueue
from src.coginvasion.globals import CIGlobals

class LocationSeeker:
    
    def __init__(self, avatar, minDistance, maxDistance, shadowScale = 1):
        self.dropShadowPath = 'phase_3/models/props/square_drop_shadow.bam'
        self.rejectSoundPath = 'phase_4/audio/sfx/ring_miss.ogg'
        self.moveShadowTaskName = 'Move Shadow'
        self.locationSelectedName = 'Location Selected'
        self.dropShadow = None
        self.shadowScale = shadowScale
        self.rejectSfx = loader.loadSfx(self.rejectSoundPath)
        self.avatar = avatar
        self.cameraNode = None
        self.cameraRay = None
        self.cameraNP = None
        self.shadowNP = None
        self.shadowRay = None
        self.minDistance = minDistance
        self.maxDistance = maxDistance
        self.legacyMode = False
        self.collHdlFl = CollisionHandlerQueue()
        self.moveShadowEventName = 'LocationSeeker-MoveShadow'
        
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
        self.dropShadow.setPos(x, y + 5, z + 2)
        
        # Let's setup the collisions for the mouse.
        self.cameraNode = CollisionNode('coll_camera')
        self.cameraNode.setFromCollideMask(CIGlobals.WallBitmask)
        self.cameraRay = CollisionRay()
        self.cameraNode.addSolid(self.cameraRay)
        self.cameraNP = camera.attachNewNode(self.cameraNode)
        base.cTrav.addCollider(self.cameraNP, CollisionHandlerQueue())
        
        if not self.legacyMode:
            # Let's setup the collisions for the shadow.
            shadowNode = CollisionNode('coll_shadow')
            self.shadowRay = CollisionRay(0, 0, 6, 0, 0, -1)
            shadowNode.addSolid(self.shadowRay)
            shadowNode.setFromCollideMask(CIGlobals.FloorBitmask)
            self.shadowNP = self.dropShadow.attachNewNode(shadowNode)
            base.cTrav.addCollider(self.shadowNP, self.collHdlFl)
        
        # Finally, let's start moving the shadow with the mouse and accept left mouse clicks.
        base.taskMgr.add(self.__moveShadow, self.moveShadowTaskName)
        self.avatar.acceptOnce('mouse1', self.locationChosen)
        
    def stopSeeking(self):
        base.taskMgr.remove(self.moveShadowTaskName)
        
    def __moveShadow(self, task):
        if base.mouseWatcherNode.hasMouse():
            prevPos = self.dropShadow.getPos(render)
            def PointAtZ(z, point, vec):
                if vec.getZ() != 0:
                    return point + vec * ((z-point.getZ()) / vec.getZ())
                else:
                    return self.getLocation()
            mouse = base.mouseWatcherNode.getMouse()
            self.cameraRay.setFromLens(base.camNode, mouse.getX(), mouse.getY())
            nearPoint = render.getRelativePoint(camera, self.cameraRay.getOrigin())
            nearVec = render.getRelativeVector(camera, self.cameraRay.getDirection())
            self.dropShadow.setPos(PointAtZ(.5, nearPoint, nearVec))
            if (prevPos - self.dropShadow.getPos(render)).length() >= 0.25:
                messenger.send(self.moveShadowEventName)
            if self.legacyMode:
                self.dropShadow.setZ(base.localAvatar.getZ(render) + 0.5)
            else:
                if self.collHdlFl.getNumEntries() > 0:
                    self.dropShadow.setZ(self.collHdlFl.getEntry(0).getSurfacePoint(render).getZ() + 0.5)
        return task.cont
        
    def locationChosen(self):
        base.taskMgr.remove(self.moveShadowTaskName)
        distance = self.avatar.getDistance(self.dropShadow)
        x, y, z = self.getLocation()
        if distance >= self.minDistance and distance <= self.maxDistance:
            gag = self.avatar.getBackpack().getActiveGag()
            self.avatar.sendUpdate('setDropLoc', [gag.getID(), x, y, z])
            messenger.send(self.locationSelectedName)
        else:
            self.rejectSfx.play()
            self.avatar.acceptOnce('mouse1', self.locationChosen)
            base.taskMgr.add(self.__moveShadow, self.moveShadowTaskName)
        
    def buildShadow(self):
        self.cleanupShadow()
        if not self.dropShadowPath or not self.avatar: return
        self.dropShadow = loader.loadModel(self.dropShadowPath)
        self.dropShadow.setScale(self.shadowScale)
        self.dropShadow.setName('LocationSeeker_Shadow')
        
    def setShadowType(self, isCircle = False, scale = 1):
        if not isCircle:
            self.dropShadowPath = 'phase_3/models/props/square_drop_shadow.bam'
        else:
            self.dropShadowPath = 'phase_3/models/props/drop_shadow.bam'
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
            if self.cameraNode:
                self.cameraNP.removeNode()
                self.cameraNP = None
                self.cameraNode = None
                self.cameraRay = None
                self.shadowNP.removeNode()
                self.shadowRay = None
                self.shadowNP = None
            
    def cleanup(self):
        if hasattr(self, 'avatar') and self.avatar:
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
            self.collHdlFl = None
            del self.collHdlFl
            del self.minDistance
            del self.maxDistance
            del self.legacyMode
            del self.dropShadow
            del self.cameraNP
            del self.cameraNode
            del self.cameraRay
            del self.shadowNP
            del self.shadowRay
            del self.shadowScale
            del self.rejectSfx
            del self.avatar
            del self.dropShadowPath
            del self.rejectSoundPath
            del self.locationSelectedName
            del self.moveShadowTaskName
            del self.moveShadowEventName
        