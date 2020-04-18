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
                          BoundingBox, Shader, Geom, GeomVertexData, GeomVertexFormat, GeomTriangles, GeomNode, GeomVertexWriter,
                          VirtualFileSystem, DirectionalLight, GeomVertexArrayFormat, InternalName, FrameBufferProperties)

from direct.gui.DirectGui import OnscreenImage
from direct.filter.FilterManager import FilterManager

import math
import random

from src.coginvasion.globals import CIGlobals
from src.coginvasion.base.Lighting import LightingConfig, OutdoorLightingConfig

class FogSpec:

    def __init__(self, color = (0, 0.3, 0.7, 1), density = 0.008):
        self.color = color
        self.density = density

class AnimatedTexture:

    def __init__(self, texPath, frameRate, shaderInput = ""):
        self.texPath = texPath
        self.frameRate = frameRate
        self.shaderInput = shaderInput

class WaterSpec:

    def __init__(self, waterTint = (0, 0, 0, 1.0), fog = FogSpec(), dudv = AnimatedTexture('phase_14/maps/water_surface_dudv', 20, "dudv"),
                 staticTex = 'phase_13/maps/water3.jpg', normal = AnimatedTexture('phase_14/maps/water_surface_normal', 20, "normal_map"),
                 dudvTile = 0.1, dudvStrength = 0.1, moveFactor = (0.05, 0.05), reflectivity = 0.75, shineDamper = 1.5,
                 reflectFactor = 0.9, envMap = "phase_14/maps/envmap001a.png", cheap = True, splashTint = (1, 1, 1, 1)):
        self.tint = waterTint
        self.fog = fog
        
        self.splashTint = splashTint
		
        self.envMap = envMap

        self.dudv = dudv
        self.staticTex = staticTex
        self.normal = normal

        self.dudvTile = dudvTile
        self.dudvStrength = dudvStrength
        self.moveFactor = moveFactor
        self.reflectivity = reflectivity
        self.shineDamper = shineDamper
        self.reflectFactor = reflectFactor

        self.animatedTextures = []
        if self.isAnimated(self.staticTex):
            self.animatedTextures.append(self.staticTex)
        if self.isAnimated(self.dudv):
            self.animatedTextures.append(self.dudv)
        if self.isAnimated(self.normal):
            self.animatedTextures.append(self.normal)
        
        self.cheap = cheap
        
    def isAnimated(self, tex):
        return tex and isinstance(tex, AnimatedTexture)

defaultWaterSpecs = {
    
    'sewer': WaterSpec(waterTint = (0.25, 0.7, 0.2, 1.0), fog = FogSpec((0, 0.09, 0, 1), 0.025), staticTex = 'phase_14/maps/sewer_water.png',
                       reflectivity = 1.0, shineDamper = 1.0,
                       reflectFactor = 0.325, splashTint = (0.4, 0.6, 0.4, 0.7)),

    'pond': WaterSpec(reflectivity = 1.0),
    'lake': WaterSpec(),
    
    'ttcPond': WaterSpec(dudvTile = 0.1, fog = FogSpec(density = 0.0), reflectFactor = 0.5),
    'ddPond': WaterSpec(fog = FogSpec((38 / 255.0, 69 / 255.0, 166 / 255.0, 1), 0.04),
                        reflectFactor = 0.3, dudvStrength = 0.2, dudvTile = 0.15)
}

class WaterNode(NodePath):
    Nothing = 0
    Touching = 2
    Submerged = 4

    def __init__(self, size, pos, depth, mask, spec = WaterSpec()):
        NodePath.__init__(self, 'waterNode')
        self.setPos(pos)

        self.spec = spec
        self.pos = pos
        self.depth = depth
        self.size = size
        self.mask = mask
        self.height = pos[2]
        
        normal = (0, 0, 1)
        tangent = (normal[0], normal[2], -normal[1])
        binormal = (normal[2], normal[1], -normal[0])
        
        # Build array for new format.
        array = GeomVertexArrayFormat()
        array.addColumn(InternalName.make('vertex'), 3, Geom.NTFloat32, Geom.CPoint)
        array.addColumn(InternalName.make('texcoord'), 2, Geom.NTFloat32, Geom.CTexcoord)
        array.addColumn(InternalName.make('normal'), 3, Geom.NTFloat32, Geom.CVector)
        array.addColumn(InternalName.make('binormal'), 3, Geom.NTFloat32, Geom.CVector)
        array.addColumn(InternalName.make('tangent'), 3, Geom.NTFloat32, Geom.CVector)

        # Create and register format.
        format = GeomVertexFormat()
        format.addArray(array)
        format = GeomVertexFormat.registerFormat(format)

        vdata = GeomVertexData('waterPlanes', format, Geom.UHStatic)
        vdata.setNumRows(4)
        vtxWriter = GeomVertexWriter(vdata, 'vertex')
        tcWriter = GeomVertexWriter(vdata, 'texcoord')
        tnWriter = GeomVertexWriter(vdata, 'tangent')
        bnWriter = GeomVertexWriter(vdata, 'binormal')
        normWriter = GeomVertexWriter(vdata, 'normal')
        # top left corner
        vtxWriter.addData3f(size[0], size[3], 0)
        tcWriter.addData2f(0, 1)
        normWriter.addData3f(*normal)
        tnWriter.addData3f(*tangent)
        bnWriter.addData3f(*binormal)
        # bottom left corner
        vtxWriter.addData3f(size[0], size[2], 0)
        tcWriter.addData2f(0, 0)
        normWriter.addData3f(*normal)
        tnWriter.addData3f(*tangent)
        bnWriter.addData3f(*binormal)
        # top right corner
        vtxWriter.addData3f(size[1], size[3], 0)
        tcWriter.addData2f(1, 1)
        normWriter.addData3f(*normal)
        tnWriter.addData3f(*tangent)
        bnWriter.addData3f(*binormal)
        # bottom right corner
        vtxWriter.addData3f(size[1], size[2], 0)
        tcWriter.addData2f(1, 0)
        normWriter.addData3f(*normal)
        tnWriter.addData3f(*tangent)
        bnWriter.addData3f(*binormal)
        
        topTris = GeomTriangles(Geom.UHStatic)
        topTris.addVertices(0, 1, 2)
        topTris.addVertices(3, 2, 1)
        topGeom = Geom(vdata)
        topGeom.addPrimitive(topTris)
        self.topNP = self.attachNewNode(GeomNode('waterTop'))
        self.topNP.node().addGeom(topGeom)
        
        # Reverse the winding for the bottom water plane
        botTris = GeomTriangles(Geom.UHStatic)
        botTris.addVertices(2, 1, 0)
        botTris.addVertices(1, 2, 3)        
        botGeom = Geom(vdata)
        botGeom.addPrimitive(botTris)
        self.botNP = self.attachNewNode(GeomNode('waterBot'))
        self.botNP.node().addGeom(botGeom)

        # Create an AABB which defines the volume of this water.
        self.aabb = BoundingBox(Point3(size[0], size[2], -depth), Point3(size[1], size[3], 0))
        self.aabb.xform(self.getMat(render))
        
        self.cubemap = base.bspLoader.getClosestCubemapTexture(self.getPos(render))

        self.dudvFrame = 0

    def setup(self):
        self.reparentTo(render)
        self.hide(CIGlobals.ReflectionCameraBitmask | CIGlobals.RefractionCameraBitmask)
        #self.setLightOff(1)
        self.setMaterialOff(1)
        self.setTransparency(1)

    def disableEffects(self):
        self.topNP.clearShader()
        self.botNP.clearShader()

    def enableFakeEffect(self):
        self.disableEffects()

        staticTex = loader.loadTexture(self.spec.staticTex)
        self.topNP.setTexture(staticTex, 1)
        self.botNP.setTexture(staticTex, 1)

    def disableFakeEffect(self):
        self.topNP.clearTexture()
        self.botNP.clearTexture()

    def enableEffects(self, reflScene, refrScene, underwaterRefrScene):
        self.disableFakeEffect()

        static = loader.loadTexture(self.spec.staticTex)
        
        if not self.spec.cheap:
            self.topNP.setShader(Shader.load(Shader.SL_GLSL, "phase_14/models/shaders/water_v.glsl",
                                             "phase_14/models/shaders/water_f.glsl"), 2)
            self.topNP.setShaderInput("dudv", static)
            self.topNP.setShaderInput("dudv_tile", self.spec.dudvTile)
            self.topNP.setShaderInput("dudv_strength", self.spec.dudvStrength)
            self.topNP.setShaderInput("move_factor", self.spec.moveFactor)
            self.topNP.setShaderInput("near", CIGlobals.DefaultCameraNear)
            self.topNP.setShaderInput("far", CIGlobals.DefaultCameraFar)
            self.topNP.setShaderInput("normal_map", static)
            self.topNP.setShaderInput("fog_density", self.spec.fog.density)
            self.topNP.setShaderInput("fog_color", self.spec.fog.color)
            self.topNP.setShaderInput("water_tint", self.spec.tint)
            self.topNP.setShaderInput("reflect_factor", self.spec.reflectFactor)
            self.topNP.setShaderInput("static_depth", self.depth)

            self.botNP.setShader(Shader.load(Shader.SL_GLSL, "phase_14/models/shaders/water_bottom_v.glsl",
                                             "phase_14/models/shaders/water_bottom_f.glsl"), 2)
            self.botNP.setShaderInput("dudv", static)
            self.botNP.setShaderInput("dudv_tile", self.spec.dudvTile)
            self.botNP.setShaderInput("dudv_strength", self.spec.dudvStrength)
            self.botNP.setShaderInput("move_factor", self.spec.moveFactor)
            self.botNP.setShaderInput("water_tint", self.spec.tint)
        else:
            # We are doing cheap water
            self.topNP.setShader(Shader.load(Shader.SL_GLSL, "phase_14/models/shaders/water_cheap_v.glsl",
                                             "phase_14/models/shaders/water_cheap_f.glsl"), 2)
            self.topNP.setShaderInput("tex_scale", self.spec.dudvTile)
            self.topNP.setShaderInput("cube_map", self.cubemap)
            self.topNP.setShaderInput("normal_map", static)
            self.topNP.setShaderInput("base_map", static)
            self.topNP.setShaderInput("reflectivity", self.spec.reflectivity)
            self.topNP.setShaderInput("_exposureAdjustment", base.shaderGenerator.getExposureAdjustment())
            self.topNP.setShaderInput("water_tint", self.spec.tint)

        self.setTextureInputs(reflScene, refrScene, underwaterRefrScene)

    def setTextureInputs(self, reflScene, refrScene, underwaterRefrScene):
        if not self.spec.cheap:
            self.topNP.setShaderInput("refl", reflScene.texture)
            self.topNP.setShaderInput("refr", refrScene.texture)
            self.topNP.setShaderInput("refr_depth", refrScene.depthTex)

            self.botNP.setShaderInput("refr", underwaterRefrScene.texture)

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
        del self.pos
        del self.size
        del self.depth
        NodePath.removeNode(self)

class WaterScene:

    def __init__(self, name, reso, height, planeVec, reflection = False, needDepth = False):
        fbp = FrameBufferProperties()
        fbp.clear()
        fbp.set_depth_bits( 8 )
        fbp.set_force_hardware( True )
        fbp.set_rgba_bits( 8, 8, 8, 8 )
        fbp.set_stencil_bits( 0 )
        fbp.set_float_color( False )
        fbp.set_float_depth( False )
        fbp.set_stereo( False )
        fbp.set_accum_bits( 0 )
        fbp.set_aux_float( 0 )
        fbp.set_aux_rgba( 0 )
        fbp.set_aux_hrgba( 0 )
        fbp.set_coverage_samples( 0 )
        fbp.set_multisamples( 0 )
        
        buffer = base.win.makeTextureBuffer(name, reso, reso, None, False, fbp)
        buffer.setSort(-10000)
        buffer.disableClears()
        buffer.setClearDepthActive(True)

        self.buffer = buffer
        
        self.camera = base.makeCamera(buffer)
        self.camera.node().setLens(base.camLens)
        if reflection:
            self.camera.node().setCameraMask(CIGlobals.ReflectionCameraBitmask)
        else:
            self.camera.node().setCameraMask(CIGlobals.RefractionCameraBitmask)

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
        #tmpnp.setShaderOff(10)
        tmpnp.setLightOff(10)
        tmpnp.setAntialias(0, 10)
        self.camera.node().setInitialState(tmpnp.getState())

        self.disable()

    def cleanup(self):
        self.disable()
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
        self.underwaterFog = [VBase4(0.0, 0.3, 0.7, 1.0), 0.008]
        self.waterNodes = []
        self.hasScenes = False
        
        self.waterNodesQueue = []

        # name to list of textures for each frame
        self.dudvs = {}

        self.underwaterSound = None
        self.wadeSounds = []
        
        sMgr = CIGlobals.getSettingsMgr()
        self.reso = sMgr.ReflectionQuality[sMgr.getSetting("refl").getValue()]
        
        self.reflScene = None
        self.refrScene = None
        self.underwaterRefrScene = None
        
    def load(self):
        self.underwaterSound = base.loadSfx("phase_14/audio/sfx/AV_ambient_water.ogg")
        self.underwaterSound.setLoop(True)
        
        wades = 8
        for i in xrange(wades):
            sound = base.loadSfx("phase_14/audio/sfx/footsteps/wade{0}.wav".format(i + 1))
            sound.setVolume(0.6)
            self.wadeSounds.append(sound)

    def getDefaultSpec(self, name):
        return defaultWaterSpecs.get(name, WaterSpec())

    def playWadeSound(self):
        random.choice(self.wadeSounds).play()

    def hasWaterEffects(self, isExpensive = None):
        
        if isExpensive is None:
            expensive = False
            
            for water in self.waterNodes:
                if not water.spec.cheap:
                    expensive = True
                    break
        else:
            expensive = isExpensive
                
        return self.reso > 0 and expensive

    def getHoodOLC(self):
        if not hasattr(base.cr, 'playGame'):
            return None
            
        pg = base.cr.playGame
        if pg:
            hood = pg.hood
            if hood:
                if hasattr(hood, 'olc') and hood.olc:
                    return hood.olc
        return None
        
    def areScenesReady(self):
        if not self.hasWaterEffects():
            return True
            
        return (self.reflScene.buffer.isValid() and self.refrScene.buffer.isValid()
                and self.underwaterRefrScene.buffer.isValid())

    def setupScene(self, height, isExpensive = None):
        if self.hasWaterEffects(isExpensive):
            self.reflScene = WaterScene("reflection", self.reso, height, Vec3(0, 0, 1), True)
            self.reflScene.enable()
            self.refrScene = WaterScene("refraction", self.reso, height, Vec3(0, 0, -1), needDepth = True)
            self.refrScene.enable()
            self.underwaterRefrScene = WaterScene("underwaterRefraction", self.reso, height, Vec3(0, 0, 1))
            self.underwaterRefrScene.disable()
            self.hasScenes = True

        self.startUpdateTask()

    def isTouchingAnyWater(self, bottom, top):
        for waterNode in self.waterNodes:
            test = waterNode.isInWater(bottom, top)

            # TOUCHING, not submerged.
            if test & WaterNode.Touching and not test & WaterNode.Submerged:
                return [True, waterNode.height]

        return [False, 0.0]
        
    def doesLineGoUnderwater(self, start, end):
        for waterNode in self.waterNodes:
            if (not waterNode.isTouchingWater(start) and
            waterNode.isTouchingWater(end)):
                # Line starts outside of water and goes in
                return [True, waterNode]
        return [False, None]
    
    def addWaterNode(self, size, pos, depth = 50, spec = defaultWaterSpecs['sewer']):
        if not self.enabled:
            return
            
        if self.reso <= 0:
            # force cheap
            spec.cheap = True

        if not self.hasScenes:
            # We will have to do 2 extra render passes to create the water.
            # One pass viewing only stuff that is above the water (reflection)
            # and another for viewing only what's underneath the water (refraction).
            # The shader will then take these 2 textures, do fancy effects,
            # and project a combined version of the 2 onto the water nodes.
            self.setupScene(pos[2], not spec.cheap)
        
        #self.waterNodesQueue.append([size, pos, depth, spec])
        
        return self.__addWaterNodeNow(size, pos, depth, spec)
        
    def __addWaterNodeNow(self, size, pos, depth, spec):
        if not self.enabled:
            return
            
        for animTex in spec.animatedTextures:
            if animTex.texPath not in self.dudvs.keys():
                frames = []
                vfs = VirtualFileSystem.getGlobalPtr()
                for vFile in vfs.scanDirectory(animTex.texPath + "/"):
                    frames.append(loader.loadTexture(vFile.getFilename()))
                self.dudvs[animTex.texPath] = frames
        
        if not isinstance(size, tuple):
            size = (-size, size, -size, size)
        node = WaterNode(size, pos, depth, spec)
        node.setup()
        node.enableEffects(self.reflScene, self.refrScene, self.underwaterRefrScene)

        self.waterNodes.append(node)

        return node

    def clearWaterNode(self, node):
        if CIGlobals.isNodePathOk(node):
            node.removeNode()
        if node in self.waterNodes:
            self.waterNodes.remove(node)

        if len(self.waterNodes) == 0 and self.hasScenes:
            self.cleanupScenes()

    def clearWaterNodes(self):
        if len(self.waterNodes) == 0:
            return

        for waterNode in self.waterNodes:
            waterNode.removeNode()

        self.waterNodes = []
        self.cleanupScenes()

    def cleanupScenes(self):
        self.stopUpdateTask()
        
        if self.reflScene:
            self.reflScene.cleanup()
            self.reflScene = None
        if self.refrScene:
            self.refrScene.cleanup()
            self.refrScene = None
        if self.underwaterRefrScene:
            self.underwaterRefrScene.cleanup()
            self.underwaterRefrScene = None
        
        self.hasScenes = False

    def startUpdateTask(self):
        taskMgr.add(self.update, "waterRefl-update", sort = -100)

    def stopUpdateTask(self):
        taskMgr.remove("waterRefl-update")

    def cleanup(self):
        if not self.enabled:
            return

        self.clearWaterNodes()
        
    def handleResolutionUpdate(self, newResolution):
        # We need to cleanup the scenes and generate new ones.
        self.reso = newResolution
        
        self.cleanupScenes()
        
        if len(self.waterNodes) > 0:
            firstNode = self.waterNodes[0]
            self.setupScene(firstNode.height)
            
            for node in self.waterNodes:
                # Let's update the textures on the shader inputs.
                node.enableEffects(self.reflScene, self.refrScene, self.underwaterRefrScene)

    def update(self, task):
        if not self.enabled:
            return task.done
           
        if self.areScenesReady():
            for data in self.waterNodesQueue:
                size, pos, depth, spec = data
                self.__addWaterNodeNow(size, pos, depth, spec)
                self.waterNodesQueue.remove(data)
                
        hasExpensive = self.hasWaterEffects()

        if hasExpensive:
            self.reflScene.camera.setMat(base.cam.getMat(render) * self.reflScene.plane.getReflectionMat())
            self.refrScene.camera.setMat(base.cam.getMat(render))
            self.underwaterRefrScene.camera.setMat(base.cam.getMat(render))

        foundCamSubmerged = False
        foundLocalAvTouching = WaterNode.Nothing
        waterLocalAvIsTouching = None
        waterCamIsTouching = None
        for waterNode in self.waterNodes:

            # Let's see if our camera is submerged in this water node.
            if not foundCamSubmerged:
                if waterNode.isTouchingWater(camera.getPos(render)):
                    waterCamIsTouching = waterNode
                    foundCamSubmerged = True
            
            if hasattr(base, 'localAvatar'):
                # Now, let's see if local avatar is touching this water node.
                if not foundLocalAvTouching:
                    test = waterNode.isInWater(base.localAvatar.getPos(render),
                                               base.localAvatar.getPos(render) + (0, 0, base.localAvatar.getHeight()))
                    if test != WaterNode.Nothing:
                        foundLocalAvTouching = test
                        waterLocalAvIsTouching = waterNode

            for animTex in waterNode.spec.animatedTextures:
                frames = self.dudvs[animTex.texPath]
                frameNum = int((globalClock.getFrameTime() * animTex.frameRate) % len(frames))
                animFrame = frames[frameNum]
                waterNode.topNP.setShaderInput(animTex.shaderInput, animFrame)
                waterNode.botNP.setShaderInput(animTex.shaderInput, animFrame)

        if foundCamSubmerged != self.cameraSubmerged:
            if foundCamSubmerged:

                if hasExpensive:
                    self.reflScene.disable()
                    self.refrScene.disable()
                    self.underwaterRefrScene.enable()

                self.underwaterSound.play()
                olc = self.getHoodOLC()
                if olc:
                    olc.modifyFog(waterCamIsTouching.spec.fog.color, waterCamIsTouching.spec.fog.density)

            else:
                if hasExpensive:
                    self.underwaterRefrScene.disable()
                    self.reflScene.enable()
                    self.refrScene.enable()

                self.underwaterSound.stop()
                olc = self.getHoodOLC()
                if olc:
                    olc.resetFog()

        if self.localAvTouching != foundLocalAvTouching:
            if foundLocalAvTouching & WaterNode.Submerged:
                base.localAvatar.isSwimming = True
                base.localAvatar.touchingWater = False
                base.localAvatar.walkControls.controller.setTouchingWater(False)
                base.localAvatar.walkControls.setCurrentSurface('swim')
                base.localAvatar.walkControls.setControlScheme(base.localAvatar.walkControls.SSwim)
                if waterLocalAvIsTouching:
                    base.localAvatar.b_splash(base.localAvatar.getX(render),
                                              base.localAvatar.getY(render),
                                              waterLocalAvIsTouching.height)
            elif foundLocalAvTouching & WaterNode.Touching:
                self.playWadeSound()
                base.localAvatar.isSwimming = False
                base.localAvatar.touchingWater = True
                base.localAvatar.walkControls.controller.setTouchingWater(True)
                base.localAvatar.walkControls.setCurrentSurface('slosh')
                base.localAvatar.walkControls.setControlScheme(base.localAvatar.walkControls.SDefault)
            else:
                base.localAvatar.isSwimming = False
                base.localAvatar.touchingWater = False
                base.localAvatar.walkControls.controller.setTouchingWater(False)
                base.localAvatar.walkControls.setCurrentSurface('default')
                base.localAvatar.walkControls.setControlScheme(base.localAvatar.walkControls.SDefault)
                self.playWadeSound()

        self.cameraSubmerged = foundCamSubmerged
        self.localAvTouching = foundLocalAvTouching
        
        return task.cont
