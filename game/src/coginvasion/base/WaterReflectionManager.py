"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file WaterReflectionManager.py
@author Brian Lach
@date September 26, 2017

"""

from panda3d.core import (BitMask32, Plane, NodePath, CullFaceAttrib, Texture,
                          TextureStage, Point3, PlaneNode, VBase4, Vec3)

from direct.filter.CommonFilters import CommonFilters

REFL_CAM_BITMASK = BitMask32.bit(10)

class WaterReflectionManager:

    def __init__(self):
        self.waterNodes = []
       
        wbuffer = base.win.makeTextureBuffer("water", 512, 512)
        wbuffer.setClearColorActive(True)
        wbuffer.setClearColor(base.win.getClearColor())

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

        self.ts = TextureStage("reflection")
        self.ts.setMode(TextureStage.MModulate)
        #self.ts.setMode(TextureStage.MAdd)
        #self.ts.setColor(VBase4(0.2, 0.2, 0.2, 1.0))

        self.filter = CommonFilters(wbuffer, self.wcamera)
        self.filter.setBlurSharpen(0.15)

        taskMgr.add(self.update, "waterRefl-update-" + str(id(self)))

        #base.bufferViewer.toggleEnable()

    def clearPlane(self):
        if self.wplanenp:
            self.wplanenp.removeNode()
            self.wplanenp = None
        self.wplane = None
        self.planeNode = None

    def makePlane(self, height):
        self.clearPlane()

        self.wplane = Plane(Vec3(0, 0, 1), Point3(0, 0, height))
        self.planeNode = PlaneNode("water", self.wplane)
        self.wplanenp = render.attachNewNode(self.planeNode)

        tmpnp = NodePath("StateInitializer")
        tmpnp.setClipPlane(self.wplanenp)
        tmpnp.setAttrib(CullFaceAttrib.makeReverse())
        self.wcamera.node().setInitialState(tmpnp.getState())
    
    def addWaterNode(self, node, height):
        self.waterNodes.append(node)
        node.hide(REFL_CAM_BITMASK)
        node.projectTexture(self.ts, self.wtexture, self.wcamera)

        self.makePlane(height)

    def clearWaterNodes(self):
        for node in self.waterNodes:
            if not node.isEmpty():
                node.clearProjectTexture(self.ts)
        self.clearPlane()

    def cleanup(self):
        taskMgr.remove("waterRefl-update-" + str(id(self)))
        self.clearWaterNodes()
        self.wplane = None
        self.wcamera.removeNode()
        self.wcamera = None
        self.water = None

    def update(self, task):
        if not self.wplane or not self.wcamera:
            return task.cont

        self.wcamera.setMat(base.cam.getMat(render) * self.wplane.getReflectionMat())
        return task.cont
