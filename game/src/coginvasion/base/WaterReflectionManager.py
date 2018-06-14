"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file WaterReflectionManager.py
@author Brian Lach
@date September 26, 2017

"""

from panda3d.core import (BitMask32, Plane, NodePath, CullFaceAttrib, Texture,
                          TextureStage, Point3, PlaneNode, VBase4, Vec3, WindowProperties,
                          FrameBufferProperties, GraphicsPipe, GraphicsOutput, TransparencyAttrib,
                          Material)

from direct.filter.FilterManager import FilterManager
from direct.gui.DirectGui import OnscreenImage

from src.coginvasion.globals import CIGlobals

REFL_CAM_BITMASK = BitMask32.bit(10)

class WaterReflectionManager:

    def __init__(self):
        self.enabled = True
        
        sMgr = CIGlobals.getSettingsMgr()
        reso = sMgr.ReflectionQuality[sMgr.getSetting("refl")]
        if reso == 0:
            self.enabled = False
            return

        self.waterNodes = []

        wbuffer = base.win.makeTextureBuffer("water", reso, reso)
        wbuffer.setSort(-1)
        wbuffer.setClearColorActive(True)
        wbuffer.setClearColor(base.win.getClearColor())
        
        depthTex = Texture("depth")
        depthTex.setWrapU(Texture.WMClamp)
        depthTex.setWrapV(Texture.WMClamp)
        wbuffer.addRenderTexture(depthTex, GraphicsOutput.RTMBindOrCopy,
                                      GraphicsOutput.RTPDepth)
        

        self.wcamera = base.makeCamera(wbuffer)
        self.wcamera.reparentTo(render)
        self.wcamera.node().setLens(base.camLens)
        self.wcamera.node().setCameraMask(REFL_CAM_BITMASK)

        self.wtexture = wbuffer.getTexture()
        self.wtexture.setWrapU(Texture.WMClamp)
        self.wtexture.setWrapV(Texture.WMClamp)
        self.wtexture.setMinfilter(Texture.FTLinearMipmapLinear)
        self.wtexture.setMagfilter(Texture.FTLinearMipmapLinear)

        self.wplanenp = None

        self.makePlane(0.0)
        
        self.filterMgr = FilterManager(wbuffer, self.wcamera)

        self.ts = TextureStage("reflection")
        self.ts.setMode(TextureStage.MModulate)
        
        self.blur = []
        
        blur0 = Texture("blur0")
        blur0.setWrapU(Texture.WMClamp)
        blur0.setWrapV(Texture.WMClamp)
        blur1 = Texture("blur1")
        blur1.setWrapU(Texture.WMClamp)
        blur1.setWrapV(Texture.WMClamp)
        self.blur.append(self.filterMgr.renderQuadInto(colortex=blur0,div=2))
        self.blur.append(self.filterMgr.renderQuadInto(colortex=blur1))
        self.blur[0].setShaderInput("src", self.wtexture)
        self.blur[0].setShader(loader.loadShader("phase_3/models/shaders/filter-blurx.sha"))
        self.blur[1].setShaderInput("src", blur0)
        self.blur[1].setShader(loader.loadShader("phase_3/models/shaders/filter-blury.sha"))
        self.currParams = [1, 100, 1, 1000 / (1000 - 1)]
        dofTex = Texture("dof")
        dofTex.setWrapU(Texture.WMClamp)
        dofTex.setWrapV(Texture.WMClamp)
        self.dofQuad = self.filterMgr.renderQuadInto(colortex = dofTex)
        self.dofQuad.setShaderInput("src", self.wtexture)
        self.dofQuad.setShaderInput("dtex", depthTex)
        self.dofQuad.setShaderInput("blurtex", blur1)
        self.dofQuad.setShaderInput("param1", self.currParams)
        self.dofQuad.setShader(loader.loadShader("phase_3/models/shaders/dof.sha"))
        
        self.finalTex = Texture("finalWater")
        self.finalTex.setWrapU(Texture.WMClamp)
        self.finalTex.setWrapV(Texture.WMClamp)
        
        self.waveQuad = self.filterMgr.renderQuadInto(colortex = self.finalTex)
        self.waveQuad.setShaderInput("src", dofTex)
        self.waveQuad.setShaderInput("time", 0.0)
        self.waveQuad.setShader(loader.loadShader("phase_3/models/shaders/waves.sha"))

        #OnscreenImage(image = self.wtexture, scale = 0.3, pos = (-0.7, 0, -0.7))
        #OnscreenImage(image = depthTex, scale = 0.3, pos = (0, 0, -0.7))
        #OnscreenImage(image = self.finalTex, scale = 0.3, pos = (0.7, 0, -0.7))

        taskMgr.add(self.update, "waterRefl-update-" + str(id(self)), sort = 45)

    def clearPlane(self):
        if not self.enabled:
            return
        if self.wplanenp:
            self.wplanenp.removeNode()
            self.wplanenp = None
        self.wplane = None
        self.planeNode = None

    def makePlane(self, height):
        if not self.enabled:
            return
        self.clearPlane()

        self.wplane = Plane(Vec3(0, 0, 1), Point3(0, 0, height))
        self.planeNode = PlaneNode("water", self.wplane)
        self.wplanenp = render.attachNewNode(self.planeNode)

        tmpnp = NodePath("StateInitializer")
        tmpnp.setClipPlane(self.wplanenp)
        tmpnp.setAttrib(CullFaceAttrib.makeReverse())
        self.wcamera.node().setInitialState(tmpnp.getState())
    
    def addWaterNode(self, node, height):
        if not self.enabled:
            return
        self.waterNodes.append(node)

        mat = Material()
        mat.setShininess(40)
        mat.setSpecular((1, 1, 1, 1))
        node.setMaterial(mat, 5)
        node.setTransparency(TransparencyAttrib.MAlpha, 1)
        node.setTexture(loader.loadTexture("phase_14/maps/water_surface.png"), 1)
        ts = TextureStage('water_nm')
        ts.setMode(TextureStage.MNormal)
        node.setTexture(ts, loader.loadTexture("phase_14/maps/water_surface_normal.png"))
        node.hide(REFL_CAM_BITMASK)
        node.projectTexture(self.ts, self.finalTex, self.wcamera)

        self.makePlane(height)

    def clearWaterNodes(self):
        if not self.enabled:
            return
        for node in self.waterNodes:
            if not node.isEmpty():
                node.clearProjectTexture(self.ts)
        self.clearPlane()

    def cleanup(self):
        if not self.enabled:
            return
        taskMgr.remove("waterRefl-update-" + str(id(self)))
        self.clearWaterNodes()
        self.wplane = None
        self.wcamera.removeNode()
        self.wcamera = None
        self.wtexture = None
        self.water = None
        for blur in self.blur:
            blur.removeNode()
        self.blur = None
        self.dofQuad.removeNode()
        self.dofQuad = None
        self.ts = None
        self.waveQuad.removeNode()
        self.waveQuad = None
        self.finalTex = None
        self.currParams = None
        self.filterMgr.cleanup()
        self.filterMgr = None

    def update(self, task):
        if not self.enabled:
            return task.done
        if not self.wplane or not self.wcamera:
            return task.cont
        
        self.waveQuad.setShaderInput("time", globalClock.getFrameTime())
        self.wcamera.setMat(base.cam.getMat(render) * self.wplane.getReflectionMat())
        return task.cont
