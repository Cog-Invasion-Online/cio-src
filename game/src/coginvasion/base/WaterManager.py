

from panda3d.core import BoundingBox
from panda3d.core import CardMaker
from panda3d.core import CullFaceAttrib
from panda3d.core import Fog
from panda3d.core import Plane
from panda3d.core import PlaneNode
from panda3d.core import Point3
from panda3d.core import RenderState
from panda3d.core import Shader
from panda3d.core import ShaderPool
from panda3d.core import Texture
from panda3d.core import TextureStage
from panda3d.core import TransparencyAttrib
from panda3d.core import Vec3
from panda3d.core import Vec4

from direct.filter.FilterManager import FilterManager
from direct.gui.DirectGui import OnscreenImage

from src.coginvasion.globals import CIGlobals

class WaterManager:

    def __init__(self):
    
        self.enabled = True
        
        sMgr = CIGlobals.getSettingsMgr()
        reso = sMgr.ReflectionQuality[sMgr.getSetting("refl").getValue()]
        if reso == 0:
            self.enabled = False
            return
    
        self.waterPlaneNP = None
    
        self.waterNodes = []

        # Buffer and reflection camera
        buffer = base.win.makeTextureBuffer('waterBuffer', reso, reso)
        buffer.setClearColor(Vec4(0, 0, 0, 1))

        cfa = CullFaceAttrib.makeReverse()
        rs = RenderState.make(cfa)

        self.watercamNP = base.makeCamera(buffer)
        self.watercamNP.reparentTo(render)
       
        
        self.makePlane(0.0)

        cam = self.watercamNP.node()
        cam.getLens().setFov(base.camLens.getFov())
        cam.getLens().setNear(1)
        cam.getLens().setFar(5000)
        cam.setInitialState(rs)
        cam.setTagStateKey('Clipped')
        
        self.ts0 = TextureStage("tex_0")
        self.tex0 = buffer.getTexture()
        self.tex0.setWrapU(Texture.WMClamp)
        self.tex0.setWrapV(Texture.WMClamp)
        
        self.ts1 = TextureStage("tex_1")
        self.waterTex = loader.loadTexture('phase_3/maps/water_distort.png')
        self.waterQuad = None
        
        self.waterStage = TextureStage("waterStage")

        image0 = OnscreenImage(image = self.tex0, scale = 0.3, pos = (-0.5, 0, 0.7))
        image1 = OnscreenImage(image = waterTex, scale = 0.3, pos = (0.5, 0, 0.7))

        taskMgr.add(self.update, "waterTask")
        
    def makePlane(self, height):
        if not self.enabled:
            return
        self.clearPlane()
        # Reflection plane
        self.waterPlane = Plane(Vec3(0, 0, height), Point3(0, 0, height))
        planeNode = PlaneNode('waterPlane')
        planeNode.setPlane(self.waterPlane)
        self.waterPlaneNP = render.attachNewNode(planeNode)
    
    def clearPlane(self):
        if not self.enabled:
            return
        if self.waterPlaneNP:
            self.waterPlaneNP.removeNode()
            self.waterPlaneNP = None
        
    def addWaterNode(self, node, height):
        if not self.enabled:
            return
        self.waterNodes.append(node)
        node.setTransparency(TransparencyAttrib.MAlpha)
        node.setTexture(ts0, self.tex0)
        node.setTexture(ts1, self.waterTex)
        node.setShaderInput('wateranim', Vec4(0.03, -0.015, 64.0, 0)) # vx, vy, scale, skip
        # offset, strength, refraction factor (0=perfect mirror, 1=total refraction), refractivity
        node.setShaderInput('waterdistort', Vec4(0.4, 4.0, 0.25, 0.45))
        node.setShaderInput('time', 0)
        node.setShader(loader.loadShader("phase_3/models/shaders/water.sha"))
        node.projectTexture(self.waterStage, self.tex0, self.watercamNP)

        self.makePlane(height)

    def clearWaterNodes(self):
        if not self.enabled:
            return
        for node in self.waterNodes:
            if not node.isEmpty():
                node.setShaderOff(1)
                node.setTextureOff(1)
        self.waterNodes = []
        self.clearPlane()

    def update(self, task):
        if not self.enabled:
            return
        # update matrix of the reflection camera
        mc = base.camera.getMat()
        mf = self.waterPlane.getReflectionMat()
        self.watercamNP.setMat(mc * mf)
        for node in self.waterNodes:
            if not node.isEmpty():
                node.setShaderInput("time", task.time)
        return task.cont
