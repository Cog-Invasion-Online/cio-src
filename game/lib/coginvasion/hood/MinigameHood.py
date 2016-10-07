"""

  Filename: MinigameHood.py
  Created by: blach (04Oct14)
  
"""

from lib.coginvasion.hood.SkyUtil import SkyUtil
from lib.coginvasion.dna.DNAParser import *

from pandac.PandaModules import NodePath

class MinigameHood:
	
	def __init__(self, cr):
		self.cr = cr
		self.isLoaded = 0
		self.dnaStore = DNAStorage()
		
	def createHood(self, loadStorage = 1):
		if loadStorage:
			loadDNAFile(self.dnaStore, "phase_13/dna/storage_party_sz.dna")
		self.node = loadDNAFile(self.dnaStore, "phase_13/dna/party_sz.dna")
		if self.node.getNumParents() == 1:
			self.geom = NodePath(self.node.getParent(0))
			self.geom.reparentTo(hidden)
		else:
			self.geom = hidden.attachNewNode(self.node)
		gsg = base.win.getGsg()
		if gsg:
			self.geom.prepareScene(gsg)
		self.geom.setName('minigames')
		
		base.hoodBGM = base.loadMusic("phase_13/audio/bgm/party_original_theme.ogg")
		base.hoodBGM.setVolume(0.7)
		base.hoodBGM.setLoop(True)
		base.hoodBGM.play()
		
		self.sky = loader.loadModel("phase_3.5/models/props/TT_sky.bam")
		self.sky.reparentTo(self.geom)
		self.sky.setPos(9.15527e-005, -1.90735e-006, 2.6226e-006)
		self.sky.setH(-90)
		
		self.skyUtil = SkyUtil()
		self.skyUtil.startSky(self.sky)
		
		self.geom.reparentTo(render)

		self.isLoaded = 1
		messenger.send("loadedHood")
		
	def unloadHood(self):
		self.isLoaded = 0
		self.skyUtil.stopSky()
		self.geom.removeNode()
		base.hoodBGM.stop()
		
