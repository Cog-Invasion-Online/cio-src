"""

  Filename: DroppableCollectableJellybeanJar.py
  Created by: blach (22Mar15)

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from DroppableCollectableJellybeans import DroppableCollectableJellybeans

class DroppableCollectableJellybeanJar(DroppableCollectableJellybeans):
	notify = directNotify.newCategory("DroppableCollectableJellybeanJar")

	def __init__(self):
		DroppableCollectableJellybeans.__init__(self)
		self.jar = None

	def loadObject(self):
		self.removeObject()
		self.jar = loader.loadModel("phase_5.5/models/estate/jellybeanJar.bam")
		self.jar.setZ(1.5)
		self.jar.setTwoSided(1)
		self.jar.reparentTo(self)

	def removeObject(self):
		if self.jar:
			self.jar.removeNode()
			self.jar = None

	def load(self):
		self.collectSfx = base.loadSfx("phase_3.5/audio/sfx/ci_s_money_bigBucks.ogg")
		DroppableCollectableJellybeans.load(self)
