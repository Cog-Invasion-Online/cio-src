"""

  Filename: DistributedDroppableCollectableHealthAI.py
  Created by: blach (03Apr15)

"""

from DistributedDroppableCollectableObjectAI import DistributedDroppableCollectableObjectAI
from direct.directnotify.DirectNotifyGlobal import directNotify

class DistributedDroppableCollectableHealthAI(DistributedDroppableCollectableObjectAI):
	notify = directNotify.newCategory("DistributedDroppableCollectableHealthAI")
	disableInterval = 30.0
	
	def __init__(self, air):
		DistributedDroppableCollectableObjectAI.__init__(self, air)
		self.health = 0
		self.disabled = 0
        
	def setDisabled(self, value):
		self.disabled = value

	def d_setDisabled(self, value):
		self.sendUpdate("setDisabled", [value])

	def b_setDisabled(self, value):
		self.setDisabled(value)
		self.d_setDisabled(value)

	def getDisabled(self):
		return self.disabled

	def disableDone(self, task):
		self.b_setDisabled(0)
		return task.done
		
	def setHealth(self, hp):
		"""
		Sets how much hp the avatar gains when the object is collected.
		"""
		
		self.health = hp
		
	def getHealth(self):
		return self.health
		
	def collectedObject(self):
		if self.getDisabled():
			return
		avId = self.air.getAvatarIdFromSender()
		av = self.air.doId2do.get(avId, None)
		if av:
			if av.getHealth() < av.getMaxHealth():
				health2Give = self.getHealth()
				if av.getMaxHealth() - av.getHealth() < 10:
					health2Give = av.getMaxHealth() - av.getHealth()
				av.b_setHealth(av.getHealth() + health2Give)
				av.d_announceHealth(1, health2Give)
			else:
				return
		self.b_setDisabled(1)
		taskMgr.doMethodLater(self.disableInterval, self.disableDone, self.uniqueName("disableInterval"))
		
	def disable(self):
		taskMgr.remove(self.uniqueName("disableInterval"))
		DistributedDroppableCollectableObjectAI.disable(self)
		
	def delete(self):
		self.health = None
		self.disabled = None
		DistributedDroppableCollectableObjectAI.delete(self)
