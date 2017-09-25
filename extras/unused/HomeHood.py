"""
  
  Filename: HomeHood.py
  Created by: blach (19June14)
  
"""

from lib.coginvasion.globals import CIGlobals
from lib.coginvasion.hood.SkyUtil import SkyUtil
from lib.coginvasion.dna.DNAParser import *

from panda3d.core import BitMask32, TransparencyAttrib, NodePath

class HomeHood:
	dnaStore = DNAStorage()
	def createHood(self, loadStorage = 1):
		self.isLoaded = 0
		if loadStorage:
			loadDNAFile(self.dnaStore, "phase_5.5/dna/storage_estate.dna")
		node = loadDNAFile(self.dnaStore, "phase_5.5/dna/estate_1.dna")
		if node.getNumParents() == 1:
			self.geom = NodePath(node.getParent(0))
			self.geom.reparentTo(hidden)
		else:
			self.geom = hidden.attachNewNode(self.node)
		gsg = base.win.getGsg()
		if gsg:
			self.geom.prepareScene(gsg)
		self.geom.setName('home')
		
		self.geom.find('**/Path').setTransparency(TransparencyAttrib.MBinary, 1)
		
		self.sky = loader.loadModel("phase_3.5/models/props/TT_sky.bam")
		self.sky.reparentTo(self.geom)
		self.sky.setPos(-4.99989, -0.000152588, 2.28882e-005)
		
		self.geom.find('**/terrain').setCollideMask(BitMask32.allOff())
		self.geom.find('**/terrain_barrier').node().setIntoCollideMask(CIGlobals.WallBitmask)
		self.geom.find("**/collision_fence").node().setIntoCollideMask(CIGlobals.WallBitmask)
		self.geom.find('**/collision4').node().setIntoCollideMask(CIGlobals.FloorBitmask)
		self.geom.find("**/collision3").node().setIntoCollideMask(CIGlobals.FloorBitmask)
		self.geom.find("**/collision1").node().setIntoCollideMask(CIGlobals.FloorBitmask)
		
		self.geom.reparentTo(render)
		
		messenger.send("loadedHood")
		
		self.skyUtil = SkyUtil()
		self.skyUtil.startSky(self.sky)
		
		self.isLoaded = 1
		
	def unloadHood(self):
		self.skyUtil.stopSky()
		self.geom.remove()
		self.isLoaded = 0
		
		
