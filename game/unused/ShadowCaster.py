# Filename: ShadowCaster.py
# Created by:  blach (03Jul15)

from panda3d.core import Camera, OrthographicLens, Texture, NodePath, TextureStage, TexGenAttrib, VBase4
from direct.showbase.DirectObject import DirectObject

from lib.coginvasion.globals import CIGlobals

class ShadowCaster(DirectObject):
	
	def __init__(self):
		DirectObject.__init__(self)
		self.shadowCamArm = None
		self.casterState = None
		self.shadowBuffer = None
		self.shadowColor = 0.5
		self.shadowColorIndex = 0
		self.shadowsEnabled = 0
		self.clearColor = VBase4(1, 1, 1, 1)
		self.setupTask = None
		self.shadowsHidden = False
		
	def enable(self):
		camNode = Camera('shadowCam')
		camNode.setCameraMask(CIGlobals.ShadowCameraBitmask)
		self.shadowLens = OrthographicLens()
		self.shadowLens.setFilmSize(60 * 4, 60 * 4)
		camNode.setLens(self.shadowLens)
		self.shadowCamArm = camera.attachNewNode('shadowCamArm')
		self.shadowCam = self.shadowCamArm.attachNewNode(camNode)
		self.shadowCamArm.setPos(0, 40, 0)
		self.shadowCam.setPos(0, -40, 0)
		self.shadowTex = Texture('shadow')
		self.shadowTex.setBorderColor(self.clearColor)
		self.shadowTex.setWrapU(Texture.WMBorderColor)
		self.shadowTex.setWrapV(Texture.WMBorderColor)
		self.casterState = NodePath('temp')
		self.casterState.setColorScaleOff(10)
		self.casterState.setColor(self.shadowColor, self.shadowColor, self.shadowColor, 1, 10)
		self.casterState.setTextureOff(10)
		self.casterState.setLightOff(10)
		self.casterState.setFogOff(10)
		camNode.setInitialState(self.casterState.getState())
		render.hide(CIGlobals.ShadowCameraBitmask)
		self.shadowStage = TextureStage('shadow')
		self.shadowStage.setSort(1000)
		self.turnOnShadows()
		
	def disable(self):
		if not self.shadowsEnabled:
			return None
        
		self.shadowsEnabled = 0
		self.shadowCamArm.removeNode()
		self.shadowCam.removeNode()
		base.camNode.clearTagState('caster')
		self.turnOffShadows()
		self.shadowTex = None
		self.shadowStage = None
		
	def turnOnShadows(self):
		render.setTexProjector(self.shadowStage, NodePath(), self.shadowCam)
		
	def turnOffShadows(self):
		render.clearTexProjector(self.shadowStage)
		self.destroyBuffer()
		
	def createBuffer(self):
		if not base.win.getGsg():
			return None
		
		self.shadowBuffer = base.win.makeTextureBuffer('shadow', 1024 * 4, 1024 * 4, tex = self.shadowTex)
		self.shadowBuffer.setSort(30)
		self.shadowBuffer.setClearColor(self.clearColor)
		dr = self.shadowBuffer.makeDisplayRegion()
		dr.setCamera(self.shadowCam)
		
		self.setupCamera()
		
	def setupCamera(self):
		groundState = NodePath('temp')
		groundState.setTexture(self.shadowStage, self.shadowTex)
		groundState.setTexGen(self.shadowStage, TexGenAttrib.MWorldPosition)
		base.camNode.setTagStateKey('cam')
		base.camNode.setTagState('shground', groundState.getState())
		
	def destroyBuffer(self):
		if self.shadowBuffer:
			base.graphicsEngine.removeWindow(self.shadowBuffer)
			self.shadowBuffer = None
