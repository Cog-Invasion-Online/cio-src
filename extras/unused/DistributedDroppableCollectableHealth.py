"""

  Filename: DistributedDroppableCollectableHealth.py
  Created by: blach (02Apr15)

"""

from DistributedDroppableCollectableObject import DistributedDroppableCollectableObject
from direct.directnotify.DirectNotifyGlobal import directNotify

class DistributedDroppableCollectableHealth(DistributedDroppableCollectableObject):
	notify = directNotify.newCategory("DistributedDroppableCollectableHealth")

	def __init__(self, cr):
		DistributedDroppableCollectableObject.__init__(self, cr)
		self.collectSfx = None
		self.disabled = 0

	def setDisabled(self, value):
		self.disabled = value
		if value:
			self.ignoreCollisions()
			self.hide()
		else:
			self.show()
			self.acceptCollisions()

	def getDisabled(self):
		return self.disabled

	def load(self):
		self.collectSfx = base.loadSfx("phase_4/audio/sfx/SZ_DD_treasure.mp3")
		DistributedDroppableCollectableObject.load(self)

	def handleCollisions(self, entry):
		if base.localAvatar.getHealth() < base.localAvatar.getMaxHealth():
			self.collectSfx.play()
			DistributedDroppableCollectableObject.handleCollisions(self, entry)

	def unload(self):
		self.collectSfx = None
		self.disabled = None
		DistributedDroppableCollectableObject.unload(self)
