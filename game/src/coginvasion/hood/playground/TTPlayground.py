# Filename: TTPlayground.py
# Created by:  blach (25Oct15)

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.interval.SoundInterval import SoundInterval

from src.coginvasion.holiday.HolidayManager import HolidayType
import Playground, random

class TTPlayground(Playground.Playground):
	notify = directNotify.newCategory("TTPlayground")

	def __init__(self, loader, parentFSM, doneEvent):
		Playground.Playground.__init__(self, loader, parentFSM, doneEvent)
		self.birdSfx = None
		self.christmasTree = None

	def load(self):
		Playground.Playground.load(self)
		
		if base.cr.holidayManager.getHoliday() == HolidayType.CHRISTMAS:
			# Let's make the Christmas Tree
			self.christmasTree = loader.loadModel('phase_4/models/props/winter_tree_Christmas.bam')
			self.christmasTree.reparentTo(self.loader.geom)
			self.christmasTree.setPos(0.651558, 23.0954, 0.00864142)
			self.christmasTree.setH(-183.108)
			
			# Winter ground
			winterTxt = loader.loadTexture('winter/maps/tt_winter_ground.png')
			self.loader.geom.find('**/ground_center').setTexture(winterTxt, 1)

	def unload(self):
		Playground.Playground.unload(self)
		
		if self.christmasTree:
			self.christmasTree.removeNode()
			self.christmasTree = None

	def enter(self, requestStatus):
		Playground.Playground.enter(self, requestStatus)
		for tree in self.loader.trees:
			tree.reparentTo(render)
		self.startBirds()

	def startBirds(self):
		taskMgr.add(self.birdTask, "TTPlayground-birdTask")

	def stopBirds(self):
		taskMgr.remove("TTPlayground-birdTask")
		if self.birdSfx:
			self.birdSfx.finish()
			self.birdSfx = None

	def birdTask(self, task):
		noiseFile = random.choice(self.loader.birdNoises)
		noise = base.loadSfx(noiseFile)
		if self.birdSfx:
			self.birdSfx.finish()
			self.birdSfx = None
		self.birdSfx = SoundInterval(noise)
		self.birdSfx.start()
		task.delayTime = random.random() * 20 + 1
		return task.again

	def exit(self):
		for tree in self.loader.trees:
			tree.reparentTo(hidden)
		self.stopBirds()
		Playground.Playground.exit(self)
