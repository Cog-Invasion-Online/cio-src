"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file WaterReflectionManager.py
@author Brian Lach
@date September 26, 2017
@author Brian Lach
@date July 04, 2018

"""

from panda3d.core import (BitMask32, Plane, NodePath, CullFaceAttrib, Texture,
                          TextureStage, Point3, PlaneNode, VBase4, Vec3, WindowProperties,
                          FrameBufferProperties, GraphicsPipe, GraphicsOutput, TransparencyAttrib,
                          Material, WeakNodePath, RigidBodyCombiner, AntialiasAttrib, CardMaker,
                          BoundingBox)

from direct.gui.DirectGui import OnscreenImage
from direct.filter.FilterManager import FilterManager

import math

from src.coginvasion.globals import CIGlobals
from src.coginvasion.base.Lighting import LightingConfig, OutdoorLightingConfig

REFL_CAM_BITMASK = BitMask32.bit(10)

class WaterNode(NodePath):
    Nothing = 0
    Touching = 2
    Submerged = 4

    def __init__(self, size, pos, depth):
        NodePath.__init__(self, 'waterNode')
        self.setPos(pos)

        self.height = pos[2]

        topCard = CardMaker('waterTop')
        topCard.setFrame(-size, size, -size, size)
        self.topNP = self.attachNewNode(topCard.generate())
        self.topNP.setP(-90)
        self.topNP.clearModelNodes()
        self.topNP.flattenStrong()

        botCard = CardMaker('waterBot')
        botCard.setFrame(-size, size, -size, size)
        self.botNP = self.attachNewNode(botCard.generate())
        self.botNP.setP(90)
        self.botNP.clearModelNodes()
        self.botNP.flattenStrong()

        # Create an AABB which defines the volume of this water.
        self.aabb = BoundingBox(Point3(-size, -size, -depth), Point3(size, size, 0))
        self.aabb.xform(self.getMat(render))

    def isInWater(self, bottom, top):
        return self.aabb.contains(bottom, top)

    def isTouchingWater(self, position):
        return self.aabb.contains(position) != BoundingBox.IFNoIntersection

    def removeNode(self):
        self.topNP.removeNode()
        del self.topNP
        self.botNP.removeNode()
        del self.botNP
        del self.aabb
        del self.height
        NodePath.removeNode(self)

class WaterScene:

    def __init__(self, name, reso, height, planeVec, reflection = False, needDepth = False):
        buffer = base.win.makeTextureBuffer(name, reso, reso)
        buffer.setSort(-1)
        buffer.setClearColorActive(True)
        buffer.setClearColor(base.win.getClearColor())

        self.buffer = buffer
        
        self.camera = base.makeCamera(buffer)
        self.camera.node().setLens(base.camLens)
        self.camera.node().setCameraMask(REFL_CAM_BITMASK)

        self.texture = buffer.getTexture()
        self.texture.setWrapU(Texture.WMClamp)
        self.texture.setWrapV(Texture.WMClamp)
        self.texture.setMinfilter(Texture.FTLinearMipmapLinear)

        if needDepth:
            depthTex = Texture(name + "_depth")
            depthTex.setWrapU(Texture.WMClamp)
            depthTex.setWrapV(Texture.WMClamp)
            depthTex.setMinfilter(Texture.FTLinearMipmapLinear)

            buffer.addRenderTexture(depthTex, GraphicsOutput.RTMBindOrCopy,
                                    GraphicsOutput.RTPDepth)

            self.depthTex = depthTex

        self.plane = Plane(planeVec, Point3(0, 0, height))
        self.planeNode = PlaneNode(name + "_plane", self.plane)
        self.planeNP = render.attachNewNode(self.planeNode)
        tmpnp = NodePath("StateInitializer")
        tmpnp.setClipPlane(self.planeNP)
        if reflection:
            tmpnp.setAttrib(CullFaceAttrib.makeReverse())
        else:
            tmpnp.setAttrib(CullFaceAttrib.makeDefault())
        # As an optimization, disable any kind of shaders (mainly the ShaderGenerator) on the
        # reflected/refracted scene.
        tmpnp.setShaderOff(10)
        tmpnp.setAntialias(0, 10)
        self.camera.node().setInitialState(tmpnp.getState())

        self.disable()

    def cleanup(self):
        if hasattr(self, 'planeNP'):
            del self.plane
            del self.planeNode
            self.planeNP.removeNode()
            del self.planeNP

        self.camera.removeNode()
        del self.camera

        del self.texture
        if hasattr(self, 'depthTex'):
            del self.depthTex

        self.buffer.clearRenderTextures()
        del self.buffer

    def enable(self):
        self.camera.unstash()
        self.camera.reparentTo(render)

    def disable(self):
        self.camera.reparentTo(hidden)
        self.camera.stash()

class WaterReflectionManager:

    def __init__(self):
        self.enabled = True
        self.cameraSubmerged = False
        self.localAvTouching = WaterNode.Nothing
        self.underwater = False
        self.underwaterFog = [VBase4(0.0, 0.3, 0.7, 1.0), 0.02]
        self.waterNodes = []

        self.uwFilterMgr = FilterManager(base.win, base.cam)
        self.dudv = loader.loadTexture("phase_14/maps/water_surface_dudv_old.png")
        self.uwFilterQuad = None
        self.colortex = Texture("filter-base-color")
        self.colortex.setWrapU(Texture.WMClamp)
        self.colortex.setWrapV(Texture.WMClamp)

        self.underwaterSound = base.loadSfx("phase_14/audio/sfx/AV_ambient_water.ogg")
        self.underwaterSound.setLoop(True)
        
        sMgr = CIGlobals.getSettingsMgr()
        self.reso = sMgr.ReflectionQuality[sMgr.getSetting("refl")]
        if self.reso == 0:
            self.enabled = False
            return

    def getHoodOLC(self):
        pg = base.cr.playGame
        if pg:
            hood = pg.hood
            if hood:
                if hasattr(hood, 'olc') and hood.olc:
                    return hood.olc
        return None

    def clearPlanes(self):
        if hasattr(self, 'reflPlaneNP'):
            del self.reflPlane
            del self.reflPlaneNode
            self.reflPlaneNP.removeNode()
            del self.reflPlaneNP
        if hasattr(self, 'refrPlaneNP'):
            del self.refrPlane
            del self.refrPlaneNode
            self.refrPlaneNP.removeNode()
            del self.refrPlaneNP

    def setupScene(self, height):
        self.reflScene = WaterScene("reflection", self.reso, height, Vec3(0, 0, 1), True)
        self.reflScene.enable()
        self.refrScene = WaterScene("refraction", self.reso, height, Vec3(0, 0, -1), needDepth = True)
        self.refrScene.enable()
        self.underwaterRefrScene = WaterScene("underwaterRefraction", self.reso, height, Vec3(0, 0, 1))
        self.underwaterRefrScene.disable()

    def isTouchingAnyWater(self, bottom, top):
        for waterNode in self.waterNodes:
            test = waterNode.isInWater(bottom, top)

            # TOUCHING, not submerged.
            if test & WaterNode.Touching and not test & WaterNode.Submerged:
                return [True, waterNode.height]

        return [False, 0.0]
    
    def addWaterNode(self, size, pos):
        if not self.enabled:
            return

        if len(self.waterNodes) == 0:
            # We will have to do 2 extra render passes to create the water.
            # One pass viewing only stuff that is above the water (reflection)
            # and another for viewing only what's underneath the water (refraction).
            # The shader will then take these 2 textures, do fancy effects,
            # and project a combined version of the 2 onto the water nodes.
            self.setupScene(pos[2])
            taskMgr.add(self.update, "waterRefl-update", sort = 45)

        node = WaterNode(size, pos, 50)

        node.reparentTo(render)
        node.hide(REFL_CAM_BITMASK)
        node.setTextureOff(1)
        node.setLightOff(1)
        node.setMaterialOff(1)
        node.setTransparency(1)

        node.topNP.setShader(loader.loadShader("phase_14/models/shaders/water.sha"))
        node.topNP.setShaderInput("refl", self.reflScene.texture)
        node.topNP.setShaderInput("refr", self.refrScene.texture)
        node.topNP.setShaderInput("dudv", self.dudv)
        node.topNP.setShaderInput("refr_depth", self.refrScene.depthTex)
        node.topNP.setShaderInput("dudv_tile", 0.02)
        node.topNP.setShaderInput("dudv_strength", 0.05)
        node.topNP.setShaderInput("move_factor", 0.0)
        node.topNP.setShaderInput("near", CIGlobals.DefaultCameraNear)
        node.topNP.setShaderInput("far", CIGlobals.DefaultCameraFar)
        node.topNP.setShaderInput("reflectivity", 1.0)
        node.topNP.setShaderInput("shine_damper", 1.5)
        node.topNP.setShaderInput("normal", loader.loadTexture("phase_14/maps/water_surface_normal.png"))

        currCfg = OutdoorLightingConfig.ActiveConfig
        if currCfg is not None and isinstance(currCfg, OutdoorLightingConfig):
            print "yes, we have an active config"
            dir = CIGlobals.anglesToVector(currCfg.sunAngle)
            col = currCfg.sun
        else:
            print "no, no active config"
            dir = CIGlobals.anglesToVector(base.loader.envConfig.defaultSunAngle)
            col = base.loader.envConfig.defaultSunColor

        print dir, col

        node.topNP.setShaderInput("lightdir", dir)
        node.topNP.setShaderInput("lightcol", col)

        node.botNP.setShader(loader.loadShader("phase_14/models/shaders/water_bottom.sha"))
        node.botNP.setShaderInput("refr", self.underwaterRefrScene.texture)
        node.botNP.setShaderInput("dudv", self.dudv)
        node.botNP.setShaderInput("dudv_tile", 0.02)
        node.botNP.setShaderInput("dudv_strength", 0.05)
        node.botNP.setShaderInput("move_factor", 0.0)

        self.waterNodes.append(node)

    def clearWaterNodes(self):
        if not self.enabled or len(self.waterNodes) == 0:
            return

        for waterNode in self.waterNodes:
            waterNode.removeNode()

        self.waterNodes = []
        self.cleanupScenes()

    def cleanupScenes(self):
        self.stopUpdateTask()

        self.reflScene.cleanup()
        del self.reflScene
        self.refrScene.cleanup()
        del self.refrScene
        self.underwaterRefrScene.cleanup()
        del self.underwaterRefrScene

    def stopUpdateTask(self):
        taskMgr.remove("waterRefl-update")

    def cleanup(self):
        if not self.enabled:
            return

        self.clearWaterNodes()

    def update(self, task):
        if not self.enabled:
            return task.done

        self.reflScene.camera.setMat(base.cam.getMat(render) * self.reflScene.plane.getReflectionMat())
        self.refrScene.camera.setMat(base.cam.getMat(render))
        self.underwaterRefrScene.camera.setMat(base.cam.getMat(render))

        time = globalClock.getFrameTime()
        moveFactor = 0.02 * time

        if self.uwFilterQuad:
            self.uwFilterQuad.setShaderInput("move_factor", moveFactor * 0.8)

        foundCamSubmerged = False
        foundLocalAvTouching = WaterNode.Nothing
        waterLocalAvIsTouching = None
        for waterNode in self.waterNodes:

            # Let's see if our camera is submerged in this water node.
            if not foundCamSubmerged:
                if waterNode.isTouchingWater(camera.getPos(render)):
                    foundCamSubmerged = True

            # Now, let's see if local avatar is touching this water node.
            if not foundLocalAvTouching:
                test = waterNode.isInWater(base.localAvatar.getPos(render),
                                           base.localAvatar.getPos(render) + (0, 0, base.localAvatar.getHeight()))
                if test != WaterNode.Nothing:
                    foundLocalAvTouching = test
                    waterLocalAvIsTouching = waterNode

            waterNode.topNP.setShaderInput("move_factor", moveFactor)
            waterNode.botNP.setShaderInput("move_factor", moveFactor)

        if foundCamSubmerged != self.cameraSubmerged:
            if foundCamSubmerged:
                self.reflScene.disable()
                self.refrScene.disable()
                self.underwaterRefrScene.enable()

                self.underwaterSound.play()
                olc = self.getHoodOLC()
                if olc:
                    olc.modifyFog(*self.underwaterFog)

                #self.uwFilterQuad = self.uwFilterMgr.renderSceneInto(colortex = self.colortex)
                #self.uwFilterQuad.setShader(loader.loadShader("phase_14/models/shaders/water_screen.sha"))
                #self.uwFilterQuad.setShaderInput("src", self.colortex)
                #self.uwFilterQuad.setShaderInput("dudv", loader.loadTexture("phase_14/maps/water_surface_dudv.png"))
                #self.uwFilterQuad.setShaderInput("dudv_tile", 1.3)
                #self.uwFilterQuad.setShaderInput("dudv_strength", 0.004)
                #self.uwFilterQuad.setShaderInput("move_factor", 0.0)
            else:
                #if self.uwFilterQuad:
                #    self.uwFilterQuad.removeNode()
                #    self.uwFilterQuad = None

                #self.uwFilterMgr.cleanup()

                self.underwaterRefrScene.disable()
                self.reflScene.enable()
                self.refrScene.enable()

                self.underwaterSound.stop()
                olc = self.getHoodOLC()
                if olc:
                    olc.resetFog()

        if self.localAvTouching != foundLocalAvTouching:
            if foundLocalAvTouching & WaterNode.Submerged:
                base.localAvatar.walkControls.setCurrentSurface('swim')
                if waterLocalAvIsTouching:
                    base.localAvatar.b_splash(base.localAvatar.getX(render),
                                              base.localAvatar.getY(render),
                                              waterLocalAvIsTouching.height)
            elif foundLocalAvTouching & WaterNode.Touching:
                base.localAvatar.walkControls.setCurrentSurface('ttslosh')
            else:
                base.localAvatar.walkControls.setCurrentSurface('hardsurface')

        self.cameraSubmerged = foundCamSubmerged
        self.localAvTouching = foundLocalAvTouching
        
        return task.cont
