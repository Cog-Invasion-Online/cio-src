"""

  Filename: DistributedDroppableCollectableJellybeansAI.py
  Created by: blach (22Mar15)

"""

from direct.directnotify.DirectNotifyGlobal import directNotify
from DistributedDroppableCollectableObjectAI import DistributedDroppableCollectableObjectAI

class DistributedDroppableCollectableJellybeansAI(DistributedDroppableCollectableObjectAI):
	notify = directNotify.newCategory("DistributedDroppableCollectableJellybeansAI")
	
	def __init__(self, air):
		DistributedDroppableCollectableObjectAI.__init__(self, air)
		self.value = 0
		
	def setValue(self, value):
		self.value = value
		
	def getValue(self):
		return self.value
		
	def collectedObject(self):
		avId = self.air.getAvatarIdFromSender()
		avatar = self.air.doId2do.get(avId)
		if avatar:
			avatar.b_setMoney(avatar.getMoney() + self.getValue())
		DistributedDroppableCollectableObjectAI.collectedObject(self)
		
	def delete(self):
		self.value = None
		DistributedDroppableCollectableObjectAI.delete(self)
