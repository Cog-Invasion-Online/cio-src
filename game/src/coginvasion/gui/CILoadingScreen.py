"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file CILoadingScreen.py
@author Brian Lach
@date June 17, 2014

"""

from direct.gui.DirectGui import OnscreenText
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.showbase.Transitions import Transitions
from src.coginvasion.base import FileUtility

loadernotify = directNotify.newCategory("CILoadingScreen")

class CILoadingScreen:
	
	def __init__(self):
		self.transitions = Transitions(loader)
		
	def createMenu(self):
		"""
		self.menuBg = loader.loadModel("phase_3/models/gui/loading-background.bam")
		self.menuBg.find('**/fg').removeNode()
		
		#self.trolleyTex = loader.loadTexture("phase_3.5/maps/trolley.jpg", "phase_3.5/maps/trolley_a.rgb")
		#self.trolley = OnscreenImage(image=self.trolleyTex, scale=(0.5, 0, 0.6))
		#self.trolley.setTransparency(True)
		
		#self.logo = loader.loadTexture("phase_3/maps/toontown_online_logo.tif")
		#self.logoImg = OnscreenImage(image=self.logo, scale=(0.6, 0, 0.225), pos=(0, 0, 0.5))
		#self.logoImg.setTransparency(True)
		
		self.logo = loader.loadTexture("phase_3/maps/CogInvasion_Logo.png")
		self.logoImg = OnscreenImage(image = self.logo, scale = (1.0, 0, 0.6))
		self.logoImg.setTransparency(True)
		self.logoImg.reparentTo(hidden)
		
		self.bg_img = OnscreenImage(image=self.menuBg, parent=render2d)
		"""
		base.graphicsEngine.renderFrame()
		base.graphicsEngine.renderFrame()
		self.version_lbl = OnscreenText(text=metadata.getBuildInformation(), scale=0.06,
                                        pos=(-1.32, -0.97, -0.97), align=TextNode.ALeft, fg = loader.progressScreen.Color)
		
	def beginLoadGame(self):
		# We'll pre-load some models so we don't get any lag
		# when they are actually loaded into the game.
		phasesToScan = ["models", "phase_3/models", "phase_3.5/models", "phase_4/models",
			#"phase_5/models", "phase_5.5/models", "phase_6/models", "phase_7/models",
			#"phase_8/models", "phase_9/models", "phase_10/models", "phase_11/models",
			#"phase_12/models", "phase_13/models"]
			]
		self.models = FileUtility.findAllModelFilesInVFS(phasesToScan)
		# self.models = []
		for model in self.models:
			loader.loadModel(model)
			loader.progressScreen.tick()
		doneInitLoad()
		self.destroy()
		
	def loadModelDone(self, array):
		self.modelsLoaded += 1
		if self.modelsLoaded == len(self.models):
			doneInitLoad()
			self.destroy()
				
	def destroy(self):
		self.version_lbl.destroy()
		#self.bg_img.destroy()
		#self.menuBg.removeNode()
		#self.trolley.destroy()
		#self.logoImg.destroy()
		#del self.menuBg
		#del self.bg_img
		#del self.trolley
		#del self.logoImg
		return
