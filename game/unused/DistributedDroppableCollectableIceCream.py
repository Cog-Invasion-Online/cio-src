"""

  Filename: DistributedDroppableCollectableIceCream.py
  Created by: blach (03Apr15)

"""

from DistributedDroppableCollectableHealth import DistributedDroppableCollectableHealth
from direct.directnotify.DirectNotifyGlobal import directNotify

class DistributedDroppableCollectableIceCream(DistributedDroppableCollectableHealth):
	notify = directNotify.newCategory("DistributedDroppableCollectableIceCream")
	
	def __init__(self, cr):
		DistributedDroppableCollectableHealth.__init__(self, cr)
		self.iceCream = None
		
	def loadObject(self):
		self.removeObject()
		self.iceCream = loader.loadModel("phase_4/models/props/icecream.bam")
		self.iceCream.reparentTo(self)
		DistributedDroppableCollectableHealth.loadObject(self)
		
	def removeObject(self):
		if self.iceCream:
			self.iceCream.removeNode()
			self.iceCream = None
		DistributedDroppableCollectableHealth.removeObject(self)
